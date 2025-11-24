# DataDuel - Quick Reference Checklist
**Use this for daily standup or quick status checks**

---

## 📊 Current Status (as of Nov 24, 2025)

### ✅ COMPLETE
- [x] Strava OAuth integration
- [x] Person object with full metrics
- [x] Activity parsing and aggregation
- [x] Score calculation system
- [x] Badge system (3 badges, auto-awarded)
- [x] Challenge system (3 challenges, weekly)
- [x] Streak tracking
- [x] Supabase database integration
- [x] Profile page with real data
- [x] Leaderboard with rankings
- [x] Route discovery system
- [x] Data storage (JSON + Supabase)

### 🚧 IN PROGRESS / TODO
- [ ] Friends backend (MrChapitas)
- [ ] Live deployment (qatarjr)
- [ ] End-to-end testing (Everyone)
- [ ] Update documentation (Everyone)

---

## 👥 Individual Tasks

### MrChapitas
**Task:** Implement Friends Backend  
**Time:** 4-6 hours  
**Checklist:**
- [ ] Create `friends_storage.py`
- [ ] Add 6 friends endpoints to `app.py`
- [ ] Test with curl/Postman
- [ ] Verify `friends.json` creates correctly
- [ ] Test with 2 user accounts
- [ ] Push to GitHub
- [ ] Notify team when done

**Files to create/edit:**
- `DataDuel/backend/friends_storage.py` (new file)
- `DataDuel/backend/app.py` (add endpoints)
- `DataDuel/backend/data/friends.json` (auto-created)

### qatarjr
**Task:** Deploy Website to Production  
**Time:** 2-3 hours  
**Checklist:**
- [ ] Create Render.com account
- [ ] Deploy backend to Render
- [ ] Get backend URL: `https://dataduel-backend.onrender.com`
- [ ] Update Strava OAuth callback URL
- [ ] Create Vercel account
- [ ] Update all frontend files with backend URL
- [ ] Deploy frontend to Vercel
- [ ] Get frontend URL: `https://dataduel.vercel.app`
- [ ] Update CORS in backend
- [ ] Test full flow on live site
- [ ] Share URLs with team

**Files to edit:**
- `DataDuel/backend/app.py` (port and CORS)
- `DataDuel/frontend/index.html` (backend URL)
- `DataDuel/frontend/profile.html` (backend URL)
- `DataDuel/frontend/Strava.html` (backend URL)
- `DataDuel/frontend/api.js` (backend URL)
- `requirements.txt` (create if missing)
- `Procfile` (create)

### Everyone
**Task:** Testing & Documentation  
**Time:** 1-2 hours  
**Checklist:**
- [ ] Test deployed site
- [ ] Test friends feature
- [ ] Test on mobile
- [ ] Update README with live URLs
- [ ] Create demo accounts
- [ ] Document any bugs found
- [ ] Prepare for presentation/demo

---

## 🎯 Priority Order

1. **HIGHEST:** Friends backend (blocking social features)
2. **HIGH:** Deployment (needed for demo)
3. **MEDIUM:** Testing (quality assurance)
4. **LOW:** Polish & documentation

---

## ⚡ Quick Commands

### Start Backend (Local)
```bash
cd DataDuel/backend
python app.py
```

### Test Endpoint (curl)
```bash
# Test friends search
curl http://localhost:5000/api/friends/search?q=test

# Test send friend request (replace TOKEN and FRIEND_ID)
curl -X POST http://localhost:5000/api/friends/request \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"friend_id":"FRIEND_ID"}'
```

### Check Logs (Render)
```bash
# Visit Render dashboard → your service → Logs tab
```

### Redeploy (Vercel)
```bash
# Just push to GitHub - auto deploys
git add .
git commit -m "Update frontend URLs"
git push origin main
```

---

## 📝 Key Files Reference

### Backend Core
- `app.py` - Main Flask server (857 lines)
- `data_storage.py` - JSON storage (139 lines)
- `strava_parser.py` - Activity parser (358 lines)
- `Person.py` - User data model (152 lines)
- `Score.py` - Scoring algorithm (56 lines)

### Frontend Core
- `index.html` - Home page with sync
- `profile.html` - User profile display
- `social.html` - Friends/leagues UI
- `Strava.html` - Strava connection page
- `api.js` - API wrapper

### Data Files (Auto-Generated)
- `data/users.json` - User profiles
- `data/activities.json` - Strava activities
- `data/scores.json` - Calculated scores
- `data/friends.json` - Friend relationships (once implemented)
- `tokens.json` - OAuth tokens

---

## 🐛 Known Issues

1. **Profile shows "0 min/km"** - Normal if no activities synced yet
2. **League data in localStorage** - Not persistent across devices
3. **Friends are static** - Waiting for backend implementation
4. **Running on localhost** - Needs deployment

---

## 🔗 Important URLs

### Development (Local)
- Backend: http://localhost:5000
- Frontend: http://localhost:5500
- Strava API: https://www.strava.com/settings/api

### Production (Once Deployed)
- Backend: https://dataduel-backend.onrender.com (or your URL)
- Frontend: https://dataduel.vercel.app (or your URL)
- Supabase: https://gbvyveaifvqneyayloks.supabase.co

### External Services
- Strava Settings: https://www.strava.com/settings/api
- Render Dashboard: https://dashboard.render.com
- Vercel Dashboard: https://vercel.com/dashboard

---

## 💬 Team Communication

### When to Message
- ✅ When you start a task
- ✅ When you complete a task
- ✅ When you're blocked/need help
- ✅ When you find a bug
- ❌ Don't disappear for hours without updates!

### Message Templates

**Starting work:**
```
Working on [task name]. Should take [time]. Will update when done.
```

**Completed work:**
```
✅ [Task name] complete!
- [Key accomplishment 1]
- [Key accomplishment 2]
- Ready for [next step]
```

**Need help:**
```
Stuck on [specific issue]. [What I've tried]. Can someone help?
```

---

## 📞 Quick Help

### MrChapitas - Friends Backend
- Copy endpoint structure from existing endpoints in `app.py`
- Use `data_storage.py` as template for `friends_storage.py`
- Test each endpoint before moving to next
- Full code provided in NEXT_STEPS_ACTION_PLAN.md

### qatarjr - Deployment
- Render.com: https://render.com/docs/deploy-flask
- Vercel: https://vercel.com/docs
- Both have free tiers - no credit card needed
- Takes ~30 min per platform

---

## ✅ Daily Checklist

### Every Day
- [ ] Pull latest from GitHub
- [ ] Read team messages
- [ ] Update team on progress
- [ ] Test your changes
- [ ] Push code at end of day
- [ ] Update this checklist

---

## 🎉 Success Criteria

### Friends Backend Success
- [ ] Can search for users
- [ ] Can send friend request
- [ ] Can accept friend request
- [ ] Friends show in list
- [ ] Can remove friend
- [ ] No errors in console

### Deployment Success
- [ ] Site loads at public URL
- [ ] Can log in with Strava
- [ ] Activities sync
- [ ] Profile shows data
- [ ] Leaderboard works
- [ ] No CORS errors

---

## 🚀 After Everything Works

### Demo Preparation
- [ ] Create 3-4 test accounts
- [ ] Sync activities for each
- [ ] Add friends between accounts
- [ ] Create a test league
- [ ] Take screenshots
- [ ] Prepare talking points

### Presentation Points
1. Show Strava integration
2. Demonstrate activity sync
3. Explain improvement-based scoring
4. Show leaderboard
5. Demonstrate social features
6. Highlight technical achievements

---

## 📊 Progress Tracker

| Day | MrChapitas | qatarjr | Team Status |
|-----|------------|---------|-------------|
| Nov 24 | Starting friends backend | Planning deployment | Both working in parallel |
| Nov 25 | [Update here] | [Update here] | [Update here] |
| Nov 26 | [Update here] | [Update here] | [Update here] |

---

## 🎯 One Week Timeline

**Day 1-2:** Friends backend + Deployment  
**Day 3:** Testing & bug fixes  
**Day 4:** Documentation & polish  
**Day 5:** Demo preparation  
**Day 6-7:** Buffer for issues

---

**Last Updated:** November 24, 2025  
**Next Update:** After friends backend or deployment complete

