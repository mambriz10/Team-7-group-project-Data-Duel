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

# =============================================================================
# FRIENDS SYSTEM - COMPLETE SUPABASE IMPLEMENTATION
# =============================================================================

def send_friend_request(from_user_id: str, to_user_id: str):
    """
    Send a friend request from one user to another.
    Returns: (success_data, error_message)
    """
    print(f"[SUPABASE FRIENDS] Sending friend request from {from_user_id} to {to_user_id}")
    
    try:
        # Validation: Can't send request to yourself
        if from_user_id == to_user_id:
            print(f"[SUPABASE FRIENDS] Error: Cannot send request to yourself")
            return None, "Cannot send friend request to yourself"
        
        # Check if already friends
        is_friend, _ = are_friends(from_user_id, to_user_id)
        if is_friend:
            print(f"[SUPABASE FRIENDS] Error: Already friends")
            return None, "Already friends with this user"
        
        # Check if request already exists (in either direction)
        existing_request = db.table("friend_requests").select("*").or_(
            f"and(from_user_id.eq.{from_user_id},to_user_id.eq.{to_user_id})",
            f"and(from_user_id.eq.{to_user_id},to_user_id.eq.{from_user_id})"
        ).eq("status", "pending").execute()
        
        if existing_request.data:
            # If the other user already sent a request, auto-accept
            if existing_request.data[0]["from_user_id"] == to_user_id:
                print(f"[SUPABASE FRIENDS] Auto-accepting: Other user already sent request")
                return accept_friend_request(from_user_id, to_user_id)
            else:
                print(f"[SUPABASE FRIENDS] Error: Request already sent")
                return None, "Friend request already sent"
        
        # Insert friend request
        response = db.table("friend_requests").insert({
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "status": "pending"
        }).execute()
        
        print(f"[SUPABASE FRIENDS] Success: Friend request sent")
        return {"success": True, "message": "Friend request sent", "request_id": response.data[0]["id"]}, None
        
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error sending request: {str(e)}")
        return None, str(e)


def accept_friend_request(user_id: str, from_user_id: str):
    """
    Accept a friend request. Creates bidirectional friendship.
    Returns: (success_data, error_message)
    """
    print(f"[SUPABASE FRIENDS] User {user_id} accepting request from {from_user_id}")
    
    try:
        # Find the pending request
        request = db.table("friend_requests").select("*").eq(
            "from_user_id", from_user_id
        ).eq("to_user_id", user_id).eq("status", "pending").maybe_single().execute()
        
        if not request.data:
            print(f"[SUPABASE FRIENDS] Error: No pending request found")
            return None, "No pending friend request from this user"
        
        # Create bidirectional friendship
        db.table("friends").insert([
            {"user_id": user_id, "friend_id": from_user_id},
            {"user_id": from_user_id, "friend_id": user_id}
        ]).execute()
        
        # Update request status to accepted
        db.table("friend_requests").update({
            "status": "accepted"
        }).eq("id", request.data["id"]).execute()
        
        print(f"[SUPABASE FRIENDS] Success: Friend request accepted")
        return {"success": True, "message": "Friend request accepted"}, None
        
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error accepting request: {str(e)}")
        return None, str(e)


def reject_friend_request(user_id: str, from_user_id: str):
    """
    Reject a friend request.
    Returns: (success_data, error_message)
    """
    print(f"[SUPABASE FRIENDS] User {user_id} rejecting request from {from_user_id}")
    
    try:
        # Find the pending request
        request = db.table("friend_requests").select("*").eq(
            "from_user_id", from_user_id
        ).eq("to_user_id", user_id).eq("status", "pending").maybe_single().execute()
        
        if not request.data:
            print(f"[SUPABASE FRIENDS] Error: No pending request found")
            return None, "No pending friend request from this user"
        
        # Update status to rejected (or delete)
        db.table("friend_requests").update({
            "status": "rejected"
        }).eq("id", request.data["id"]).execute()
        
        print(f"[SUPABASE FRIENDS] Success: Friend request rejected")
        return {"success": True, "message": "Friend request rejected"}, None
        
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error rejecting request: {str(e)}")
        return None, str(e)


def remove_friend(user_id: str, friend_id: str):
    """
    Remove a friendship (unfriend). Deletes bidirectional relationship.
    Returns: (success_data, error_message)
    """
    print(f"[SUPABASE FRIENDS] User {user_id} removing friend {friend_id}")
    
    try:
        # Check if they are actually friends
        is_friend, _ = are_friends(user_id, friend_id)
        if not is_friend:
            print(f"[SUPABASE FRIENDS] Error: Not friends")
            return None, "Not friends with this user"
        
        # Delete both directions of the friendship
        db.table("friends").delete().or_(
            f"and(user_id.eq.{user_id},friend_id.eq.{friend_id})",
            f"and(user_id.eq.{friend_id},friend_id.eq.{user_id})"
        ).execute()
        
        print(f"[SUPABASE FRIENDS] Success: Friend removed")
        return {"success": True, "message": "Friend removed"}, None
        
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error removing friend: {str(e)}")
        return None, str(e)


def get_friends_list(user_id: str):
    """
    Get list of all friends for a user (returns friend_ids only).
    Returns: (friend_ids_list, error_message)
    """
    print(f"[SUPABASE FRIENDS] Getting friends list for user {user_id}")
    
    try:
        # Get all friendships where user is either user_id or friend_id
        response = db.table("friends").select("user_id, friend_id").or_(
            f"user_id.eq.{user_id}",
            f"friend_id.eq.{user_id}"
        ).execute()
        
        # Extract the friend IDs (the other person in each friendship)
        friend_ids = []
        for row in response.data:
            if row["user_id"] == user_id:
                friend_ids.append(row["friend_id"])
            else:
                friend_ids.append(row["user_id"])
        
        print(f"[SUPABASE FRIENDS] Found {len(friend_ids)} friends")
        return friend_ids, None
        
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error getting friends: {str(e)}")
        return None, str(e)


def get_pending_requests(user_id: str):
    """
    Get incoming pending friend requests for a user.
    Returns: (requests_list, error_message)
    """
    print(f"[SUPABASE FRIENDS] Getting pending requests for user {user_id}")
    
    try:
        response = db.table("friend_requests").select("*").eq(
            "to_user_id", user_id
        ).eq("status", "pending").execute()
        
        print(f"[SUPABASE FRIENDS] Found {len(response.data)} pending requests")
        return response.data, None
        
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error getting pending requests: {str(e)}")
        return None, str(e)


def get_sent_requests(user_id: str):
    """
    Get outgoing pending friend requests sent by a user.
    Returns: (requests_list, error_message)
    """
    print(f"[SUPABASE FRIENDS] Getting sent requests for user {user_id}")
    
    try:
        response = db.table("friend_requests").select("*").eq(
            "from_user_id", user_id
        ).eq("status", "pending").execute()
        
        print(f"[SUPABASE FRIENDS] Found {len(response.data)} sent requests")
        return response.data, None
        
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error getting sent requests: {str(e)}")
        return None, str(e)


def are_friends(user_id: str, friend_id: str):
    """
    Check if two users are friends.
    Returns: (is_friends_boolean, error_message)
    """
    try:
        response = db.table("friends").select("id").or_(
            f"and(user_id.eq.{user_id},friend_id.eq.{friend_id})",
            f"and(user_id.eq.{friend_id},friend_id.eq.{user_id})"
        ).maybe_single().execute()
        
        return response.data is not None, None
        
    except Exception as e:
        return False, str(e)


def get_friend_status(user_id: str, other_user_id: str):
    """
    Get the friendship status between two users.
    Returns: ('friends', 'pending_sent', 'pending_received', 'none')
    """
    print(f"[SUPABASE FRIENDS] Checking status between {user_id} and {other_user_id}")
    
    try:
        # Check if friends
        is_friend, _ = are_friends(user_id, other_user_id)
        if is_friend:
            return "friends", None
        
        # Check if pending request sent
        sent_request = db.table("friend_requests").select("id").eq(
            "from_user_id", user_id
        ).eq("to_user_id", other_user_id).eq("status", "pending").maybe_single().execute()
        
        if sent_request.data:
            return "pending_sent", None
        
        # Check if pending request received
        received_request = db.table("friend_requests").select("id").eq(
            "from_user_id", other_user_id
        ).eq("to_user_id", user_id).eq("status", "pending").maybe_single().execute()
        
        if received_request.data:
            return "pending_received", None
        
        return "none", None
        
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error checking status: {str(e)}")
        return "none", str(e)


def get_friend_profiles(friend_ids: list[str]):
    """
    Get full profile info for a list of UUIDs from user_strava.
    Returns: (profiles_list, error_message)
    """
    if not friend_ids:
        return [], None

    print(f"[SUPABASE FRIENDS] Getting profiles for {len(friend_ids)} friends")
    
    try:
        response = (
            db.table("user_strava")
            .select("*")
            .in_("user_id", friend_ids)
            .execute()
        )

        print(f"[SUPABASE FRIENDS] Retrieved {len(response.data)} profiles")
        return response.data, None
    
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error getting profiles: {str(e)}")
        return None, str(e)


def search_users_by_name(query: str, limit: int = 50):
    """
    Search for users by username or email.
    Returns: (users_list, error_message)
    """
    print(f"[SUPABASE FRIENDS] Searching users with query: '{query}'")
    
    try:
        if not query or len(query) < 2:
            return [], "Query must be at least 2 characters"
        
        # Search in user_strava table
        response = db.table("user_strava").select("user_id, username, email").or_(
            f"username.ilike.%{query}%",
            f"email.ilike.%{query}%"
        ).limit(limit).execute()
        
        print(f"[SUPABASE FRIENDS] Found {len(response.data)} matching users")
        return response.data, None
        
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error searching users: {str(e)}")
        return None, str(e)


# =============================================================================
# LEGACY FUNCTIONS (Backwards Compatibility - Deprecated)
# =============================================================================
# These are kept for backwards compatibility but should be replaced
# with the new functions above

def add_friend(user_id: str, friend_id: str):
    """
    DEPRECATED: Use send_friend_request() instead.
    Direct add friend (no request system).
    """
    print("[SUPABASE FRIENDS] WARNING: Using deprecated add_friend(). Use send_friend_request() instead.")
    try:
        response = db.table("friends").insert([
            {"user_id": user_id, "friend_id": friend_id},
            {"user_id": friend_id, "friend_id": user_id}
        ]).execute()
        return None
    except Exception as e:
        return str(e)


def get_friends_user(user_id: str):
    """
    DEPRECATED: Use get_friends_list() instead.
    Return list of friends' user_ids.
    """
    print("[SUPABASE FRIENDS] WARNING: Using deprecated get_friends_user(). Use get_friends_list() instead.")
    return get_friends_list(user_id)
    



# Load local credentials on import
load_local_credentials()
