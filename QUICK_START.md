# DataDuel MVP - Quick Start Guide

**⚡ Get your MVP running in 5 minutes!**

---

## 🚀 Setup (First Time Only)

### 1. Install Dependencies
```bash
cd Team-7-group-project-Data-Duel
pip install -r requirements.txt
```

### 2. Get Strava API Credentials
1. Go to https://www.strava.com/settings/api
2. Create a new application
3. Set "Authorization Callback Domain" to: `localhost`
4. Copy your **Client ID** and **Client Secret**

### 3. Configure Environment
Create `DataDuel/backend/.env`:
```env
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:5000/auth/strava/callback
```

---

## ▶️ Run the Application

### Start Backend Server
```bash
cd DataDuel/backend
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### Open Frontend
Open in your browser:
```
file:///path/to/DataDuel/frontend/index.html
```

Or simply double-click `DataDuel/frontend/index.html`

---

## ✅ Test the Complete Flow

### Test 1: Check Backend
1. Backend should be running on port 5000
2. Visit: http://localhost:5000
3. Should see: `{"message": "🏃 DataDuel API Server Running!", ...}`

### Test 2: Connect Strava
1. Open `frontend/index.html` in browser
2. Home page should show "✅ Backend reachable" or "⚠️ Not connected to Strava"
3. Click "Connect Strava"
4. Authorize on Strava website
5. Should redirect back with success message
6. Check: `backend/tokens.json` file should exist

### Test 3: Sync Activities
1. Home page should now show "✅ Connected to Strava"
2. Click "🔄 Sync Activities"
3. Wait 2-5 seconds
4. Alert should show:
   ```
   ✅ Sync successful!
   
   Workouts: X
   Distance: X km
   Score: X
   ```
5. Check: `backend/data/` folder should contain:
   - `users.json` (your profile)
   - `activities.json` (your runs)
   - `scores.json` (your score)

### Test 4: View Profile
1. Click "My Profile" or navigate to `profile.html`
2. Should see YOUR actual data:
   - Name from Strava
   - Username
   - Location
   - Number of runs
   - Distance
   - Pace
   - Score

### Test 5: Check Leaderboard
1. Click "View Leaderboards" or navigate to `leaderboards.html`
2. Should see a table with:
   - Your username
   - Your rank
   - Your score
   - Your row highlighted

---

## 🐛 Troubleshooting

### ❌ "Backend not reachable"
**Solution:** Make sure Flask server is running
```bash
cd DataDuel/backend
python app.py
```

### ❌ "tokens.json not found"
**Solution:** You need to authenticate first
1. Click "Connect Strava" on home page
2. Complete OAuth authorization

### ❌ "No module named 'flask_cors'"
**Solution:** Install dependencies
```bash
pip install flask-cors
# OR
pip install -r requirements.txt
```

### ❌ Leaderboard shows no data
**Solution:** Sync your activities first
1. Go to home page
2. Click "🔄 Sync Activities"
3. Then check leaderboard

### ❌ "Failed to fetch activities"
**Possible causes:**
1. Token expired (try re-authenticating)
2. Strava API is down (wait and try again)
3. No running activities in your Strava account

---

## 📁 Important Files

### Backend
- `app.py` - Main Flask server
- `.env` - API credentials (YOU CREATE THIS)
- `tokens.json` - OAuth tokens (auto-generated)
- `data/` - Stored data (auto-generated)

### Frontend
- `index.html` - Home page (auth & sync)
- `profile.html` - User profile
- `leaderboards.html` - Rankings
- `api.js` - API client

---

## 🎯 Demo Checklist

Before your demo, verify:
- [ ] Backend server running on port 5000
- [ ] You're authenticated with Strava (`tokens.json` exists)
- [ ] Activities synced (`backend/data/` folder populated)
- [ ] Profile page loads your data
- [ ] Leaderboard shows your score
- [ ] All pages load without errors

---

## 📚 Full Documentation

For detailed technical documentation, see:
- **`MVP_IMPLEMENTATION.md`** - Complete implementation guide
- **`README.md`** - Project overview
- **`route-guide.md`** - Route generation feature plan

---

## 🆘 Need Help?

Common issues and solutions documented in `MVP_IMPLEMENTATION.md` under "Known Issues & Limitations".

---

**🎉 You're ready for the demo! Good luck! 🚀**

