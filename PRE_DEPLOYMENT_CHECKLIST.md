# ✅ Pre-Deployment Checklist for Render

## 🎯 Before Your Groupmate Clicks "Deploy"

### ✅ Code Changes (DONE)
- [x] Updated CORS to allow Cloudflare Pages
- [x] REDIRECT_URI now uses environment variables
- [x] Supabase credentials use environment variables (with fallback)
- [x] Port configured for Render (0.0.0.0:PORT)
- [x] Production/development detection
- [x] `.gitignore` created (prevents committing secrets)

### ✅ Files Ready (DONE)
- [x] `requirements.txt` - All Python dependencies
- [x] `Procfile` - Correct start command
- [x] `app.py` - Production-ready configuration
- [x] `strava_user.py` - Uses environment variables

---

## 📋 Render Configuration Checklist

### Step 1: Web Service Settings
- [ ] **Name:** `dataduel-backend` (or your choice)
- [ ] **Environment:** Python 3
- [ ] **Branch:** `render` ← **CRITICAL!**
- [ ] **Build Command:** `pip install -r requirements.txt`
- [ ] **Start Command:** `cd DataDuel/backend && python app.py`
- [ ] **Instance Type:** Free

### Step 2: Environment Variables (CRITICAL!)

Copy these **exactly** from `CREDENTIALS_SUMMARY.md`:

- [ ] `PORT` = `10000`
- [ ] `STRAVA_CLIENT_ID` = `131027`
- [ ] `STRAVA_CLIENT_SECRET` = `08cfbed2075d251d1401123ccbe163c5e154a4f5`
- [ ] `REDIRECT_URI` = `https://dataduel-backend.onrender.com/auth/strava/callback`
- [ ] `SUPABASE_URL` = `https://gbvyveaifvqneyayloks.supabase.co`
- [ ] `SUPABASE_KEY` = (long key from CREDENTIALS_SUMMARY.md)

**Note:** If your app name is different from `dataduel-backend`, update `REDIRECT_URI` accordingly!

---

## 🔧 After Deployment Completes

### Step 1: Get Your Render URL
- [ ] Copy the URL: `https://your-app-name.onrender.com`
- [ ] Test it: Visit the URL, should see API info

### Step 2: Update Strava OAuth
- [ ] Go to https://www.strava.com/settings/api
- [ ] **Authorization Callback Domain:** Change to your Render domain (e.g., `dataduel-backend.onrender.com`)
- [ ] **NO https://**, just the domain name!
- [ ] Click "Update"

### Step 3: Update Cloudflare Pages URL in CORS

**If your actual Cloudflare Pages URL is different from `dataduel.pages.dev`:**

1. Find your actual Cloudflare URL (e.g., `dataduel-abc123.pages.dev`)
2. Update `DataDuel/backend/app.py` line 47:
   ```python
   "https://your-actual-url.pages.dev",  # Replace with real URL
   ```
3. OR: Add environment variable in Render:
   - `FRONTEND_URL` = `https://your-actual-url.pages.dev`

**This allows Render to accept requests from your Cloudflare frontend!**

### Step 4: Verify Everything Works

Test these URLs (replace with your actual URL):

- [ ] **Health check:** `https://your-app.onrender.com/`
  - Should return JSON with "DataDuel API Server Running!"

- [ ] **Strava OAuth:** `https://your-app.onrender.com/auth/strava`
  - Should redirect to Strava

- [ ] **From frontend:** Open Cloudflare site, check console
  - Should show: `API URL: https://your-app.onrender.com`

---

## 🎯 What Your Groupmate Needs:

Send them this message:

```
All code is ready on the 'render' branch! Here's what to do:

1. Create Web Service on Render.com
2. Connect to our GitHub repo
3. Select branch: "render" (important!)
4. Build command: pip install -r requirements.txt
5. Start command: cd DataDuel/backend && python app.py
6. Add environment variables from CREDENTIALS_SUMMARY.md

Full guide: RENDER_DEPLOYMENT.md

Let me know your Render URL when it's deployed so I can:
- Update Strava OAuth callback
- Add your URL to CORS if needed
```

---

## ⚠️ Common Issues to Avoid

### Issue 1: Wrong Branch
- ❌ Don't select `main` branch
- ✅ Select `render` branch

### Issue 2: Missing Environment Variables
- ❌ Missing `REDIRECT_URI` → OAuth will fail
- ✅ Add all 6 environment variables

### Issue 3: Wrong Start Command
- ❌ `python app.py` (wrong directory)
- ✅ `cd DataDuel/backend && python app.py`

### Issue 4: Strava Callback Not Updated
- After deployment, MUST update Strava settings
- Go to strava.com/settings/api
- Change callback domain to your Render URL

---

## 🚀 Timeline

**Render deployment:** 5-10 minutes  
**Strava OAuth update:** 2 minutes  
**Testing:** 5 minutes  
**Total:** ~15-20 minutes to fully working backend

---

## 📊 What Happens Next

```
1. Groupmate creates Render service ✅
   ↓
2. Render clones 'render' branch
   ↓
3. Runs: pip install -r requirements.txt
   ↓
4. Starts: cd DataDuel/backend && python app.py
   ↓
5. Backend is LIVE! 🎉
   ↓
6. Update Strava OAuth callback
   ↓
7. Test from Cloudflare frontend
   ↓
8. FULLY WORKING! 🚀
```

---

**Everything is ready!** Once your groupmate deploys and shares the URL, you'll just need to update the Strava OAuth settings and you're done! 🎉

