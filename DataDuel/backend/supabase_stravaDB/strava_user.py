# strava_credentials.py

import json
from supabase import create_client

CREDENTIALS_FILE = "strava_credentials.json"
# db_URL = "https://gbvyveaifvqneyayloks.db.co"
db_URL = "https://gbvyveaifvqneyayloks.supabase.co"
db_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdidnl2ZWFpZnZxbmV5YXlsb2tzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTU4NTU4OCwiZXhwIjoyMDc3MTYxNTg4fQ.aGxQOGIY7VKV0GjLPOkORAlfoz5M2JGeY-8b5YQxTvo"
db = create_client(db_URL, db_KEY)

CLIENT_ID = None
CLIENT_SECRET = None

def load_local_credentials():
    global CLIENT_ID, CLIENT_SECRET
    try:
        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)
            CLIENT_ID = data.get("client_id")
            CLIENT_SECRET = data.get("client_secret")
    except FileNotFoundError:
        CLIENT_ID = None
        CLIENT_SECRET = None


def save_credentials(client_id: str, client_secret: str):
    """Save credentials locally and to db."""
    global CLIENT_ID, CLIENT_SECRET

    # Save locally
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({"client_id": client_id, "client_secret": client_secret}, f)

    CLIENT_ID = client_id
    CLIENT_SECRET = client_secret

    # Save to db table `strava_credentials`
    # Make sure table has columns: id (PK), client_id (text), client_secret (text)
    db.table("strava_credentials").upsert({
        "id": 1,  # always overwrite same row
        "client_id": client_id,
        "client_secret": client_secret
    }).execute()

def save_credentials_new(client_id: str, client_secret: str, access_token: str):
    """
    Save Strava API credentials both locally and per-user in the database.
    Requires the Supabase access token from the frontend.
    """

    # 1. Get the Supabase session from the access token
    session = db.auth.get_user(access_token)
    user = session.user
    user_id = user.id  # <-- the real logged-in user ID

    # ---------------------
    #  Save locally
    # ---------------------
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({
            "client_id": client_id,
            "client_secret": client_secret,
            "user_id": user_id
        }, f)

    # ---------------------
    # Save to DB (per user)
    # ---------------------

    response = db.table("user_strava").upsert({
        "user_id": user_id,
        "client_id": client_id,
        "client_secret": client_secret
    }).execute()

    return response


def load_credentials_from_supabase():
    """Load credentials from db into memory (optional)."""
    global CLIENT_ID, CLIENT_SECRET

    result = db.table("strava_credentials").select("client_id, client_secret").eq("id", 1).single().execute()
    data = result.data
    if data:
        CLIENT_ID = data.get("client_id")
        CLIENT_SECRET = data.get("client_secret")

def insert_person_response(person_response: dict, access_token: str):
    
    
    """
    Update the Strava activity data for the currently authenticated user.
    Requires the Supabase access token to identify the user.
    """
    # 1. Get user info from Supabase using the access token
    try:
        session = db.auth.get_user(access_token)
        user_id = session.user.id
    except Exception as e:
        raise ValueError(f"Invalid access token or user not found: {str(e)}")
    
    # 2. Prepare the fields to update (exclude client_id/client_secret)
    update_data = {
        "username": person_response.get("username"),
        "total_workouts": person_response.get("total_workouts"),
        "total_distance": person_response.get("total_distance"),
        "average_speed": person_response.get("average_speed"),
        "max_speed": person_response.get("max_speed"),
        "streak": person_response.get("streak"),
        "badges": person_response.get("badges"),
        "weekly_challenges": person_response.get("weekly_challenges")
    }

    # 3. Update the user's record
    try:
        response = db.table("user_strava").update(update_data).eq("user_id", user_id).execute()
    except Exception as e:
        raise RuntimeError(f"Failed to update user activities in DB: {str(e)}")
    
    return response

def fetch_person_response(access_token: str):
    """
    Fetch stored Strava activity summary for a given user using their Supabase access token.
    Returns only the activity summary, excluding sensitive fields.
    """
    try:
        # Get the user from Supabase using the access token
        user = db.auth.get_user(access_token).user
        user_id = user.id

        # Fetch the stored row
        result = db.table("user_strava").select("*").eq("user_id", user_id).single().execute()
        if not result.data:
            return None

        data = result.data

        # Remove sensitive fields before returning
        for field in ["client_id", "client_secret"]:
            if field in data:
                del data[field]

        return data

    except Exception as e:
        raise RuntimeError(f"Failed to fetch data from DB: {str(e)}")

# Load local credentials on import
load_local_credentials()
