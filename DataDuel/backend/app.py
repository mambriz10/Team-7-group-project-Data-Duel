from flask import Flask, redirect, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import json
import time
import sys

# Add parent directory to path to import Person, Score, etc.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_storage import DataStorage
from friends_storage import FriendsStorage
from strava_parser import StravaParser
from route_generator import SimpleRouteGenerator
from Person import Person
from Score import Score
from datetime import datetime
from supabase_stravaDB.strava_user import (
    # User & credentials
    create_leaderboard, add_member_to_leaderboard, insert_user_profile, fetch_person_response, save_credentials_new, save_credentials, 
    insert_person_response, load_credentials_from_supabase, CLIENT_ID, CLIENT_SECRET,
    # Token storage (Supabase)
    save_strava_tokens, get_strava_tokens, refresh_strava_token,
    # Friends system (Supabase)
    send_friend_request as supabase_send_request,
    accept_friend_request as supabase_accept_request,
    reject_friend_request as supabase_reject_request,
    remove_friend as supabase_remove_friend,
    get_friends_list as supabase_get_friends,
    get_pending_requests as supabase_get_pending,
    get_sent_requests as supabase_get_sent,
    get_friend_status as supabase_get_status,
    get_friend_profiles, search_users_by_name,
    # Legacy (deprecated)
    get_friends_user, add_friend
)


load_dotenv()

app = Flask(__name__)

# CORS: Allow requests from multiple origins (local + deployed)
CORS(app, origins=[
    "http://localhost:5500",                                    # Local development
    "http://127.0.0.1:5500",                                     # Local development (alternative)
    "https://team-7-group-project-data-duel.pages.dev",         # Cloudflare Pages (production)
    os.getenv("FRONTEND_URL", ""),                               # Custom frontend URL (if set)
])

# Initialize data storage
storage = DataStorage()
# friends_storage = FriendsStorage()  # DEPRECATED: Now using Supabase for friends

CREDENTIALS_FILE = "credentials.json"

# Strava OAuth Configuration
# In production (Render), these come from environment variables
# In development, they come from .env file or credentials.json
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://127.0.0.1:5000/auth/strava/callback")

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

def load_saved_credentials():
    global CLIENT_ID, CLIENT_SECRET
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)
            CLIENT_ID = data.get("client_id", CLIENT_ID)
            CLIENT_SECRET = data.get("client_secret", CLIENT_SECRET)

# Endpoint to save credentials from frontend
@app.route("/save-strava-credentials", methods=["POST"])
def save_strava_credentials():
    data = request.get_json()
    client_id = data.get("clientId")
    client_secret = data.get("clientSecret")
    access_token = data.get("access_token")

    save_credentials_new(client_id, client_secret, access_token)

    if not client_id or not client_secret:
        return jsonify({"error": "Missing client_id or client_secret"}), 400

    # Save to JSON file
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({
            "client_id": client_id,
            "client_secret": client_secret
        }, f)

    # Update in-memory variables
    global CLIENT_ID, CLIENT_SECRET
    CLIENT_ID = client_id
    CLIENT_SECRET = client_secret

    return jsonify({"status": "ok"})

@app.route("/")
def home():
    return jsonify({
        "message": "DataDuel API Server Running!",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth/strava",
            "profile": "/api/profile",
            "leaderboard": "/api/leaderboard",
            "sync": "/api/sync",
            "activities": "/strava/activities"
        }
    })

@app.route("/auth/strava")
def auth_strava():
    """Redirect to Strava OAuth authorization"""
    auth_url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&approval_prompt=auto"
        f"&scope=read,activity:read_all"
    )
    return redirect(auth_url)

@app.route("/auth/strava/callback")
def auth_callback():
    """Handle OAuth callback and exchange code for access token"""
    print("\n" + "="*80)
    print("[AUTH CALLBACK] Starting OAuth token exchange")
    print("="*80)
    
    code = request.args.get("code")
    print(f"[AUTH] Authorization code received: {code[:20]}..." if code else "[ERROR] No code received")
    
    if not code:
        print("[ERROR] Missing authorization code")
        return jsonify({"error": "Missing authorization code"}), 400

    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    
    print(f"[API] Requesting tokens from Strava...")
    print(f"   Client ID: {CLIENT_ID}")

    response = requests.post(token_url, data=payload)
    data = response.json()
    
    print(f"[API] Token response status: {response.status_code}")
    print(f"   Response keys: {list(data.keys())}")

    if "access_token" not in data:
        print(f"[ERROR] Failed to get access token")
        print(f"   Response: {json.dumps(data, indent=2)}")
        return jsonify({"error": "Failed to get access token", "details": data}), 400

    # Extract and validate athlete data
    print(f"\n[ATHLETE] Extracting athlete data from response...")
    athlete = data.get("athlete", {})
    
    if not athlete:
        print(f"[ERROR] No athlete data in response!")
        print(f"   Full response: {json.dumps(data, indent=2)}")
        return jsonify({"error": "No athlete data in response"}), 400
    
    print(f"   Athlete data keys: {list(athlete.keys())}")
    print(f"   Full athlete data: {json.dumps(athlete, indent=2)}")
    
    athlete_id = athlete.get("id")
    if not athlete_id:
        print(f"[ERROR] Athlete ID is missing!")
        return jsonify({"error": "Athlete ID missing from response"}), 400
    
    athlete_id = str(athlete_id)
    
    print(f"[SUCCESS] Token exchange successful!")
    print(f"   Athlete ID: {athlete_id}")
    print(f"   Athlete firstname: {athlete.get('firstname')}")
    print(f"   Athlete lastname: {athlete.get('lastname')}")
    print(f"   Athlete username: {athlete.get('username')}")
    print(f"   Athlete city: {athlete.get('city')}")
    print(f"   Athlete state: {athlete.get('state')}")

    # Store tokens securely in Supabase (for production) and file (for local dev fallback)
    print(f"\n[STORAGE] Saving tokens to Supabase...")
    token_result, token_error = save_strava_tokens(
        athlete_id,
        data["access_token"],
        data["refresh_token"],
        data["expires_at"]
    )
    
    if token_error:
        print(f"[WARNING] Failed to save tokens to Supabase: {token_error}")
        print(f"[FALLBACK] Saving tokens to tokens.json for local development...")
        # Fallback to file storage for local dev
        with open("tokens.json", "w") as f:
            json.dump({
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_at": data["expires_at"],
                "athlete_id": athlete_id
            }, f)
        print(f"[SUCCESS] Tokens saved to file (local dev fallback)")
    else:
        print(f"[SUCCESS] Tokens saved to Supabase successfully")
        # Also save to file for local dev compatibility
        try:
            with open("tokens.json", "w") as f:
                json.dump({
                    "access_token": data["access_token"],
                    "refresh_token": data["refresh_token"],
                    "expires_at": data["expires_at"],
                    "athlete_id": athlete_id
                }, f)
        except:
            pass  # File write not critical if Supabase worked
    
    # Create or update user in storage
    print(f"\n[PERSON] Creating Person object from athlete data...")
    print(f"   Passing athlete data to StravaParser.create_person_from_athlete()...")
    
    try:
        person = StravaParser.create_person_from_athlete(athlete)
        print(f"[SUCCESS] Person object created:")
        print(f"   Name (via name mangling): {person._Person__name}")
        print(f"   Username (via name mangling): {person._Person__user_name}")
        print(f"   Display name: {person.display_name}")
    except Exception as e:
        print(f"[ERROR] Failed to create Person object: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to create Person object", "details": str(e)}), 500
    
    # Build user_data dictionary
    print(f"\n[DATA] Building user_data dictionary...")
    
    # Extract location components
    city = athlete.get('city', '')
    state = athlete.get('state', '')
    location_parts = [part for part in [city, state] if part]
    location = ", ".join(location_parts) if location_parts else "Unknown"
    
    print(f"   City: '{city}'")
    print(f"   State: '{state}'")
    print(f"   Combined location: '{location}'")
    
    user_data = {
        "id": athlete_id,
        "name": person._Person__name,
        "username": person._Person__user_name,
        "display_name": person.display_name,
        "avatar": athlete.get("profile", ""),
        "location": location,
        "strava_id": athlete_id
    }
    
    print(f"\n[DATA] user_data dictionary built:")
    print(f"   Keys: {list(user_data.keys())}")
    print(f"   Values:")
    for key, value in user_data.items():
        print(f"      {key}: {value}")
    
    print(f"\n[STORAGE] Saving user data to storage...")
    print(f"   Calling storage.save_user({athlete_id}, user_data)")
    
    try:
        storage.save_user(athlete_id, user_data)
        print(f"[SUCCESS] User data saved successfully to DataStorage")
        
        # Verify the save by reading it back
        print(f"\n[VERIFY] Reading user data back from storage to verify...")
        verified_data = storage.get_user(athlete_id)
        if verified_data:
            print(f"[SUCCESS] Verification successful - user data found in storage")
            print(f"   Verified keys: {list(verified_data.keys())}")
            print(f"   Verified name: {verified_data.get('name')}")
        else:
            print(f"[WARNING] Could not verify user data - not found in storage!")
    except Exception as e:
        print(f"[ERROR] Failed to save user data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to save user data", "details": str(e)}), 500
    
    print(f"\n[REDIRECT] Redirecting to frontend...")
    print("="*80 + "\n")
    # Redirect to frontend - use environment variable or default to localhost for dev
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5500")
    return redirect(f"{frontend_url}/index.html")

def get_valid_token():
    """
    Load and refresh the access token if expired.
    Uses Supabase in production, falls back to file storage for local dev.
    
    Strategy:
    1. Try Supabase first (if USE_SUPABASE_STORAGE=true and athlete_id available)
    2. Fall back to file storage (local dev or if Supabase fails)
    """
    # Check if we should use Supabase (default: true for production)
    use_supabase = os.getenv("USE_SUPABASE_STORAGE", "true").lower() == "true"
    
    # Get athlete_id from file (if exists) to look up in Supabase
    FILE_NAME = "tokens.json"
    athlete_id = None
    
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as f:
                file_tokens = json.load(f)
                athlete_id = file_tokens.get("athlete_id")
        except:
            pass
    
    # Try Supabase first (production)
    if use_supabase and athlete_id:
        tokens, error = get_strava_tokens(athlete_id)
        if not error and tokens and tokens.get("access_token"):
            # Check if expired
            if time.time() > tokens.get("expires_at", 0):
                print("[TOKEN] Access token expired — refreshing from Supabase...")
                refreshed, refresh_error = refresh_strava_token(athlete_id, CLIENT_ID, CLIENT_SECRET)
                if not refresh_error:
                    tokens = refreshed
                    print("[TOKEN] Token refreshed and saved to Supabase")
                else:
                    print(f"[TOKEN] Supabase refresh failed: {refresh_error}, falling back to file")
                    use_supabase = False
            else:
                print("[TOKEN] Using valid token from Supabase")
                return tokens["access_token"], tokens.get("athlete_id")
    
    # Fallback to file storage (local development or if Supabase unavailable)
    if not os.path.exists(FILE_NAME):
        raise FileNotFoundError("tokens.json not found. Please authenticate first.")
    
    with open(FILE_NAME, "r") as f:
        tokens = json.load(f)

    # Check if expired
    if time.time() > tokens.get("expires_at", 0):
        print("[TOKEN] Access token expired — refreshing from file storage...")

        refresh_payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
        }

        response = requests.post("https://www.strava.com/oauth/token", data=refresh_payload)
        new_data = response.json()

        # Update stored tokens
        tokens.update({
            "access_token": new_data["access_token"],
            "refresh_token": new_data["refresh_token"],
            "expires_at": new_data["expires_at"],
        })

        with open(FILE_NAME, "w") as f:
            json.dump(tokens, f)
        
        # Also save to Supabase if enabled and we have athlete_id
        if use_supabase and tokens.get("athlete_id"):
            save_result, save_error = save_strava_tokens(
                tokens["athlete_id"],
                tokens["access_token"],
                tokens["refresh_token"],
                tokens["expires_at"]
            )
            if not save_error:
                print("[TOKEN] Token also saved to Supabase")

        print("[TOKEN] New access token saved.")

    return tokens["access_token"], tokens.get("athlete_id")

@app.route("/api/add-user-info", methods=["POST"])
def add_user_info():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing authorization header"}), 401

    token = auth_header.split(" ")[1]  # 'Bearer <token>'



# ============================================================================
# STRAVA DATA ENDPOINTS
# ============================================================================

@app.route("/strava/activities")
def get_activities():
    """Fetch recent Strava activities using a valid access token."""
    try:
        access_token, _ = get_valid_token()
    except Exception as e:
        return jsonify({"error": f"Could not load or refresh token: {str(e)}"}), 500

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params={"per_page": 30})

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch activities", "details": response.json()}), response.status_code

    data = response.json()
    from datetime import datetime

    # Initialize map for all weekdays
    activities_by_day = {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": [],
        "Sunday": []
    }
    # --- Group activities by weekday ---
    for activity in data:
        # Convert ISO timestamp
        start_local = datetime.fromisoformat(activity["start_date_local"].replace("Z", "+00:00"))
        weekday = start_local.strftime("%A")

        # Collect relevant metrics
        activity_info = {
            "id": activity.get("id"),
            "name": activity.get("name"),
            "date": start_local.strftime("%Y-%m-%d"),
            "distance": activity.get("distance"),
            "moving_time": activity.get("moving_time"),
            "elapsed_time": activity.get("elapsed_time"),
            "average_speed": activity.get("average_speed"),
            "max_speed": activity.get("max_speed"),
            "average_cadence": activity.get("average_cadence"),
            "average_heartrate": activity.get("average_heartrate"),
            "max_heartrate": activity.get("max_heartrate"),
            "total_elevation_gain": activity.get("total_elevation_gain"),
        }

        # Add to appropriate weekday
        activities_by_day[weekday].append(activity_info)
    #print(activities_by_day)
    return jsonify(activities_by_day)

def flatten_weekly_activities(weekly_data: dict):
    all_activities = []
    for day_activities in weekly_data.values():
        # Only include dicts
        all_activities.extend([act for act in day_activities if isinstance(act, dict)])
    return all_activities


@app.route("/person/update-activities", methods=["POST"])
def update_person_activities():
    """
    Receive Strava activities from frontend and update Person instance,
    then store the response in the DB.
    """
    payload = request.get_json()
    
    data = payload["activities"]
    access_token = payload["access_token"]
    print("accessToken: " + access_token)
    #print(f"this is data: \n{data}")
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Flatten the JSON data
    activities_list = flatten_weekly_activities(data)
    
    if not activities_list:
        return jsonify({"error": "No activities found"}), 400

    # Create a new Person instance
    person = Person()
    
    # Parse activities
    StravaParser.parse_activities_new(activities_list, person)
    
    # Calculate streak
    person.streak = StravaParser.calculate_streak(activities_list)
    
    # Check badges
    StravaParser.check_badges(person)
    
    # Check weekly challenges
    StravaParser.check_challenges(person, activities_list)
    
    # Prepare response dictionary
    response_data = {
        "username": person.display_name,
        "total_workouts": person.total_workouts,
        "total_distance": person.total_distance,
        "average_speed": person.average_speed,
        "max_speed": person.max_speed,
        "streak": person.streak,
        "badges": {
            "moving_time": person.badges.moving_time,
            "distance": person.badges.distance,
            "max_speed": person.badges.max_speed
        },
        "weekly_challenges": {
            "first_challenge": person.weekly_challenges.first_challenge,
            "second_challenge": person.weekly_challenges.second_challenge,
            "third_challenge": person.weekly_challenges.third_challenge
        }
    }

    #print(response_data)
    
    # Store in DB
    try:
        insert_person_response(response_data, access_token)
        
    except Exception as e:
        return jsonify({"error": f"Failed to insert into DB: {str(e)}"}), 500

    return jsonify(response_data), 200


# ============================================================================
# LEGACY FRIENDS ENDPOINTS (DEPRECATED - Use /api/friends/* instead)
# ============================================================================
# These endpoints use direct add (no request system)
# Kept for backwards compatibility only

@app.route("/friends/add", methods=["POST"])
def add_friend_route():
    """
    DEPRECATED: Use POST /api/friends/request instead
    Direct add friend (no request system)
    """
    print("[DEPRECATED] /friends/add called - use /api/friends/request instead")
    
    data = request.get_json()
    access_token = data.get("access_token")
    friend_id = data.get("friend_id")

    if not access_token or not friend_id:
        return jsonify({"error": "Missing fields"}), 400

    # who is adding the friend?
    user = fetch_person_response(access_token)
    if not user:
        return jsonify({"error": "Invalid access token"}), 401

    user_id = user["user_id"]

    # store friendship (direct add - no request)
    error = add_friend(user_id, friend_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Friend added!"}), 200

@app.route("/friends/list", methods=["POST"])
def list_friends_route():
    """
    DEPRECATED: Use GET /api/friends instead
    Get friends list using old format
    """
    print("[DEPRECATED] /friends/list called - use GET /api/friends instead")
    
    data = request.get_json()
    access_token = data.get("access_token")

    if not access_token:
        return jsonify({"error": "Missing access token"}), 400

    user = fetch_person_response(access_token)
    if not user:
        return jsonify({"error": "Invalid access token"}), 401

    user_id = user["user_id"]

    # Get friend IDs (uses deprecated function)
    friends_data, error = get_friends_user(user_id)
    if error:
        return jsonify({"error": error}), 500
        
    print("friends: " + str(friends_data))

    if not friends_data:
        return jsonify({"friends": []}), 200

    friend_ids = [f["friend_id"] for f in friends_data]  if isinstance(friends_data, list) else []

    # Get full profiles
    profiles, error = get_friend_profiles(friend_ids)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"friends": profiles}), 200


@app.route("/person/get-activities", methods=["POST"])
def get_person_activities():
    payload = request.get_json()
    
    
    access_token = payload["access_token"]

    data = fetch_person_response(access_token)
    if not data:
        return jsonify({"error": "No activity data found"}), 404

    return jsonify(data), 200
    
# creating the leaderboards;
@app.route("/leaderboard/create", methods=["POST"])
def create_leaderboard_route():
    data = request.get_json()
    access_token = data.get("access_token")
    name = data.get("name")
    metric = data.get("metric")
    members = data.get("members")

    if not access_token or not name or not metric or not members:
        return jsonify({"error": "Missing fields"}), 400

    result, error = create_leaderboard(access_token, name, metric, members)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Leaderboard created!", "leaderboard_id": result["leaderboard_id"]}), 200

@app.route("/leaderboard/add_member", methods=["POST"])
def add_member_route():
    data = request.get_json()

    access_token = data.get("access_token")
    leaderboard_id = data.get("leaderboard_id")
    user_id = data.get("user_id")

    if not access_token or not leaderboard_id or not user_id:
        return jsonify({"error": "Missing fields"}), 400

    result, error = add_member_to_leaderboard(access_token, leaderboard_id, user_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(result), 200

@app.route("/leaderboards/my", methods=["POST"])
def get_user_leaderboards_route():
    data = request.get_json()
    access_token = data.get("access_token")

    if not access_token:
        return jsonify({"error": "Missing access token"}), 400

    leaderboards, error = fetch_user_leaderboards(access_token)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(leaderboards), 200


@app.route("/api/sync", methods=["POST", "GET"])
def sync_data():
    """Sync Strava data and calculate scores"""
    print("\n" + "="*80)
    print("[SYNC] Starting activity sync process")
    print("="*80)
    
    try:
        access_token, athlete_id = get_valid_token()
        print(f"[SUCCESS] Token validated successfully")
        print(f"   Athlete ID: {athlete_id}")
    except Exception as e:
        print(f"[ERROR] Token validation failed: {str(e)}")
        return jsonify({"error": f"Not authenticated: {str(e)}"}), 401

    # Fetch activities from Strava
    print(f"\n[API] Fetching activities from Strava API...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params={"per_page": 30})
    
    print(f"[API] Strava API response status: {response.status_code}")

    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch activities from Strava")
        return jsonify({"error": "Failed to fetch activities"}), response.status_code

    activities = response.json()
    print(f"[SUCCESS] Fetched {len(activities)} activities from Strava")
    if activities:
        print(f"   First activity: {activities[0].get('name')} ({activities[0].get('type')})")
        print(f"   Activity types: {set(a.get('type') for a in activities)}")
    
    # Get user data
    print(f"\n[STORAGE] Loading user data from storage...")
    user_data = storage.get_user(athlete_id)
    if not user_data:
        print(f"[ERROR] User not found in storage (ID: {athlete_id})")
        return jsonify({"error": "User not found. Please authenticate first."}), 404
    
    print(f"[SUCCESS] User data loaded:")
    print(f"   Name: {user_data.get('name')}")
    print(f"   Username: {user_data.get('username')}")
    
    # Create Person object
    print(f"\n[PERSON] Creating Person object...")
    person = Person()
    person.change_name(user_data.get('name', 'Unknown'))
    person.change_username(user_data.get('username', 'unknown'))
    print(f"[SUCCESS] Person object created")
    
    # Parse activities and update person
    print(f"\n[PARSER] Parsing activities with StravaParser...")
    metrics = StravaParser.parse_activities(activities, person)
    
    if not metrics:
        print(f"[WARNING] No running activities found in {len(activities)} activities")
        return jsonify({"message": "No running activities found"}), 200
    
    print(f"[SUCCESS] Activities parsed successfully:")
    print(f"   Total workouts: {person.total_workouts}")
    print(f"   Total distance: {person.total_distance} meters ({person.total_distance/1000:.2f} km)")
    print(f"   Total moving time: {person.total_moving_time} seconds ({person.total_moving_time/60:.1f} min)")
    print(f"   Average speed: {person.average_speed:.2f} m/s")
    print(f"   Baseline average speed: {person.baseline_average_speed:.2f} m/s")
    print(f"   Baseline distance: {person.baseline_distance:.0f} meters")
    
    # Calculate streak
    print(f"\n[STREAK] Calculating streak...")
    person.streak = StravaParser.calculate_streak(activities)
    print(f"[SUCCESS] Streak calculated: {person.streak} days")
    
    # Check badges and challenges
    print(f"\n[BADGES] Checking badges...")
    StravaParser.check_badges(person)
    badge_points = person.badges.get_points()
    print(f"[SUCCESS] Badges checked:")
    print(f"   Moving time badge: {person.badges.moving_time}")
    print(f"   Distance badge: {person.badges.distance}")
    print(f"   Max speed badge: {person.badges.max_speed}")
    print(f"   Total badge points: {badge_points}")
    
    print(f"\n[CHALLENGES] Checking challenges...")
    StravaParser.check_challenges(person, activities)
    challenge_points = person.weekly_challenges.get_points()
    print(f"[SUCCESS] Challenges checked:")
    print(f"   Challenge 1: {person.weekly_challenges.first_challenge}")
    print(f"   Challenge 2: {person.weekly_challenges.second_challenge}")
    print(f"   Challenge 3: {person.weekly_challenges.third_challenge}")
    print(f"   Total challenge points: {challenge_points}")
    
    # Calculate score
    print(f"\n[SCORE] Calculating score...")
    print(f"   Input metrics:")
    print(f"     Average speed: {person.average_speed:.2f} vs baseline {person.baseline_average_speed:.2f}")
    print(f"     Max speed: {person.max_speed:.2f} vs baseline {person.baseline_max_speed:.2f}")
    print(f"     Distance: {person.distance:.0f} vs baseline {person.baseline_distance:.0f}")
    print(f"     Moving time: {person.moving_time:.0f} vs baseline {person.baseline_moving_time:.0f}")
    
    person.score.calculate_score(
        person.average_speed,
        person.max_speed,
        person.distance,
        person.moving_time,
        person.baseline_average_speed,
        person.baseline_max_speed,
        person.baseline_distance,
        person.baseline_moving_time,
        badge_points,
        challenge_points,
        person.streak
    )
    print(f"[SUCCESS] Score calculated: {person.score.score}")
    print(f"   Improvement: {person.score.improvement:.2f}")
    
    # Save activities
    print(f"\n[STORAGE] Saving data to storage...")
    print(f"   Saving {len(activities)} activities...")
    storage.save_activities(athlete_id, activities)
    print(f"[SUCCESS] Activities saved")
    
    # Update user data with metrics
    print(f"   Updating user data with metrics...")
    user_data.update({
        'total_workouts': person.total_workouts,
        'total_distance': person.total_distance,
        'total_moving_time': person.total_moving_time,
        'average_speed': person.average_speed,
        'max_speed': person.max_speed,
        'streak': person.streak
    })
    storage.save_user(athlete_id, user_data)
    print(f"[SUCCESS] User data updated")
    
    # Save score data
    print(f"   Saving score data...")
    score_data = {
        'user_id': athlete_id,
        'username': person.display_name,
        'score': person.score.score,
        'improvement': person.score.improvement,
        'total_workouts': person.total_workouts,
        'badge_points': badge_points,
        'challenge_points': challenge_points,
        'streak': person.streak
    }
    storage.save_score(athlete_id, score_data)
    print(f"[SUCCESS] Score data saved")
    
    print(f"\n[RESPONSE] Preparing response...")
    response_data = {
        "message": "Sync successful!",
        "metrics": {
            "total_workouts": person.total_workouts,
            "total_distance_km": round(person.total_distance / 1000, 2),
            "average_pace_per_km": round(person.baseline_moving_time / (person.baseline_distance / 1000) / 60, 2) if person.baseline_distance > 0 else 0,
            "streak": person.streak,
            "score": person.score.score,
            "improvement": round(person.score.improvement, 2)
        }
    }
    print(f"[SUCCESS] Response data:")
    print(f"   {json.dumps(response_data, indent=2)}")
    print("="*80 + "\n")
    
    return jsonify(response_data)

@app.route("/register", methods=["POST"])
def register_route():
    data = request.get_json()
    user_id = data.get("user_id")
    username = data.get("username")
    email = data.get("email")

    if not username or not email:
        return jsonify({"error": "Missing fields"}), 400

    error = insert_user_profile(user_id, username, email)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "User created successfully!"}), 200


# ============================================================================
# API ENDPOINTS FOR FRONTEND
# ============================================================================

@app.route("/api/profile")
def get_profile():
    """Get user profile data"""
    print("\n" + "="*80)
    print("[PROFILE] Loading profile data")
    print("="*80)
    
    try:
        _, athlete_id = get_valid_token()
        print(f"[SUCCESS] Token validated")
        print(f"   Athlete ID: {athlete_id}")
    except Exception as e:
        print(f"[ERROR] Not authenticated: {str(e)}")
        return jsonify({"error": "Not authenticated"}), 401
    
    print(f"\n[STORAGE] Loading user data from storage...")
    user_data = storage.get_user(athlete_id)
    if not user_data:
        print(f"[ERROR] User not found in storage (ID: {athlete_id})")
        return jsonify({"error": "User not found"}), 404
    
    print(f"[SUCCESS] User data loaded:")
    print(f"   Keys in user_data: {list(user_data.keys())}")
    print(f"   Name: {user_data.get('name')}")
    print(f"   Username: {user_data.get('username')}")
    print(f"   Total workouts: {user_data.get('total_workouts', 'NOT SET')}")
    print(f"   Total distance: {user_data.get('total_distance', 'NOT SET')}")
    print(f"   Streak: {user_data.get('streak', 'NOT SET')}")
    
    print(f"\n[STORAGE] Loading score data from storage...")
    score_data = storage.get_score(athlete_id)
    if score_data:
        print(f"[SUCCESS] Score data loaded:")
        print(f"   Score: {score_data.get('score')}")
        print(f"   Improvement: {score_data.get('improvement')}")
    else:
        print(f"[WARNING] No score data found for user {athlete_id}")
    
    # Calculate pace
    print(f"\n[CALC] Calculating metrics...")
    total_distance_km = user_data.get('total_distance', 0) / 1000
    total_time_min = user_data.get('total_moving_time', 0) / 60
    avg_pace = total_time_min / total_distance_km if total_distance_km > 0 else 0
    
    print(f"   Total distance: {total_distance_km:.2f} km")
    print(f"   Total time: {total_time_min:.1f} min")
    print(f"   Average pace: {avg_pace:.2f} min/km")
    
    profile_response = {
        "name": user_data.get('name', 'Unknown'),
        "username": user_data.get('username', 'unknown'),
        "location": user_data.get('location', ''),
        "avatar": user_data.get('avatar', 'https://api.dicebear.com/7.x/identicon/svg?seed=runner'),
        "stats": {
            "runs": user_data.get('total_workouts', 0),
            "distance_km": round(total_distance_km, 1),
            "avg_pace": round(avg_pace, 1),
            "streak": user_data.get('streak', 0),
            "score": score_data.get('score', 0) if score_data else 0
        }
    }
    
    print(f"\n[RESPONSE] Sending profile response:")
    print(f"   {json.dumps(profile_response, indent=2)}")
    print("="*80 + "\n")
    
    return jsonify(profile_response)

@app.route("/api/leaderboard")
def get_leaderboard():
    """Get leaderboard data"""
    all_scores = storage.get_all_scores()
    all_users = storage.get_all_users()
    
    # Build leaderboard entries
    leaderboard = []
    for user_id, score_data in all_scores.items():
        user_data = all_users.get(user_id, {})
        
        leaderboard.append({
            "user_id": user_id,
            "username": score_data.get('username', user_data.get('username', 'Unknown')),
            "score": score_data.get('score', 0),
            "runs": score_data.get('total_workouts', 0),
            "improvement": round(score_data.get('improvement', 0), 1),
            "streak": score_data.get('streak', 0)
        })
    
    # Sort by score (highest first)
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    
    # Add ranks
    for i, entry in enumerate(leaderboard):
        entry['rank'] = i + 1
    
    return jsonify({
        "leaderboard": leaderboard,
        "total_users": len(leaderboard),
        "updated_at": time.time()
    })

@app.route("/api/friends")
def get_friends():
    """Get friends list (placeholder - returns sample data)"""
    try:
        _, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": "Not authenticated"}), 401
    
    # For MVP, return sample friends data
    # In future, this would query actual friendships
    all_users = storage.get_all_users()
    friends = []
    
    for user_id, user_data in all_users.items():
        if user_id != athlete_id:  # Don't include self
            score_data = storage.get_score(user_id)
            friends.append({
                "user_id": user_id,
                "username": user_data.get('username', 'Unknown'),
                "avatar": user_data.get('avatar', 'https://api.dicebear.com/7.x/identicon/svg?seed=' + user_id),
                "last_run_distance": round(user_data.get('total_distance', 0) / user_data.get('total_workouts', 1) / 1000, 1),
                "improvement": round(score_data.get('improvement', 0), 1) if score_data else 0
            })
    
    return jsonify({
        "friends": friends[:5],  # Limit to 5 for MVP
        "total": len(friends)
    })

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route("/api/status")
def api_status():
    """Check API status and authentication state"""
    try:
        _, athlete_id = get_valid_token()
        authenticated = True
    except:
        authenticated = False
        athlete_id = None
    
    return jsonify({
        "api_online": True,
        "authenticated": authenticated,
        "athlete_id": athlete_id,
        "storage_initialized": True
    })

# ============================================================================
# ROUTE GENERATION ENDPOINTS (MVP - Simplified)
# ============================================================================

@app.route("/api/routes/search", methods=["GET", "POST"])
def search_routes():
    """
    Search for routes matching criteria
    Query params: distance_km, difficulty, surface
    """
    if request.method == "POST":
        data = request.get_json()
        distance_km = data.get("distance_km")
        difficulty = data.get("difficulty")
        surface = data.get("surface")
    else:
        distance_km = request.args.get("distance_km", type=float)
        difficulty = request.args.get("difficulty")
        surface = request.args.get("surface")
    
    routes = SimpleRouteGenerator.find_routes(
        distance_km=distance_km,
        difficulty=difficulty,
        surface=surface,
        max_results=5
    )
    
    return jsonify({
        "routes": routes,
        "count": len(routes),
        "criteria": {
            "distance_km": distance_km,
            "difficulty": difficulty,
            "surface": surface
        }
    })

@app.route("/api/routes/all")
def get_all_routes():
    """Get all available routes"""
    routes = SimpleRouteGenerator.get_all_routes()
    return jsonify({
        "routes": routes,
        "count": len(routes)
    })

@app.route("/api/routes/<route_id>")
def get_route(route_id):
    """Get specific route by ID"""
    route = SimpleRouteGenerator.get_route_by_id(route_id)
    if route:
        return jsonify(route)
    return jsonify({"error": "Route not found"}), 404

@app.route("/api/routes/generate", methods=["POST"])
def generate_custom_route():
    """Generate a custom route based on distance"""
    data = request.get_json()
    distance_km = data.get("distance_km", 5.0)
    start_location = data.get("start_location")
    
    route = SimpleRouteGenerator.generate_custom_route(
        distance_km=distance_km,
        start_location=start_location
    )
    
    return jsonify({
        "message": "Custom route generated",
        "route": route
    })

# ============================================================================
# FRIENDS ENDPOINTS (SUPABASE VERSION)
# ============================================================================

@app.route("/api/friends/search", methods=["GET"])
def search_users():
    """Search for users by name or username"""
    print(f"\n[FRIENDS API - SUPABASE] Search users endpoint called")
    
    try:
        _, athlete_id = get_valid_token()
        print(f"   Authenticated user: {athlete_id}")
    except Exception as e:
        print(f"   [ERROR] Not authenticated: {str(e)}")
        return jsonify({"error": "Not authenticated"}), 401
    
    query = request.args.get("q", "")
    print(f"   Search query: '{query}'")
    
    if not query or len(query) < 2:
        print(f"   [WARNING] Query too short")
        return jsonify({"users": [], "message": "Query must be at least 2 characters"})
    
    # Search in Supabase
    users, error = search_users_by_name(query)
    if error:
        print(f"   [ERROR] Search failed: {error}")
        return jsonify({"error": error}), 500
    
    results = []
    for user in users:
        user_id = user.get('user_id')
        if user_id == athlete_id:  # Don't include self
            continue
        
        # Check friendship status
        status, _ = supabase_get_status(athlete_id, user_id)
        
        # Get additional data from storage for avatar, location, etc.
        user_data = storage.get_user(user_id) or {}
        
        results.append({
            "user_id": user_id,
            "name": user_data.get('name', 'Unknown'),
            "username": user.get('username', 'unknown'),
            "avatar": user_data.get('avatar', f'https://api.dicebear.com/7.x/identicon/svg?seed={user_id}'),
            "location": user_data.get('location', ''),
            "friendship_status": status
        })
    
    print(f"   [SUCCESS] Found {len(results)} matching users")
    return jsonify({"users": results, "count": len(results)})

@app.route("/api/friends/request", methods=["POST"])
def send_friend_request_endpoint():
    """Send a friend request"""
    print(f"\n[FRIENDS API - SUPABASE] Send friend request endpoint called")
    
    try:
        _, athlete_id = get_valid_token()
        print(f"   From user: {athlete_id}")
    except Exception as e:
        print(f"   [ERROR] Not authenticated: {str(e)}")
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    friend_id = data.get("friend_id")
    
    print(f"   To user: {friend_id}")
    
    if not friend_id:
        print(f"   [ERROR] Missing friend_id")
        return jsonify({"error": "Missing friend_id parameter"}), 400
    
    # Send request via Supabase
    result, error = supabase_send_request(athlete_id, friend_id)
    
    if error:
        print(f"   [ERROR] {error}")
        return jsonify({"error": error}), 400
    
    print(f"   [SUCCESS] Friend request sent")
    return jsonify(result)

@app.route("/api/friends/accept/<friend_id>", methods=["POST"])
def accept_friend_request_endpoint(friend_id):
    """Accept a friend request"""
    print(f"\n[FRIENDS API - SUPABASE] Accept friend request endpoint called")
    
    try:
        _, athlete_id = get_valid_token()
        print(f"   User: {athlete_id}")
        print(f"   Accepting: {friend_id}")
    except Exception as e:
        print(f"   [ERROR] Not authenticated: {str(e)}")
        return jsonify({"error": "Not authenticated"}), 401
    
    result, error = supabase_accept_request(athlete_id, friend_id)
    
    if error:
        print(f"   [ERROR] {error}")
        return jsonify({"error": error}), 400
    
    print(f"   [SUCCESS] Friend request accepted")
    return jsonify(result)

@app.route("/api/friends/reject/<friend_id>", methods=["POST"])
def reject_friend_request_endpoint(friend_id):
    """Reject a friend request"""
    print(f"\n[FRIENDS API - SUPABASE] Reject friend request endpoint called")
    
    try:
        _, athlete_id = get_valid_token()
        print(f"   User: {athlete_id}")
        print(f"   Rejecting: {friend_id}")
    except Exception as e:
        print(f"   [ERROR] Not authenticated: {str(e)}")
        return jsonify({"error": "Not authenticated"}), 401
    
    result, error = supabase_reject_request(athlete_id, friend_id)
    
    if error:
        print(f"   [ERROR] {error}")
        return jsonify({"error": error}), 400
    
    print(f"   [SUCCESS] Friend request rejected")
    return jsonify(result)

@app.route("/api/friends/remove/<friend_id>", methods=["DELETE"])
def remove_friend_endpoint(friend_id):
    """Remove a friend (unfriend)"""
    print(f"\n[FRIENDS API - SUPABASE] Remove friend endpoint called")
    
    try:
        _, athlete_id = get_valid_token()
        print(f"   User: {athlete_id}")
        print(f"   Removing: {friend_id}")
    except Exception as e:
        print(f"   [ERROR] Not authenticated: {str(e)}")
        return jsonify({"error": "Not authenticated"}), 401
    
    result, error = supabase_remove_friend(athlete_id, friend_id)
    
    if error:
        print(f"   [ERROR] {error}")
        return jsonify({"error": error}), 400
    
    print(f"   [SUCCESS] Friend removed")
    return jsonify(result)

@app.route("/api/friends", methods=["GET"])
def get_friends_list_endpoint():
    """Get current user's friends with their data"""
    print(f"\n[FRIENDS API - SUPABASE] Get friends list endpoint called")
    
    try:
        _, athlete_id = get_valid_token()
        print(f"   User: {athlete_id}")
    except Exception as e:
        print(f"   [ERROR] Not authenticated: {str(e)}")
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get friend IDs from Supabase
    friend_ids, error = supabase_get_friends(athlete_id)
    if error:
        print(f"   [ERROR] Failed to get friends: {error}")
        return jsonify({"error": error}), 500
    
    all_users = storage.get_all_users()
    
    friends = []
    for friend_id in friend_ids:
        user_data = all_users.get(friend_id, {})
        score_data = storage.get_score(friend_id)
        
        # Calculate average run distance
        total_workouts = user_data.get('total_workouts', 0)
        total_distance = user_data.get('total_distance', 0)
        avg_distance = (total_distance / total_workouts / 1000) if total_workouts > 0 else 0
        
        friends.append({
            "user_id": friend_id,
            "name": user_data.get('name', 'Unknown'),
            "username": user_data.get('username', 'unknown'),
            "avatar": user_data.get('avatar', f'https://api.dicebear.com/7.x/identicon/svg?seed={friend_id}'),
            "location": user_data.get('location', ''),
            "total_workouts": total_workouts,
            "last_run_distance": round(avg_distance, 1),
            "improvement": round(score_data.get('improvement', 0), 1) if score_data else 0,
            "streak": user_data.get('streak', 0),
            "score": score_data.get('score', 0) if score_data else 0
        })
    
    print(f"   [SUCCESS] Returning {len(friends)} friends")
    return jsonify({"friends": friends, "count": len(friends)})

@app.route("/api/friends/requests", methods=["GET"])
def get_friend_requests_endpoint():
    """Get pending friend requests (incoming)"""
    print(f"\n[FRIENDS API - SUPABASE] Get friend requests endpoint called")
    
    try:
        _, athlete_id = get_valid_token()
        print(f"   User: {athlete_id}")
    except Exception as e:
        print(f"   [ERROR] Not authenticated: {str(e)}")
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get pending requests from Supabase
    pending_requests, error = supabase_get_pending(athlete_id)
    if error:
        print(f"   [ERROR] Failed to get pending requests: {error}")
        return jsonify({"error": error}), 500
    
    all_users = storage.get_all_users()
    
    requests = []
    for req in pending_requests:
        user_id = req.get('from_user_id')
        user_data = all_users.get(user_id, {})
        requests.append({
            "user_id": user_id,
            "name": user_data.get('name', 'Unknown'),
            "username": user_data.get('username', 'unknown'),
            "avatar": user_data.get('avatar', f'https://api.dicebear.com/7.x/identicon/svg?seed={user_id}'),
            "location": user_data.get('location', ''),
            "request_id": req.get('id'),
            "created_at": req.get('created_at')
        })
    
    print(f"   [SUCCESS] Returning {len(requests)} pending requests")
    return jsonify({"requests": requests, "count": len(requests)})

@app.route("/api/friends/sent", methods=["GET"])
def get_sent_requests_endpoint():
    """Get outgoing friend requests (pending)"""
    print(f"\n[FRIENDS API - SUPABASE] Get sent requests endpoint called")
    
    try:
        _, athlete_id = get_valid_token()
        print(f"   User: {athlete_id}")
    except Exception as e:
        print(f"   [ERROR] Not authenticated: {str(e)}")
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get sent requests from Supabase
    sent_requests, error = supabase_get_sent(athlete_id)
    if error:
        print(f"   [ERROR] Failed to get sent requests: {error}")
        return jsonify({"error": error}), 500
    
    all_users = storage.get_all_users()
    
    sent = []
    for req in sent_requests:
        user_id = req.get('to_user_id')
        user_data = all_users.get(user_id, {})
        sent.append({
            "user_id": user_id,
            "name": user_data.get('name', 'Unknown'),
            "username": user_data.get('username', 'unknown'),
            "avatar": user_data.get('avatar', f'https://api.dicebear.com/7.x/identicon/svg?seed={user_id}'),
            "location": user_data.get('location', ''),
            "request_id": req.get('id'),
            "created_at": req.get('created_at')
        })
    
    print(f"   [SUCCESS] Returning {len(sent)} sent requests")
    return jsonify({"sent": sent, "count": len(sent)})

# @app.post("/api/login")
# def login():
#     data = request.get_json()
#     email = data.get("email")
#     password = data.get("password")

#     if email not in USERS:
#         return jsonify({"error": "User not found"}), 401

#     if USERS[email]["password"] != password:
#         return jsonify({"error": "Incorrect password"}), 401

#     return jsonify({
#         "success": True,
#         "user": {
#             "email": email,
#             "name": USERS[email]["name"]
#         }
#     })


if __name__ == "__main__":
    # Get PORT from environment variable for cloud deployment (Render, Heroku, etc.)
    port = int(os.environ.get("PORT", 5000))
    
    # Determine if we're in production
    is_production = os.environ.get("RENDER") or os.environ.get("RAILWAY_ENVIRONMENT")
    
    # Use 0.0.0.0 to allow external connections (required for cloud deployment)
    app.run(
        host="0.0.0.0",
        port=port,
        debug=not is_production  # Disable debug in production
    )
