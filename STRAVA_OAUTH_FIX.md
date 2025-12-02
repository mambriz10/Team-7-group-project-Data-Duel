# 🔧 Strava OAuth 400 Error - Fix Guide

## ❌ The Error You're Seeing

```
{"message":"Bad Request","errors":[{"resource":"Application","field":"redirect_uri","code":"invalid"}]}
```

**What this means:** Strava doesn't recognize your Render callback URL as authorized.

---

## ✅ The Fix (2 Steps)

### Step 1: Add Redirect URI to Strava App Settings

1. **Go to Strava API Settings:**
   - Visit: https://www.strava.com/settings/api
   - Log in with your Strava account

2. **Find Your App:**
   - Look for app with **Client ID: 131027**

3. **Add Authorization Callback Domain:**
   - In the **"Authorization Callback Domain"** field, enter:
     ```
     dataduel-backend.onrender.com
     ```
   - ⚠️ **IMPORTANT:** 
     - NO `https://`
     - NO `/auth/strava/callback`
     - Just the domain: `dataduel-backend.onrender.com`

4. **Click "Update"**

5. **Wait 1-2 minutes** for changes to propagate

---

### Step 2: Verify Render Environment Variables

Make sure your Render backend has these environment variables set:

```bash
REDIRECT_URI=https://dataduel-backend.onrender.com/auth/strava/callback
FRONTEND_URL=https://team-7-group-project-data-duel.pages.dev
```

**To check in Render:**
1. Go to your Render dashboard
2. Click on your web service
3. Go to "Environment" tab
4. Verify `REDIRECT_URI` is set correctly

**If it's missing or wrong:**
1. Click "Add Environment Variable"
2. Key: `REDIRECT_URI`
3. Value: `https://dataduel-backend.onrender.com/auth/strava/callback`
4. Click "Save Changes"
5. Render will automatically redeploy

---

## 🎯 How It Works

### The OAuth Flow:

1. **User clicks "Connect Strava"** on your frontend
   - Frontend: `https://team-7-group-project-data-duel.pages.dev/`
   - Redirects to: `https://dataduel-backend.onrender.com/auth/strava`

2. **Backend redirects to Strava:**
   - Backend sends: `redirect_uri=https://dataduel-backend.onrender.com/auth/strava/callback`
   - Strava checks: "Is this domain authorized?" ✅

3. **User authorizes on Strava:**
   - Strava redirects back to: `https://dataduel-backend.onrender.com/auth/strava/callback?code=...`

4. **Backend exchanges code for token:**
   - Backend gets access token from Strava
   - Backend redirects user to: `https://team-7-group-project-data-duel.pages.dev/index.html`

---

## 🔍 Troubleshooting

### Still Getting 400 Error?

**Check these:**

1. **Domain matches exactly?**
   - Strava setting: `dataduel-backend.onrender.com`
   - Render URL: `https://dataduel-backend.onrender.com`
   - ✅ Should match (minus https://)

2. **Render app name different?**
   - If your Render app is named something else (e.g., `dataduel-api`), use that domain instead
   - Update both:
     - Strava: `your-actual-app-name.onrender.com`
     - Render `REDIRECT_URI`: `https://your-actual-app-name.onrender.com/auth/strava/callback`

3. **Wait time:**
   - Strava changes can take 1-2 minutes to propagate
   - Try again after waiting

4. **Check Render logs:**
   - Go to Render dashboard → Your service → "Logs"
   - Look for any errors about `REDIRECT_URI`

---

## ✅ Success Indicators

After fixing, you should see:

1. **No more 400 error** when clicking "Connect Strava"
2. **Strava authorization page** appears
3. **After authorizing**, you're redirected back to your frontend
4. **Console shows:** `[Connected] Connected to Strava`

---

## 📝 Quick Checklist

- [ ] Added `dataduel-backend.onrender.com` to Strava app settings
- [ ] Set `REDIRECT_URI` in Render environment variables
- [ ] Set `FRONTEND_URL` in Render environment variables  
- [ ] Waited 1-2 minutes after Strava changes
- [ ] Tested "Connect Strava" button again

---

## 🚀 After This Fix

Once OAuth is working:
- Users can connect their Strava accounts
- Activities will sync automatically
- Leaderboards will populate
- Full app functionality unlocked! 🎉

