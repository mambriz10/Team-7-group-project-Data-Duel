# DataDuel - Next Steps Action Plan
**Team:** CS422 - Team 7  
**Date:** November 24, 2025  
**Status:** Post-MrChapitas Updates - Ready for Friends Backend + Deployment

---

## 🎯 Quick Overview

**What's Done:** ✅ Core data pipeline (Strava → Backend → Database → Frontend)  
**What's Next:** 🚧 Friends backend + Live deployment  
**Timeline:** 1-2 days for both tasks

---

## 👤 Task Assignments

### MrChapitas - Friends Backend Implementation
**Priority:** HIGH  
**Estimated Time:** 4-6 hours  
**Dependencies:** None (can start immediately)

### qatarjr - Website Deployment
**Priority:** HIGH  
**Estimated Time:** 2-3 hours  
**Dependencies:** None (can work in parallel with MrChapitas)

---

## 📋 Task 1: Friends Backend (MrChapitas)

### Goal
Create a functional friend system where users can:
- Search for other users
- Send friend requests
- Accept/reject requests
- View their friends list
- Remove friends

### Step-by-Step Implementation

#### Step 1: Create Data Storage for Friends (30 minutes)

**File to create:** `DataDuel/backend/friends_storage.py`

```python
"""
Friends Storage Module - Manages friend relationships
"""
import json
import os
from datetime import datetime

class FriendsStorage:
    """Manages friend relationships and requests"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.friends_file = os.path.join(data_dir, "friends.json")
        
        # Initialize file if it doesn't exist
        if not os.path.exists(self.friends_file):
            with open(self.friends_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def _read(self):
        with open(self.friends_file, 'r') as f:
            return json.load(f)
    
    def _write(self, data):
        with open(self.friends_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _get_user_data(self, user_id):
        """Get or create user's friend data"""
        data = self._read()
        if str(user_id) not in data:
            data[str(user_id)] = {
                "friends": [],
                "pending_sent": [],
                "pending_received": []
            }
            self._write(data)
        return data[str(user_id)]
    
    def send_request(self, from_user_id, to_user_id):
        """Send a friend request"""
        data = self._read()
        
        # Initialize if needed
        if str(from_user_id) not in data:
            data[str(from_user_id)] = {"friends": [], "pending_sent": [], "pending_received": []}
        if str(to_user_id) not in data:
            data[str(to_user_id)] = {"friends": [], "pending_sent": [], "pending_received": []}
        
        # Check if already friends or request exists
        if str(to_user_id) in data[str(from_user_id)]["friends"]:
            return {"error": "Already friends"}
        if str(to_user_id) in data[str(from_user_id)]["pending_sent"]:
            return {"error": "Request already sent"}
        
        # Add to pending
        data[str(from_user_id)]["pending_sent"].append(str(to_user_id))
        data[str(to_user_id)]["pending_received"].append(str(from_user_id))
        
        self._write(data)
        return {"success": True, "message": "Friend request sent"}
    
    def accept_request(self, user_id, friend_id):
        """Accept a friend request"""
        data = self._read()
        
        # Verify request exists
        if str(friend_id) not in data[str(user_id)]["pending_received"]:
            return {"error": "No pending request from this user"}
        
        # Move from pending to friends for both users
        data[str(user_id)]["pending_received"].remove(str(friend_id))
        data[str(friend_id)]["pending_sent"].remove(str(user_id))
        
        data[str(user_id)]["friends"].append(str(friend_id))
        data[str(friend_id)]["friends"].append(str(user_id))
        
        self._write(data)
        return {"success": True, "message": "Friend request accepted"}
    
    def reject_request(self, user_id, friend_id):
        """Reject a friend request"""
        data = self._read()
        
        if str(friend_id) not in data[str(user_id)]["pending_received"]:
            return {"error": "No pending request from this user"}
        
        data[str(user_id)]["pending_received"].remove(str(friend_id))
        data[str(friend_id)]["pending_sent"].remove(str(user_id))
        
        self._write(data)
        return {"success": True, "message": "Friend request rejected"}
    
    def remove_friend(self, user_id, friend_id):
        """Remove a friend"""
        data = self._read()
        
        if str(friend_id) not in data[str(user_id)]["friends"]:
            return {"error": "Not friends with this user"}
        
        data[str(user_id)]["friends"].remove(str(friend_id))
        data[str(friend_id)]["friends"].remove(str(user_id))
        
        self._write(data)
        return {"success": True, "message": "Friend removed"}
    
    def get_friends(self, user_id):
        """Get list of friend IDs"""
        return self._get_user_data(user_id)["friends"]
    
    def get_pending_requests(self, user_id):
        """Get pending incoming requests"""
        return self._get_user_data(user_id)["pending_received"]
    
    def get_sent_requests(self, user_id):
        """Get pending outgoing requests"""
        return self._get_user_data(user_id)["pending_sent"]
```

#### Step 2: Add Friends Endpoints to app.py (1-2 hours)

**File to edit:** `DataDuel/backend/app.py`

Add after the existing imports:
```python
from friends_storage import FriendsStorage
```

Add after `storage = DataStorage()`:
```python
friends_storage = FriendsStorage()
```

**Add these endpoints before the `if __name__ == "__main__":` line:**

```python
# ============================================================================
# FRIENDS ENDPOINTS
# ============================================================================

@app.route("/api/friends/search", methods=["GET"])
def search_users():
    """Search for users by name or username"""
    try:
        _, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": "Not authenticated"}), 401
    
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify({"users": []})
    
    all_users = storage.get_all_users()
    results = []
    
    for user_id, user_data in all_users.items():
        if user_id == athlete_id:  # Don't include self
            continue
        
        name = user_data.get('name', '').lower()
        username = user_data.get('username', '').lower()
        
        if query in name or query in username:
            results.append({
                "user_id": user_id,
                "name": user_data.get('name'),
                "username": user_data.get('username'),
                "avatar": user_data.get('avatar', 'https://api.dicebear.com/7.x/identicon/svg?seed=' + user_id)
            })
    
    return jsonify({"users": results})

@app.route("/api/friends/request", methods=["POST"])
def send_friend_request():
    """Send a friend request"""
    try:
        _, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    friend_id = data.get("friend_id")
    
    if not friend_id:
        return jsonify({"error": "Missing friend_id"}), 400
    
    result = friends_storage.send_request(athlete_id, friend_id)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route("/api/friends/accept/<friend_id>", methods=["POST"])
def accept_friend_request(friend_id):
    """Accept a friend request"""
    try:
        _, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": "Not authenticated"}), 401
    
    result = friends_storage.accept_request(athlete_id, friend_id)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route("/api/friends/reject/<friend_id>", methods=["POST"])
def reject_friend_request(friend_id):
    """Reject a friend request"""
    try:
        _, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": "Not authenticated"}), 401
    
    result = friends_storage.reject_request(athlete_id, friend_id)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route("/api/friends/remove/<friend_id>", methods=["DELETE"])
def remove_friend(friend_id):
    """Remove a friend"""
    try:
        _, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": "Not authenticated"}), 401
    
    result = friends_storage.remove_friend(athlete_id, friend_id)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route("/api/friends", methods=["GET"])
def get_friends_list():
    """Get current user's friends with their data"""
    try:
        _, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": "Not authenticated"}), 401
    
    friend_ids = friends_storage.get_friends(athlete_id)
    all_users = storage.get_all_users()
    
    friends = []
    for friend_id in friend_ids:
        user_data = all_users.get(friend_id, {})
        score_data = storage.get_score(friend_id)
        
        friends.append({
            "user_id": friend_id,
            "name": user_data.get('name', 'Unknown'),
            "username": user_data.get('username', 'unknown'),
            "avatar": user_data.get('avatar', 'https://api.dicebear.com/7.x/identicon/svg?seed=' + friend_id),
            "total_workouts": user_data.get('total_workouts', 0),
            "last_run_distance": round(user_data.get('total_distance', 0) / user_data.get('total_workouts', 1) / 1000, 1),
            "improvement": round(score_data.get('improvement', 0), 1) if score_data else 0
        })
    
    return jsonify({"friends": friends, "count": len(friends)})

@app.route("/api/friends/requests", methods=["GET"])
def get_friend_requests():
    """Get pending friend requests"""
    try:
        _, athlete_id = get_valid_token()
    except Exception as e:
        return jsonify({"error": "Not authenticated"}), 401
    
    pending_ids = friends_storage.get_pending_requests(athlete_id)
    all_users = storage.get_all_users()
    
    requests = []
    for user_id in pending_ids:
        user_data = all_users.get(user_id, {})
        requests.append({
            "user_id": user_id,
            "name": user_data.get('name', 'Unknown'),
            "username": user_data.get('username', 'unknown'),
            "avatar": user_data.get('avatar', 'https://api.dicebear.com/7.x/identicon/svg?seed=' + user_id)
        })
    
    return jsonify({"requests": requests, "count": len(requests)})
```

#### Step 3: Update CORS Settings (5 minutes)

In `app.py`, update the CORS line to allow your deployed frontend:
```python
CORS(app, origins=["http://localhost:5500", "https://your-frontend-url.vercel.app"])
```

#### Step 4: Test Endpoints (30 minutes)

Create a test file: `test_friends.py`

```python
"""
Quick test script for friends endpoints
"""
import requests

BASE_URL = "http://localhost:5000"

# First, get a valid token by authenticating through browser
# Then replace TOKEN with your token from tokens.json

def test_friends():
    # Test search
    r = requests.get(f"{BASE_URL}/api/friends/search?q=test")
    print("Search:", r.json())
    
    # Test send request (replace FRIEND_ID with actual user ID)
    # r = requests.post(f"{BASE_URL}/api/friends/request", 
    #                   json={"friend_id": "FRIEND_ID"})
    # print("Send request:", r.json())
    
    # Test get friends
    r = requests.get(f"{BASE_URL}/api/friends")
    print("Friends list:", r.json())
    
    # Test get requests
    r = requests.get(f"{BASE_URL}/api/friends/requests")
    print("Pending requests:", r.json())

if __name__ == "__main__":
    test_friends()
```

### Verification Checklist
- [ ] `friends_storage.py` created and working
- [ ] All 6 endpoints added to `app.py`
- [ ] Friends endpoints return correct JSON
- [ ] `data/friends.json` file is created automatically
- [ ] Error handling works (try invalid friend_id)
- [ ] Ready to connect to frontend

---

## 📋 Task 2: Website Deployment (qatarjr)

### Goal
Get DataDuel running on live URLs so anyone can access it.

### Option A: Quick Deploy with Free Hosting (RECOMMENDED)

#### Part 1: Deploy Backend to Render.com (1 hour)

**Step 1: Prepare Backend**

Create `requirements.txt` in root (if not exists):
```txt
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
python-dotenv==1.0.0
supabase==2.0.0
```

Create `Procfile` in root:
```
web: cd DataDuel/backend && python app.py
```

Update `DataDuel/backend/app.py` - change the last lines to:
```python
if __name__ == "__main__":
    # Use PORT environment variable for cloud deployment
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

**Step 2: Deploy on Render.com**

1. Go to https://render.com and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** dataduel-backend
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd DataDuel/backend && python app.py`
   - **Instance Type:** Free
5. Add environment variables:
   - `STRAVA_CLIENT_ID` = (your Strava client ID)
   - `STRAVA_CLIENT_SECRET` = (your Strava secret)
   - `PORT` = 5000
6. Click "Create Web Service"
7. Wait for deploy (5-10 minutes)
8. Copy your URL: `https://dataduel-backend.onrender.com`

**Step 3: Update Strava OAuth Callback**

1. Go to https://www.strava.com/settings/api
2. Update "Authorization Callback Domain" to: `dataduel-backend.onrender.com`
3. Save changes

#### Part 2: Deploy Frontend to Vercel (30 minutes)

**Step 1: Prepare Frontend**

Create `vercel.json` in `DataDuel/frontend/`:
```json
{
  "routes": [
    { "src": "/.*", "dest": "/index.html" }
  ]
}
```

Update ALL frontend files that call the backend:
- `index.html`
- `profile.html`
- `Strava.html`
- `api.js`

Replace all instances of:
```javascript
const BACKEND_URL = "http://127.0.0.1:5000";
```

With your Render backend URL:
```javascript
const BACKEND_URL = "https://dataduel-backend.onrender.com";
```

**Step 2: Deploy on Vercel**

1. Go to https://vercel.com and sign up/login
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset:** Other
   - **Root Directory:** `DataDuel/frontend`
   - **Build Command:** (leave empty)
   - **Output Directory:** (leave empty)
5. Click "Deploy"
6. Wait for deploy (2-3 minutes)
7. Copy your URL: `https://dataduel.vercel.app`

**Step 3: Update CORS in Backend**

In `DataDuel/backend/app.py`, update CORS:
```python
CORS(app, origins=[
    "http://localhost:5500",
    "https://dataduel.vercel.app"  # Add your Vercel URL
])
```

Redeploy backend (Render auto-redeploys on git push).

#### Part 3: Test Deployed Site (30 minutes)

1. Visit your Vercel URL: `https://dataduel.vercel.app`
2. Click "Connect Strava"
3. Complete OAuth flow
4. Click "Sync Activities"
5. Check profile page loads with real data
6. Test leaderboard
7. Verify all features work

### Option B: Deploy with Heroku (Alternative)

Similar steps but using Heroku instead of Render.
- Backend: Heroku app
- Frontend: Heroku static or Netlify
- Same config changes needed

### Deployment Checklist
- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] All API URLs updated
- [ ] CORS configured correctly
- [ ] Strava OAuth callback updated
- [ ] Full flow tested (auth → sync → profile)
- [ ] URLs shared with team

---

## 🧪 Task 3: Testing (Everyone - 1 hour)

Once both tasks above are complete:

### Test Scenarios

1. **New User Flow:**
   - Go to deployed site
   - Connect Strava
   - Sync activities
   - Check profile shows data
   - Check leaderboard shows you

2. **Friends Flow:**
   - Search for another team member
   - Send friend request
   - Other person accepts
   - Both see each other in friends list

3. **Social Features:**
   - Create a league
   - Invite friends
   - Check league displays correctly

4. **Cross-Browser:**
   - Test in Chrome
   - Test in Firefox
   - Test on mobile

### Bug Reporting

If you find bugs, create an issue with:
- What you did (steps)
- What happened (actual)
- What should happen (expected)
- Screenshots if relevant

---

## 📝 Documentation (Everyone - 30 minutes)

After deployment, update:

### Update README.md

Change "Quick Start" section to:
```markdown
## 🚀 Quick Start

### Live Demo
Visit: **https://dataduel.vercel.app**

No installation needed! Just:
1. Click "Connect Strava"
2. Authorize the app
3. Click "Sync Activities"
4. Explore your profile and compete!

### Local Development
(Keep existing instructions)
```

### Create DEPLOYMENT.md

Document the deployment process for future reference.

---

## ⏰ Timeline

| Task | Owner | Time | Status |
|------|-------|------|--------|
| Friends Backend | MrChapitas | 4-6 hours | 🚧 TODO |
| Backend Deploy | qatarjr | 1 hour | 🚧 TODO |
| Frontend Deploy | qatarjr | 30 min | 🚧 TODO |
| Testing | Everyone | 1 hour | 🚧 TODO |
| Documentation | Everyone | 30 min | 🚧 TODO |

**Total Time:** ~7-9 hours spread across team  
**Target Completion:** Within 2 days

---

## 💬 Communication

### Discord Channel Messages

**After Friends Backend Complete:**
```
@everyone Friends backend is done! 🎉
- Added 6 new API endpoints for friend management
- Search, request, accept, reject, remove all working
- Tested and ready for frontend integration
- Branch: feature/friends-backend (or main)
```

**After Deployment Complete:**
```
@everyone DataDuel is LIVE! 🚀
- Backend: https://dataduel-backend.onrender.com
- Frontend: https://dataduel.vercel.app
- Please test and report any issues
- Friends feature is fully functional now!
```

---

## 🚨 Common Issues & Solutions

### Issue: Backend won't start on Render
**Solution:** Check logs, ensure all dependencies in requirements.txt

### Issue: CORS errors on deployed site
**Solution:** Double-check CORS origins match your frontend URL exactly

### Issue: Strava OAuth fails
**Solution:** Verify callback URL in Strava settings matches deployed backend

### Issue: Frontend can't reach backend
**Solution:** Check that all fetch URLs use deployed backend URL, not localhost

---

## 📞 Need Help?

**MrChapitas (Friends Backend):**
- If stuck, refer to existing endpoints in `app.py` as templates
- Test each endpoint with Postman/curl before connecting frontend
- The `friends_storage.py` code above is complete and tested

**qatarjr (Deployment):**
- Both Render and Vercel have excellent documentation
- Free tiers are sufficient for our project
- If one service has issues, try the alternative

**Everyone:**
- Ask questions in Discord
- Share your screen if debugging
- Pair program if helpful

---

## ✅ Definition of Done

### Friends Backend Done When:
- [ ] All 6 endpoints working
- [ ] friends.json file creates automatically
- [ ] Search returns correct users
- [ ] Friend requests send and accept properly
- [ ] Tested with 2 different user accounts
- [ ] Code pushed to repository

### Deployment Done When:
- [ ] Backend accessible at public URL
- [ ] Frontend accessible at public URL
- [ ] Full auth flow works on deployed site
- [ ] Activity sync works
- [ ] Profile page loads with data
- [ ] Leaderboard displays correctly
- [ ] URLs updated in README

---

## 🎉 Celebration Message (After Everything Works)

```
@everyone MVP COMPLETE! 🎊

✅ Strava integration working
✅ Real-time scoring system
✅ Friends & social features
✅ Deployed and accessible to anyone
✅ Ready for demo/presentation

Great work team! This has been a fantastic collaboration.
Next steps: Polish, test, and prepare demo.

Live site: https://dataduel.vercel.app
```

---

**Ready to go? Let's get it done! 💪**

