# strava_credentials.py

import json
import os
import time
from datetime import datetime
from supabase import create_client

CREDENTIALS_FILE = "strava_credentials.json"

# Supabase Configuration
# Use environment variables in production (Render), fallback to hardcoded for local dev
db_URL = os.getenv("SUPABASE_URL", "https://gbvyveaifvqneyayloks.supabase.co")
db_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdidnl2ZWFpZnZxbmV5YXlsb2tzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTU4NTU4OCwiZXhwIjoyMDc3MTYxNTg4fQ.aGxQOGIY7VKV0GjLPOkORAlfoz5M2JGeY-8b5YQxTvo")

print(f"[SUPABASE] Connecting to: {db_URL}")
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
        "client_secret": client_secret,
        "access_token": access_token
    }, on_conflict="user_id").execute()

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


def get_all_users_from_db():
    """
    Get all users from the user_strava table.
    Returns: (users_list, error_message)
    """
    print(f"[SUPABASE] Fetching all users from database")
    
    try:
        response = (
            db.table("user_strava")
            .select("user_id, username, email")
            .execute()
        )
        
        print(f"[SUPABASE] Found {len(response.data)} users")
        return response.data, None
        
    except Exception as e:
        print(f"[SUPABASE] Error fetching all users: {str(e)}")
        return None, str(e)


def auto_friend_all_users():
    """
    Make all users in the database friends with each other (for MVP demo).
    Creates bidirectional friendships for all user pairs.
    Returns: (success_data, error_message)
    """
    print(f"[SUPABASE FRIENDS] Auto-friending all users for MVP demo")
    
    try:
        # Get all users
        users, error = get_all_users_from_db()
        if error:
            return None, error
        
        if not users or len(users) < 2:
            return {"success": True, "message": "Not enough users to create friendships", "friendships_created": 0}, None
        
        user_ids = [user["user_id"] for user in users]
        print(f"[SUPABASE FRIENDS] Processing {len(user_ids)} users")
        
        # Get existing friendships to avoid duplicates
        existing_friends = db.table("friends").select("user_id, friend_id").execute()
        existing_pairs = set()
        for friendship in existing_friends.data:
            # Store both directions to check easily
            pair = tuple(sorted([friendship["user_id"], friendship["friend_id"]]))
            existing_pairs.add(pair)
        
        # Create friendships for all pairs
        friendships_to_create = []
        friendships_created = 0
        
        for i in range(len(user_ids)):
            for j in range(i + 1, len(user_ids)):
                user1_id = user_ids[i]
                user2_id = user_ids[j]
                
                # Check if already friends
                pair = tuple(sorted([user1_id, user2_id]))
                if pair in existing_pairs:
                    continue
                
                # Add bidirectional friendship
                friendships_to_create.append({
                    "user_id": user1_id,
                    "friend_id": user2_id
                })
                friendships_to_create.append({
                    "user_id": user2_id,
                    "friend_id": user1_id
                })
        
        # Insert all friendships in batches (Supabase has limits)
        if friendships_to_create:
            batch_size = 100
            for i in range(0, len(friendships_to_create), batch_size):
                batch = friendships_to_create[i:i + batch_size]
                db.table("friends").insert(batch).execute()
                friendships_created += len(batch) // 2  # Divide by 2 since we count pairs
        
        print(f"[SUPABASE FRIENDS] Successfully created {friendships_created} friendships")
        return {
            "success": True,
            "message": f"Successfully created {friendships_created} friendships",
            "friendships_created": friendships_created,
            "total_users": len(user_ids)
        }, None
        
    except Exception as e:
        print(f"[SUPABASE FRIENDS] Error auto-friending users: {str(e)}")
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
    
def create_leaderboard(user_access_token: str, name: str, metric: str, members: list[str]):
    """
    Create a leaderboard and add members to it.
    
    Args:
        user_access_token: Access token of the user creating the leaderboard
        name: Name of the leaderboard
        metric: The metric used for the leaderboard (e.g., total_distance)
        members: List of user_ids to add (should include creator)

    Returns:
        dict: {"leaderboard_id": str} on success
        tuple: (None, str) on failure
    """
    try:
        # Get the creator user
        user = db.auth.get_user(user_access_token).user
        if not user:
            return None, "Invalid access token"

        # Insert leaderboard
        lb = db.table("leaderboards").insert({
            "name": name,
            "creator_id": user.id,
            "metric": metric
        }).execute()

        if not lb.data or len(lb.data) == 0:
            return None, "Failed to create leaderboard"

        leaderboard_id = lb.data[0]["id"]

        # Add members
        for uid in members:
            db.table("leaderboard_members").insert({
                "leaderboard_id": leaderboard_id,
                "user_id": uid
            }).execute()

        return {"leaderboard_id": leaderboard_id}, None

    except Exception as e:
        return None, str(e)

def add_member_to_leaderboard(access_token: str, leaderboard_id, user_id_to_add: str):
        """
        Adds a member to a leaderboard.
        Handles:
            - Invalid token
            - Leaderboard not found
            - Caller not creator
            - Insert errors
        Returns: (data, error)
        """
        # Validate user / token
        try:
            caller = db.auth.get_user(access_token).user
        except Exception:
            return None, "Invalid access token"

        if not caller:
            return None, "Invalid access token"

        caller_id = caller.id

        # Check leaderboard exists
        lb = (
            db.table("leaderboards")
            .select("creator_id")
            .eq("id", leaderboard_id)
            .execute()
        )

        if not lb.data:
            return None, "Leaderboard does not exist"

        creator_id = lb.data[0]["creator_id"]

        # Only creator may add members
        if creator_id != caller_id:
            return None, "Only the leaderboard creator can add members"

        # Insert new member
        try:
            db.table("leaderboard_members").insert({
                "leaderboard_id": leaderboard_id,
                "user_id": user_id_to_add
            }).execute()

            return {"message": "Member added successfully!"}, None

        except Exception as e:
            return None, str(e)


def delete_leaderboard(access_token: str, leaderboard_id):
    """
    Delete a leaderboard. Only the creator can delete it.
    This will also delete all associated members and challenges (via CASCADE).
    
    Args:
        access_token: Access token of the user attempting to delete
        leaderboard_id: UUID of the leaderboard to delete
    
    Returns: (success_data, error_message)
    """
    print(f"[SUPABASE LEADERBOARD] Deleting league {leaderboard_id}")
    
    try:
        # Validate user / token
        caller = db.auth.get_user(access_token).user
        if not caller:
            return None, "Invalid access token"
        
        caller_id = caller.id
        
        # Check leaderboard exists and get creator
        lb = (
            db.table("leaderboards")
            .select("creator_id, name")
            .eq("id", leaderboard_id)
            .maybe_single()
            .execute()
        )
        
        if not lb.data:
            return None, "Leaderboard does not exist"
        
        creator_id = lb.data[0]["creator_id"]
        league_name = lb.data[0].get("name", "League")
        
        # Only creator may delete
        if creator_id != caller_id:
            return None, "Only the league creator can delete the league"
        
        # Delete the leaderboard (CASCADE will delete members and challenges)
        db.table("leaderboards").delete().eq("id", leaderboard_id).execute()
        
        print(f"[SUPABASE LEADERBOARD] Successfully deleted league: {league_name}")
        return {"success": True, "message": f"League '{league_name}' deleted successfully"}, None
        
    except Exception as e:
        print(f"[SUPABASE LEADERBOARD] Error deleting league: {str(e)}")
        return None, str(e)


def fetch_user_leaderboards(access_token):
    """
    Fetch all leaderboards (leagues) for a user - both owned and joined.
    Uses only columns from leaderboards schema: id, name, creator_id, metric, created_at
    Returns: ({"owned": [...], "joined": [...]}, error_message)
    """
    user = db.auth.get_user(access_token).user
    if not user:
        return None, "Invalid access token"

    # Fetch owned leaderboards - using only schema columns
    # Schema shows: id, name, creator_id, metric, created_at
    owned_resp = (
        db.table("leaderboards")
        .select("id, name, creator_id, metric, created_at")
        .eq("creator_id", user.id)
        .execute()
    )
    owned = []
    for lb in owned_resp.data:
        # Count members
        members_resp = db.table("leaderboard_members").select("user_id").eq("leaderboard_id", lb["id"]).execute()
        lb["members_count"] = len(members_resp.data)
        owned.append(lb)

    # Fetch leaderboards user joined
    joined_resp = db.table("leaderboard_members").select("leaderboard_id").eq("user_id", user.id).execute()
    joined = []
    for join in joined_resp.data:
        # Using only schema columns
        lb_resp = (
            db.table("leaderboards")
            .select("id, name, creator_id, metric, created_at")
            .eq("id", join["leaderboard_id"])
            .execute()
        )
        if lb_resp.data:
            lb_data = lb_resp.data[0]
            # Count members
            members_resp = db.table("leaderboard_members").select("user_id").eq("leaderboard_id", lb_data["id"]).execute()
            lb_data["members_count"] = len(members_resp.data)
            joined.append(lb_data)

    return {"owned": owned, "joined": joined}, None


# =============================================================================
# GLOBAL LEADERBOARD - ALL USERS
# =============================================================================

def get_global_leaderboard(limit: int = 100):
    """
    Get global leaderboard of ALL users ranked by score (simple format).
    Uses only columns from user_strava table: user_id, username, score
    Returns: (leaderboard_list, error_message)
    """
    print(f"[SUPABASE LEADERBOARD] Fetching global leaderboard (limit: {limit})")
    
    try:
        # Fetch all users with their scores from user_strava, sorted by score
        # Using only columns shown in schema: user_id, username, score
        response = (
            db.table("user_strava")
            .select("user_id, username, score")
            .not_.is_("score", "null")
            .order("score", desc=True)
            .limit(limit)
            .execute()
        )
        
        leaderboard = []
        for idx, user in enumerate(response.data, start=1):
            leaderboard.append({
                "rank": idx,
                "user_id": user.get("user_id"),
                "username": user.get("username", "unknown"),
                "score": int(user.get("score", 0))  # score is int4 in schema
            })
        
        print(f"[SUPABASE LEADERBOARD] Found {len(leaderboard)} users")
        return leaderboard, None
        
    except Exception as e:
        print(f"[SUPABASE LEADERBOARD] Error: {str(e)}")
        return None, str(e)


# =============================================================================
# LEAGUE LEADERBOARD - SPECIFIC LEAGUE
# =============================================================================

def get_league_leaderboard(league_id):
    """
    Get leaderboard for a specific league (custom league).
    Returns members ranked by score (simple format).
    Uses only columns from schema: user_id, username, score
    Args:
        league_id: UUID string (from leaderboards.id)
    Returns: (leaderboard_list, error_message)
    """
    print(f"[SUPABASE LEADERBOARD] Fetching league leaderboard for league {league_id}")
    
    try:
        # Get all members of this league using leaderboard_members table
        # Schema shows: id, leaderboard_id, user_id, joined_at
        # leaderboard_id is UUID (matches leaderboards.id)
        members_resp = (
            db.table("leaderboard_members")
            .select("user_id")
            .eq("leaderboard_id", league_id)
            .execute()
        )
        
        if not members_resp.data:
            return [], None
        
        user_ids = [member["user_id"] for member in members_resp.data]
        
        # Fetch user data for all members, sorted by score
        # Using only columns from user_strava schema: user_id, username, score
        users_resp = (
            db.table("user_strava")
            .select("user_id, username, score")
            .in_("user_id", user_ids)
            .not_.is_("score", "null")
            .order("score", desc=True)
            .execute()
        )
        
        leaderboard = []
        for idx, user in enumerate(users_resp.data, start=1):
            leaderboard.append({
                "rank": idx,
                "user_id": user.get("user_id"),
                "username": user.get("username", "unknown"),
                "score": int(user.get("score", 0))  # score is int4 in schema
            })
        
        print(f"[SUPABASE LEADERBOARD] Found {len(leaderboard)} members in league")
        return leaderboard, None
        
    except Exception as e:
        print(f"[SUPABASE LEADERBOARD] Error: {str(e)}")
        return None, str(e)


def get_league_info(league_id):
    """
    Get information about a specific league.
    Uses only columns from leaderboards schema: id, name, creator_id, metric, created_at
    Args:
        league_id: UUID string (from leaderboards.id)
    Returns: (league_data, error_message)
    """
    print(f"[SUPABASE LEADERBOARD] Fetching league info for league {league_id}")
    
    try:
        # Get league details - using only columns from schema
        # Schema shows: id, name, creator_id, metric, created_at
        league_resp = (
            db.table("leaderboards")
            .select("id, name, creator_id, metric, created_at")
            .eq("id", league_id)
            .maybe_single()
            .execute()
        )
        
        if not league_resp.data:
            return None, "League not found"
        
        league = league_resp.data
        
        # Count members using leaderboard_members table
        # Schema shows: id, leaderboard_id, user_id, joined_at
        members_resp = (
            db.table("leaderboard_members")
            .select("user_id")
            .eq("leaderboard_id", league_id)
            .execute()
        )
        
        league["members_count"] = len(members_resp.data)
        league["member_ids"] = [m["user_id"] for m in members_resp.data]
        
        return league, None
        
    except Exception as e:
        print(f"[SUPABASE LEADERBOARD] Error: {str(e)}")
        return None, str(e)


# =============================================================================
# LEAGUE CHALLENGES (Simple Format - Like challenges.py)
# =============================================================================

def get_league_challenges(league_id):
    """
    Get the 3 simple challenges for a league.
    Returns format like challenges.py: first_challenge, second_challenge, third_challenge
    Challenge columns are added via migration (not in base schema diagram)
    Args:
        league_id: UUID string (from leaderboards.id)
    Returns: (challenges_dict, error_message)
    """
    print(f"[SUPABASE LEAGUE] Fetching challenges for league {league_id}")
    
    try:
        # Get league with challenge data
        # Base schema: id, name, creator_id, metric, created_at
        # Challenge columns added via migration: first_challenge, second_challenge, third_challenge, etc.
        league_resp = (
            db.table("leaderboards")
            .select("id, first_challenge, second_challenge, third_challenge, first_description, second_description, third_description")
            .eq("id", league_id)
            .maybe_single()
            .execute()
        )
        
        if not league_resp.data:
            return None, "League not found"
        
        league = league_resp.data
        
        # Return simple challenge format (defaults if not set)
        challenges = {
            "first_challenge": league.get("first_challenge", False),
            "second_challenge": league.get("second_challenge", False),
            "third_challenge": league.get("third_challenge", False),
            "first_description": league.get("first_description", "Run 3 times this week"),
            "second_description": league.get("second_description", "Total distance ≥ 20 km"),
            "third_description": league.get("third_description", "Set 1 segment PR")
        }
        
        print(f"[SUPABASE LEAGUE] Returning simple challenges format")
        return challenges, None
        
    except Exception as e:
        print(f"[SUPABASE LEAGUE] Error fetching challenges: {str(e)}")
        return None, str(e)


def update_league_challenges(access_token: str, league_id, 
                            first_challenge: bool = None,
                            second_challenge: bool = None,
                            third_challenge: bool = None,
                            first_description: str = None,
                            second_description: str = None,
                            third_description: str = None):
    """
    Update league challenges. Only league creator can update.
    Returns: (success_data, error_message)
    """
    print(f"[SUPABASE LEAGUE] Updating challenges for league {league_id}")
    
    try:
        # Verify user is the league creator
        user = db.auth.get_user(access_token).user
        if not user:
            return None, "Invalid access token"
        
        league_resp = (
            db.table("leaderboards")
            .select("creator_id")
            .eq("id", league_id)
            .maybe_single()
            .execute()
        )
        
        if not league_resp.data:
            return None, "League not found"
        
        if league_resp.data["creator_id"] != user.id:
            return None, "Only the league creator can update challenges"
        
        # Build update data
        update_data = {}
        if first_challenge is not None:
            update_data["first_challenge"] = first_challenge
        if second_challenge is not None:
            update_data["second_challenge"] = second_challenge
        if third_challenge is not None:
            update_data["third_challenge"] = third_challenge
        if first_description is not None:
            update_data["first_description"] = first_description
        if second_description is not None:
            update_data["second_description"] = second_description
        if third_description is not None:
            update_data["third_description"] = third_description
        
        if not update_data:
            return None, "No fields to update"
        
        # Update league
        update_resp = (
            db.table("leaderboards")
            .update(update_data)
            .eq("id", league_id)
            .execute()
        )
        
        print(f"[SUPABASE LEAGUE] Challenges updated successfully")
        return {"success": True, "league": update_resp.data[0] if update_resp.data else None}, None
        
    except Exception as e:
        print(f"[SUPABASE LEAGUE] Error updating challenges: {str(e)}")
        return None, str(e)




# Load local credentials on import
load_local_credentials()
