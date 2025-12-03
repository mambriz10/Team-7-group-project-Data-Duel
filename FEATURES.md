# 🎯 DataDuel - Features & Technical Documentation

This document provides technical details on all implemented features, data models, algorithms, and APIs.

---

## 📋 Table of Contents
1. [Scoring System](#scoring-system)
2. [Friends System (Supabase)](#friends-system-supabase)
3. [Badge & Challenge Systems](#badge--challenge-systems)
4. [Route Generation](#route-generation)
5. [Data Models](#data-models)
6. [API Endpoints](#api-endpoints)
7. [Authentication Flow](#authentication-flow)

---

## 📊 Scoring System

### Core Philosophy
**Score = Improvement × Consistency + Bonuses**

Traditional fitness apps reward raw performance. DataDuel rewards **personal growth**.

### The Algorithm

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

| Runner | Baseline Pace | Current Pace | Scale | Badges | Streak | Final Score |
|--------|---------------|--------------|-------|--------|--------|-------------|
| **Beginner** | 7:00/km | 6:30/km (improved) | +3 | 10 pts | 5 days | **~150 pts** |
| **Elite** | 4:00/km | 3:50/km (improved) | +3 | 15 pts | 10 days | **~160 pts** |
| **Declining** | 6:00/km | 6:30/km (slower) | -2 | 10 pts | 3 days | **~10 pts** |

**Why It's Fair:** Both runners improved similarly relative to their baselines → similar scores!

### Baseline Calculation

Baselines are **averages of all historical activities**:

```python
baseline_average_speed = sum(all_speeds) / len(activities)
baseline_max_speed = max(all_max_speeds)
baseline_distance = sum(all_distances) / len(activities)
baseline_moving_time = sum(all_times) / len(activities)
```

**Updated:** Every time activities are synced

---

## 🤝 Friends System (Supabase)

### Overview
Complete friend request system with:
- Send/accept/reject requests
- Bidirectional friendships
- Status tracking (pending, friends, none)
- Search users by name
- Full Supabase integration (production-ready)

### Database Schema

#### Table: `friends`
```sql
CREATE TABLE friends (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    friend_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP,
    UNIQUE(user_id, friend_id)
);
```

**Bidirectional:** Each friendship has 2 rows (user1→user2 and user2→user1)

#### Table: `friend_requests`
```sql
CREATE TABLE friend_requests (
    id UUID PRIMARY KEY,
    from_user_id UUID REFERENCES auth.users(id),
    to_user_id UUID REFERENCES auth.users(id),
    status TEXT CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(from_user_id, to_user_id)
);
```

### Functions (Supabase)

**File:** `DataDuel/backend/supabase_stravaDB/strava_user.py`

```python
send_friend_request(from_user_id, to_user_id)
    # Returns: (success_data, error_message)
    # Auto-accepts if mutual request

accept_friend_request(user_id, from_user_id)
    # Creates bidirectional friendship
    # Updates request status to 'accepted'

reject_friend_request(user_id, from_user_id)
    # Updates request status to 'rejected'

remove_friend(user_id, friend_id)
    # Deletes both friendship rows

get_friends_list(user_id)
    # Returns: list of friend_ids

get_pending_requests(user_id)
    # Returns: incoming friend requests

get_sent_requests(user_id)
    # Returns: outgoing friend requests

get_friend_status(user_id, other_user_id)
    # Returns: 'friends', 'pending_sent', 'pending_received', 'none'

search_users_by_name(query)
    # Searches username and email (case-insensitive)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/friends/search?q=name` | GET | Search users |
| `/api/friends/request` | POST | Send friend request |
| `/api/friends/accept/<id>` | POST | Accept request |
| `/api/friends/reject/<id>` | POST | Reject request |
| `/api/friends/remove/<id>` | DELETE | Remove friend |
| `/api/friends` | GET | Get friends list |
| `/api/friends/requests` | GET | Get pending requests |
| `/api/friends/sent` | GET | Get sent requests |

### Frontend Integration

**File:** `DataDuel/frontend/social.html`

**Features:**
- Search dialog with real-time filtering
- Friendship status badges (pending, friends, etc.)
- Pending requests tab with accept/reject buttons
- Friends list with stats
- Remove friend functionality

---

## 🏆 Badge & Challenge Systems

### Badges (Auto-Awarded)

**File:** `DataDuel/badges.py`

```python
class badges:
    def __init__(self):
        self.moving_time_badge = False  # ≥1000 seconds avg
        self.distance_badge = False     # ≥5000 meters avg
        self.max_speed_badge = False    # ≥4 m/s max speed
```

**Points:** 5 points per badge (max 15 total)

**Checked:** Every activity sync

### Challenges (Weekly Reset)

**File:** `DataDuel/challenges.py`

```python
class challenges:
    def __init__(self):
        self.first_challenge = False   # 3+ runs this week
        self.second_challenge = False  # 15+ km this week
        self.third_challenge = False   # 5+ day streak
```

**Points:** 5 points per challenge (max 15 total)

**Reset:** Weekly (implementation tracks week)

### Streak Calculation

**Algorithm:**
1. Get all activity dates
2. Sort chronologically
3. Count consecutive days
4. Break if gap >24 hours from most recent activity

**Implementation:** `StravaParser.calculate_streak()`

---

## 🗺️ Route Generation

### Current Implementation

**File:** `DataDuel/backend/route_generator.py`

**5 Pre-defined Routes:**
- Campus Loop (5km, easy, 50m elevation)
- River Trail (10km, moderate, 100m elevation)
- Hill Climb (8km, hard, 300m elevation)
- Park Circuit (3km, easy, 20m elevation)
- Long Distance (21km, hard, 200m elevation)

### Route Search/Filter

**Criteria:**
- Distance (min/max)
- Difficulty (easy/moderate/hard)
- Elevation gain
- Surface type (future)

**API Endpoint:**
```
GET/POST /api/routes/search
Body: {
  "min_distance": 5000,
  "max_distance": 15000,
  "difficulty": "moderate"
}
```

### Future: LLM-Generated Routes

**Planned:** Use OpenAI/LLM to generate custom routes based on:
- User preferences
- Location
- Training goals
- Historical performance

**Endpoint:** `POST /api/routes/generate`

---

## 📊 Data Models

### Person Object

**File:** `DataDuel/Person.py`

```python
class Person:
    # Identity
    name: str
    username: str
    display_name: str
    athlete_id: str
    
    # Current Period Metrics (for scoring)
    average_speed: float      # m/s
    max_speed: float          # m/s
    distance: float           # meters
    moving_time: float        # seconds
    
    # Historical Totals
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

**Key Methods:**
```python
populate_player_activities_by_day(activities_by_day)
    # Parses activities, calculates metrics

sum_activities()
    # Aggregates total workouts, distance, time

update_baseline()
    # Calculates new baselines from all activities
```

### Score Object

**File:** `DataDuel/Score.py`

```python
class Score:
    score: float
    improvement: float
    badge_points: int
    challenge_points: int
    streak: int
```

**Calculation:** `Score.calculate(person)` (see Scoring System above)

### Storage Schema (Supabase)

**All data stored in `user_strava` table:**

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

**Key Features:**
- ✅ All user data in single table
- ✅ Row-level security (RLS) enabled
- ✅ Persistent across server restarts
- ✅ Multi-user support
- ✅ Indexed for fast lookups by `strava_athlete_id`

**Note:** Activities are fetched on-demand from Strava API, not stored in database (can be cached if needed).

---

## 🔌 API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/strava` | GET | Redirect to Strava OAuth |
| `/auth/strava/callback` | GET | OAuth callback, store tokens |
| `/api/status` | GET | Check auth status |

### Data Sync

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sync` | POST | Full sync: activities → calculate → store |
| `/strava/activities` | GET | Get raw Strava activities |
| `/person/update-activities` | POST | Update Supabase with activities |
| `/person/get-activities` | POST | Fetch activities from Supabase (deprecated, use `/api/profile`) |
| `/api/test-login` | POST | Test login with stored credentials (for testing) |

### User Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/profile` | GET | Get user profile + stats |
| `/api/leaderboard` | GET | Get sorted leaderboard |

### Friends (See Friends System above)

All `/api/friends/*` endpoints

### Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/routes/all` | GET | Get all routes |
| `/api/routes/search` | GET/POST | Search/filter routes |
| `/api/routes/<id>` | GET | Get specific route |
| `/api/routes/generate` | POST | Generate custom route (future) |

---

## 🔐 Authentication Flow

### Strava OAuth 2.0

```
1. User clicks "Connect Strava"
   → Frontend: Redirects to /auth/strava
   → Backend: Redirects to Strava OAuth URL

2. User authorizes on Strava
   → Strava redirects to /auth/strava/callback?code=xxx

3. Backend exchanges code for access token
   → POST to Strava token endpoint
   → Receives: access_token, refresh_token, expires_at

4. Backend stores tokens
   → Saved in Supabase (user_strava table)
   → Also saved to tokens.json (local dev fallback only)

5. Frontend receives auth confirmation
   → Can now make authenticated requests
   → Token sent in cookies automatically
```

### Token Refresh

**Auto-refresh:** Backend checks expiration before API calls

```python
def get_valid_token():
    if token_expired:
        refresh_token()
    return access_token
```

### Supabase Auth

**Parallel system:**
- Supabase for user accounts
- Strava for activity data

**Integration:**
- Supabase `user_id` stored with Strava credentials
- Supabase session token passed from frontend
- Backend validates both: Supabase session + Strava token

---

## 🔧 How Features Work Together

### Complete Data Flow Example

**Scenario:** User syncs activities and views leaderboard

```
1. User clicks "Sync Activities"
   ↓
2. Frontend → POST /api/sync
   ↓
3. Backend:
   a. get_valid_token() → Ensures Strava token valid
   b. GET /athlete/activities → Fetch from Strava
   c. StravaParser.parse_activities() → Filter & aggregate
   d. Person.populate_player_activities_by_day() → Build Person object
   e. Person.update_baseline() → Calculate baselines
   f. Badge checking → Award badges
   g. Challenge checking → Award challenges
   h. Streak calculation → Count consecutive days
   i. Score.calculate() → Compute improvement score
   j. save_user_profile() → Save to Supabase user_strava table
   k. save_score() → Save score to Supabase user_strava table
   l. save_activities() → Process activities (stored in Supabase via user profile)
   m. insert_person_response() → Save to Supabase
   ↓
4. Backend → Returns success + summary
   ↓
5. Frontend displays: "Synced 15 activities!"
   ↓
6. User goes to Leaderboard page
   ↓
7. Frontend → GET /api/leaderboard
   ↓
8. Backend:
   a. get_all_scores() → Load all scores from Supabase
   b. get_all_users() → Load all users from Supabase
   c. Sort by improvement score (descending)
   d. Format leaderboard entries
   ↓
9. Backend → Returns ranked list
   ↓
10. Frontend displays leaderboard table
```

---

**Last Updated:** November 24, 2025  
**Status:** All Features Documented ✅

