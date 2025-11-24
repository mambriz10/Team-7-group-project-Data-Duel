# Friends Feature - Testing Guide

## ✅ What Was Implemented

### Backend Files Created/Modified:
1. **`DataDuel/backend/friends_storage.py`** ✅ NEW
   - FriendsStorage class for managing friend relationships
   - Methods: send_request, accept_request, reject_request, remove_friend
   - JSON-based storage in `data/friends.json`

2. **`DataDuel/backend/app.py`** ✅ MODIFIED
   - Added 8 new friends endpoints
   - Integrated FriendsStorage
   - Full logging for debugging

### Frontend Files Updated:
3. **`DataDuel/frontend/social.html`** ✅ REPLACED
   - Real-time friends list from API
   - Friend request management
   - User search functionality
   - Send/accept/reject/remove friends
   - League creation with real friends

### Test Script Created:
4. **`DataDuel/backend/test_friends_api.py`** ✅ NEW
   - Automated API testing script

---

## 🧪 How to Test Locally

### Step 1: Install Dependencies (if needed)

```bash
# Navigate to project root
cd C:\Users\Aiden\Desktop\school\CS422\code\Team-7-group-project-Data-Duel

# Install requirements
pip install flask flask-cors requests python-dotenv supabase
```

### Step 2: Start Backend Server

```bash
# Navigate to backend
cd DataDuel\backend

# Start Flask server
python app.py
```

You should see:
```
[FRIENDS STORAGE] Initialized with file: data\friends.json
* Running on http://127.0.0.1:5000
```

### Step 3: Test with Browser

1. **Open** `http://localhost:5500/DataDuel/frontend/social.html` in your browser
   (or use Live Server extension in VSCode)

2. **You should see:**
   - "Find Friends" button
   - "Your Friends" section (empty initially)
   - League creation

3. **Test Friends Feature:**
   - Click "Find Friends"
   - Search for a user (need 2+ authenticated users)
   - Click "Add Friend"
   - Other user accepts request
   - Both users see each other in friends list

### Step 4: Test with Multiple Accounts

**To fully test, you need 2+ Strava accounts:**

#### Terminal 1 (User 1):
1. Open `http://localhost:5500/DataDuel/frontend/index.html`
2. Click "Connect Strava"
3. Authenticate with Account 1
4. Note your user ID from console or profile

#### Terminal 2 (User 2) - Incognito/Different Browser:
1. Open same URL in incognito mode
2. Connect with different Strava account
3. Authenticate with Account 2

#### Test Flow:
1. User 2: Go to Social page
2. User 2: Click "Find Friends"
3. User 2: Search for User 1 (by name)
4. User 2: Click "Add Friend"
5. User 1: Refresh Social page
6. User 1: See friend request → Click "Accept"
7. Both users: See each other in "Your Friends" list ✅

---

## 🔍 API Endpoints Reference

### GET /api/friends
Get authenticated user's friends list

**Response:**
```json
{
  "friends": [
    {
      "user_id": "12345",
      "name": "John Doe",
      "username": "johndoe",
      "avatar": "https://...",
      "last_run_distance": 5.2,
      "improvement": 2.1,
      "streak": 5,
      "score": 150
    }
  ],
  "count": 1
}
```

### GET /api/friends/requests
Get incoming friend requests

**Response:**
```json
{
  "requests": [
    {
      "user_id": "67890",
      "name": "Jane Smith",
      "username": "janesmith",
      "avatar": "https://..."
    }
  ],
  "count": 1
}
```

### GET /api/friends/search?q=query
Search for users by name or username

**Parameters:**
- `q` - Search query (min 2 characters)

**Response:**
```json
{
  "users": [
    {
      "user_id": "11111",
      "name": "Alice Runner",
      "username": "alice",
      "avatar": "https://...",
      "friendship_status": "none"
    }
  ],
  "count": 1
}
```

**Friendship Status Values:**
- `"none"` - Not friends, can send request
- `"friends"` - Already friends
- `"pending_sent"` - You sent them a request
- `"pending_received"` - They sent you a request

### POST /api/friends/request
Send a friend request

**Body:**
```json
{
  "friend_id": "12345"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Friend request sent"
}
```

### POST /api/friends/accept/<friend_id>
Accept a friend request

**Response:**
```json
{
  "success": true,
  "message": "Friend request accepted"
}
```

### POST /api/friends/reject/<friend_id>
Reject a friend request

**Response:**
```json
{
  "success": true,
  "message": "Friend request rejected"
}
```

### DELETE /api/friends/remove/<friend_id>
Remove a friend

**Response:**
```json
{
  "success": true,
  "message": "Friend removed"
}
```

### GET /api/friends/sent
Get outgoing friend requests

**Response:**
```json
{
  "sent": [
    {
      "user_id": "99999",
      "name": "Bob Runner",
      "username": "bob"
    }
  ],
  "count": 1
}
```

---

## 📊 Data Structure

### friends.json Format

```json
{
  "user_id_1": {
    "friends": ["user_id_2", "user_id_3"],
    "pending_sent": ["user_id_4"],
    "pending_received": ["user_id_5"],
    "created_at": "2025-11-24T12:00:00",
    "last_updated": "2025-11-24T12:30:00"
  }
}
```

---

## ✅ Testing Checklist

- [ ] Backend server starts without errors
- [ ] `data/friends.json` file is created automatically
- [ ] Social page loads without errors
- [ ] "Find Friends" button opens search dialog
- [ ] Search returns users (with 2+ accounts)
- [ ] "Add Friend" button sends request
- [ ] Friend requests appear in target user's list
- [ ] "Accept" button makes users friends
- [ ] Both users see each other in friends list
- [ ] "Remove" button unfriends users
- [ ] "Decline" button rejects requests
- [ ] League creation shows real friends in invite list

---

## 🐛 Troubleshooting

### Issue: "Failed to load friends"
**Cause:** Backend not running or CORS issue  
**Fix:** 
1. Ensure Flask server is running
2. Check console for CORS errors
3. Verify CORS settings in app.py

### Issue: "No users found" in search
**Cause:** Only one user in database  
**Fix:** Create and authenticate another Strava account

### Issue: Endpoints return 401
**Cause:** Not authenticated  
**Fix:** Go through Strava OAuth flow first

### Issue: Friends.json not created
**Cause:** File permissions or path issue  
**Fix:** Check `DataDuel/backend/data/` folder exists

---

## 🎯 Expected Behavior

### When User A sends request to User B:
1. User A's `pending_sent` array includes User B's ID
2. User B's `pending_received` array includes User A's ID
3. User B sees request in "Friend Requests" section
4. User A sees "Request Sent" badge in search

### When User B accepts:
1. Both users' `pending_*` arrays are cleared
2. Both users' `friends` arrays include each other
3. Both users see each other in "Your Friends" list
4. Both can remove each other

### When User B rejects:
1. Both users' `pending_*` arrays are cleared
2. No friendship is created
3. User A can send another request later

### When friendship exists:
1. Search shows "Friends" badge
2. Each user sees other in friends list
3. Either can remove the friendship
4. Can invite each other to leagues

---

## 🚀 Next Steps After Testing

Once friends feature works locally:
1. ✅ Test all endpoints
2. ✅ Verify data persistence
3. ✅ Test edge cases
4. 🚧 Prepare for CloudFlare Pages deployment

---

## 📞 Quick Debug Commands

### Check if server is running:
```bash
curl http://localhost:5000/
```

### Test friends endpoint:
```bash
curl http://localhost:5000/api/friends
```

### View friends.json:
```bash
cat DataDuel\backend\data\friends.json
```

### Check Flask logs:
Look at terminal running `python app.py`

---

**Status:** ✅ Friends feature fully implemented and ready to test!  
**Next:** Test locally, then configure for CloudFlare Pages

