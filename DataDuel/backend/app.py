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
from strava_parser import StravaParser
from route_generator import SimpleRouteGenerator
from Person import Person
from Score import Score

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize data storage
storage = DataStorage()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

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
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=payload)
    data = response.json()

    if "access_token" not in data:
        return jsonify({"error": "Failed to get access token", "details": data}), 400

    athlete = data.get("athlete", {})
    athlete_id = str(athlete.get("id"))

    # Store tokens securely
    with open("tokens.json", "w") as f:
        json.dump({
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": data["expires_at"],
            "athlete_id": athlete_id
        }, f)
    
    # Create or update user in storage
    person = StravaParser.create_person_from_athlete(athlete)
    
    user_data = {
        "id": athlete_id,
        "name": person._Person__name,
        "username": person._Person__user_name,
        "display_name": person.display_name,
        "avatar": athlete.get("profile"),
        "location": f"{athlete.get('city', '')}, {athlete.get('state', '')}".strip(', '),
        "strava_id": athlete_id
    }
    
    storage.save_user(athlete_id, user_data)

    return jsonify({
        "message": "Authentication successful! Please sync your activities.",
        "athlete": athlete,
        "redirect": "/api/sync"
    })

def get_valid_token():
    """Load and refresh the access token if expired."""
    FILE_NAME = "tokens.json"
    if not os.path.exists(FILE_NAME):
        raise FileNotFoundError("tokens.json not found. Please authenticate first.")
    
    with open(FILE_NAME, "r") as f:
        tokens = json.load(f)

    # Check if expired
    if time.time() > tokens.get("expires_at", 0):
        print("Access token expired — refreshing...")

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

        print("New access token saved.")

    return tokens["access_token"], tokens.get("athlete_id")

# ============================================================================
# STRAVA DATA ENDPOINTS
# ============================================================================

@app.route("/strava/activities")
def get_activities():
    """Fetch recent Strava activities"""
    try:
        access_token, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": f"Could not load or refresh token: {str(e)}"}), 500

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch activities", "details": response.json()}), response.status_code

    return jsonify(response.json())

@app.route("/api/sync", methods=["POST", "GET"])
def sync_data():
    """Sync Strava data and calculate scores"""
    try:
        access_token, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": f"Not authenticated: {str(e)}"}), 401

    # Fetch activities from Strava
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params={"per_page": 30})

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch activities"}), response.status_code

    activities = response.json()
    
    # Get user data
    user_data = storage.get_user(athlete_id)
    if not user_data:
        return jsonify({"error": "User not found. Please authenticate first."}), 404
    
    # Create Person object
    person = Person()
    person.change_name(user_data.get('name', 'Unknown'))
    person.change_username(user_data.get('username', 'unknown'))
    
    # Parse activities and update person
    metrics = StravaParser.parse_activities(activities, person)
    
    if not metrics:
        return jsonify({"message": "No running activities found"}), 200
    
    # Calculate streak
    person.streak = StravaParser.calculate_streak(activities)
    
    # Check badges and challenges
    StravaParser.check_badges(person)
    StravaParser.check_challenges(person, activities)
    
    # Calculate score
    person.score.calculate_score(
        person.average_speed,
        person.max_speed,
        person.distance,
        person.moving_time,
        person.baseline_average_speed,
        person.baseline_max_speed,
        person.baseline_distance,
        person.baseline_moving_time,
        person.badges.get_points(),
        person.weekly_challenges.get_points(),
        person.streak
    )
    
    # Save activities
    storage.save_activities(athlete_id, activities)
    
    # Update user data with metrics
    user_data.update({
        'total_workouts': person.total_workouts,
        'total_distance': person.total_distance,
        'total_moving_time': person.total_moving_time,
        'average_speed': person.average_speed,
        'max_speed': person.max_speed,
        'streak': person.streak
    })
    storage.save_user(athlete_id, user_data)
    
    # Save score data
    score_data = {
        'user_id': athlete_id,
        'username': person.display_name,
        'score': person.score.score,
        'improvement': person.score.improvement,
        'total_workouts': person.total_workouts,
        'badge_points': person.badges.get_points(),
        'challenge_points': person.weekly_challenges.get_points(),
        'streak': person.streak
    }
    storage.save_score(athlete_id, score_data)
    
    return jsonify({
        "message": "Sync successful!",
        "metrics": {
            "total_workouts": person.total_workouts,
            "total_distance_km": round(person.total_distance / 1000, 2),
            "average_pace_per_km": round(person.baseline_moving_time / (person.baseline_distance / 1000) / 60, 2) if person.baseline_distance > 0 else 0,
            "streak": person.streak,
            "score": person.score.score,
            "improvement": round(person.score.improvement, 2)
        }
    })

# ============================================================================
# API ENDPOINTS FOR FRONTEND
# ============================================================================

@app.route("/api/profile")
def get_profile():
    """Get user profile data"""
    try:
        _, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_data = storage.get_user(athlete_id)
    if not user_data:
        return jsonify({"error": "User not found"}), 404
    
    score_data = storage.get_score(athlete_id)
    
    # Calculate pace
    total_distance_km = user_data.get('total_distance', 0) / 1000
    total_time_min = user_data.get('total_moving_time', 0) / 60
    avg_pace = total_time_min / total_distance_km if total_distance_km > 0 else 0
    
    return jsonify({
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
    })

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
