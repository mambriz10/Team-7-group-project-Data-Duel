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
    
    data = fetch_person_response(access_token)
    print("this is the data:\n" + data["username"])
    
    update_data = {
        "username": data["username"],
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
        print("before the db update in inserting")
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
        # Get the user from Supabase Auth
        auth_response = db.auth.get_user(access_token)
        
        # if auth_response.error:
        #     raise RuntimeError(f"Auth error: {auth_response.error.message}")

        user = auth_response.user
        user_id = user.id

        # Fetch the row from user_strava safely
        #print("before")
        result = db.table("user_strava").select("*").eq("user_id", user_id).maybe_single().execute()
        #print("before")
        ret = result.data
        print("this is the from fetch_person_response : " + str(ret))
        # if result.error:
        #     raise RuntimeError(f"DB error: {result.error.message}")

        # if not result.data:
        #     return None

        # data = result.data

        # # Remove sensitive fields
        # for field in ["client_id", "client_secret"]:
        #     data.pop(field, None)

        return ret

    except Exception as e:
        raise RuntimeError(f"Failed to fetch data from DB: {str(e)}")

    
def insert_user_profile( user_id, username, email):

    """
    Insert a new user profile into user_strava.
    """
    try:
        response = db.table("user_strava").insert({
            "user_id": user_id,
            "username": username,
            "email": email
        }).execute()

        return response

    except Exception as e:
        return str(e)

def add_friend(user_id: str, friend_id: str):
    """
    Add a friend for a user.
    """
    try:
        response = db.table("friends").insert({
            "user_id": user_id,
            "friend_id": friend_id
        }).execute()


        return None
    except Exception as e:
        return str(e)
    
def get_friends_user(user_id: str):
    """
    Return list of friends' user_ids.
    """
    try:
        response = (
            db.table("friends")
            .select("friend_id")
            .eq("user_id", user_id)
            .execute()
        )

        return response.data, None
    except Exception as e:
        return None, str(e)


def get_friend_profiles(friend_ids: list[str]):
    """
    Get full profile info for a list of UUIDs from user_strava.
    """
    if not friend_ids:
        return [], None

    try:
        response = (
            db.table("user_strava")
            .select("*")
            .in_("user_id", friend_ids)
            .execute()
        )

        print("this is get_friend_profiles:" + str(response.data))
        return response.data, None
    
    except Exception as e:
        return None, str(e)
    



# Load local credentials on import
load_local_credentials()
