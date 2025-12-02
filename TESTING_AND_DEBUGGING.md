# 🧪 DataDuel - Testing & Debugging Guide

## 📋 Table of Contents
1. [Friends System Testing (Supabase)](#friends-system-testing-supabase)
2. [Backend API Testing](#backend-api-testing)
3. [Frontend Testing](#frontend-testing)
4. [Common Issues & Solutions](#common-issues--solutions)
5. [Logging Reference](#logging-reference)

---

## 🤝 Friends System Testing (Supabase)

### Prerequisites

1. **Run the SQL Migration:**
   - Open Supabase Dashboard → SQL Editor
   - Execute `DataDuel/backend/supabase_stravaDB/migration_friends.sql`
   - Verify tables created:
     ```sql
     SELECT * FROM friends;
     SELECT * FROM friend_requests;
     ```

2. **Update Backend:**
   - Ensure you've pulled latest code with Supabase friends implementation
   - Backend should be using functions from `strava_user.py`

3. **Have 2 Test Accounts:**
   - You need 2 Strava accounts to fully test friend requests
   - Or have a groupmate help test

### Step-by-Step Testing

#### Test 1: Send Friend Request

**Backend:**
```bash
cd DataDuel/backend
python app.py
```

**Frontend:**
1. Open `social.html` in browser
2. Click "Find Friends" button
3. Search for another user
4. Click "Add Friend" button
5. **Expected Result:** "Friend request sent" message

**Verify in Supabase:**
```sql
SELECT * FROM friend_requests WHERE status = 'pending';
```
Should show your request.

#### Test 2: Accept Friend Request

**As the other user:**
1. Log in with second account
2. Go to `social.html`
3. Click "View Friend Requests"
4. Should see pending request
5. Click "Accept"
6. **Expected Result:** "Friend request accepted" message

**Verify in Supabase:**
```sql
-- Request should be marked accepted
SELECT * FROM friend_requests WHERE status = 'accepted';

-- Friendship should be bidirectional
SELECT * FROM friends;
-- Should see 2 rows (one for each direction)
```

#### Test 3: View Friends List

1. Refresh `social.html`
2. Friends list should now show the accepted friend
3. Should display:
   - Name
   - Username
   - Stats (workouts, streak, improvement)

**Verify via API:**
```bash
curl http://localhost:5000/api/friends \
  -H "Cookie: strava_token=YOUR_TOKEN"
```

#### Test 4: Remove Friend

1. Click "Remove" button next to friend
2. **Expected Result:** Friend removed, disappears from list

**Verify in Supabase:**
```sql
-- Both rows should be deleted
SELECT * FROM friends WHERE user_id = 'YOUR_ID' OR friend_id = 'YOUR_ID';
-- Should return 0 rows
```

#### Test 5: Reject Friend Request

1. Send another friend request
2. As receiver, go to requests
3. Click "Reject"
4. **Expected Result:** Request disappears

**Verify in Supabase:**
```sql
SELECT * FROM friend_requests WHERE status = 'rejected';
```

#### Test 6: Search Users

1. Click "Find Friends"
2. Type at least 2 characters
3. Should see matching users with friendship status:
   - "none" - not friends
   - "pending_sent" - you sent request
   - "pending_received" - they sent request
   - "friends" - already friends

### API Endpoint Testing

**Search Users:**
```bash
curl "http://localhost:5000/api/friends/search?q=john" \
  -H "Cookie: strava_token=YOUR_TOKEN"
```

**Send Friend Request:**
```bash
curl -X POST http://localhost:5000/api/friends/request \
  -H "Content-Type: application/json" \
  -H "Cookie: strava_token=YOUR_TOKEN" \
  -d '{"friend_id": "FRIEND_USER_ID"}'
```

**Accept Friend Request:**
```bash
curl -X POST http://localhost:5000/api/friends/accept/FRIEND_USER_ID \
  -H "Cookie: strava_token=YOUR_TOKEN"
```

**Reject Friend Request:**
```bash
curl -X POST http://localhost:5000/api/friends/reject/FRIEND_USER_ID \
  -H "Cookie: strava_token=YOUR_TOKEN"
```

**Remove Friend:**
```bash
curl -X DELETE http://localhost:5000/api/friends/remove/FRIEND_USER_ID \
  -H "Cookie: strava_token=YOUR_TOKEN"
```

**Get Friends List:**
```bash
curl http://localhost:5000/api/friends \
  -H "Cookie: strava_token=YOUR_TOKEN"
```

**Get Pending Requests:**
```bash
curl http://localhost:5000/api/friends/requests \
  -H "Cookie: strava_token=YOUR_TOKEN"
```

**Get Sent Requests:**
```bash
curl http://localhost:5000/api/friends/sent \
  -H "Cookie: strava_token=YOUR_TOKEN"
```

### Expected Console Output

When friends system works correctly, you should see:

```
[SUPABASE FRIENDS] Sending friend request from user1 to user2
[SUPABASE FRIENDS] Success: Friend request sent

[SUPABASE FRIENDS] User user2 accepting request from user1
[SUPABASE FRIENDS] Success: Friend request accepted

[SUPABASE FRIENDS] Getting friends list for user user1
[SUPABASE FRIENDS] Found 1 friends
```

---

## 🔌 Backend API Testing

### Complete Test Suite

Run the automated test suite:

```bash
cd DataDuel/backend
python test_friends_api.py
```

### Manual Testing Script

```python
# test_supabase_friends.py
import requests

BASE_URL = "http://localhost:5000"

def test_friends_flow():
    # 1. Search for users
    response = requests.get(f"{BASE_URL}/api/friends/search?q=test")
    print(f"Search: {response.status_code}")
    print(response.json())
    
    # 2. Send friend request
    response = requests.post(
        f"{BASE_URL}/api/friends/request",
        json={"friend_id": "12345"}
    )
    print(f"Send request: {response.status_code}")
    print(response.json())
    
    # 3. Check sent requests
    response = requests.get(f"{BASE_URL}/api/friends/sent")
    print(f"Sent requests: {response.status_code}")
    print(response.json())
    
    # 4. Accept request (as other user)
    response = requests.post(f"{BASE_URL}/api/friends/accept/12345")
    print(f"Accept: {response.status_code}")
    print(response.json())
    
    # 5. Get friends list
    response = requests.get(f"{BASE_URL}/api/friends")
    print(f"Friends list: {response.status_code}")
    print(response.json())
    
    # 6. Remove friend
    response = requests.delete(f"{BASE_URL}/api/friends/remove/12345")
    print(f"Remove: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    test_friends_flow()
```

### Test Data Flow

```bash
cd DataDuel/backend
python test_data_flow.py
```

This tests:
- Strava OAuth
- Activity sync
- Person object creation
- Score calculation
- Data storage

---

## 🎨 Frontend Testing

### Test Checklist

- [ ] **Home Page** (`index.html`)
  - [ ] Shows auth status
  - [ ] "Connect Strava" button works
  - [ ] "Sync Activities" button works
  - [ ] Success messages display

- [ ] **Profile Page** (`profile.html`)
  - [ ] Displays user stats
  - [ ] Shows badges
  - [ ] Shows challenges
  - [ ] Streak counter works

- [ ] **Social Page** (`social.html`)
  - [ ] "Find Friends" dialog opens
  - [ ] Search works (min 2 chars)
  - [ ] Friendship status shows correctly
  - [ ] Add friend button works
  - [ ] Pending requests tab works
  - [ ] Accept/reject buttons work
  - [ ] Friends list displays
  - [ ] Remove friend works

- [ ] **Leaderboard** (`leaderboards.html`)
  - [ ] Shows all users
  - [ ] Sorted by improvement score
  - [ ] Stats display correctly

- [ ] **Routes** (`routes.html`)
  - [ ] 5 routes display
  - [ ] Search filters work
  - [ ] Route details show

### Browser Console Testing

Open browser DevTools (F12) and check:

1. **No Errors:** Console should be clean (or only warnings)
2. **Config Detection:**
   ```
   [DataDuel Config]
     Environment: development
     API URL: http://127.0.0.1:5000
   ```
3. **API Calls:** Network tab shows successful requests (200 status)
4. **Data Loading:** Check responses contain expected data

### Test with Different Browsers

- [ ] Chrome
- [ ] Firefox
- [ ] Edge
- [ ] Safari (if Mac)
- [ ] Mobile browser (responsive)

---

## 🐛 Common Issues & Solutions

### Issue: "Not authenticated" error

**Symptoms:** API calls return 401 error

**Solution:**
1. Check if you've connected Strava (`/auth/strava`)
2. Verify token is stored (check browser cookies)
3. Token might be expired - reconnect Strava

**Debug:**
```javascript
// In browser console
document.cookie // Should show strava_token
```

### Issue: Friend request fails

**Symptoms:** "Error sending friend request"

**Possible Causes:**
1. **Target user doesn't exist**
   - Solution: Verify user_id is correct
   
2. **Already friends**
   - Solution: Check friendship status first
   
3. **Request already sent**
   - Solution: Check sent requests list

**Debug:**
```sql
-- In Supabase SQL Editor
SELECT * FROM friend_requests WHERE from_user_id = 'YOUR_ID';
SELECT * FROM friends WHERE user_id = 'YOUR_ID';
```

### Issue: Supabase RLS errors

**Symptoms:** "Row level security policy violated"

**Solution:**
1. Check RLS policies are created (from migration)
2. Verify you're passing correct user_id
3. Check Supabase logs in dashboard

**Debug:**
```sql
-- Disable RLS temporarily for testing
ALTER TABLE friends DISABLE ROW LEVEL SECURITY;
ALTER TABLE friend_requests DISABLE ROW LEVEL SECURITY;

-- Re-enable after testing
ALTER TABLE friends ENABLE ROW LEVEL SECURITY;
ALTER TABLE friend_requests ENABLE ROW LEVEL SECURITY;
```

### Issue: CORS errors

**Symptoms:** "Access blocked by CORS policy"

**Solution:**
Update `app.py`:
```python
CORS(app, origins=[
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "your-frontend-url"
])
```

### Issue: "Cannot find module" errors

**Symptoms:** Import errors in Python

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Friends not showing in list

**Symptoms:** Friends list empty but friendships exist in DB

**Possible Causes:**
1. **User data not in storage**
   - Solution: Sync activities for all users
   
2. **Bidirectional friendship missing**
   - Solution: Check both directions exist in DB

**Debug:**
```sql
-- Check friendships
SELECT * FROM friends WHERE user_id = 'YOUR_ID' OR friend_id = 'YOUR_ID';

-- Should see 2 rows for each friendship (bidirectional)
```

### Issue: Strava OAuth fails

**Symptoms:** Redirect to Strava works but callback fails

**Solution:**
1. Check `REDIRECT_URI` in `app.py` matches Strava settings
2. Verify Strava credentials in `.env`
3. Check Strava API app settings at strava.com/settings/api

**Strava Callback URL should be:**
```
http://localhost:5000/auth/strava/callback
```

### Issue: Database connection fails

**Symptoms:** "Connection refused" or "Invalid credentials"

**Solution:**
1. Check `db_URL` and `db_KEY` in `strava_user.py`
2. Verify Supabase project is active
3. Check internet connection

---

## 📊 Logging Reference

### Backend Logging Levels

All backend operations log with prefixes:

**Data Storage:**
```
[DATA STORAGE] Loading users from data/users.json
[DATA STORAGE] Saved user: 67126670
```

**Friends System:**
```
[SUPABASE FRIENDS] Sending friend request from X to Y
[SUPABASE FRIENDS] Success: Friend request sent
[SUPABASE FRIENDS] Error: Already friends
```

**API Endpoints:**
```
[FRIENDS API - SUPABASE] Search users endpoint called
[FRIENDS API - SUPABASE] Found 5 matching users
```

**Strava Parser:**
```
[STRAVA PARSER] Parsing 15 activities
[STRAVA PARSER] Filtered to 12 running activities
```

### Enabling Debug Mode

**Backend:**
```python
# In app.py
app.run(debug=True)  # Shows detailed error traces
```

**Frontend:**
```javascript
// In config.js
console.log(`[DEBUG] API Response:`, response);
```

### Log Locations

**Development:**
- Backend: Terminal where `python app.py` is running
- Frontend: Browser DevTools → Console

**Production:**
- Backend: Render/Railway dashboard logs
- Frontend: Browser console (user's browser)

---

## 🧪 Testing Checklist Before Deployment

### Backend Testing
- [ ] All endpoints return correct status codes
- [ ] Authentication works (OAuth flow)
- [ ] Activity sync completes without errors
- [ ] Friends system (all CRUD operations)
- [ ] Leaderboard calculates correctly
- [ ] Routes system works
- [ ] Error handling works (try invalid inputs)

### Frontend Testing
- [ ] All pages load without errors
- [ ] Forms validate input
- [ ] Buttons trigger correct actions
- [ ] Success/error messages display
- [ ] Loading states work
- [ ] Mobile responsive (test on phone)

### Integration Testing
- [ ] Frontend → Backend communication works
- [ ] Backend → Supabase communication works
- [ ] Backend → Strava API communication works
- [ ] OAuth flow end-to-end works
- [ ] Data flows: Strava → Backend → Database → Frontend

### Data Integrity
- [ ] No duplicate friendships
- [ ] Bidirectional friendships maintained
- [ ] Scores calculate consistently
- [ ] Activity data syncs correctly
- [ ] User profiles update properly

### Security Testing
- [ ] Can't access other users' data
- [ ] API endpoints require authentication
- [ ] RLS policies work (Supabase)
- [ ] No secrets exposed in frontend
- [ ] CORS configured correctly

---

## 🚀 Quick Debug Commands

**Check if backend is running:**
```bash
curl http://localhost:5000/
```

**Check authentication:**
```bash
curl http://localhost:5000/api/status
```

**Test Supabase connection:**
```python
from supabase_stravaDB.strava_user import db
print(db.table("user_strava").select("*").execute())
```

**Clear browser cache:**
- Chrome: Ctrl+Shift+Del → Clear cached images/files
- Firefox: Ctrl+Shift+Del → Cache
- Or open in Incognito/Private mode

**Reset database (careful!):**
```sql
-- In Supabase SQL Editor
TRUNCATE TABLE friends CASCADE;
TRUNCATE TABLE friend_requests CASCADE;
```

---

## 📞 Getting Help

If tests fail:

1. **Check logs** - Backend terminal and browser console
2. **Verify setup** - Database tables created, env vars set
3. **Test incrementally** - One feature at a time
4. **Use debug commands** - Above quick commands
5. **Check this guide** - Common issues section

**Still stuck?**
- Check Supabase dashboard for errors
- Review API endpoint logs
- Verify data in database matches expectations

---

**Last Updated:** November 24, 2025  
**Status:** Supabase Friends Implementation Complete ✅

