# CloudFlare Pages Deployment Guide for DataDuel

## 📋 Overview

**CloudFlare Pages** is perfect for our frontend (static HTML/JS/CSS).  
**CloudFlare Workers** or external service needed for Flask backend.

### Architecture:
```
Frontend (Static) → CloudFlare Pages
Backend (Flask)   → Render/Railway/Heroku
Database (JSON)   → Upgraded to Supabase storage
```

---

## 🎯 Deployment Strategy

### Option A: Hybrid (Recommended)
- **Frontend:** CloudFlare Pages (free, fast CDN)
- **Backend:** Render.com or Railway.app (free tier)
- **Reason:** Flask needs a Python runtime, CloudFlare Pages is static-only

### Option B: Full CloudFlare
- **Frontend:** CloudFlare Pages
- **Backend:** CloudFlare Workers (requires rewriting Flask → Workers)
- **Reason:** More complex, but fully on CloudFlare infrastructure

**We'll use Option A** (easier and faster to deploy)

---

## 🚀 Phase 1: Prepare Frontend for CloudFlare Pages

### Step 1: Create CloudFlare-Specific Config

Create `DataDuel/frontend/_headers`:
```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  
/api/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  Access-Control-Allow-Headers: Content-Type, Authorization
```

Create `DataDuel/frontend/_redirects`:
```
# SPA-like routing (optional)
/*    /index.html   200

# API proxy to backend (configure after backend is deployed)
/api/*  https://your-backend-url.onrender.com/api/:splat  200
```

### Step 2: Update Frontend API URLs

We need to use environment-aware URLs. Let's create a config file:

Create `DataDuel/frontend/config.js`:
```javascript
// Configuration for different environments
const config = {
  development: {
    apiUrl: 'http://127.0.0.1:5000'
  },
  production: {
    apiUrl: 'https://dataduel-backend.onrender.com'  // Update after backend deploy
  }
};

// Auto-detect environment
const ENV = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'development'
  : 'production';

export const API_URL = config[ENV].apiUrl;
export const ENVIRONMENT = ENV;

console.log(`[CONFIG] Running in ${ENV} mode`);
console.log(`[CONFIG] API URL: ${API_URL}`);
```

### Step 3: Update All Frontend Files

We need to update these files to use the config:

**Files to update:**
- `index.html`
- `profile.html`
- `social.html`
- `Strava.html`
- `api.js`

**Example update for social.html:**

Change this:
```javascript
const BACKEND_URL = "http://127.0.0.1:5000";
```

To this:
```javascript
import { API_URL } from './config.js';
const BACKEND_URL = API_URL;
```

### Step 4: Create Build Config

Create `DataDuel/frontend/wrangler.toml` (for CloudFlare):
```toml
name = "dataduel-frontend"
compatibility_date = "2025-11-24"

[site]
bucket = "./"
```

---

## 🚀 Phase 2: Deploy Backend First

Before deploying frontend, we need the backend URL.

### Option 1: Deploy to Render.com (Easiest - FREE)

#### A. Prepare Backend Files

Create `requirements.txt` in **project root**:
```txt
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
python-dotenv==1.0.0
supabase==2.0.0
```

Create `Procfile` in **project root**:
```
web: cd DataDuel/backend && python app.py
```

Update `DataDuel/backend/app.py` - change last lines:
```python
if __name__ == "__main__":
    # Get PORT from environment (for cloud deployment)
    port = int(os.environ.get("PORT", 5000))
    
    # Allow external connections
    app.run(host="0.0.0.0", port=port, debug=False)
```

#### B. Deploy on Render.com

1. Go to https://render.com and sign up (free)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `dataduel-backend`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd DataDuel/backend && python app.py`
   - **Instance Type:** Free
5. Add **Environment Variables:**
   - `PORT` = `10000` (or leave blank)
   - `STRAVA_CLIENT_ID` = (your Strava client ID)
   - `STRAVA_CLIENT_SECRET` = (your Strava secret)
6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deploy
8. Copy your URL: `https://dataduel-backend.onrender.com`

#### C. Update Strava OAuth Callback

1. Go to https://www.strava.com/settings/api
2. Update "Authorization Callback Domain" to:
   ```
   dataduel-backend.onrender.com
   ```
3. Update redirect URI in `app.py`:
   ```python
   REDIRECT_URI = "https://dataduel-backend.onrender.com/auth/strava/callback"
   ```
4. Redeploy backend (Render auto-redeploys on git push)

### Option 2: Deploy to Railway.app

1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway auto-detects Flask and deploys
6. Copy deployment URL
7. Add environment variables in Railway dashboard

---

## 🚀 Phase 3: Deploy Frontend to CloudFlare Pages

### Your Groupmate's Steps (Who Owns the Repo)

#### Step 1: Connect GitHub to CloudFlare

1. Go to https://dash.cloudflare.com
2. Click **"Workers & Pages"**
3. Click **"Create application"**
4. Click **"Pages"** tab
5. Click **"Connect to Git"**
6. Authorize CloudFlare to access GitHub
7. Select repository: `Team-7-group-project-Data-Duel`

#### Step 2: Configure Build Settings

- **Project name:** `dataduel`
- **Production branch:** `main`
- **Build command:** Leave empty (static files)
- **Build output directory:** `DataDuel/frontend`
- **Root directory:** Leave empty

#### Step 3: Add Environment Variables (Optional)

In CloudFlare dashboard → Project → Settings → Environment variables:
- `API_URL` = `https://dataduel-backend.onrender.com`

#### Step 4: Deploy

1. Click **"Save and Deploy"**
2. Wait 2-3 minutes
3. Your site will be at: `https://dataduel.pages.dev`
4. Can add custom domain later

#### Step 5: Configure CORS in Backend

Update `DataDuel/backend/app.py`:
```python
CORS(app, origins=[
    "http://localhost:5500",
    "https://dataduel.pages.dev",
    "https://dataduel-backend.onrender.com"
])
```

Push changes and backend will auto-redeploy.

---

## 📝 Configuration Files Summary

### Files You Need to Create:

1. **`requirements.txt`** (project root)
2. **`Procfile`** (project root)  
3. **`DataDuel/frontend/config.js`**
4. **`DataDuel/frontend/_headers`** (optional)
5. **`DataDuel/frontend/_redirects`** (optional)

### Files You Need to Modify:

1. **`DataDuel/backend/app.py`** - Update CORS, port, redirect URI
2. **`DataDuel/frontend/social.html`** - Use config.js
3. **`DataDuel/frontend/index.html`** - Use config.js
4. **`DataDuel/frontend/profile.html`** - Use config.js
5. **`DataDuel/frontend/Strava.html`** - Use config.js
6. **`DataDuel/frontend/api.js`** - Use config.js

---

## 🎯 Quick Setup Commands

Run these in your project root:

```bash
# Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
python-dotenv==1.0.0
supabase==2.0.0
EOF

# Create Procfile
echo "web: cd DataDuel/backend && python app.py" > Procfile

# Commit changes
git add .
git commit -m "Prepare for CloudFlare Pages + Render deployment"
git push origin main
```

---

## ✅ Deployment Checklist

### Backend (Render.com):
- [ ] Create requirements.txt
- [ ] Create Procfile
- [ ] Update app.py for PORT and host
- [ ] Deploy on Render.com
- [ ] Get backend URL
- [ ] Update Strava OAuth callback
- [ ] Test API endpoints

### Frontend (CloudFlare Pages):
- [ ] Create config.js
- [ ] Update all HTML files to use config
- [ ] Update CORS in backend
- [ ] Groupmate connects GitHub to CloudFlare
- [ ] Configure build settings
- [ ] Deploy to CloudFlare Pages
- [ ] Get frontend URL
- [ ] Test full flow

### Final Testing:
- [ ] Visit CloudFlare Pages URL
- [ ] Click "Connect Strava"
- [ ] Complete OAuth (should redirect properly)
- [ ] Sync activities
- [ ] Check profile loads with data
- [ ] Test friends feature
- [ ] Test leaderboard
- [ ] Verify all features work

---

## 🐛 Common Issues & Solutions

### Issue: CORS errors on deployed site
**Solution:** Add your CloudFlare Pages URL to CORS origins in app.py

### Issue: Strava OAuth fails
**Solution:** Verify callback URL in Strava settings matches deployed backend

### Issue: API calls fail from frontend
**Solution:** Check config.js has correct backend URL

### Issue: Backend doesn't start on Render
**Solution:** Check logs, ensure all dependencies in requirements.txt

### Issue: CloudFlare Pages build fails
**Solution:** It shouldn't! No build needed for static files

---

## 🔄 Update Workflow

After initial deployment:

### To Update Backend:
1. Make changes to backend files
2. Commit and push to GitHub
3. Render auto-deploys (or manual deploy in dashboard)

### To Update Frontend:
1. Make changes to frontend files
2. Commit and push to GitHub
3. CloudFlare auto-deploys from main branch

---

## 💰 Cost Breakdown

- **CloudFlare Pages:** FREE (500 builds/month)
- **Render.com Free Tier:** FREE (spins down after 15 min inactivity)
- **Railway Free Tier:** $5/month credit (FREE for small apps)
- **Total:** $0/month for MVP!

**Limitations:**
- Render free tier: Slow cold starts (15-30 seconds)
- CloudFlare Pages: 25,000 requests/day (plenty for MVP)

---

## 🎓 What Your Groupmate Needs to Do

Send this message to whoever owns the GitHub repo:

```
Hi! Here's how to set up CloudFlare Pages for DataDuel:

1. Go to https://dash.cloudflare.com
2. Click "Workers & Pages" → "Create application" → "Pages"
3. Connect to Git → Select our repo
4. Configuration:
   - Project name: dataduel
   - Build output: DataDuel/frontend
   - Build command: (leave empty)
5. Deploy!

The site will be at: https://dataduel.pages.dev

Let me know when it's done so I can test!
```

---

## 📞 Next Steps

1. **Test friends feature locally** first
2. **Deploy backend** to Render (you can do this)
3. **Send CloudFlare instructions** to groupmate
4. **Update all URLs** after backend is deployed
5. **Test deployed site** together
6. **Demo ready!** 🎉

---

**Status:** ✅ Configuration files ready  
**Next:** Deploy backend, then frontend

