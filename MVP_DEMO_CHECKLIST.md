# DataDuel MVP Demo Checklist

**Demo Date:** [Your Demo Date]  
**Presentation Length:** 10 minutes

---

## Pre-Demo Setup (Do This BEFORE Demo)

### Environment Preparation
- [ ] **Backend dependencies installed**
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Environment configured**
  - [ ] `.env` file exists in `DataDuel/backend/`
  - [ ] Contains valid Strava API credentials
  - [ ] Callback domain set to `localhost` on Strava

- [ ] **Test authentication**
  - [ ] Start backend: `python DataDuel/backend/app.py`
  - [ ] Connect to Strava successfully
  - [ ] `tokens.json` file created

- [ ] **Sync test data**
  - [ ] Click "Sync Activities" button
  - [ ] Verify data in `backend/data/` folder
  - [ ] Check: `users.json`, `activities.json`, `scores.json` exist

- [ ] **Test all pages**
  - [ ] Home page loads
  - [ ] Profile shows real data
  - [ ] Leaderboard displays rankings
  - [ ] Routes page shows available routes

### Backup Preparation
- [ ] **Take screenshots** of working features
  - [ ] Home page with auth status
  - [ ] Profile with your data
  - [ ] Leaderboard with rankings
  - [ ] Routes page
  - [ ] Successful sync alert

- [ ] **Export data files** (backup)
  - [ ] Copy `backend/data/` folder
  - [ ] Copy `tokens.json`

- [ ] **Prepare presentation slides**
  - [ ] Problem statement
  - [ ] Solution overview
  - [ ] Live demo slides
  - [ ] Technical architecture
  - [ ] Future roadmap

---

## Demo Day - 30 Minutes Before

### Technical Checks
- [ ] **Computer fully charged** or plugged in
- [ ] **Internet connection** stable
- [ ] **Backend server running**
  ```bash
  cd DataDuel/backend
  python app.py
  ```
- [ ] **Browser ready** with tabs:
  - [ ] `file:///path/to/DataDuel/frontend/index.html`
  - [ ] Backup: screenshots folder
- [ ] **Terminal visible** (for showing backend/data files if needed)
- [ ] **Close unnecessary applications**
- [ ] **Notifications silenced**

### Quick Functionality Test
- [ ] Open home page - auth status shows "[Connected]"
- [ ] Profile page loads with data
- [ ] Leaderboard shows rankings
- [ ] Routes page displays routes

---

## 10-Minute Demo Script

### [1-2 minutes] Introduction & Problem
**SAY:**
> "Traditional running apps reward natural ability. Fast runners always win, which discourages beginners and makes competition unfair. DataDuel solves this with improvement-based scoring that rewards consistency and personal growth."

**SHOW:** Slide with problem statement

---

### [5-6 minutes] Live Demo

#### Part 1: Authentication & Home (1 min)
**DO:**
1. Open home page
2. Point out "[Connected] Connected to Strava" status
3. Show user ID displayed

**SAY:**
> "Our app integrates with Strava using OAuth 2.0. Once authenticated, users can sync their running data with one click."

#### Part 2: Data Sync (1 min)
**DO:**
1. Click "Sync Activities" button
2. Show alert with results:
   - Workouts count
   - Distance
   - Score

**SAY:**
> "The sync process fetches activities from Strava, calculates personal baselines, and generates an improvement-based score."

#### Part 3: Behind the Scenes - Optional (30 seconds)
**DO:**
1. Open `backend/data/` folder in file explorer
2. Briefly show JSON files with data

**SAY:**
> "Data is currently stored in JSON files for the MVP. We'll migrate to PostgreSQL for production."

#### Part 4: Profile (1 min)
**DO:**
1. Navigate to Profile page
2. Point out:
   - Real name from Strava
   - Location
   - Stats (runs, distance, pace)
   - Score

**SAY:**
> "The profile displays real data synced from Strava, including our calculated improvement score."

#### Part 5: Leaderboard (1.5 min)
**DO:**
1. Navigate to Leaderboard
2. Point out:
   - Rankings sorted by score
   - Your row highlighted
   - Improvement percentages
   - Number of runs

**SAY:**
> "Here's the key differentiator: the leaderboard ranks users by improvement score, not raw speed. A beginner who improves 10% can outscore an advanced runner who plateaus. This creates fair competition across all fitness levels."

#### Part 6: Routes (1 min)
**DO:**
1. Navigate to Routes page
2. Show route filters
3. Click "Search" with filters
4. Show route results with details

**SAY:**
> "Users can discover pre-defined running routes filtered by distance, difficulty, and surface type. This helps runners plan their workouts."

---

### [2-3 minutes] Technical Highlights

**SHOW:** Architecture slide or talk through it

**SAY:**
> "Technically, we have:"
> - **Backend:** Flask API with Strava OAuth integration
> - **Frontend:** Vanilla JavaScript with dynamic data rendering
> - **Scoring Algorithm:** Rewards improvement over personal baselines
> - **Data:** Person, Score, Badge, and Challenge classes fully integrated
> - **Storage:** JSON for MVP, database migration planned

**KEY POINTS:**
- Strava API integration working
- Real-time data sync
- Improvement-based scoring algorithm
- Multi-page dynamic frontend
- All core features functional

---

### [1 minute] Future Plans & Q&A

**SAY:**
> "Next steps include:"
> - Database migration for multi-user support
> - Friends and custom leagues
> - Advanced route generation with LLM
> - Mobile app development

**THEN:** "Happy to answer questions!"

---

## Emergency Backup Plan

### If Live Demo Fails:

#### Option 1: Use Screenshots
- [ ] Open screenshots folder
- [ ] Walk through each feature using screenshots
- [ ] Explain what each screenshot shows

#### Option 2: Show Code
- [ ] Open `backend/app.py`
- [ ] Show API endpoints (sync, profile, leaderboard, routes)
- [ ] Open `strava_parser.py`
- [ ] Show scoring algorithm in `Score.py`

#### Option 3: Explain Architecture
- [ ] Draw flow diagram on board/screen
- [ ] Explain: Strava → Backend → Parser → Scoring → Frontend
- [ ] Show data structures in Person.py

---

## Common Demo Issues & Solutions

### Issue: Backend not starting
**Solution:** Show error message, explain dependencies needed, move to screenshots

### Issue: Auth fails during demo
**Solution:** You're already authenticated - show existing data instead

### Issue: Sync button doesn't work
**Solution:** Data is already synced - show profile/leaderboard with existing data

### Issue: Pages don't load
**Solution:** Use screenshots, explain what should happen

### Issue: Questions you can't answer
**Solution:** "Great question! That's part of our future roadmap. Let me take your email and follow up."

---

## Key Messages to Emphasize

### What Makes DataDuel Different
1. **Fair Competition** - Improvement-based, not ability-based
2. **Inclusive** - Beginners can compete with advanced runners
3. **Motivating** - Progress is rewarded, not just performance
4. **Integrated** - Real Strava data, not mock data
5. **Functional** - Complete MVP with all core features working

### What's Working Now
- Strava OAuth authentication
- Activity data sync
- Improvement-based scoring
- Dynamic leaderboard
- Real-time profile updates
- Route discovery system

### Be Honest About
- Single-user limitation (one token at a time)
- JSON storage (not database yet)
- Basic route system (no LLM yet)
- Friends feature (sample data only)

---

## Post-Demo

### If Demo Goes Well
- [ ] Celebrate!
- [ ] Note questions asked
- [ ] Document feedback
- [ ] Plan next sprint

### If Demo Has Issues
- [ ] Don't panic - explain what should work
- [ ] Use screenshots/slides as backup
- [ ] Focus on architecture and approach
- [ ] Emphasize learning and problem-solving

---

## Quick Reference

### API Endpoints
- `/` - Server status
- `/auth/strava` - OAuth redirect
- `/api/sync` - Sync activities
- `/api/profile` - User profile
- `/api/leaderboard` - Rankings
- `/api/routes/all` - Get routes
- `/api/routes/search` - Search routes

### Key Files
- `backend/app.py` - Main API
- `backend/strava_parser.py` - Activity parser
- `backend/route_generator.py` - Route system
- `frontend/index.html` - Home page
- `frontend/api.js` - API client

### Scoring Formula
```
Scale = comparison to baseline (4 metrics)
Base = scale + badges + challenges + streak
Improvement Bonus = (improvement%) * 5
Total Score = base + improvement_bonus
```

---

## Final Checks (5 Minutes Before Demo)

- [ ] Backend running on localhost:5000
- [ ] Browser tabs open and working
- [ ] Screenshots accessible
- [ ] Notes/talking points handy
- [ ] Water nearby
- [ ] Deep breath - you've got this!

---

**Remember:** You built a fully functional MVP in one session. All core features work. You have comprehensive documentation. Even if something goes wrong during the demo, you can explain what you built and show alternative proof (screenshots, code, architecture). You're prepared!

**Good luck! Show them what you built!**

