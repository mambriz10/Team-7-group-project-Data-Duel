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

#### Backend (Python)
- **Person Class** (`Person.py`)
  - User information (name, username, display name)
  - Running metrics (speed, distance, cadence, elevation, etc.)
  - Baseline calculation for improvement tracking
  - Streak and total workout tracking
  - Score object integration
  - Methods for updating baselines from new workouts
- **Score Class** (`Score.py`)
  - Scoring algorithm that rewards improvement over baseline
  - Improvement bonus calculation
  - Comparison against personal baselines (not absolute performance)
  - Handles positive and negative performance changes
  - Incorporates badges, challenges, and streaks into scoring
- **League Leaderboard Class** (`leagueLeaderboard.py`)
  - Player sorting by score
  - Rank assignment
  - Basic structure for custom leagues

---

## 🚧 Missing Features & TODOs

### High Priority

#### 1. **Strava API Integration**
- [ ] OAuth authentication flow
- [ ] User authorization and token management
- [ ] Fetch user activities (runs) from Strava
- [ ] Import running metrics (distance, pace, elevation, etc.)
- [ ] Periodic sync for new activities
- [ ] Error handling for API rate limits

#### 2. **Backend Server & API**
- [ ] Set up web framework (Flask/FastAPI/Django)
- [ ] Create RESTful API endpoints for:
  - User authentication
  - Profile data
  - Leaderboard data
  - Friends management
  - League management
  - Route management
  - Score calculation
- [ ] Connect Python classes to API endpoints

#### 3. **Database Implementation**
- [ ] Design database schema
- [ ] Set up database (PostgreSQL/MySQL/SQLite)
- [ ] User table
- [ ] Activities/workouts table
- [ ] Scores and history table
- [ ] Friends/relationships table
- [ ] Leagues table
- [ ] Routes table
- [ ] Challenges table
- [ ] Implement database queries and ORM

#### 4. **User Authentication System**
- [ ] User registration flow
- [ ] Login/logout functionality
- [ ] Session management
- [ ] Password hashing and security
- [ ] Connect Strava account to DataDuel account

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

#### 7. **Challenges System**
- [ ] Weekly challenge creation
- [ ] Challenge types (distance, consistency, improvement)
- [ ] Challenge progress tracking
- [ ] Challenge completion rewards
- [ ] Challenge history

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

#### 10. **Route Generation**
- [ ] Create custom routes
- [ ] Route recommendations based on preferences
- [ ] Integration with mapping services
- [ ] Save favorite routes
- [ ] Share routes with friends
- [ ] Route difficulty ratings
- [ ] Route reviews and ratings

#### 11. **Badges & Achievements**
- [ ] Badge system implementation
- [ ] Achievement criteria definition
- [ ] Badge display on profiles
- [ ] Badge points integration with scoring
- [ ] Special badges for milestones

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
- **Backend:** Python 3.x
- **API Integration:** Strava API (planned)

### Recommended Additions
- **Backend Framework:** Flask or FastAPI
- **Database:** PostgreSQL or MongoDB
- **Authentication:** OAuth 2.0, JWT tokens
- **Deployment:** Docker, AWS/Heroku/Vercel

---

## 📁 Project Structure

```
DataDuel/
├── index.html              # Home/landing page
├── leaderboards.html       # Leaderboard display
├── profile.html            # User profile page
├── social.html             # Friends and leagues
├── routes.html             # Saved routes
├── settings.html           # App settings
├── styles.css              # Global styles
├── script.js               # Client-side JavaScript
├── Person.py               # User data model
├── Score.py                # Scoring algorithm
└── leagueLeaderboard.py    # League management
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Modern web browser
- Strava account (for future integration)

### Current Setup (Development)
1. Clone the repository
   ```bash
   git clone <repository-url>
   cd Team-7-group-project-Data-Duel
   ```

2. Open `DataDuel/index.html` in your browser to view the static frontend

3. Backend classes can be imported and tested:
   ```python
   from Person import Person
   from Score import Score
   
   user = Person()
   # Test scoring logic
   ```

### Future Setup (Once Backend is Implemented)
Instructions will be added for:
- Installing dependencies
- Setting up the database
- Configuring Strava API credentials
- Running the development server

---

## 🤝 Contributing

### Development Workflow
1. Create a feature branch
2. Implement your feature
3. Test thoroughly
4. Submit a pull request

### Priority Areas for Contribution
1. Strava API integration
2. Backend server setup
3. Database implementation
4. User authentication
5. Converting static pages to dynamic data-driven pages

---

## 📝 Notes

- The current implementation is a **frontend prototype** with **backend data models**
- All frontend data is currently **static/hardcoded**
- The scoring algorithm in `Score.py` is **ready for integration** but needs:
  - Real workout data from Strava
  - Badge system implementation
  - Challenge system implementation
- The `Person.py` class structure is **ready** but needs:
  - Database persistence
  - API endpoints for data access
  - Integration with Strava activity data

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

**Last Updated:** November 10, 2025

