# DataDuel 🏃‍♂️

**Fair fitness competition through improvement, not performance.**

DataDuel is a web application that integrates with Strava to create an equitable running competition platform. Instead of rewarding raw athletic ability, DataDuel scores users based on improvement relative to their personal baselines, consistency, and challenge completion—ensuring that anyone can compete regardless of fitness level.

---

## 🎯 Project Vision

**The Problem:** Traditional fitness competitions favor naturally athletic individuals, leaving casual runners feeling demotivated and excluded.

**Our Solution:** An improvement-based scoring system that rewards:
- **Personal Growth** - Progress relative to your own baselines
- **Consistency** - Regular activity and maintaining streaks
- **Challenges** - Meeting weekly goals and earning badges

This creates fair competition where a beginner improving their 5K time by 30 seconds earns the same recognition as an elite runner improving by 10 seconds.

---

## 📋 Current Status: **Production-Ready & Fully Deployed**

**Deployment Status:**
- ✅ **Frontend:** Deployed on Cloudflare Pages
- ✅ **Backend:** Deployed on Render.com
- ✅ **Database:** Supabase PostgreSQL (fully migrated)
- ✅ **Storage:** 100% Supabase (no JSON dependencies)

### ✅ Fully Implemented Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Strava OAuth** | ✅ Working | Full OAuth 2.0 flow with automatic token refresh |
| **Activity Sync** | ✅ Working | Fetches, parses, and stores running data from Strava |
| **Scoring System** | ✅ Working | Improvement-based algorithm with badges, challenges, streaks |
| **Profile Page** | ✅ Working | Dynamic user profiles with stats and warnings |
| **Leaderboard** | ✅ Working | Real-time rankings sorted by improvement score |
| **Route System** | ✅ Working | 5 pre-defined routes with search/filter capabilities |
| **Badge System** | ✅ Working | Automatic badge awarding (moving time, distance, speed) |
| **Challenge System** | ✅ Working | Weekly challenges (3+ runs, 15km+, 5-day streak) |
| **Streak Tracking** | ✅ Working | Consecutive day calculation with proper validation |
| **Data Storage** | ✅ Working | Supabase PostgreSQL (production-ready, persistent) |

### 🚧 Planned Enhancements
- Social features (custom leagues, groups)
- Mobile optimization & PWA
- Advanced route generation with LLM
- Notification system
- Real-time updates (WebSockets)

---

## 🏗️ System Architecture

### Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER JOURNEY                             │
└─────────────────────────────────────────────────────────────────┘

1. AUTHENTICATION
   ┌─────────────┐    OAuth Redirect    ┌─────────────┐
   │   Browser   │ ──────────────────>  │   Strava    │
   │   (User)    │ <──────────────────  │  OAuth API  │
   └─────────────┘    Authorization     └─────────────┘
         │                                      │
         │ Authorization Code                  │
         ↓                                      │
   ┌─────────────┐                             │
   │   Backend   │ ←────Token Exchange─────────┘
   │  /callback  │
   └─────────────┘
         │
         │ Stores: Tokens + User Profile in Supabase
         ↓
   ✅ User Authenticated


2. ACTIVITY SYNC
   ┌─────────────┐    POST /api/sync    ┌─────────────┐
   │  Frontend   │ ──────────────────>  │   Backend   │
   │ (Sync Btn)  │                       │   Server    │
   └─────────────┘                       └─────────────┘
                                               │
                                               │ GET activities
                                               ↓
                                         ┌─────────────┐
                                         │   Strava    │
                                         │ Activity API│
                                         └─────────────┘
                                               │
                                               ↓ Raw JSON
                                         ┌─────────────┐
                                         │ StravaParser│
                                         │  • Filter   │
                                         │  • Parse    │
                                         │  • Calc     │
                                         └─────────────┘
                                               │
        ┌──────────────────┬───────────────────┼──────────────────┐
        ↓                  ↓                   ↓                  ↓
  [Person Object]    [Badge Check]      [Challenge Check]   [Streak Calc]
  • Metrics          • 3 types          • 3 weekly         • Consecutive
  • Baselines        • Auto-award       • Auto-check       • days
        │                  │                   │                  │
        └──────────────────┴───────────────────┴──────────────────┘
                                   │
                                   ↓
                           ┌─────────────┐
                           │Score System │
                           │  calculate  │
                           └─────────────┘
                                   │
        ┌──────────────────┬───────┴──────┬──────────────────┐
        ↓                  ↓               ↓                  ↓
  Supabase DB        Supabase DB      Supabase DB      Frontend Display
  (activities)       (user profiles)  (scores)         (success msg)


3. PROFILE DISPLAY
   ┌─────────────┐   GET /api/profile   ┌─────────────┐
   │ profile.html│ ──────────────────>  │   Backend   │
   │  (Page Load)│                       │   Server    │
   └─────────────┘                       └─────────────┘
         ↑                                      │
         │                              ┌───────┴───────┐
         │                              │ Load from:    │
         │                              │ • Supabase    │
         │                              │   user_strava │
         │                              │   table       │
         │                              └───────┬───────┘
         │                                      │
         │ JSON Response                        │ Calculate
         │ {name, stats, score}                 │ • Pace
         │                                      │ • Format
         └──────────────────────────────────────┘
```

---

## 🔢 Scoring Algorithm Explained

### Core Philosophy
**Score = Improvement × Consistency + Bonuses**

### Calculation Steps

```python
# 1. Compare current metrics to personal baselines
scale = 0
scale += 1 if average_speed >= baseline_average_speed else -1
scale += 1 if max_speed >= baseline_max_speed else -1
scale += 1 if distance >= baseline_distance else -1
scale += 1 if moving_time >= baseline_moving_time else -1

# 2. Apply scaling logic
if scale > 0:  # IMPROVING
    score += (scale + badge_points + challenge_points + streak)
    improvement_bonus = (improvement * 0.01) * 5  # 1% = 5 points
    score += improvement_bonus
    
elif scale < 0:  # DECLINING
    score -= (scale * scale)  # Gentle penalty
    score += (badge_points + challenge_points + streak) * 0.5  # Half credit
    
else:  # MAINTAINING
    score += (badge_points + challenge_points + streak)
    improvement_bonus = (improvement * 0.01) * 5 * 0.5  # Half bonus
    score += improvement_bonus

# 3. Ensure non-negative
score = max(0, score)
```

### Example Scenarios

| Runner | Baseline Pace | Current Pace | Scale | Badges | Streak | Score |
|--------|---------------|--------------|-------|--------|--------|-------|
| **Beginner** | 7:00/km | 6:30/km | +3 | 10 pts | 5 days | **~150 pts** |
| **Elite** | 4:00/km | 3:50/km | +3 | 15 pts | 10 days | **~160 pts** |

Both runners improved similarly relative to their baselines → similar scores!

### Badge System (Auto-Awarded)
- **Moving Time Badge** - Average moving time ≥ 1000 seconds → **5 pts**
- **Distance Badge** - Average distance ≥ 5000 meters → **5 pts**
- **Speed Badge** - Max speed ≥ 4 m/s (14.4 km/h) → **5 pts**

### Challenge System (Weekly Reset)
- **3+ Runs This Week** → **5 pts**
- **15+ km This Week** → **5 pts**
- **5+ Day Streak** → **5 pts**

### Streak Calculation
- Counts consecutive days with at least 1 activity
- Streak breaks if most recent activity is >24 hours ago
- Multiple activities per day count as 1 day

---

## 📊 Data Models

### Person Object
```python
class Person:
    # Identity
    name: str
    username: str
    display_name: str
    
    # Current Period Metrics (used for scoring)
    average_speed: float      # m/s
    max_speed: float          # m/s
    distance: float           # meters
    moving_time: float        # seconds
    
    # Historical Totals (all-time)
    total_workouts: int
    total_distance: float
    total_moving_time: float
    
    # Baselines (averages of all workouts)
    baseline_average_speed: float
    baseline_max_speed: float
    baseline_distance: float
    baseline_moving_time: float
    
    # Gamification
    streak: int
    score: Score
    badges: badges
    weekly_challenges: challenges
```

### Data Storage (Supabase PostgreSQL)

**user_strava Table**
```sql
CREATE TABLE user_strava (
    user_id UUID PRIMARY KEY,
    strava_athlete_id TEXT UNIQUE,
    username TEXT,
    name TEXT,
    display_name TEXT,
    email TEXT,
    location TEXT,
    avatar TEXT,
    total_workouts INTEGER,
    total_distance NUMERIC,
    total_moving_time BIGINT,
    average_speed NUMERIC,
    max_speed NUMERIC,
    streak INTEGER,
    score NUMERIC,
    improvement NUMERIC,
    badge_points INTEGER,
    challenge_points INTEGER,
    badges JSONB,
    weekly_challenges JSONB,
    strava_access_token TEXT,
    strava_refresh_token TEXT,
    strava_expires_at BIGINT,
    updated_at TIMESTAMP
);
```

**All data is stored in Supabase:**
- ✅ User profiles and metrics
- ✅ Activity statistics
- ✅ Scores and improvements
- ✅ OAuth tokens (persistent)
- ✅ Friends and friend requests
- ✅ Leaderboards

**Benefits:**
- Persistent across server restarts
- Multi-user support
- Production-ready scalability
- Row-level security (RLS)

---

## 🔄 API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/strava` | GET | Redirects to Strava OAuth |
| `/auth/strava/callback` | GET | Handles OAuth callback, stores tokens in Supabase |
| `/api/test-login` | POST | Test login with stored credentials (for testing) |
| `/api/status` | GET | Check auth status |

### Data Sync
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sync` | POST/GET | Sync activities from Strava, calculate scores, save to Supabase |
| `/strava/activities` | GET | Get raw Strava activities (grouped by weekday) |

### User Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/profile` | GET | Get user profile + stats from Supabase |
| `/person/get-activities` | POST | Get activity data (deprecated, use `/api/profile`) |
| `/api/leaderboard` | GET | Get sorted leaderboard from Supabase |
| `/api/friends` | GET | Get friends list from Supabase |

### Friends System (Supabase)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/friends/request` | POST | Send friend request |
| `/api/friends/accept` | POST | Accept friend request |
| `/api/friends/reject` | POST | Reject friend request |
| `/api/friends/remove` | POST | Remove friend |
| `/api/friends/search` | GET | Search users by name |
| `/api/friends/pending` | GET | Get pending friend requests |
| `/api/friends/sent` | GET | Get sent friend requests |

### Routes
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/routes/all` | GET | Get all routes |
| `/api/routes/search` | GET/POST | Search routes by criteria |
| `/api/routes/<id>` | GET | Get specific route |
| `/api/routes/generate` | POST | Generate custom route |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+
- Strava account
- Strava API credentials ([Get them here](https://www.strava.com/settings/api))

### Setup (5 Minutes)

#### 1. Clone & Install
```bash
git clone <repository-url>
cd Team-7-group-project-Data-Duel
pip install -r requirements.txt
```

#### 2. Configure Environment Variables
Create `DataDuel/backend/.env`:
```env
# Strava API
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:5000/auth/strava/callback

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Optional
USE_SUPABASE_STORAGE=true
FRONTEND_URL=http://localhost:5500
```

**Get Supabase credentials:**
1. Go to https://supabase.com
2. Create a project (or use existing)
3. Go to Settings → API
4. Copy `Project URL` and `anon public` key

#### 3. Run Database Migrations
1. Open Supabase Dashboard → SQL Editor
2. Run migrations in order:
   - `DataDuel/backend/supabase_stravaDB/migration_tokens.sql`
   - `DataDuel/backend/supabase_stravaDB/migration_friends.sql`
   - `DataDuel/backend/supabase_stravaDB/migration_user_profile.sql`

#### 4. Start Backend
```bash
cd DataDuel/backend
python app.py
```
Server runs at `http://localhost:5000`

#### 5. Open Frontend
Open `DataDuel/frontend/index.html` in your browser  
Or use a local server:
```bash
cd DataDuel/frontend
python -m http.server 5500
```
Then visit `http://localhost:5500`

#### 6. Complete Flow
1. Click **"Connect Strava"** (or use **"Test Login"** for testing)
2. Authorize the app (if using OAuth)
3. Click **"Sync Activities"**
4. View your **Profile** and **Leaderboard**
5. Try **Friends** features (search, send requests)

---

## 📁 Project Structure

```
Team-7-group-project-Data-Duel/
├── README.md                      # This file - complete documentation
├── requirements.txt               # Python dependencies
│
└── DataDuel/
    ├── backend/
    │   ├── .env                   # Environment variables (create this)
    │   ├── app.py                 # Flask server (1,650+ lines)
    │   ├── data_storage.py        # DEPRECATED (Supabase only now)
    │   ├── strava_parser.py       # Activity parser & calculator
    │   ├── route_generator.py     # Route system
    │   ├── supabase_stravaDB/     # Supabase integration
    │   │   ├── strava_user.py     # Supabase functions (1,100+ lines)
    │   │   ├── migration_tokens.sql      # Token storage migration
    │   │   ├── migration_friends.sql     # Friends system migration
    │   │   └── migration_user_profile.sql # User profile migration
    │   └── data/                  # DEPRECATED (legacy JSON files)
    │
    ├── frontend/
    │   ├── index.html             # Home page (auth status, sync button)
    │   ├── profile.html           # User profile (dynamic data)
    │   ├── profile-stats.html     # Detailed stats page
    │   ├── leaderboards.html      # Global leaderboard
    │   ├── social.html            # Friends & leagues (UI only)
    │   ├── routes.html            # Route discovery
    │   ├── settings.html          # App settings (UI only)
    │   ├── Strava.html            # Strava connection page
    │   ├── api.js                 # API client wrapper
    │   ├── script.js              # Tab navigation
    │   └── styles.css             # Global styles
    │
    ├── Person.py                  # User data model
    ├── Score.py                   # Scoring algorithm
    ├── badges.py                  # Badge system
    ├── challenges.py              # Challenge system
    ├── leagueLeaderboard.py       # League management
    └── main_test.py               # Test suite
```

---

## 💻 Technology Stack

### Backend
- **Framework:** Flask 3.0.0
- **CORS:** flask-cors 4.0.0
- **HTTP Client:** requests 2.31.0
- **Config:** python-dotenv 1.0.0
- **Language:** Python 3.8+

### Frontend
- **Core:** Vanilla JavaScript (ES6+)
- **HTTP:** Fetch API
- **Styling:** CSS3 with responsive design
- **No frameworks:** Lightweight, fast, simple

### APIs & Services
- **Strava API v3** - Activity data, OAuth 2.0
- **Future:** OpenAI (route generation), Google Maps (route visualization)

### Data Storage
- **Current:** Supabase PostgreSQL (production-ready)
- **Features:** Row-level security, persistent storage, multi-user support
- **Migrations:** SQL migration files for schema management

---

## 🧪 Testing

### Run Test Suite
```bash
cd DataDuel
python main_test.py
```

### Manual Testing Flow
1. **Auth Test:** Visit `/auth/strava` → should redirect to Strava
2. **Token Test:** After auth, check `backend/tokens.json` exists
3. **Sync Test:** Click "Sync Activities" → should show success message
4. **Profile Test:** Visit profile page → should show your stats
5. **Leaderboard Test:** Visit leaderboard → should show rankings

---

## 🎓 Key Technical Decisions

### Why Supabase?
- **Production-ready** - PostgreSQL database with managed infrastructure
- **Persistent storage** - Data survives server restarts (critical for Render)
- **Multi-user support** - Row-level security for data isolation
- **Scalable** - Handles growth from MVP to production
- **Developer-friendly** - SQL migrations, auto-generated APIs, real-time subscriptions

### Why Improvement-Based Scoring?
- **Fairness** - Everyone can compete regardless of fitness level
- **Motivation** - Rewards personal growth, not genetics
- **Retention** - Beginners don't feel discouraged
- **Real Competition** - Elite runners still compete on improvement

### Why Flask over Django?
- **Simplicity** - Minimal boilerplate for MVP
- **Flexibility** - Easy to add features incrementally
- **API-first** - Perfect for RESTful backend
- **Lightweight** - Fast development and debugging

---

## 🐛 Known Issues & Limitations

### Current Limitations
- **Cold start delays** - Render free tier spins down after 15 min (30-60s first request)
- **No user accounts** - Strava OAuth only (no local accounts)
- **Client-side rendering** - Full page reloads for navigation
- **Rate limiting** - No protection against Strava API limits
- **No caching** - Fetches fresh data every time

### Security Notes
- ✅ **Tokens in Supabase** - Encrypted at rest, secure storage
- ✅ **Row-level security** - Users can only access their own data
- ✅ **CORS configured** - Restricted to frontend domain
- ✅ **HTTPS enforced** - All production traffic encrypted
- ⚠️ **Session management** - Could add Flask-Login or JWT for enhanced security

---

## 🗺️ Future Roadmap

### Phase 1: Social Features (High Priority)
- ✅ Friend system (complete - Supabase)
- Custom leagues (create, join, invite)
- Friend activity feed
- Social challenges
- Group competitions

### Phase 2: Enhanced Features (Medium Priority)
- Real-time updates (WebSockets)
- Push notifications
- Advanced analytics and charts
- Training plan recommendations

### Phase 3: Advanced Features (Lower Priority)
- LLM-powered route generation
- Progressive Web App (PWA)
- Push notifications
- Mobile app (React Native)
- Data visualization (charts, graphs)

---

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open Pull Request

### Priority Areas
1. **Social features** - Custom leagues, groups, challenges
2. **Real-time updates** - WebSockets for live data
3. **Route generation** - LLM integration for custom routes
4. **Mobile app** - React Native or PWA
5. **Testing** - Expand test coverage

---

## 📞 Support & Contact

**Team:** CS422 - Team 7  
**Repository:** [Add GitHub link]  
**Issues:** [Add issue tracker link]

---

## 📄 License

[Add your license here]

---

**Last Updated:** December 2, 2025  
**Status:** Production-Ready - Fully Deployed  
**Version:** 2.0.0 (Supabase Migration Complete)

**Recent Updates:**
- ✅ Complete Supabase migration (100% database storage)
- ✅ All data pipeline issues resolved
- ✅ Standardized API endpoints
- ✅ Enhanced token management
- ✅ Test login feature for easy testing
- ✅ Frontend code cleanup
