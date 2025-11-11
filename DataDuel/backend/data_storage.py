"""
Data Storage Module - JSON-based temporary storage for MVP
This will be replaced with a database in the future.
"""
import json
import os
from datetime import datetime

class DataStorage:
    """Manages JSON file storage for users, activities, and scores"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.activities_file = os.path.join(data_dir, "activities.json")
        self.scores_file = os.path.join(data_dir, "scores.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_file(self.users_file, {})
        self._init_file(self.activities_file, {})
        self._init_file(self.scores_file, {})
    
    def _init_file(self, filepath, default_data):
        """Initialize a JSON file with default data if it doesn't exist"""
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                json.dump(default_data, f, indent=2)
    
    def _read_file(self, filepath):
        """Read and return data from a JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def _write_file(self, filepath, data):
        """Write data to a JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    # User operations
    def get_user(self, user_id):
        """Get user data by ID"""
        users = self._read_file(self.users_file)
        return users.get(str(user_id))
    
    def save_user(self, user_id, user_data):
        """Save or update user data"""
        users = self._read_file(self.users_file)
        users[str(user_id)] = user_data
        users[str(user_id)]['updated_at'] = datetime.now().isoformat()
        self._write_file(self.users_file, users)
    
    def get_all_users(self):
        """Get all users"""
        return self._read_file(self.users_file)
    
    # Activity operations
    def get_activities(self, user_id):
        """Get activities for a specific user"""
        activities = self._read_file(self.activities_file)
        return activities.get(str(user_id), [])
    
    def save_activities(self, user_id, activities_data):
        """Save activities for a user"""
        activities = self._read_file(self.activities_file)
        activities[str(user_id)] = activities_data
        self._write_file(self.activities_file, activities)
    
    def add_activity(self, user_id, activity_data):
        """Add a single activity to user's activities"""
        activities = self._read_file(self.activities_file)
        if str(user_id) not in activities:
            activities[str(user_id)] = []
        activities[str(user_id)].append(activity_data)
        self._write_file(self.activities_file, activities)
    
    # Score operations
    def get_score(self, user_id):
        """Get score data for a specific user"""
        scores = self._read_file(self.scores_file)
        return scores.get(str(user_id))
    
    def save_score(self, user_id, score_data):
        """Save score data for a user"""
        scores = self._read_file(self.scores_file)
        scores[str(user_id)] = score_data
        scores[str(user_id)]['updated_at'] = datetime.now().isoformat()
        self._write_file(self.scores_file, scores)
    
    def get_all_scores(self):
        """Get all scores for leaderboard"""
        return self._read_file(self.scores_file)
    
    def clear_all_data(self):
        """Clear all data (for testing/reset)"""
        self._write_file(self.users_file, {})
        self._write_file(self.activities_file, {})
        self._write_file(self.scores_file, {})

