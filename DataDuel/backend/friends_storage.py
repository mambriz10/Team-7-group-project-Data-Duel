"""
Friends Storage Module - Manages friend relationships
Handles friend requests, accepts/rejects, and friend lists
"""
import json
import os
from datetime import datetime


class FriendsStorage:
    """Manages friend relationships and requests"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.friends_file = os.path.join(data_dir, "friends.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not os.path.exists(self.friends_file):
            with open(self.friends_file, 'w') as f:
                json.dump({}, f, indent=2)
        
        print(f"[FRIENDS STORAGE] Initialized with file: {self.friends_file}")
    
    def _read(self):
        """Read friends data from JSON file"""
        with open(self.friends_file, 'r') as f:
            return json.load(f)
    
    def _write(self, data):
        """Write friends data to JSON file"""
        with open(self.friends_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _get_user_data(self, user_id):
        """Get or create user's friend data"""
        data = self._read()
        user_id_str = str(user_id)
        
        if user_id_str not in data:
            data[user_id_str] = {
                "friends": [],
                "pending_sent": [],
                "pending_received": [],
                "created_at": datetime.now().isoformat()
            }
            self._write(data)
            print(f"[FRIENDS STORAGE] Created new friend data for user {user_id_str}")
        
        return data[user_id_str]
    
    def send_request(self, from_user_id, to_user_id):
        """Send a friend request from one user to another"""
        print(f"[FRIENDS] Sending friend request from {from_user_id} to {to_user_id}")
        
        data = self._read()
        from_id = str(from_user_id)
        to_id = str(to_user_id)
        
        # Initialize both users if needed
        if from_id not in data:
            data[from_id] = {"friends": [], "pending_sent": [], "pending_received": []}
        if to_id not in data:
            data[to_id] = {"friends": [], "pending_sent": [], "pending_received": []}
        
        # Validation checks
        if from_id == to_id:
            print(f"[FRIENDS] Error: Cannot send request to yourself")
            return {"error": "Cannot send friend request to yourself"}
        
        if to_id in data[from_id]["friends"]:
            print(f"[FRIENDS] Error: Already friends")
            return {"error": "Already friends with this user"}
        
        if to_id in data[from_id]["pending_sent"]:
            print(f"[FRIENDS] Error: Request already sent")
            return {"error": "Friend request already sent"}
        
        # Check if there's already a pending request FROM the other user
        if to_id in data[from_id]["pending_received"]:
            print(f"[FRIENDS] Auto-accepting: Other user already sent you a request")
            # Automatically accept since both want to be friends
            return self.accept_request(from_id, to_id)
        
        # Add to pending lists
        data[from_id]["pending_sent"].append(to_id)
        data[to_id]["pending_received"].append(from_id)
        
        self._write(data)
        print(f"[FRIENDS] Success: Friend request sent")
        return {"success": True, "message": "Friend request sent"}
    
    def accept_request(self, user_id, friend_id):
        """Accept a friend request"""
        print(f"[FRIENDS] User {user_id} accepting request from {friend_id}")
        
        data = self._read()
        user_id_str = str(user_id)
        friend_id_str = str(friend_id)
        
        # Verify request exists
        if friend_id_str not in data.get(user_id_str, {}).get("pending_received", []):
            print(f"[FRIENDS] Error: No pending request from {friend_id}")
            return {"error": "No pending friend request from this user"}
        
        # Remove from pending lists
        data[user_id_str]["pending_received"].remove(friend_id_str)
        data[friend_id_str]["pending_sent"].remove(user_id_str)
        
        # Add to friends lists for both users
        data[user_id_str]["friends"].append(friend_id_str)
        data[friend_id_str]["friends"].append(user_id_str)
        
        # Add timestamp
        data[user_id_str]["last_updated"] = datetime.now().isoformat()
        data[friend_id_str]["last_updated"] = datetime.now().isoformat()
        
        self._write(data)
        print(f"[FRIENDS] Success: Friend request accepted")
        return {"success": True, "message": "Friend request accepted"}
    
    def reject_request(self, user_id, friend_id):
        """Reject a friend request"""
        print(f"[FRIENDS] User {user_id} rejecting request from {friend_id}")
        
        data = self._read()
        user_id_str = str(user_id)
        friend_id_str = str(friend_id)
        
        # Verify request exists
        if friend_id_str not in data.get(user_id_str, {}).get("pending_received", []):
            print(f"[FRIENDS] Error: No pending request from {friend_id}")
            return {"error": "No pending friend request from this user"}
        
        # Remove from pending lists
        data[user_id_str]["pending_received"].remove(friend_id_str)
        data[friend_id_str]["pending_sent"].remove(user_id_str)
        
        self._write(data)
        print(f"[FRIENDS] Success: Friend request rejected")
        return {"success": True, "message": "Friend request rejected"}
    
    def remove_friend(self, user_id, friend_id):
        """Remove a friend (unfriend)"""
        print(f"[FRIENDS] User {user_id} removing friend {friend_id}")
        
        data = self._read()
        user_id_str = str(user_id)
        friend_id_str = str(friend_id)
        
        # Verify friendship exists
        if friend_id_str not in data.get(user_id_str, {}).get("friends", []):
            print(f"[FRIENDS] Error: Not friends with {friend_id}")
            return {"error": "Not friends with this user"}
        
        # Remove from both friends lists
        data[user_id_str]["friends"].remove(friend_id_str)
        data[friend_id_str]["friends"].remove(user_id_str)
        
        self._write(data)
        print(f"[FRIENDS] Success: Friend removed")
        return {"success": True, "message": "Friend removed"}
    
    def get_friends(self, user_id):
        """Get list of friend IDs for a user"""
        user_data = self._get_user_data(user_id)
        friends_list = user_data.get("friends", [])
        print(f"[FRIENDS] User {user_id} has {len(friends_list)} friends")
        return friends_list
    
    def get_pending_requests(self, user_id):
        """Get list of incoming pending friend requests"""
        user_data = self._get_user_data(user_id)
        requests = user_data.get("pending_received", [])
        print(f"[FRIENDS] User {user_id} has {len(requests)} pending requests")
        return requests
    
    def get_sent_requests(self, user_id):
        """Get list of outgoing pending friend requests"""
        user_data = self._get_user_data(user_id)
        sent = user_data.get("pending_sent", [])
        print(f"[FRIENDS] User {user_id} has {len(sent)} sent requests")
        return sent
    
    def are_friends(self, user_id_1, user_id_2):
        """Check if two users are friends"""
        user_data = self._get_user_data(user_id_1)
        return str(user_id_2) in user_data.get("friends", [])
    
    def get_friend_status(self, user_id, other_user_id):
        """
        Get the friendship status between two users
        Returns: 'friends', 'pending_sent', 'pending_received', or 'none'
        """
        user_data = self._get_user_data(user_id)
        other_id = str(other_user_id)
        
        if other_id in user_data.get("friends", []):
            return "friends"
        elif other_id in user_data.get("pending_sent", []):
            return "pending_sent"
        elif other_id in user_data.get("pending_received", []):
            return "pending_received"
        else:
            return "none"

