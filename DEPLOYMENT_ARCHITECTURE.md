# 🏗️ DataDuel - Complete Deployment Architecture

## 📊 System Overview

DataDuel is a **three-tier web application** with the following architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│  Browser (Desktop/Mobile) - Static HTML/CSS/JS              │
│  Hosted on: Cloudflare Pages (CDN + Edge Network)           │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS Requests
                  │ (API calls via fetch)
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  Flask Backend API (Python 3.8+)                            │
│  Hosted on: Render.com / Railway.app / Heroku               │
│  Endpoints: Auth, Sync, Profile, Friends, Routes            │
└─────────────────┬───────────────────────────────────────────┘
                  │ Database Queries
                  │ (Supabase SDK + JSON)
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  Primary: Supabase PostgreSQL (user profiles, activities)   │
│  Secondary: JSON Files (scores, friends, temporary data)    │
│  External: Strava API (activity sync, OAuth)                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌐 Frontend Deployment (Cloudflare Pages)

### What Gets Deployed
**Location:** `DataDuel/frontend/`

**Static Files:**
- **HTML Pages** (14 files):
  - `index.html` - Home/dashboard
  - `profile.html`, `profile-*.html` - User profiles
  - `social.html`, `socialTest.html` - Friends system
  - `leaderboards.html` - Rankings
  - `routes.html` - Route discovery
  - `login.html`, `register.html` - Auth pages
  - `Strava.html` - Strava connection
  - `settings.html` - App settings

- **JavaScript Modules** (ES6+):
  - `config.js` - **Environment auto-detection**
  - `api.js` - API client wrapper
  - `script.js` - Tab navigation
  - `strava_user_frontend.js` - Strava integration
  - `testBackend.js`, `testingAPI.js` - Testing utilities
  - `js/login.js`, `js/register.js` - Auth logic
  - `supabaseClient/supabaseClient.js` - DB client

- **Styling:**
  - `styles.css` - Global responsive styles

- **Cloudflare Config:**
  - `_headers` - Security headers (CSP, CORS, etc.)
  - `_redirects` - SPA routing, API proxying

### Configuration Files

#### 1. `wrangler.toml` (Root directory)
**Purpose:** Tells Cloudflare Pages where files are and how to serve them

**Key Settings:**
```toml
name = "dataduel"
pages_build_output_dir = "DataDuel/frontend"
[site]
bucket = "./DataDuel/frontend"
```

**Features:**
- ✅ Security headers (XSS, clickjacking protection)
- ✅ Cache optimization (CSS/JS/HTML)
- ✅ HTTP → HTTPS redirect
- ✅ Asset immutability for performance
- ✅ Environment-specific configs

#### 2. `config.js` (DataDuel/frontend/)
**Purpose:** Auto-detects dev vs prod and sets backend API URL

**How It Works:**
```javascript
// Detects environment based on hostname
if (window.location.hostname === 'localhost') {
  // Development: http://127.0.0.1:5000
} else {
  // Production: https://dataduel-backend.onrender.com
}
```

**You Update Once:** Change production URL after backend deployment

#### 3. `_headers` (DataDuel/frontend/)
**Purpose:** Custom HTTP headers for security and CORS

**Key Headers:**
- `X-Frame-Options: DENY` - Prevent clickjacking
- `X-Content-Type-Options: nosniff` - Prevent MIME sniffing
- `Access-Control-Allow-Origin` - CORS for API calls

#### 4. `_redirects` (DataDuel/frontend/)
**Purpose:** URL redirects and SPA routing

**Example Use:**
```
/*    /index.html   200     # SPA fallback
/api/*  https://backend.com/api/:splat  200  # API proxy
```

### Deployment Process

**Method 1: Cloudflare Dashboard (Recommended)**
1. Go to https://dash.cloudflare.com
2. **Workers & Pages** → **Create application** → **Pages**
3. **Connect to Git** → Select `Team-7-group-project-Data-Duel`
4. Configure:
   - **Project name:** `dataduel`
   - **Production branch:** `main`
   - **Build command:** *(leave empty)*
   - **Build output directory:** `DataDuel/frontend`
   - **Root directory:** *(leave empty)*
5. **Save and Deploy**

**Method 2: Wrangler CLI**
```bash
npm install -g wrangler
wrangler pages deploy DataDuel/frontend --project-name=dataduel
```

**Result:** Site live at `https://dataduel-xxx.pages.dev` in 1-3 minutes

### Environment Variables (Optional)
Set in **Cloudflare Dashboard** → **Pages** → **Settings** → **Environment variables**:

| Variable | Purpose | Required? |
|----------|---------|-----------|
| `BACKEND_API_URL` | Override production backend URL | No (config.js handles it) |
| `SUPABASE_URL` | Supabase project URL | No (set in client JS) |
| `SUPABASE_ANON_KEY` | Supabase public key | No (set in client JS) |

**Note:** These are **public** (client-side). Never store secrets here.

---

## ⚙️ Backend Deployment (Render.com / Railway / Heroku)

### What Gets Deployed
**Location:** `DataDuel/backend/`

**Python Application:**
- **Main Server:** `app.py` (1190 lines)
  - Flask server with 30+ endpoints
  - Strava OAuth flow
  - Activity sync and parsing
  - Friends system API
  - Route generation
  - Scoring calculations

- **Core Modules:**
  - `data_storage.py` - JSON file operations
  - `friends_storage.py` - Friends data management
  - `strava_parser.py` - Activity parsing logic
  - `route_generator.py` - Route discovery
  - `supabase_stravaDB/strava_user.py` - Database operations

- **Data Models:** (Parent directory)
  - `Person.py` - User data model
  - `Score.py` - Scoring algorithm
  - `badges.py` - Badge system
  - `challenges.py` - Challenge system
  - `leagueLeaderboard.py` - League management

- **Data Storage:**
  - `data/users.json` - User profiles
  - `data/activities.json` - Strava activities
  - `data/scores.json` - Calculated scores
  - `data/friends.json` - Friend relationships
  - `tokens.json` - OAuth tokens (auto-created)
  - `credentials.json` - Strava API keys (auto-created)

### Configuration Files

#### 1. `requirements.txt` (Root directory)
**Purpose:** Python dependencies for backend

```
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
python-dotenv==1.0.0
supabase==2.0.0
```

#### 2. `Procfile` (Root directory)
**Purpose:** Tells cloud platform how to start the app

```
web: cd DataDuel/backend && python app.py
```

**Why `cd DataDuel/backend`?**
- App needs to run from backend directory
- Ensures relative imports work correctly
- Finds data/ directory properly

#### 3. `.env` (DataDuel/backend/ - **NOT COMMITTED**)
**Purpose:** Local development secrets

```env
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
REDIRECT_URI=http://localhost:5000/auth/strava/callback
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key-here
```

**Production:** Set these as **environment variables** in hosting dashboard

#### 4. `app.py` Configuration Updates

**Current (Local):**
```python
CORS(app, origins="http://localhost:5500")
REDIRECT_URI = "http://127.0.0.1:5000/auth/strava/callback"

if __name__ == "__main__":
    app.run(debug=True)
```

**Production (Update to):**
```python
CORS(app, origins=[
    "http://localhost:5500",  # Local development
    "https://dataduel-xxx.pages.dev",  # Cloudflare Pages
    os.getenv("FRONTEND_URL", "")  # Custom domain (optional)
])

REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/auth/strava/callback")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

### Deployment Process

#### Render.com (Recommended - Easiest)

**Step 1: Create Service**
1. Go to https://render.com (sign up free)
2. **New +** → **Web Service**
3. **Connect GitHub** → Select repo
4. Configure:
   - **Name:** `dataduel-backend`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd DataDuel/backend && python app.py`
   - **Instance Type:** Free

**Step 2: Environment Variables**
Add in **Environment** tab:
```
STRAVA_CLIENT_ID=<your_value>
STRAVA_CLIENT_SECRET=<your_value>
REDIRECT_URI=https://dataduel-backend.onrender.com/auth/strava/callback
SUPABASE_URL=<your_value>
SUPABASE_KEY=<your_value>
PORT=10000
```

**Step 3: Deploy**
- Click **Create Web Service**
- Wait 5-10 minutes for deployment
- Copy URL: `https://dataduel-backend.onrender.com`

**Free Tier Limitations:**
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds (cold start)
- 750 hours/month free (enough for MVP/demo)

#### Railway.app (Alternative)

**Simpler Setup:**
1. Go to https://railway.app
2. **New Project** → **Deploy from GitHub**
3. Select repo
4. Railway auto-detects Flask
5. Add environment variables in dashboard
6. Deploy automatically

**Pricing:** $5/month credit (free for small apps)

#### Heroku (Traditional)

**Setup:**
```bash
heroku login
heroku create dataduel-backend
heroku config:set STRAVA_CLIENT_ID=xxx
heroku config:set STRAVA_CLIENT_SECRET=xxx
# ... set other env vars
git push heroku main
```

**Pricing:** $7/month minimum (no free tier anymore)

---

## 🔗 Integration Checklist

After deploying both frontend and backend, follow this checklist:

### 1. Update Frontend Config
**File:** `DataDuel/frontend/config.js`

```javascript
production: {
  apiUrl: 'https://dataduel-backend.onrender.com',  // ← Update this
  environment: 'production'
}
```

**Commit and push:**
```bash
git add DataDuel/frontend/config.js
git commit -m "Update production API URL"
git push origin main
```

### 2. Update Backend CORS
**File:** `DataDuel/backend/app.py`

```python
CORS(app, origins=[
    "http://localhost:5500",
    "https://dataduel-xxx.pages.dev",  # ← Add your Cloudflare URL
    "https://dataduel-backend.onrender.com"
])
```

**Redeploy backend** (auto-deploys on git push for Render/Railway)

### 3. Update Strava OAuth Settings
1. Go to: https://www.strava.com/settings/api
2. **Authorization Callback Domain:**
   ```
   dataduel-backend.onrender.com
   ```
3. **Authorization Callback URL:**
   ```
   https://dataduel-backend.onrender.com/auth/strava/callback
   ```

### 4. Update Backend Redirect URI
**File:** `DataDuel/backend/app.py`

```python
REDIRECT_URI = os.getenv(
    "REDIRECT_URI",
    "https://dataduel-backend.onrender.com/auth/strava/callback"
)
```

**Set in Render environment variables:**
```
REDIRECT_URI=https://dataduel-backend.onrender.com/auth/strava/callback
```

### 5. Test Complete Flow
1. ✅ Visit: `https://dataduel-xxx.pages.dev`
2. ✅ Click "Connect Strava" → Redirects to Strava
3. ✅ Authorize app → Redirects back to app
4. ✅ Click "Sync Activities" → Shows success
5. ✅ Visit Profile → Shows your stats
6. ✅ Visit Leaderboard → Shows rankings
7. ✅ Test Friends → Search and add friends
8. ✅ Check browser console → No errors

---

## 🗄️ Database Architecture

### Supabase (Primary Database)

**Tables:**
- `user_strava`:
  - `user_id` (UUID) - Supabase user ID
  - `client_id`, `client_secret` - Strava API credentials
  - `username`, `email`, `avatar` - Profile data
  - `total_workouts`, `total_distance`, `total_moving_time` - Aggregates
  - `average_speed`, `max_speed` - Performance metrics
  - `streak` - Consecutive days
  - `badges` (JSONB) - Earned badges
  - `weekly_challenges` (JSONB) - Challenge status

**Authentication:**
- Supabase Auth for user accounts
- Strava OAuth for activity data access
- Session tokens passed in API requests

### JSON Files (Secondary Storage)

**Location:** `DataDuel/backend/data/`

**Files:**
1. `users.json` - User profiles (synced with Supabase)
2. `activities.json` - Raw Strava activity data
3. `scores.json` - Calculated improvement scores
4. `friends.json` - Friend relationships and requests

**Why Both?**
- **Supabase:** Persistent, scalable, multi-user
- **JSON:** Fast local cache, easier debugging, MVP simplicity

**Future:** Migrate entirely to Supabase PostgreSQL

---

## 📊 Data Flow Diagram

```
┌──────────────┐
│   Browser    │
│  (Frontend)  │
└──────┬───────┘
       │
       │ 1. User clicks "Connect Strava"
       ↓
┌──────────────────────────────────────────────────┐
│  GET /auth/strava                                 │
│  → Redirects to Strava OAuth                     │
└──────┬───────────────────────────────────────────┘
       │
       │ 2. User authorizes on Strava
       ↓
┌──────────────────────────────────────────────────┐
│  GET /auth/strava/callback?code=xxx              │
│  → Exchanges code for access token               │
│  → Fetches user profile from Strava              │
│  → Creates Person object                         │
│  → Stores in Supabase + users.json               │
└──────┬───────────────────────────────────────────┘
       │
       │ 3. User clicks "Sync Activities"
       ↓
┌──────────────────────────────────────────────────┐
│  POST /api/sync                                   │
│  → GET /strava/activities (fetch from Strava)    │
│  → parse_activities() (filter, aggregate)        │
│  → Person.populate_player_activities_by_day()    │
│  → Calculate baselines, badges, challenges       │
│  → Score.calculate() (improvement scoring)       │
│  → Store: activities.json, scores.json, Supabase │
└──────┬───────────────────────────────────────────┘
       │
       │ 4. User views Profile
       ↓
┌──────────────────────────────────────────────────┐
│  GET /api/profile?user_id=xxx                    │
│  → Load from users.json + scores.json            │
│  → Fetch from Supabase                           │
│  → Calculate pace, format data                   │
│  → Return JSON: {name, stats, score, badges}     │
└──────┬───────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│   Browser    │
│  Displays    │
│   Profile    │
└──────────────┘
```

---

## 🔒 Security Considerations

### Frontend (Public)
- ✅ No secrets in JavaScript (all code is visible)
- ✅ Supabase anon key is safe (public by design)
- ✅ HTTPS enforced via Cloudflare
- ✅ Security headers (XSS, clickjacking protection)
- ✅ CORS restricted to known origins

### Backend (Private)
- ✅ Strava client secret in environment variables
- ✅ OAuth tokens stored server-side (tokens.json)
- ✅ Supabase service key (if needed) in env vars
- ❌ TODO: Encrypt tokens.json in production
- ❌ TODO: Implement rate limiting
- ❌ TODO: Add request validation/sanitization

### Strava API
- ✅ OAuth 2.0 authorization flow
- ✅ Scopes: `read,activity:read_all` (no write access)
- ✅ Token refresh handled automatically
- ✅ Rate limit: 100 requests/15min, 1000/day

---

## 📈 Monitoring & Debugging

### Frontend Debugging
**Browser Console:**
```javascript
// Check environment detection
// Should log: [DataDuel Config] Environment: production
// Open: DevTools → Console

// Test API connectivity
fetch('https://your-backend.onrender.com/')
  .then(r => r.json())
  .then(console.log);
```

**Cloudflare Analytics:**
- Dashboard → Pages → Analytics
- Monitor: Page views, requests, bandwidth
- Check: Error rates, response times

### Backend Debugging
**Logs on Render:**
- Dashboard → Your Service → Logs
- Real-time logs of all requests
- Look for: `[DATA STORAGE]`, `[FRIENDS]` logs

**Test Endpoints:**
```bash
# Health check
curl https://your-backend.onrender.com/

# Auth status (requires user_id)
curl https://your-backend.onrender.com/api/status?user_id=123

# Profile data (requires user_id)
curl https://your-backend.onrender.com/api/profile?user_id=123
```

**Common Issues:**
1. **CORS errors** → Check origins in app.py
2. **Cold start delays** → Free tier limitation (Render)
3. **404 errors** → Check API URL in config.js
4. **Auth failures** → Verify Strava callback URL
5. **Data not saving** → Check file permissions (Render handles this)

---

## 💰 Cost Breakdown

| Service | Tier | Cost | Limits |
|---------|------|------|--------|
| **Cloudflare Pages** | Free | $0/month | 500 builds/month, 25,000 requests/day |
| **Render.com** | Free | $0/month | 750 hours/month, 512MB RAM, cold starts |
| **Supabase** | Free | $0/month | 500MB database, 2GB bandwidth, 50,000 active users |
| **Strava API** | Free | $0/month | 100 req/15min, 1000 req/day |
| **Total** | - | **$0/month** | Sufficient for MVP/demo |

**Upgrade Paths (if needed):**
- Render Starter: $7/month (no cold starts, 512MB RAM)
- Cloudflare Pages Pro: $20/month (5000 builds, unlimited requests)
- Supabase Pro: $25/month (8GB database, 50GB bandwidth)

---

## 🚀 Quick Deployment Script

Save this as `deploy.sh` for quick setup:

```bash
#!/bin/bash

echo "🚀 DataDuel Deployment Helper"
echo ""

# Check if backend URL is set
read -p "Enter your Render backend URL (e.g., dataduel-backend.onrender.com): " BACKEND_URL
read -p "Enter your Cloudflare Pages URL (e.g., dataduel-xxx.pages.dev): " FRONTEND_URL

# Update config.js
echo "📝 Updating config.js..."
sed -i "s|apiUrl: 'https://.*\.onrender\.com'|apiUrl: 'https://$BACKEND_URL'|" DataDuel/frontend/config.js

# Update app.py CORS (manual step - can't automate safely)
echo "⚠️  Manual step required:"
echo "   Update CORS in DataDuel/backend/app.py to include: https://$FRONTEND_URL"
echo ""

# Commit changes
read -p "Commit and push changes? (y/n): " COMMIT
if [ "$COMMIT" = "y" ]; then
    git add DataDuel/frontend/config.js
    git commit -m "Update production URLs for deployment"
    git push origin main
    echo "✅ Changes pushed!"
fi

echo ""
echo "✅ Next steps:"
echo "1. Update Strava OAuth callback: https://www.strava.com/settings/api"
echo "2. Set callback to: https://$BACKEND_URL/auth/strava/callback"
echo "3. Wait for deployments to complete (2-5 minutes)"
echo "4. Test: https://$FRONTEND_URL"
echo ""
echo "🎉 Done! Happy deploying!"
```

---

## 📞 Support & Troubleshooting

**If deployment fails:**
1. Check logs in hosting dashboard
2. Verify environment variables are set
3. Test endpoints individually
4. Review CORS and OAuth settings
5. Check browser console for frontend errors

**Team Resources:**
- `START_HERE.md` - Quick start guide
- `CLOUDFLARE_FIX.md` - Cloudflare-specific fixes
- `CLOUDFLARE_SETUP_CARD.md` - Quick reference
- `CLOUDFLARE_DEPLOYMENT_GUIDE.md` - Full guide
- `PROJECT_STATUS_SUMMARY.md` - Feature status

---

**Last Updated:** November 24, 2025  
**Maintained By:** CS422 Team 7  
**Status:** Production-Ready Architecture ✅

