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

## 📋 Current Status: **MVP Complete & Demo-Ready**

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
| **Data Storage** | ✅ Working | JSON-based storage (MVP; database ready for upgrade) |

### 🚧 Planned Enhancements
- Database migration (PostgreSQL/SQLite)
- Social features (friends, custom leagues)
- Mobile optimization & PWA
- Advanced route generation with LLM
- Notification system

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
         │ Stores: tokens.json + data/users.json
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
  activities.json    users.json      scores.json      Frontend Display
  (raw data)         (metrics)       (scores)         (success msg)


3. PROFILE DISPLAY
   ┌─────────────┐   GET /api/profile   ┌─────────────┐
   │ profile.html│ ──────────────────>  │   Backend   │
   │  (Page Load)│                       │   Server    │
   └─────────────┘                       └─────────────┘
         ↑                                      │
         │                              ┌───────┴───────┐
         │                              │ Load from:    │
         │                              │ • users.json  │
         │                              │ • scores.json │
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

### Data Storage (JSON Files)

**users.json**
```json
{
  "67126670": {
    "id": "67126670",
    "name": "Daniel Chavez",
    "username": "daniel_runner",
    "avatar": "https://...",
    "total_workouts": 15,
    "total_distance": 75000,
    "total_moving_time": 18000,
    "streak": 7
  }
}
```

**scores.json**
```json
{
  "67126670": {
    "score": 250,
    "improvement": 15.5,
    "badge_points": 15,
    "challenge_points": 10,
    "streak": 7
  }
}
```

**activities.json**
```json
{
  "67126670": [
    {
      "id": 123456789,
      "name": "Morning Run",
      "distance": 5000,
      "moving_time": 1800,
      "average_speed": 2.78,
      "type": "Run"
    }
  ]
}
```

---

## 🔄 API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/strava` | GET | Redirects to Strava OAuth |
| `/auth/strava/callback` | GET | Handles OAuth callback, stores tokens |
| `/api/status` | GET | Check auth status |

### Data Sync
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sync` | POST | Sync activities from Strava, calculate scores |
| `/strava/activities` | GET | Get raw Strava activities |

### User Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/profile` | GET | Get user profile + stats |
| `/api/leaderboard` | GET | Get sorted leaderboard |
| `/api/friends` | GET | Get friends list |

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

#### 2. Configure Strava API
Create `DataDuel/backend/.env`:
```env
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:5000/auth/strava/callback
```

#### 3. Start Backend
```bash
cd DataDuel/backend
python app.py
```
Server runs at `http://localhost:5000`

#### 4. Open Frontend
Open `DataDuel/frontend/index.html` in your browser

#### 5. Complete Flow
1. Click **"Connect Strava"**
2. Authorize the app
3. Click **"Sync Activities"**
4. View your **Profile** and **Leaderboard**

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
    │   ├── app.py                 # Flask server (528 lines)
    │   ├── data_storage.py        # JSON storage manager
    │   ├── strava_parser.py       # Activity parser & calculator
    │   ├── route_generator.py     # Route system
    │   ├── tokens.json            # OAuth tokens (auto-generated)
    │   └── data/                  # Data storage
    │       ├── users.json         # User profiles
    │       ├── activities.json    # Strava activities
    │       └── scores.json        # Calculated scores
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
- **Current:** JSON files (MVP)
- **Planned:** PostgreSQL with SQLAlchemy ORM

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

### Why JSON Storage?
- **Fast MVP development** - No database setup required
- **Easy debugging** - Human-readable files
- **Simple deployment** - No database server needed
- **Future-proof** - Easy migration to PostgreSQL

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
- **Single-session storage** - JSON files, no concurrent users
- **No user accounts** - Strava OAuth only (no local accounts)
- **Client-side rendering** - Full page reloads for navigation
- **Rate limiting** - No protection against Strava API limits
- **No caching** - Fetches fresh data every time

### Security Notes
- **Tokens in JSON** - Move to encrypted database in production
- **No session management** - Implement Flask-Login or JWT
- **CORS wide open** - Restrict origins in production
- **No HTTPS** - Use SSL in production deployment

---

## 🗺️ Future Roadmap

### Phase 1: Database Migration (High Priority)
- Migrate to PostgreSQL/SQLite
- Implement SQLAlchemy ORM
- Add migrations (Alembic)
- Multi-user support with proper sessions

### Phase 2: Social Features (Medium Priority)
- Friend system (add, remove, search)
- Custom leagues (create, join, invite)
- Friend activity feed
- Social challenges

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
1. **Database migration** - Replace JSON with PostgreSQL
2. **User authentication** - Add Flask-Login or JWT
3. **Social features** - Friends, leagues, challenges
4. **Route generation** - LLM integration
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

**Last Updated:** November 11, 2025  
**Status:** MVP Complete - Ready for Demo  
**Version:** 1.0.0
