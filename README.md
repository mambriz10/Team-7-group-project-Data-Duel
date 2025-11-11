# DataDuel 🏃‍♂️

**DataDuel** is a fitness tracking application designed to create a fair and inclusive running competition platform by emphasizing improvement, consistency, and personal growth rather than raw athletic performance.

## 🎯 Project Vision

DataDuel integrates with the Strava API to track workout and running data, assigning scores based on:
- **Consistency** - Regular activity and streaks
- **Improvement** - Progress relative to personal baselines
- **Growth** - Meeting challenges and earning badges

This scoring system ensures that users who are naturally faster or more fit don't dominate leaderboards, making competition more equitable and motivating for all fitness levels.

---

## 📋 Current Implementation Status

### ✅ Implemented Features

#### Frontend (HTML/CSS/JavaScript)
Located in `DataDuel/frontend/`

- **Navigation Structure** - Five main pages with responsive bottom tab navigation
- **Home Page** (`index.html`) - Landing page with navigation to leaderboards
- **Leaderboard Page** (`leaderboards.html`)
  - Static demo leaderboard with improvement-based scoring
  - Filter options (Last 4 weeks, All-time, This week) - UI only
  - Display columns: Rank, Name, Runs, Improvement %, Total Points
  - Highlight for current user
- **Profile Page** (`profile.html`)
  - User avatar display
  - Static stats display (runs, distance, average pace)
  - Edit profile button (placeholder)
- **Social Page** (`social.html`)
  - Friends list with static demo data
  - Friend activity preview
  - Placeholder buttons for "Find Friends" and "Create League"
  - Friend request section (empty state)
- **Routes Page** (`routes.html`)
  - Saved routes display with distance, elevation, and last run time
  - Placeholder buttons for "Create Route", "Import from Strava", and "Start Run"
- **Settings Page** (`settings.html`)
  - Theme selector (Light/Dark) - UI only
  - Units selector (Metric/Imperial) - UI only
  - Notifications toggle - demo functionality only
  - Strava connection button (disabled)
- **Styling** (`styles.css`) - Clean, modern UI with accessibility features
- **Client Script** (`script.js`) - Active tab highlighting logic

#### Backend (Python)
Located in `DataDuel/`

##### Core Data Models
- **Person Class** (`Person.py`)
  - User information (name, username, display name) with privacy controls
  - Running metrics (average_speed, max_speed, distance, moving_time, cadence, watts, elevation)
  - Baseline calculation for improvement tracking (average of all workouts)
  - Streak tracking and total workout counting
  - **Integrated objects:**
    - `score` (Score instance)
    - `badges` (badges instance)
    - `weekly_challenges` (challenges instance)
  - Methods for updating baselines from new workouts
  - `update_baseline_from_workout()` - updates totals and recalculates baselines
  - `show_real_name()` - privacy control for leaderboard display
  - `increase_total_workouts()` - increments workout counter
  
- **Score Class** (`Score.py`)
  - Scoring algorithm that rewards improvement over baseline
  - Improvement bonus calculation (1% improvement = 5 points)
  - Comparison against personal baselines (not absolute performance)
  - Handles positive and negative performance changes
  - Incorporates badges, challenges, and streaks into scoring
  - Dynamic scaling based on multiple performance metrics
  
- **League Leaderboard Class** (`leagueLeaderboard.py`)
  - Player sorting by score
  - Rank assignment
  - Basic structure for custom leagues
  - Support for league size and duration settings

##### New Features
- **Badges Class** (`badges.py`)
  - Badge tracking system for moving_time, distance, max_watts, max_speed
  - Points calculation (5 points per badge)
  - Badge descriptions and names
  - Integrated with Person class
  - Ready for automatic awarding logic
  
- **Challenges Class** (`challenges.py`)
  - Weekly challenge completion tracking (3 concurrent challenges)
  - Points calculation (5 points per completed challenge)
  - Challenge descriptions and names
  - Integrated with Person class and scoring system
  - Support for multiple concurrent challenges

##### Backend Server
- **Flask API Server** (`backend/app.py`)
  - ✅ **Strava OAuth Authentication Flow** - FULLY IMPLEMENTED
    - Home route (`/`) - Server status endpoint
    - Authorization endpoint (`/auth/strava`) - Redirects to Strava OAuth
    - OAuth callback handler (`/auth/strava/callback`) - Exchanges code for tokens
    - Token storage (JSON file: `tokens.json`)
    - Automatic token refresh when expired via `get_valid_token()`
    - Returns athlete information after successful authentication
  - ✅ **Activity Fetching** (`/strava/activities`) - FULLY IMPLEMENTED
    - Retrieves recent user activities from Strava API v3
    - Automatically refreshes expired tokens
    - Returns activity data in JSON format
    - Handles authentication errors gracefully
  - Environment variable configuration via `.env` file
  - Comprehensive error handling for authentication failures and API errors
  - Uses python-dotenv for secure credential management

##### Testing
- **Test Suite** (`main_test.py`)
  - Person class instantiation and initialization tests
  - Baseline calculation verification (average speed, max speed, distance, moving time)
  - Score calculation integration tests with badges and challenges
  - End-to-end test demonstrating complete scoring workflow
  - Validates Person-Score-Badge-Challenge integration

---

## 🚧 Missing Features & TODOs

### High Priority

#### 1. **Strava API Integration** ⚡ *Partially Complete*
- [x] OAuth authentication flow ✅
- [x] User authorization and token management ✅
- [x] Fetch user activities (runs) from Strava ✅
- [ ] Parse and store running metrics (distance, pace, elevation, etc.)
- [ ] Map Strava data to Person class attributes
- [ ] Periodic sync for new activities (webhook or polling)
- [ ] Error handling for API rate limits
- [ ] Frontend integration with Strava auth flow

#### 2. **Backend Server & API** ⚡ *Partially Complete*
- [x] Set up web framework (Flask) ✅
- [x] Strava authentication endpoints ✅
- [ ] Create additional RESTful API endpoints for:
  - User profile data (GET/PUT)
  - Leaderboard data (GET with filters)
  - Friends management (GET/POST/DELETE)
  - League management (CRUD operations)
  - Route management (CRUD operations)
  - Score calculation (POST with activity data)
  - Badges and challenges (GET/UPDATE)
- [ ] Connect Python classes to API endpoints
- [ ] Frontend-to-backend communication layer

#### 3. **Database Implementation**
- [ ] Design database schema
- [ ] Set up database (PostgreSQL/MySQL/SQLite)
- [ ] User table with profile information
- [ ] Activities/workouts table (from Strava sync)
- [ ] Scores and history table
- [ ] Friends/relationships table
- [ ] Leagues table with membership
- [ ] Routes table (saved routes)
- [ ] Badges table (achievement tracking)
- [ ] Challenges table (active/completed)
- [ ] Implement database queries and ORM (SQLAlchemy recommended)
- [ ] Database migrations setup

#### 4. **User Authentication System**
- [ ] User registration flow (email/password or Strava-only)
- [ ] Login/logout functionality
- [ ] Session management (JWT or Flask sessions)
- [ ] Password hashing and security (if not Strava-only auth)
- [ ] Connect DataDuel account with Strava OAuth
- [ ] User profile completion flow after Strava auth

### Medium Priority

#### 5. **Social Features**
- [ ] Add friends functionality
- [ ] Friend request system (send, accept, reject)
- [ ] Remove friends
- [ ] View friend profiles
- [ ] Friend activity feed
- [ ] Search for users

#### 6. **Custom Leagues**
- [ ] Create league interface
- [ ] Join existing leagues
- [ ] League-specific leaderboards
- [ ] League duration and size settings
- [ ] Invite friends to leagues
- [ ] Leave leagues
- [ ] League discovery

#### 7. **Challenges System** ⚡ *Partially Complete*
- [x] Challenge data model (`challenges.py`) ✅
- [x] Challenge points calculation ✅
- [x] Integration with scoring system ✅
- [ ] Weekly challenge creation UI
- [ ] Challenge types (distance, consistency, improvement)
- [ ] Challenge progress tracking and updates
- [ ] Challenge completion detection from activities
- [ ] Challenge history and analytics
- [ ] Social challenges (compete with friends)

#### 8. **Profile Management**
- [ ] Edit profile information
- [ ] Upload custom avatar
- [ ] Privacy settings (show real name vs username)
- [ ] View personal statistics
- [ ] Activity history
- [ ] Performance graphs and trends

#### 9. **Leaderboard Enhancements**
- [ ] Real-time data updates
- [ ] Filter by time period (functional)
- [ ] Multiple leaderboard types (global, friends, leagues)
- [ ] Pagination for large leaderboards
- [ ] Export leaderboard data

### Lower Priority

#### 10. **Route Generation** 📚 *Documentation Complete*
- [x] Comprehensive implementation guide (`route-guide.md`) ✅
- [ ] LLM-powered natural language route parsing
- [ ] Create custom routes with waypoints
- [ ] Route recommendations based on preferences
- [ ] Integration with Google Maps/Mapbox APIs
- [ ] Strava segment integration for popular routes
- [ ] Save favorite routes
- [ ] Share routes with friends
- [ ] Route difficulty ratings and elevation profiles
- [ ] Route reviews and ratings

*See [`route-guide.md`](route-guide.md) for detailed implementation strategy, API usage examples, and MVP roadmap.*

#### 11. **Badges & Achievements** ⚡ *Partially Complete*
- [x] Badge data model (`badges.py`) ✅
- [x] Badge points calculation ✅
- [x] Integration with scoring system ✅
- [ ] Badge criteria definition and checking logic
- [ ] Automatic badge awarding based on activities
- [ ] Badge display on profiles (UI)
- [ ] Badge notifications
- [ ] Special badges for milestones (streaks, totals, PRs)
- [ ] Badge collection and showcase features

#### 12. **Notifications**
- [ ] Push notification system
- [ ] Email notifications
- [ ] Weekly summary reports
- [ ] Challenge updates
- [ ] Friend activity notifications
- [ ] Leaderboard position changes

#### 13. **Settings & Preferences**
- [ ] Functional theme switching (dark mode)
- [ ] Unit conversion (metric ↔ imperial)
- [ ] Language preferences
- [ ] Privacy controls
- [ ] Data export functionality

#### 14. **Mobile Optimization**
- [ ] Progressive Web App (PWA) support
- [ ] Touch gesture support
- [ ] Offline functionality
- [ ] Mobile-specific UI refinements

#### 15. **Data Visualization**
- [ ] Performance graphs (distance over time, pace improvements)
- [ ] Score history charts
- [ ] Comparison with friends
- [ ] Weekly/monthly summaries
- [ ] Goal tracking visualizations

---

## 🏗️ Technology Stack

### Current
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend Framework:** Flask (Python 3.x)
- **API Integration:** 
  - Strava API (OAuth 2.0) ✅
  - OpenAI API (for route generation - planned)
  - Google Maps/Mapbox API (for route generation - planned)
- **Authentication:** OAuth 2.0 (Strava)
- **Data Storage:** JSON files (temporary, needs database migration)
- **Environment Management:** python-dotenv

### Recommended Additions
- **Database:** PostgreSQL or SQLite (for development)
- **ORM:** SQLAlchemy
- **Authentication Extension:** Flask-Login or JWT tokens
- **API Documentation:** Swagger/OpenAPI
- **Frontend Framework:** React or Vue.js (for dynamic pages)
- **Deployment:** Docker, AWS/Heroku/Render
- **Testing:** pytest, unittest

---

## 📁 Project Structure

```
Team-7-group-project-Data-Duel/
├── .gitignore                     # Git ignore rules (tokens, env, cache)
├── README.md                      # Project documentation (this file)
├── requirements.txt               # Python dependencies
├── route-guide.md                 # Route generation implementation guide
│
└── DataDuel/
    ├── backend/
    │   ├── .env                   # Environment variables (create from .env.example)
    │   ├── app.py                 # Flask API server with Strava OAuth
    │   └── tokens.json            # Strava tokens (auto-generated after auth)
    │
    ├── frontend/
    │   ├── index.html             # Home/landing page
    │   ├── leaderboards.html      # Leaderboard display
    │   ├── profile.html           # User profile page
    │   ├── social.html            # Friends and leagues
    │   ├── routes.html            # Saved routes
    │   ├── settings.html          # App settings
    │   └── styles.css             # Global styles
    │
    ├── Person.py                  # User data model
    ├── Score.py                   # Scoring algorithm
    ├── leagueLeaderboard.py       # League management
    ├── badges.py                  # Badge system
    ├── challenges.py              # Challenge system
    ├── script.js                  # Client-side JavaScript
    └── main_test.py               # Test suite
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Modern web browser
- Strava account (for API integration)
- Strava API credentials (Client ID & Secret) - [Register an app](https://www.strava.com/settings/api)

### Setup Instructions

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd Team-7-group-project-Data-Duel
```

#### 2. Install Python Dependencies

Using the included `requirements.txt` file:
```bash
pip install -r requirements.txt
```

> **Tip:** Use a virtual environment for isolated dependencies:
> ```bash
> python -m venv venv
> source venv/bin/activate  # On Windows: venv\Scripts\activate
> pip install -r requirements.txt
> ```

#### 3. Configure Strava API Credentials

**First, register your app with Strava:**
1. Go to [https://www.strava.com/settings/api](https://www.strava.com/settings/api)
2. Create a new application
3. Set "Authorization Callback Domain" to `localhost`
4. Note your **Client ID** and **Client Secret**

**Then, create a `.env` file in the `DataDuel/backend/` directory:**

```env
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:5000/auth/strava/callback
```

Replace `your_client_id_here` and `your_client_secret_here` with your actual Strava API credentials.

> **Security Note:** Never commit your `.env` file to Git! It's already in `.gitignore` to prevent accidental commits.

#### 4. Run the Flask Backend

```bash
cd DataDuel/backend
python app.py
```

The server will start at `http://localhost:5000`

#### 5. Test Strava Authentication

1. Visit `http://localhost:5000/auth/strava` in your browser
2. Authorize the app with your Strava account (you'll be redirected to Strava)
3. You'll be redirected back to the callback endpoint
4. You should see a JSON response with athlete info and token data
5. A `tokens.json` file will be created in the `backend/` directory with your access token

> **Troubleshooting:** If you see "tokens.json not found" errors, ensure the callback successfully created the token file. Check console output for any OAuth errors.

#### 6. Fetch Strava Activities

Once authenticated, visit:
```
http://localhost:5000/strava/activities
```

This will return your recent Strava activities in JSON format. Example response structure:
```json
[
  {
    "id": 123456789,
    "name": "Morning Run",
    "distance": 5000,
    "moving_time": 1800,
    "elapsed_time": 1900,
    "total_elevation_gain": 50,
    "type": "Run",
    "average_speed": 2.78,
    "max_speed": 3.5,
    ...
  }
]
```

#### 7. View Frontend (Static)

Open `DataDuel/frontend/index.html` in your browser to view the UI prototype.

#### 8. Run Tests

```bash
cd DataDuel
python main_test.py
```

### Next Steps for Development

**Immediate Priority:**
1. **Fix token file naming bug** in `backend/app.py` (line 57: change `tokens_.json` to `tokens.json`)
2. **Set up database** (PostgreSQL or SQLite with SQLAlchemy)
3. **Create data parser** to map Strava activity JSON to Person object attributes
4. **Implement multi-user support** - Allow multiple users to authenticate and store separate tokens

**Short-term Goals:**
5. Connect frontend to backend API (add fetch calls in `script.js`)
6. Implement user registration and session management (Flask-Login or JWT)
7. Create API endpoints for profile, leaderboard, friends, leagues
8. Parse Strava activities and automatically update Person/Score objects

**Medium-term Goals:**
9. Implement real-time leaderboard updates
10. Add social features (friends, leagues)
11. Deploy to a cloud platform (Heroku, Render, or AWS)

---

## 🤝 Contributing

### Development Workflow
1. Create a feature branch
2. Implement your feature
3. Test thoroughly
4. Submit a pull request

### Priority Areas for Contribution
1. ~~Strava API integration~~ ✅ OAuth flow complete
2. ~~Backend server setup~~ ✅ Flask server with endpoints
3. **Database implementation** (🔥 HIGHEST PRIORITY)
   - Set up PostgreSQL or SQLite
   - Create schema for users, activities, scores, badges, challenges, leagues
   - Implement SQLAlchemy ORM models
4. **Parse Strava activity data into Person objects** (🔥 HIGH PRIORITY)
   - Map Strava activity JSON fields to Person attributes
   - Automatically calculate baselines from activity history
   - Trigger score calculations on new activities
5. **User authentication and session management**
   - Flask-Login or JWT implementation
   - Multi-user support (currently single-token)
6. **Frontend-backend integration**
   - Add JavaScript fetch calls to API endpoints
   - Dynamic data rendering for all pages
   - User authentication flow in UI
7. **Converting static pages to dynamic data-driven pages**
8. **Route generation system** (see [`route-guide.md`](route-guide.md))

---

## 📝 Notes

### Current State
- **Backend**: Flask server operational with Strava OAuth authentication ✅
- **Frontend**: Static HTML/CSS prototype with all main pages ✅
- **Data Models**: Complete Python classes for Person, Score, Badges, Challenges, Leagues ✅
- **Testing**: Basic test suite for core functionality ✅

### Integration Needs
- The scoring algorithm in `Score.py` is **ready for integration** but needs:
  - Real workout data from Strava API responses
  - Automatic badge awarding logic
  - Challenge completion detection
  
- The `Person.py` class structure is **ready** but needs:
  - Database persistence layer
  - API endpoints for CRUD operations
  - Mapping from Strava activity JSON to Person attributes
  - User profile management system

- The frontend pages need:
  - JavaScript fetch calls to backend API endpoints
  - Dynamic data rendering (replace hardcoded values)
  - User authentication flow integration
  - Real-time updates for leaderboards

### Known Issues & Limitations
- **Tokens stored in JSON file** (temporary solution, move to secure database)
- **No user session management** yet (Flask sessions or JWT needed)
- **Frontend and backend not connected** (need to integrate API calls)
- **No error handling for failed API calls** in frontend
- **Single-user token storage** (app.py stores one token set; needs multi-user support)
- **Strava activities not parsed** into Person objects yet
- **No database persistence** for users, activities, or scores
- **Token file naming inconsistency** in app.py (uses `tokens_.json` in callback, but `tokens.json` in get_valid_token)

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - 5-minute guide to get the MVP running (START HERE!)
- **[MVP_IMPLEMENTATION.md](MVP_IMPLEMENTATION.md)** - Complete implementation guide with all changes, testing procedures, and demo script
- **[route-guide.md](route-guide.md)** - Comprehensive guide for implementing the route generation feature using LLM, Strava API, and mapping services

---

## 📄 License

[Add your license here]

---

## 👥 Team

CS422 - Team 7

---

## 📞 Contact

[Add contact information or links]

---

---

## 🎉 MVP Complete - Demo Ready!

**Status:** ALL FEATURES WORKING - Ready for demo tomorrow

### What's New (Latest Session)
- ✅ **Route Generation System** - 5 pre-defined routes, searchable/filterable
- ✅ **All Emojis Removed** - Professional appearance
- ✅ **Complete Demo Guide** - [`MVP_DEMO_CHECKLIST.md`](MVP_DEMO_CHECKLIST.md)
- ✅ **Updated Test Suite** - All tests passing

### Quick Start for Demo
1. **Start Backend:** `cd DataDuel/backend && python app.py`
2. **Open Frontend:** `DataDuel/frontend/index.html`
3. **Connect Strava** → **Sync Activities** → **View Profile/Leaderboard/Routes**

### Documentation
- **[MVP_DEMO_CHECKLIST.md](MVP_DEMO_CHECKLIST.md)** - Complete 10-minute demo script (START HERE)
- **[FINAL_MVP_SUMMARY.md](FINAL_MVP_SUMMARY.md)** - Feature overview & stats
- **[MVP_IMPLEMENTATION.md](MVP_IMPLEMENTATION.md)** - Technical implementation details
- **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide
- **[route-guide.md](route-guide.md)** - Future route generation roadmap

---

**Last Updated:** November 11, 2025 - Route system added, all emojis removed, demo-ready

