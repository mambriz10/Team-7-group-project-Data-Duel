# 🚀 Cloudflare Pages Setup - Quick Reference Card

## For the Person Deploying (Copy & Paste This)

### Option 1: Fix Current Deployment (FASTEST) ⚡

If you already connected GitHub to Cloudflare and it failed:

1. Open: https://dash.cloudflare.com
2. Click: **Workers & Pages** → Your project name
3. Click: **Settings** → **Builds & deployments**
4. Update settings:
   ```
   Framework preset: None
   Build command: (leave blank)
   Build output directory: DataDuel/frontend
   Root directory: (leave blank)
   ```
5. Click **Save**
6. Go to **Deployments** tab → Click **Retry deployment**

✅ Done! Should deploy in 1-2 minutes.

---

### Option 2: New Setup from Scratch

If you haven't connected to Cloudflare yet:

1. Go to: https://dash.cloudflare.com
2. Click: **Workers & Pages** → **Create application** → **Pages**
3. Click: **Connect to Git**
4. Select: `Team-7-group-project-Data-Duel`
5. Configure:
   ```
   Project name: dataduel
   Production branch: main
   Framework preset: None
   Build command: (leave blank)
   Build output directory: DataDuel/frontend
   Root directory: (leave blank)
   ```
6. Click: **Save and Deploy**

✅ Your site will be at: `https://dataduel-xxx.pages.dev`

---

## 📱 What to Share After Deployment

Once it works, share this info:

```
✅ Frontend deployed!
🌐 URL: [paste your Cloudflare Pages URL]

The site should load, but features needing the backend 
(like Strava sync) won't work until we deploy that too.
```

---

## ❓ Troubleshooting

**"Repository not found"**
→ Make sure you authorized Cloudflare to access the org/repo

**"Build failed: error occurred"**
→ Check that you set `DataDuel/frontend` exactly (case-sensitive)

**"No files to deploy"**
→ Make sure build command is BLANK (empty)

**"Still getting errors"**
→ Send a screenshot of the error log from Cloudflare dashboard

---

## 🎯 After Successful Deploy

Next steps:
1. ✅ Frontend is live
2. ⏳ Need to deploy backend (separate step)
3. ⏳ Connect Strava OAuth
4. ⏳ Test full application

---

**Time needed:** 5 minutes  
**Cost:** $0 (Free tier)  
**Difficulty:** Easy 🟢

