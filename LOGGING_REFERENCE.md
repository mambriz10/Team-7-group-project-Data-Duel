# Logging Reference

**Added:** November 11, 2025  
**Purpose:** Debug data flow from Strava API to Storage to Frontend

---

## Log Prefixes

| Prefix | Purpose |
|--------|---------|
| `[AUTH]` | Authentication operations |
| `[SYNC]` | Activity sync operations |
| `[STORAGE]` | Data storage operations |
| `[PARSER]` | Data parsing operations |
| `[SUCCESS]` | Successful operations |
| `[ERROR]` | Error conditions |
| `[WARNING]` | Warning conditions |
| `[INFO]` | General information |
| `[API]` | External API calls |
| `[PERSON]` | Person object operations |
| `[REDIRECT]` | Page redirects |

---

## Authentication Flow

```
[AUTH CALLBACK] Starting OAuth token exchange
[AUTH] Authorization code received
[API] Requesting tokens from Strava
[API] Token response status: 200
[SUCCESS] Token exchange successful
[STORAGE] Saving tokens to tokens.json
[SUCCESS] Tokens saved successfully
[PERSON] Creating Person object from athlete data
[SUCCESS] Person object created
[STORAGE] Saving user data to storage
[SUCCESS] User data saved successfully
[REDIRECT] Redirecting to frontend
```

---

## Sync Flow

```
[SYNC] Starting activity sync process
[SUCCESS] Token validated successfully
[API] Fetching activities from Strava API
[API] Strava API response status: 200
[SUCCESS] Fetched X activities from Strava
[STORAGE] Loading user data from storage
[SUCCESS] User data loaded
[PERSON] Creating Person object
[SUCCESS] Person object created
[PARSER] Parsing activities with StravaParser
[SUCCESS] Activities parsed successfully
[SYNC] Calculating streak
[SUCCESS] Streak calculated
[SYNC] Checking badges
[SUCCESS] Badges checked
[SYNC] Checking challenges
[SUCCESS] Challenges checked
[SYNC] Calculating score
[SUCCESS] Score calculated
[STORAGE] Saving data to storage
[SUCCESS] Activities saved
[SUCCESS] User data updated
[SUCCESS] Score data saved
```

---

## Profile Display Flow

```
[PROFILE] Loading profile data
[SUCCESS] Token validated
[STORAGE] Loading user data from storage
[SUCCESS] User data loaded
[STORAGE] Loading score data
[SUCCESS] Score data loaded
[PROFILE] Calculating metrics
[PROFILE] Sending profile response
```

---

## Data Storage Operations

```
[STORAGE] DataStorage.save_user() called
[SUCCESS] User data written to data/users.json

[STORAGE] DataStorage.get_user() called
[SUCCESS] User found

[STORAGE] DataStorage.save_score() called
[SUCCESS] Score data written to data/scores.json

[STORAGE] DataStorage.get_score() called
[SUCCESS] Score found
```

---

## Common Error Patterns

### User Not Found
```
[STORAGE] Loading user data from storage
[ERROR] User not found in storage (ID: 67126670)
```
**Cause:** User wasn't saved during auth  
**Fix:** Check auth callback logs

### No Running Activities
```
[PARSER] Parsing activities with StravaParser
[WARNING] No running activities found in X activities
```
**Cause:** All activities are non-running types  
**Solution:** User needs Run activities

### Missing Metrics
```
[STORAGE] Loading user data from storage
[WARNING] Total workouts: NOT SET
[WARNING] Total distance: NOT SET
```
**Cause:** Sync never completed  
**Fix:** Check sync endpoint logs

---

## Example Full Trace

```
================================================================================
[AUTH CALLBACK] Starting OAuth token exchange
================================================================================
[AUTH] Authorization code received: 1234567890abcdef...
[API] Requesting tokens from Strava...
       Client ID: 123456
[API] Token response status: 200
       Response keys: ['token_type', 'expires_at', 'expires_in', 'refresh_token', 'access_token', 'athlete']
[SUCCESS] Token exchange successful!
          Athlete ID: 67126670
          Athlete name: Daniel Chavez

[STORAGE] Saving tokens to tokens.json...
[SUCCESS] Tokens saved successfully

[PERSON] Creating Person object from athlete data...
[SUCCESS] Person object created:
          Name: Daniel Chavez
          Username: daniel

[STORAGE] Saving user data to storage...
          User ID: 67126670
          User data keys: ['id', 'name', 'username', 'display_name', 'avatar', 'location', 'strava_id']
[STORAGE] DataStorage.save_user() called
          User ID: 67126670
          User data keys: ['id', 'name', 'username', 'display_name', 'avatar', 'location', 'strava_id']
          Existing users in storage: []
[SUCCESS] User data written to data/users.json
          Total users in storage: 1
[SUCCESS] User data saved successfully

[REDIRECT] Redirecting to frontend...
================================================================================
```

---

## How to Use

1. Start backend: `cd DataDuel/backend && python app.py`
2. Watch console output during:
   - Strava authentication
   - Activity sync
   - Profile viewing
3. Look for `[ERROR]` and `[WARNING]` messages
4. Trace data flow through `[STORAGE]` operations
5. Verify calculations in `[PARSER]` output

---

## Debugging Tips

- Look for mismatches between saved and retrieved data
- Check if all expected keys are present in storage operations
- Verify numeric values are non-zero after sync
- Ensure user exists before sync operation
- Confirm activities are being filtered correctly (Run vs other types)

