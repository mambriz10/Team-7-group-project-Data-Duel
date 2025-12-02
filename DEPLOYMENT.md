# 🚀 DataDuel - Deployment Guide

Complete guide for deploying DataDuel to production (Cloudflare Pages + Render/Railway).

---

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Deployment (Render)](#backend-deployment-render)
4. [Frontend Deployment (Cloudflare Pages)](#frontend-deployment-cloudflare-pages)
5. [Supabase Setup](#supabase-setup)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│  Browser (Desktop/Mobile) - Static HTML/CSS/JS              │
│  Hosted on: Cloudflare Pages (CDN + Edge Network)           │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS/REST API Calls
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  Flask Backend API (Python 3.8+)                            │
│  Hosted on: Render.com / Railway.app / Heroku               │
│  Endpoints: Auth, Sync, Profile, Friends, Routes            │
└─────────────────┬───────────────────────────────────────────┘
                  │ Database Queries + API Calls
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  Primary: Supabase PostgreSQL (user profiles, friends)      │
│  Secondary: JSON Files (scores, activities, cache)          │
│  External: Strava API (activity sync, OAuth)                │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Prerequisites

### Accounts Needed
- [ ] GitHub account (for code repository)
- [ ] Cloudflare account (for frontend hosting)
- [ ] Render.com account (for backend hosting)
- [ ] Supabase account (for database)
- [ ] Strava API app (for OAuth)

### Local Setup Verified
- [ ] Backend runs locally (`python app.py` works)
- [ ] Frontend loads in browser
- [ ] Strava OAuth works
- [ ] Friends system tested

---

## ⚙️ Backend Deployment (Render)

### Step 1: Prepare Repository

Files should already be in your repo:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Start command
- ✅ `DataDuel/backend/app.py` - Flask server

### Step 2: Create Web Service

1. Go to https://render.com (sign up/login)
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect GitHub"** → Select your repository
4. Configure:
   - **Name:** `dataduel-backend`
   - **Environment:** Python 3
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd DataDuel/backend && python app.py`
   - **Instance Type:** Free

### Step 3: Add Environment Variables

In Render dashboard → Your service → Environment

Add these variables:

```
PORT=10000
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
REDIRECT_URI=https://dataduel-backend.onrender.com/auth/strava/callback
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
```

**Get Strava credentials:** https://www.strava.com/settings/api  
**Get Supabase credentials:** Supabase dashboard → Settings → API

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for initial deploy
3. Check logs for errors
4. Copy your backend URL: `https://dataduel-backend.onrender.com`

### Step 5: Verify Backend

Test the deployment:

```bash
curl https://dataduel-backend.onrender.com/
```

Should return: `{"message": "DataDuel API Server Running!", ...}`

---

## 🌐 Frontend Deployment (Cloudflare Pages)

### Step 1: Cloudflare Dashboard

1. Go to https://dash.cloudflare.com
2. Click **"Workers & Pages"**
3. Click **"Create application"** → **"Pages"** tab
4. Click **"Connect to Git"**

### Step 2: Connect Repository

1. Authorize Cloudflare to access GitHub
2. Select repository: `Team-7-group-project-Data-Duel`
3. Click **"Begin setup"**

### Step 3: Configure Build Settings

**Project name:** `dataduel`  
**Production branch:** `main`

**Build settings:**
- **Framework preset:** None
- **Build command:** *(leave empty)*
- **Build output directory:** `DataDuel/frontend`
- **Root directory:** *(leave empty)*

### Step 4: Deploy

1. Click **"Save and Deploy"**
2. Wait 2-3 minutes
3. Your site will be at: `https://dataduel-xxx.pages.dev`

**The `wrangler.toml` file in your repo already configures:**
- Security headers (XSS protection, clickjacking prevention)
- Caching strategy (assets 1yr, CSS/JS 1day, HTML 1hr)
- HTTP → HTTPS redirect

---

## 🗄️ Supabase Setup

### Step 1: Run Migration

1. Open Supabase Dashboard → SQL Editor
2. Copy contents of `DataDuel/backend/supabase_stravaDB/migration_friends.sql`
3. Paste and click **"Run"**
4. Verify tables created:
   ```sql
   SELECT * FROM friends;
   SELECT * FROM friend_requests;
   ```

### Step 2: Verify Row Level Security

Check that RLS is enabled:

```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('friends', 'friend_requests');
```

Both should show `rowsecurity = true`

### Step 3: Test Tables

Insert test data:

```sql
-- Test friend request (replace UUIDs with real ones)
INSERT INTO friend_requests (from_user_id, to_user_id)
VALUES ('your-user-uuid', 'friend-user-uuid');

-- Verify
SELECT * FROM friend_requests;
```

---

## 🔗 Post-Deployment Configuration

### Step 1: Update Frontend Config

**File:** `DataDuel/frontend/config.js`

```javascript
production: {
  apiUrl: 'https://dataduel-backend.onrender.com',  // ← Your Render URL
  environment: 'production'
}
```

### Step 2: Update Backend CORS

**File:** `DataDuel/backend/app.py`

```python
CORS(app, origins=[
    "http://localhost:5500",
    "https://dataduel-xxx.pages.dev",  // ← Your Cloudflare URL
    "https://dataduel-backend.onrender.com"
])
```

### Step 3: Update Strava OAuth

1. Go to: https://www.strava.com/settings/api
2. **Authorization Callback Domain:**
   ```
   dataduel-backend.onrender.com
   ```
3. **Authorization Callback URL:**
   ```
   https://dataduel-backend.onrender.com/auth/strava/callback
   ```

### Step 4: Update Backend Redirect URI

**File:** `DataDuel/backend/app.py`

```python
REDIRECT_URI = os.getenv(
    "REDIRECT_URI",
    "https://dataduel-backend.onrender.com/auth/strava/callback"
)
```

Or set in Render environment variables (recommended).

### Step 5: Commit and Deploy

```bash
git add DataDuel/frontend/config.js DataDuel/backend/app.py
git commit -m "Configure production URLs"
git push origin main
```

- Cloudflare auto-deploys (2-3 min)
- Render auto-deploys (5-10 min)

---

## ✅ Testing Checklist

### Backend Tests

1. **Health Check:**
   ```bash
   curl https://dataduel-backend.onrender.com/
   ```
   Should return API info

2. **Strava OAuth:**
   - Visit `https://dataduel-backend.onrender.com/auth/strava`
   - Should redirect to Strava
   - Authorize and check callback works

3. **API Endpoints:**
   ```bash
   curl https://dataduel-backend.onrender.com/api/leaderboard
   ```
   Should return JSON data

### Frontend Tests

1. **Site Loads:**
   - Visit `https://dataduel-xxx.pages.dev`
   - All pages should load without errors

2. **Environment Detection:**
   - Open browser console
   - Should show: `[DataDuel Config] Environment: production`
   - Should show: `API URL: https://dataduel-backend.onrender.com`

3. **Connect Strava:**
   - Click "Connect Strava" button
   - OAuth flow should complete
   - Redirect back to app

4. **Sync Activities:**
   - Click "Sync Activities"
   - Should fetch from backend
   - Success message displays

5. **Friends System:**
   - Go to social page
   - Search for users
   - Send friend request
   - Accept/reject works

### End-to-End Test

Complete user journey:
1. ✅ Visit site
2. ✅ Connect Strava
3. ✅ Sync activities
4. ✅ View profile (stats display)
5. ✅ View leaderboard (rankings show)
6. ✅ Add friend (request sends)
7. ✅ Accept request (becomes friends)
8. ✅ View friends list (friend displays)

---

## 🐛 Troubleshooting

### Issue: "Not authenticated" error

**Solution:**
1. Clear browser cookies
2. Reconnect Strava
3. Check backend logs in Render dashboard

### Issue: CORS errors

**Symptoms:** "Access blocked by CORS policy" in browser console

**Solution:**
1. Verify CORS origins in `app.py` include your Cloudflare URL
2. Redeploy backend
3. Wait for deployment to complete
4. Hard refresh browser (Ctrl+Shift+R)

### Issue: Backend returns 500 errors

**Solution:**
1. Check Render logs: Dashboard → Your service → Logs
2. Look for Python errors
3. Verify environment variables are set correctly
4. Check Supabase connection

### Issue: Strava OAuth fails

**Solution:**
1. Verify `REDIRECT_URI` in Render env vars matches Strava settings
2. Check Strava API app settings at strava.com/settings/api
3. Ensure callback domain is correct (no http://, just domain)

### Issue: Friends system not working

**Solution:**
1. Verify migration ran in Supabase (check tables exist)
2. Check RLS policies are enabled
3. Test with Supabase SQL directly
4. Check backend logs for errors

### Issue: Cold start delays (Render)

**Symptoms:** First request after 15 min takes 30-60 seconds

**This is normal for Render free tier:**
- Server spins down after 15 min of inactivity
- First request wakes it up (cold start)
- Subsequent requests are fast

**Solutions:**
- Accept the delay (free tier limitation)
- Upgrade to paid tier ($7/month - no cold starts)
- Use a service like UptimeRobot to ping every 10 min

### Issue: Cloudflare deployment fails

**Solution:**
1. Check build logs in Cloudflare dashboard
2. Verify `wrangler.toml` has correct `pages_build_output_dir`
3. Ensure `DataDuel/frontend` directory exists
4. Check that `index.html` is in that directory

---

## 💰 Cost Breakdown

| Service | Tier | Cost | Limitations |
|---------|------|------|-------------|
| **Cloudflare Pages** | Free | $0/month | 500 builds/month, 25,000 requests/day |
| **Render.com** | Free | $0/month | 750 hours/month, 512MB RAM, cold starts |
| **Supabase** | Free | $0/month | 500MB database, 2GB bandwidth |
| **Strava API** | Free | $0/month | 100 req/15min, 1000 req/day |
| **Total** | - | **$0/month** | Sufficient for MVP/demo! |

**Upgrade Options (if needed):**
- Render Starter: $7/month (no cold starts)
- Cloudflare Pages Pro: $20/month (more builds)
- Supabase Pro: $25/month (more storage)

---

## 🔐 Security Best Practices

### Environment Variables

**Never commit these:**
- `STRAVA_CLIENT_SECRET`
- `SUPABASE_KEY` (service role key)
- Any API keys or passwords

**Always set in:**
- Render dashboard (Environment tab)
- Local `.env` file (git-ignored)

### Cloudflare Security

Already configured in `wrangler.toml`:
- ✅ XSS Protection
- ✅ Clickjacking Prevention
- ✅ MIME Sniffing Protection
- ✅ HTTPS Enforcement

### Supabase Security

Already configured in migration:
- ✅ Row Level Security enabled
- ✅ Policies restrict data access
- ✅ Users can only access their own data

---

## 📊 Monitoring

### Backend Monitoring (Render)

1. Dashboard → Your service → **Logs**
2. Real-time logs of all requests
3. Search for `[ERROR]` to find issues

### Frontend Monitoring (Cloudflare)

1. Dashboard → Pages → Your project → **Analytics**
2. View: Page views, requests, bandwidth
3. Check error rates

### Uptime Monitoring

Use a service like:
- UptimeRobot (free)
- Pingdom
- StatusCake

Ping your backend every 5-10 min to prevent cold starts.

---

## 🚀 Quick Deployment Script

Save as `deploy.sh`:

```bash
#!/bin/bash

echo "🚀 DataDuel Deployment Helper"

# Get URLs
read -p "Backend URL (e.g., dataduel-backend.onrender.com): " BACKEND
read -p "Frontend URL (e.g., dataduel-xxx.pages.dev): " FRONTEND

# Update config.js
sed -i "s|apiUrl: 'https://.*\.onrender\.com'|apiUrl: 'https://$BACKEND'|" \
  DataDuel/frontend/config.js

echo "✅ Updated config.js"
echo "⚠️  Manual: Update CORS in app.py to include: https://$FRONTEND"
echo "⚠️  Manual: Update Strava callback to: $BACKEND"

# Commit
git add DataDuel/frontend/config.js
git commit -m "Configure production URLs"
git push origin main

echo "✅ Pushed to GitHub"
echo "⏳ Wait 2-3 min for auto-deploy"
echo "🎉 Done!"
```

---

**Last Updated:** November 24, 2025  
**Status:** Production-Ready Configuration ✅

