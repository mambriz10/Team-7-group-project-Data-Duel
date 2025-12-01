# 🚀 DataDuel - Render.com Deployment Guide

This guide walks you through deploying your Flask backend to Render.com.

---

## 📋 Prerequisites

- [x] Code pushed to `render` branch
- [x] Strava API credentials (from https://www.strava.com/settings/api)
- [x] Supabase project URL and key (from Supabase dashboard)
- [ ] Render.com account (sign up with GitHub)

---

## 🎯 Step-by-Step Deployment

### Step 1: Create Render Account

1. Go to https://render.com
2. Click **"Get Started"**
3. **Sign up with GitHub** (easiest for auto-deploys)
4. Authorize Render to access your repositories

### Step 2: Create New Web Service

1. Click **"New +"** in top right
2. Select **"Web Service"**
3. Click **"Connect a repository"** (or "Build and deploy from a Git repository")
4. Find and select: `Team-7-group-project-Data-Duel`
5. Click **"Connect"**

### Step 3: Configure Service Settings

**Basic Settings:**
- **Name:** `dataduel-backend` (or your preferred name)
- **Region:** Choose closest to your users (e.g., Oregon for US West)
- **Branch:** `render` ← **IMPORTANT: Select your render branch!**
- **Runtime:** Python 3

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `cd DataDuel/backend && python app.py`

**Instance Type:**
- Select **"Free"** (for MVP/demo)
- Or **"Starter ($7/month)"** if you want no cold starts

### Step 4: Add Environment Variables

Click **"Advanced"** → Scroll to **"Environment Variables"** → Click **"Add Environment Variable"**

Add these **one by one**:

| Key | Value | Where to Get It |
|-----|-------|-----------------|
| `PORT` | `10000` | (Render default) |
| `STRAVA_CLIENT_ID` | Your Strava Client ID | https://www.strava.com/settings/api |
| `STRAVA_CLIENT_SECRET` | Your Strava Client Secret | https://www.strava.com/settings/api |
| `REDIRECT_URI` | `https://dataduel-backend.onrender.com/auth/strava/callback` | (Use your Render URL - see note below) |
| `SUPABASE_URL` | Your Supabase URL | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | Your Supabase anon key | Supabase Dashboard → Settings → API |
| `FRONTEND_URL` | Your Cloudflare Pages URL | (Optional - add after frontend is deployed) |

**Note:** Your Render URL will be `https://[your-app-name].onrender.com`. If you named it `dataduel-backend`, use `https://dataduel-backend.onrender.com`.

### Step 5: Deploy!

1. Click **"Create Web Service"**
2. Render will start deploying (watch the logs)
3. Wait 5-10 minutes for first deployment
4. Look for: `✅ Build successful` and `✅ Deploy successful`

### Step 6: Get Your Backend URL

Once deployed, you'll see:
- Your app URL: `https://dataduel-backend.onrender.com` (or whatever you named it)
- Click the URL to test - should see: `{"message": "DataDuel API Server Running!", ...}`

**Copy this URL** - you'll need it for the next steps!

---

## 🔧 Post-Deployment Configuration

### Step 1: Update Strava OAuth Settings

1. Go to https://www.strava.com/settings/api
2. Find **"Authorization Callback Domain"**
3. Change from `localhost` to: `dataduel-backend.onrender.com` (your Render domain - NO https://)
4. Click **"Update"**

### Step 2: Update Frontend Config (if needed)

If your actual Render URL is different from `https://dataduel-backend.onrender.com`:

1. Edit `DataDuel/frontend/config.js`
2. Update line 14 with your actual Render URL:
   ```javascript
   apiUrl: 'https://YOUR-ACTUAL-URL.onrender.com',
   ```
3. Commit and push to trigger Cloudflare redeploy

### Step 3: Update Cloudflare Pages URL in Render

If you know your Cloudflare Pages URL:

1. Go to Render Dashboard → Your service
2. **Environment** tab
3. Add/Update `FRONTEND_URL` with your Cloudflare URL
4. Click **"Save Changes"** (triggers redeploy)

---

## ✅ Testing Your Deployment

### Test 1: Backend Health Check

Visit: `https://your-app.onrender.com/`

**Expected response:**
```json
{
  "message": "DataDuel API Server Running!",
  "version": "1.0.0",
  "endpoints": { ... }
}
```

### Test 2: Strava OAuth

Visit: `https://your-app.onrender.com/auth/strava`

**Expected:** Redirects to Strava authorization page

### Test 3: From Frontend

1. Open your Cloudflare Pages site
2. Open browser console (F12)
3. Look for: `[DataDuel Config] API URL: https://your-app.onrender.com`
4. Click "Connect Strava"
5. Should complete OAuth flow successfully

---

## 🐛 Troubleshooting

### Issue: "Application failed to respond"

**Cause:** App didn't start properly

**Solution:**
1. Check Render logs (Dashboard → Logs tab)
2. Look for Python errors
3. Verify all environment variables are set
4. Check `requirements.txt` has all dependencies

### Issue: CORS errors in browser

**Cause:** Cloudflare URL not in CORS origins

**Solution:**
1. Add `FRONTEND_URL` environment variable in Render
2. Or manually update `app.py` CORS list
3. Redeploy

### Issue: Strava OAuth fails

**Cause:** Callback domain mismatch

**Solution:**
1. Verify Strava settings have your Render domain (no https://)
2. Verify `REDIRECT_URI` environment variable is correct
3. Must be exact: `https://your-app.onrender.com/auth/strava/callback`

### Issue: "Cold start" - slow first load

**This is normal for free tier:**
- Render spins down after 15 min of inactivity
- First request wakes it up (30-60 seconds)
- Subsequent requests are instant

**Solutions:**
- Accept it (good enough for demo)
- Set up UptimeRobot to ping every 10 min (keeps it awake)
- Upgrade to Starter plan ($7/month - no cold starts)

### Issue: Deployment fails

**Check:**
1. Branch is set to `render`
2. `requirements.txt` exists in root
3. Build command is correct
4. Start command is correct
5. Python version compatible (Render uses Python 3.11 by default)

---

## 📊 Understanding the Free Tier

**Limits:**
- 750 hours/month (plenty for demo - about 31 days)
- 512MB RAM
- Shared CPU
- Spins down after 15 min inactivity
- 100GB bandwidth/month

**Good for:**
- ✅ MVP/Demo
- ✅ School projects
- ✅ Low-traffic apps

**Upgrade if:**
- ❌ Need 24/7 uptime (no cold starts)
- ❌ High traffic (>1000 users/day)
- ❌ Need more RAM

---

## 🔄 Auto-Deployments

**Render automatically redeploys when you:**
1. Push to the `render` branch
2. Change environment variables
3. Manually trigger deploy in dashboard

**Deployment time:** 2-5 minutes

---

## 📝 Environment Variables Reference

```bash
# Required
PORT=10000
STRAVA_CLIENT_ID=your_id
STRAVA_CLIENT_SECRET=your_secret
REDIRECT_URI=https://your-app.onrender.com/auth/strava/callback
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_key

# Optional but recommended
FRONTEND_URL=https://your-site.pages.dev
```

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Backend URL loads and shows API info
- [ ] `/auth/strava` redirects to Strava
- [ ] Strava OAuth completes successfully
- [ ] Frontend detects production environment
- [ ] API calls work from frontend
- [ ] No CORS errors in browser console
- [ ] Friends system works
- [ ] Activity sync works

---

## 💡 Pro Tips

1. **Watch the logs:** Render Dashboard → Logs tab shows real-time output
2. **Use environment variables:** Never hardcode secrets in code
3. **Test locally first:** Make sure it works on `localhost` before deploying
4. **Keep dependencies updated:** Render uses latest Python 3
5. **Monitor usage:** Check metrics to ensure you're within free tier limits

---

## 🔗 Useful Links

- **Render Dashboard:** https://dashboard.render.com
- **Render Docs:** https://render.com/docs
- **Strava API Settings:** https://www.strava.com/settings/api
- **Supabase Dashboard:** https://app.supabase.com

---

## 🆘 Need Help?

**Render logs showing errors?**
- Copy the error message
- Check if it's an environment variable issue
- Verify all dependencies are in `requirements.txt`

**Still stuck?**
- Check `DEPLOYMENT.md` for general deployment help
- Check `TESTING_AND_DEBUGGING.md` for common issues

---

**Good luck! Your backend should be live in ~10 minutes!** 🚀

