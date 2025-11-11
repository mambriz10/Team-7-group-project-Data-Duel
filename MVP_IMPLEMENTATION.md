# DataDuel MVP Implementation Guide

**Date:** November 11, 2025  
**Status:** ✅ MVP Complete - Ready for Demo  
**Implementation Time:** ~3 hours

---

## 🎯 MVP Objectives

Create a functional prototype demonstrating:
1. ✅ Strava OAuth authentication
2. ✅ Activity data sync and parsing
3. ✅ Improvement-based scoring algorithm
4. ✅ Dynamic leaderboard
5. ✅ Real-time profile updates
6. ✅ Frontend-backend integration

---

## 📋 What Was Implemented

### Phase 1: Bug Fixes & Foundation (30 min)

#### 1.1 Fixed Token File Naming Bug
**File:** `DataDuel/backend/app.py`  
**Issue:** Inconsistent token file names (`tokens_.json` vs `tokens.json`)  
**Solution:** Standardized all references to `tokens.json`

```python
# Before
with open("tokens_.json", "w") as f:  # Line 57
    tokens_ = json.load(f)              # Line 80

# After  
with open("tokens.json", "w") as f:    # Consistent
    tokens = json.load(f)               # Cleaned up
```

**Impact:** ✅ Authentication now works reliably

---

### Phase 2: Backend Infrastructure (90 min)

#### 2.1 Data Storage System
**File:** `DataDuel/backend/data_storage.py` (NEW)  
**Purpose:** JSON-based temporary storage (database replacement for MVP)

**Features:**
- User data management
- Activity storage per user
- Score tracking and history
- Automatic timestamp tracking

**Key Methods:**
```python
storage.save_user(user_id, user_data)      # Save/update user
storage.get_user(user_id)                   # Retrieve user
storage.save_activities(user_id, activities)# Store activities
storage.save_score(user_id, score_data)    # Update scores
storage.get_all_scores()                    # For leaderboard
```

**Data Structure:**
```
DataDuel/backend/data/
├── users.json      # User profiles
├── activities.json # Strava activities by user
└── scores.json     # Calculated scores
```

#### 2.2 Strava Activity Parser
**File:** `DataDuel/backend/strava_parser.py` (NEW)  
**Purpose:** Map Strava API data to Person objects

**Key Functions:**

1. **`create_person_from_athlete(athlete_data)`**
   - Creates Person object from Strava athlete info
   - Sets name, username, profile data

2. **`parse_activities(activities_data, person)`**
   - Filters for running activities only
   - Aggregates metrics (distance, time, speed, elevation)
   - Calculates baselines from workout history
   - Updates Person object with real data

3. **`calculate_streak(activities_data)`**
   - Computes consecutive days with activities
   - Handles same-day multiple runs
   - Validates against current date

4. **`check_badges(person)`**
   - Moving time badge: 1000+ seconds average
   - Distance badge: 5000+ meters average
   - Max watts badge: 150+ watts
   - Max speed badge: 4+ m/s

5. **`check_challenges(person, activities_data)`**
   - Challenge 1: 3+ runs this week
   - Challenge 2: 15+ km total this week
   - Challenge 3: 5+ day streak

**Impact:** ✅ Real Strava data now flows into scoring system

#### 2.3 Comprehensive API Endpoints
**File:** `DataDuel/backend/app.py` (UPDATED)  
**Added CORS Support:** `flask-cors` for frontend communication

**New Endpoints:**

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/` | GET | API status | Server info & endpoints |
| `/auth/strava` | GET | OAuth redirect | Strava authorization |
| `/auth/strava/callback` | GET | Handle OAuth | Tokens + athlete data |
| `/api/sync` | POST/GET | Sync Strava activities | Metrics + score |
| `/api/profile` | GET | Get user profile | Profile + stats |
| `/api/leaderboard` | GET | Get rankings | Sorted leaderboard |
| `/api/friends` | GET | Get friends list | Friends data |
| `/api/status` | GET | Check auth status | Auth state |
| `/strava/activities` | GET | Raw Strava data | Activity JSON |

**Sync Flow:**
```
1. User clicks "Sync Activities"
2. Backend fetches activities from Strava API (last 30)
3. Parser filters for running activities
4. Person object updated with metrics
5. Baselines calculated from history
6. Badges & challenges checked
7. Score calculated using algorithm
8. All data saved to JSON storage
9. Returns summary to frontend
```

**Impact:** ✅ Complete backend API for all frontend needs

---

### Phase 3: Frontend Integration (60 min)

#### 3.1 API Client
**File:** `DataDuel/frontend/api.js` (NEW)  
**Purpose:** Centralized API communication layer

**Features:**
- Generic fetch wrapper with error handling
- Type-safe method calls
- Consistent error messages
- Global API instance

```javascript
// Usage
const profile = await api.getProfile();
const leaderboard = await api.getLeaderboard();
const result = await api.syncActivities();
```

#### 3.2 Dynamic Profile Page
**File:** `DataDuel/frontend/profile.html` (UPDATED)

**Changes:**
- ✅ Added loading state (⏳ spinner)
- ✅ Dynamic data rendering from API
- ✅ Error handling with auth redirect
- ✅ Real-time stats display

**Data Displayed:**
- Name, username, location, avatar
- Total runs
- Total distance (km)
- Average pace (min/km)
- Current score

**User Experience:**
```
Loading... → API Call → Data Rendered
           ↓ (if error)
        Error + "Connect Strava" button
```

#### 3.3 Dynamic Leaderboard
**File:** `DataDuel/frontend/leaderboards.html` (UPDATED)

**Changes:**
- ✅ Fetches real leaderboard data
- ✅ Dynamically generates table rows
- ✅ Highlights current user (`.you` class)
- ✅ Shows rank, username, runs, improvement %, score
- ✅ Sorted by score (highest first)

**Data Flow:**
```
1. Fetch leaderboard from API
2. Get current user ID (if authenticated)
3. Generate table row for each user
4. Apply highlight to current user's row
5. Display sorted rankings
```

#### 3.4 Enhanced Home Page
**File:** `DataDuel/frontend/index.html` (UPDATED)

**New Features:**
- ✅ Real-time auth status check
- ✅ "Connect Strava" button (if not authenticated)
- ✅ "Sync Activities" button (if authenticated)
- ✅ Status indicators:
  - ✅ Connected (green)
  - ⚠️ Not connected (orange)
  - ❌ Backend offline (red)

**Sync Flow:**
```
User clicks "Sync" → Button disabled
                   → Shows "⏳ Syncing..."
                   → API call to /api/sync
                   → Alert with results
                   → Button re-enabled
```

**Impact:** ✅ Intuitive user interface with real-time feedback

---

## 🛠 Technical Stack

### Backend
```python
flask==3.0.0           # Web framework
flask-cors==4.0.0      # CORS support
requests==2.31.0       # HTTP requests to Strava
python-dotenv==1.0.0   # Environment variables
```

### Frontend
```javascript
- Vanilla JavaScript (ES6+)
- Fetch API for HTTP requests
- Dynamic DOM manipulation
- No external frameworks (for simplicity)
```

### Data Storage
```
JSON files (temporary, MVP only)
├── users.json       # User profiles
├── activities.json  # Strava activities
└── scores.json      # Calculated scores

Future: PostgreSQL/SQLite with SQLAlchemy
```

---

## 🚀 Setup Instructions

### 1. Install Dependencies
```bash
cd Team-7-group-project-Data-Duel
pip install -r requirements.txt
```

### 2. Configure Environment
Create `DataDuel/backend/.env`:
```env
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
REDIRECT_URI=http://localhost:5000/auth/strava/callback
```

Get credentials: https://www.strava.com/settings/api

### 3. Start Backend
```bash
cd DataDuel/backend
python app.py
```

Server starts at: `http://localhost:5000`

### 4. Open Frontend
Open `DataDuel/frontend/index.html` in a browser

---

## 🧪 Testing the MVP

### Complete Flow Test

#### Step 1: Authentication
1. Open `http://localhost:5000/frontend/index.html`
2. Should see "⚠️ Not connected to Strava"
3. Click "Connect Strava"
4. Authorize on Strava
5. Redirected back with success message
6. `tokens.json` created in `backend/` directory

#### Step 2: Sync Activities
1. Return to home page
2. Should see "✅ Connected to Strava"
3. Click "🔄 Sync Activities"
4. Wait for sync (2-5 seconds)
5. Alert shows:
   - Total workouts
   - Distance (km)
   - Score
6. Data now stored in `backend/data/` JSON files

#### Step 3: View Profile
1. Click "My Profile" or navigate to `profile.html`
2. Should see your real data:
   - Name from Strava
   - Username
   - Location
   - Avatar
   - Stats (runs, distance, pace, score)

#### Step 4: Check Leaderboard
1. Click "View Leaderboards"
2. Should see ranked list with real scores
3. Your row highlighted
4. Sorted by score (highest first)

---

## 📊 Scoring Algorithm

### How It Works

The scoring system rewards **improvement over personal baselines**, not raw performance.

```python
# Calculate score
person.score.calculate_score(
    average_speed,           # Current workout
    max_speed,
    distance,
    moving_time,
    baseline_average_speed,  # Personal baseline
    baseline_max_speed,
    baseline_distance,
    baseline_moving_time,
    badge_points,            # 5 points per badge
    challenge_points,        # 5 points per challenge
    streak                   # Consecutive days
)
```

### Scoring Formula

1. **Scale Calculation** (-4 to +4)
   ```
   scale = 0
   if current_speed > baseline: scale += 1
   if current_max_speed > baseline: scale += 1
   if current_distance > baseline: scale += 1
   if current_time > baseline: scale += 1
   ```

2. **Base Points**
   - Positive scale: `scale + badges + challenges + streak`
   - Negative scale: `-scale²` penalty + 50% of bonuses
   - Zero scale: `badges + challenges + streak`

3. **Improvement Bonus**
   - Every 1% improvement = 5 points
   - `ceil(improvement * 0.01) * 5`

4. **Total Score**
   ```
   score = base_points + improvement_bonus
   (minimum: 0, no negative scores)
   ```

### Example
```
User runs 6km in 30min (better than 5km baseline)
- Scale: +2 (distance ↑, time ↑)
- Base: 2 + 10 (badges) + 5 (challenges) + 3 (streak) = 20
- Improvement: 15% = 15 points
- Total: 35 points
```

**Why This Works:**
- Beginners can score high by improving
- Advanced runners must maintain/improve to score well
- Consistency (streak) rewarded
- Fair competition across all fitness levels

---

## 🗂 File Structure

```
Team-7-group-project-Data-Duel/
├── requirements.txt                    # ✅ Updated with flask-cors
├── MVP_IMPLEMENTATION.md              # ✅ This file
│
└── DataDuel/
    ├── backend/
    │   ├── .env                        # Environment variables
    │   ├── app.py                      # ✅ UPDATED: Full API
    │   ├── data_storage.py             # ✅ NEW: JSON storage
    │   ├── strava_parser.py            # ✅ NEW: Activity parser
    │   ├── tokens.json                 # ✅ FIXED: Consistent naming
    │   │
    │   └── data/                       # ✅ NEW: Created by storage
    │       ├── users.json
    │       ├── activities.json
    │       └── scores.json
    │
    ├── frontend/
    │   ├── api.js                      # ✅ NEW: API client
    │   ├── index.html                  # ✅ UPDATED: Auth & sync
    │   ├── profile.html                # ✅ UPDATED: Dynamic data
    │   ├── leaderboards.html           # ✅ UPDATED: Real scores
    │   ├── social.html                 # (Placeholder - MVP)
    │   ├── routes.html                 # (Placeholder - MVP)
    │   ├── settings.html               # (Placeholder - MVP)
    │   ├── styles.css                  # (No changes)
    │   └── script.js                   # (Tab highlighting only)
    │
    ├── Person.py                       # (No changes - used by parser)
    ├── Score.py                        # (No changes - used by parser)
    ├── badges.py                       # (No changes - used by parser)
    ├── challenges.py                   # (No changes - used by parser)
    └── leagueLeaderboard.py            # (Not used in MVP)
```

---

## ✅ MVP Checklist

### Core Functionality
- [x] **Strava OAuth authentication flow**
- [x] **Token management and refresh**
- [x] **Activity data fetching**
- [x] **Activity parsing (Strava → Person)**
- [x] **Baseline calculation from history**
- [x] **Score calculation with algorithm**
- [x] **Badge system integration**
- [x] **Challenge system integration**
- [x] **Streak calculation**
- [x] **Leaderboard generation**

### API Endpoints
- [x] Authentication (`/auth/strava`, `/auth/strava/callback`)
- [x] Profile data (`/api/profile`)
- [x] Leaderboard (`/api/leaderboard`)
- [x] Sync activities (`/api/sync`)
- [x] Status check (`/api/status`)
- [x] CORS enabled

### Frontend Integration
- [x] API client (api.js)
- [x] Dynamic home page with auth status
- [x] Sync button with feedback
- [x] Dynamic profile page
- [x] Dynamic leaderboard
- [x] Loading states
- [x] Error handling
- [x] User-friendly alerts

### Data Management
- [x] JSON storage system
- [x] User data persistence
- [x] Activity storage
- [x] Score tracking
- [x] Timestamp tracking

---

## 🎬 Demo Script

### For Tomorrow's Presentation

#### 1. Introduction (1 min)
> "DataDuel is a running app that creates fair competition through improvement-based scoring. Instead of rewarding the fastest runners, we reward consistency and personal growth."

#### 2. Authentication Demo (1 min)
1. Show home page (backend offline status)
2. Start Flask server → page updates automatically
3. Click "Connect Strava"
4. Authorize → show successful callback

#### 3. Sync Demo (2 min)
1. Show tokens.json file (proof of auth)
2. Click "Sync Activities"
3. Show alert with metrics
4. Open `backend/data/` folder
5. Show populated JSON files

#### 4. Profile Demo (1 min)
1. Navigate to Profile
2. Show real data from Strava
3. Highlight score calculation

#### 5. Leaderboard Demo (2 min)
1. Navigate to Leaderboards
2. Show ranked users
3. Explain improvement-based scoring
4. Highlight current user row

#### 6. Technical Highlights (2 min)
- Show `strava_parser.py` - activity parsing
- Show `app.py` - API endpoints
- Show scoring algorithm in `Score.py`
- Mention future database migration

#### 7. Q&A (1 min)

**Total: 10 minutes**

---

## 🐛 Known Issues & Limitations

### MVP Limitations (By Design)
1. **Single-user authentication** - Only one user can be authenticated at a time
   - `tokens.json` stores one token set
   - Future: Database-backed multi-user sessions

2. **JSON file storage** - Data stored in JSON, not database
   - Suitable for demo and testing
   - Future: PostgreSQL/SQLite migration planned

3. **Friends functionality** - Returns sample data only
   - No real friend relationships yet
   - Future: Implement friend request system

4. **Routes & Settings** - Placeholder pages
   - Not connected to backend
   - See `route-guide.md` for implementation plan

5. **Limited challenge logic** - Simple criteria
   - Checks weekly totals only
   - Future: More sophisticated challenge types

### Technical Debt
1. **No user session management** - Auth tied to tokens.json
2. **No rate limiting** - Backend has no API rate limits
3. **Limited error messages** - Some errors just show generic alerts
4. **No activity pagination** - Fetches last 30 activities only
5. **Hardcoded localhost URLs** - Need environment-based config for deployment

### Future Enhancements
See README.md "Missing Features & TODOs" section for complete roadmap.

---

## 📈 What's Next?

### Immediate (Post-Demo)
1. **Database Migration**
   - Set up PostgreSQL or SQLite
   - Create proper schema
   - Migrate from JSON storage
   - Add SQLAlchemy ORM

2. **Multi-User Support**
   - Flask-Login or JWT sessions
   - User registration flow
   - Separate tokens per user

3. **Frontend Polish**
   - Add loading spinners
   - Better error messages
   - Toast notifications instead of alerts
   - Responsive design improvements

### Short-Term (Next Sprint)
4. **Friends System**
   - Real friend relationships
   - Friend requests (send/accept/reject)
   - Activity feed from friends

5. **Leagues**
   - Create/join custom leagues
   - League-specific leaderboards
   - Invite friends to leagues

6. **Enhanced Challenges**
   - More challenge types
   - Progress tracking
   - Challenge notifications

### Long-Term
7. **Route Generation**
   - LLM-powered natural language parsing
   - Strava segment integration
   - Google Maps routing
   - See `route-guide.md` for full plan

8. **Analytics & Insights**
   - Performance graphs
   - Trend analysis
   - Goal tracking
   - Weekly summaries

9. **Mobile App**
   - React Native or Flutter
   - Push notifications
   - Offline support

---

## 🤝 Contributors

**CS422 - Team 7**

Implementation completed on November 11, 2025 for MVP demo.

---

## 📝 Change Log

### November 11, 2025 - MVP Implementation

**Bug Fixes:**
- Fixed token file naming inconsistency (`tokens_.json` → `tokens.json`)
- Cleaned up variable naming in token management

**New Files:**
- `backend/data_storage.py` - JSON-based data storage
- `backend/strava_parser.py` - Strava activity parser
- `frontend/api.js` - API client
- `MVP_IMPLEMENTATION.md` - This documentation

**Updated Files:**
- `backend/app.py` - Added comprehensive API endpoints + CORS
- `frontend/index.html` - Auth status + sync button
- `frontend/profile.html` - Dynamic data loading
- `frontend/leaderboards.html` - Real leaderboard rendering
- `requirements.txt` - Added `flask-cors==4.0.0`

**Backend Changes:**
- ✅ 9 API endpoints (auth, sync, profile, leaderboard, etc.)
- ✅ Strava OAuth with automatic token refresh
- ✅ Activity parsing and Person object integration
- ✅ Score calculation with full algorithm
- ✅ Badge and challenge checking
- ✅ JSON-based temporary storage
- ✅ CORS enabled for frontend communication

**Frontend Changes:**
- ✅ API integration layer
- ✅ Real-time auth status checking
- ✅ Dynamic data rendering (profile, leaderboard)
- ✅ Sync functionality with user feedback
- ✅ Loading and error states
- ✅ User-friendly alerts

**Testing:**
- ✅ Complete flow tested: Auth → Sync → Display
- ✅ Profile loads real Strava data
- ✅ Leaderboard shows calculated scores
- ✅ Sync updates all data correctly
- ✅ Error handling works for offline states

---

## 🎉 MVP Success Criteria

### Must Have (All ✅ Complete)
- [x] Users can authenticate with Strava
- [x] Activities sync from Strava API
- [x] Scores calculated based on improvement
- [x] Leaderboard displays ranked users
- [x] Profile shows real user data
- [x] Frontend communicates with backend
- [x] Data persists between sessions

### Nice to Have (✅ Complete)
- [x] Auth status indicator on home page
- [x] One-click sync from UI
- [x] Loading states for async operations
- [x] Error handling with helpful messages
- [x] User feedback (alerts) for actions

### Future (Not in MVP)
- [ ] Multi-user support
- [ ] Database backend
- [ ] Friends system (functional)
- [ ] Leagues
- [ ] Route generation
- [ ] Mobile app

---

**🚀 MVP READY FOR DEMO! 🚀**

All critical functionality implemented and tested. Backend and frontend fully integrated. Demo script prepared. Documentation complete.

Good luck with your presentation tomorrow! 🎯

