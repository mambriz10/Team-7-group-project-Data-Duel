# How app.py Works - Complete Guide

## What is app.py?

`app.py` is your **Flask web server** - it's the backend that runs continuously and handles all HTTP requests from your frontend. Think of it as the "brain" of your application that processes data and communicates with Strava.

---

## Execution Flow

### 1. Starting the Server

```bash
cd DataDuel/backend
python app.py
```

When you run this command, Python executes `app.py` line by line:

```python
# Lines 1-18: Import all dependencies
from flask import Flask, redirect, request, jsonify
from data_storage import DataStorage
from Person import Person
# ... etc

# Line 20: Load environment variables from .env file
load_dotenv()

# Line 22: Create Flask application instance
app = Flask(__name__)

# Line 24: Enable CORS (allow frontend to communicate)
CORS(app, origins="http://localhost:5500")

# Line 27: Initialize data storage system
storage = DataStorage()

# Lines 30-33: Load Strava API credentials
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Lines 688-689: Start the web server
if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

**Result:** Server starts listening at `http://localhost:5000`

---

## How It Processes Requests

### Step-by-Step Request Handling

```
1. Frontend makes request
   ↓
2. Request arrives at localhost:5000
   ↓
3. Flask routes request to appropriate function
   ↓
4. Function processes data
   ↓
5. Function returns response
   ↓
6. Frontend receives data
```

### Example: User Clicks "Sync Activities"

**Frontend JavaScript:**
```javascript
// In frontend/index.html
document.getElementById('syncBtn').addEventListener('click', async () => {
    const result = await api.syncActivities();  // Calls /api/sync
});
```

**What Happens:**

1. **Browser sends HTTP POST request:**
   ```
   POST http://localhost:5000/api/sync
   ```

2. **Flask receives request and routes it:**
   ```python
   @app.route("/api/sync", methods=["POST", "GET"])
   def sync_data():
       # This function gets called
   ```

3. **Function executes:**
   ```python
   # Validate token
   access_token, athlete_id = get_valid_token()
   
   # Fetch from Strava
   response = requests.get("https://www.strava.com/api/v3/athlete/activities", ...)
   
   # Parse activities
   metrics = StravaParser.parse_activities(activities, person)
   
   # Calculate score
   person.score.calculate_score(...)
   
   # Save to storage
   storage.save_user(athlete_id, user_data)
   
   # Return response
   return jsonify({"message": "Sync successful!", "metrics": {...}})
   ```

4. **Browser receives JSON response:**
   ```json
   {
     "message": "Sync successful!",
     "metrics": {
       "total_workouts": 15,
       "total_distance_km": 75.0,
       "score": 150
     }
   }
   ```

5. **Frontend displays success message**

---

## All Routes (Endpoints) in app.py

### Authentication Routes
| Route | Method | Purpose | Called When |
|-------|--------|---------|-------------|
| `/auth/strava` | GET | Redirects to Strava OAuth | User clicks "Connect Strava" |
| `/auth/strava/callback` | GET | Handles OAuth return | Strava redirects back after auth |

### Data Routes
| Route | Method | Purpose | Called When |
|-------|--------|---------|-------------|
| `/api/sync` | POST | Syncs activities from Strava | User clicks "Sync Activities" |
| `/api/profile` | GET | Gets user profile data | User opens profile page |
| `/api/leaderboard` | GET | Gets leaderboard data | User opens leaderboard page |
| `/api/friends` | GET | Gets friends list | User opens social page |
| `/strava/activities` | GET | Gets raw Strava activities | Direct activity viewing |
| `/api/status` | GET | Checks auth status | Page load on index.html |

### Route Routes
| Route | Method | Purpose | Called When |
|-------|--------|---------|-------------|
| `/api/routes/all` | GET | Gets all routes | User opens routes page |
| `/api/routes/search` | GET/POST | Searches for routes | User filters routes |
| `/api/routes/<id>` | GET | Gets specific route | User clicks route details |
| `/api/routes/generate` | POST | Generates custom route | User creates route |

---

## Route Decorators Explained

```python
@app.route("/api/profile")
def get_profile():
    # function code
```

**What `@app.route()` does:**
- Tells Flask: "When a request comes to `/api/profile`, call `get_profile()`"
- It's like registering a phone number - Flask knows which function to "call" for each URL

**Multiple Methods:**
```python
@app.route("/api/sync", methods=["POST", "GET"])
def sync_data():
    # Handles both POST and GET requests
```

---

## Complete User Journey Through app.py

### Journey 1: Authentication

```
1. User opens frontend (index.html)
   ↓
2. JavaScript calls: GET /api/status
   ↓
3. app.py checks for tokens.json
   ↓
4. Returns: {"authenticated": false}
   ↓
5. User clicks "Connect Strava"
   ↓
6. Browser navigates to: GET /auth/strava
   ↓
7. app.py redirects to: https://www.strava.com/oauth/authorize
   ↓
8. User authorizes on Strava
   ↓
9. Strava redirects to: GET /auth/strava/callback?code=ABC123
   ↓
10. app.py:
    - Exchanges code for access token
    - Saves to tokens.json
    - Creates Person object
    - Saves user to data/users.json
   ↓
11. app.py redirects to: http://localhost:5500/index.html
   ↓
12. User is now authenticated!
```

### Journey 2: Sync Activities

```
1. User clicks "Sync Activities" button
   ↓
2. JavaScript calls: POST /api/sync
   ↓
3. app.py executes sync_data():
   - Loads token from tokens.json
   - Calls Strava API: GET /athlete/activities
   - Receives 30 activities
   - Filters for Run activities
   - Creates Person object
   - Calls StravaParser.parse_activities()
   - Calculates metrics, badges, challenges, score
   - Saves to:
     * data/activities.json
     * data/users.json (updated with metrics)
     * data/scores.json
   ↓
4. app.py returns metrics JSON
   ↓
5. Frontend displays "Sync successful!"
```

### Journey 3: View Profile

```
1. User opens profile.html
   ↓
2. JavaScript calls: GET /api/profile
   ↓
3. app.py executes get_profile():
   - Loads token from tokens.json
   - Gets athlete_id
   - Loads user data from data/users.json
   - Loads score data from data/scores.json
   - Calculates pace
   - Formats response
   ↓
4. app.py returns profile JSON:
   {
     "name": "Daniel Chavez",
     "stats": {
       "runs": 15,
       "distance_km": 75.0,
       "avg_pace": 6.2,
       "score": 150
     }
   }
   ↓
5. Frontend displays profile with all stats
```

---

## Key Components in app.py

### 1. Flask Application Object
```python
app = Flask(__name__)
```
- The main application instance
- All routes are registered to this object

### 2. CORS Configuration
```python
CORS(app, origins="http://localhost:5500")
```
- Allows frontend (port 5500) to communicate with backend (port 5000)
- Without this, browser blocks requests (security policy)

### 3. Data Storage Instance
```python
storage = DataStorage()
```
- Created once when server starts
- Used by all routes to read/write data
- Manages data/users.json, data/scores.json, data/activities.json

### 4. Environment Variables
```python
load_dotenv()
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
```
- Loads credentials from .env file
- Keeps API keys secure (not in code)

---

## When Does app.py Run?

### Runs Continuously
- **Start:** When you execute `python app.py`
- **Stops:** When you press Ctrl+C or close terminal
- **While Running:** Waits for HTTP requests and processes them

### Does NOT Run
- ❌ When you just open frontend files in browser
- ❌ After responding to a request (it keeps running)
- ❌ When frontend is closed (independent process)

---

## Why Flask?

**Flask is a web framework that:**
1. **Listens** for HTTP requests on port 5000
2. **Routes** requests to the right Python function
3. **Processes** data using your Python classes (Person, Score, etc.)
4. **Returns** JSON responses to frontend
5. **Handles** errors and logging

**Without Flask, you would need to:**
- Manually parse HTTP requests
- Handle TCP/IP connections
- Format HTTP responses
- Route URLs yourself
- Much more complex!

---

## app.py vs frontend

| Aspect | app.py (Backend) | frontend files |
|--------|------------------|----------------|
| **Language** | Python | JavaScript/HTML/CSS |
| **Runs** | As a server process | In user's browser |
| **Purpose** | Process data, call APIs | Display UI, handle clicks |
| **Started by** | `python app.py` command | Opening HTML file |
| **Stops when** | You press Ctrl+C | Close browser tab |
| **Can access** | Strava API, files, database | Only what backend sends |

---

## Debugging app.py

### See It In Action
```bash
# Terminal 1: Start server
cd DataDuel/backend
python app.py

# Watch console output:
[AUTH] Starting OAuth token exchange
[SUCCESS] Token exchange successful
[SYNC] Starting activity sync process
[SUCCESS] Activities parsed successfully
```

### Test Endpoints Directly
```bash
# Check server is running
curl http://localhost:5000/

# Check auth status
curl http://localhost:5000/api/status
```

---

## Summary

**app.py is:**
- ✓ A Python web server using Flask
- ✓ Running continuously when started
- ✓ Listening for HTTP requests on port 5000
- ✓ Processing data and calling Strava API
- ✓ Managing data storage (JSON files)
- ✓ Responding with JSON data

**It does NOT:**
- ✗ Display anything in a browser itself
- ✗ Run automatically when you open frontend
- ✗ Store data permanently (uses JSON files)
- ✗ Have a GUI of its own

**Think of it as:**
- Your frontend (HTML) = Restaurant customer
- app.py (Flask) = Kitchen
- Strava API = Grocery supplier
- Routes (@app.route) = Menu items
- Functions = Recipes
- JSON responses = Plated food delivered to customer

