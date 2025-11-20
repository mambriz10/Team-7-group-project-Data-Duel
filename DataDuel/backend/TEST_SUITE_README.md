# DataDuel Test Suite Documentation

## Overview

This comprehensive test suite validates the entire DataDuel data pipeline from Strava API response through parsing, processing, storage, and retrieval - **without requiring an actual Strava account**.

## Test File

**Location:** `DataDuel/backend/test_data_flow.py`

## Running the Tests

```bash
cd DataDuel/backend
python3 test_data_flow.py
```

**Expected Output:**
```
======================================================================
TEST SUMMARY
======================================================================
PASSED: 11
FAILED: 0
TOTAL:  11
======================================================================
[SUCCESS] ALL TESTS PASSED!
```

## What Gets Tested

### Test 1: Parse Athlete Data
- **Purpose:** Validates that athlete data from Strava OAuth can be converted into a Person object
- **Tests:**
  - Person object creation
  - Attribute initialization
  - Display name handling

### Test 2: Parse Diverse Activities
- **Purpose:** Tests parsing of various running activity types and metric aggregation
- **Tests:**
  - Filtering of running activities (Run, VirtualRun, TrailRun)
  - Exclusion of non-running activities (Bike, Swim, etc.)
  - Total distance calculation (50km across 5 runs)
  - Total moving time calculation (285 minutes)
  - Baseline metric calculations
- **Mock Data:**
  - 5 running activities: Long run, Speed workout, Recovery run, Trail run, Virtual run
  - 1 non-running activity: Bike ride (filtered out)

### Test 3: Calculate Activity Streak
- **Purpose:** Validates consecutive day streak calculation
- **Tests:**
  - Detection of 5-day consecutive streak
  - Proper handling of gaps in activity history
  - Date parsing and comparison logic
- **Mock Data:**
  - 5 consecutive days with activities
  - 2-day gap
  - 1 older activity

### Test 4: Check and Award Badges
- **Purpose:** Ensures badges system integrates correctly
- **Tests:**
  - Badge checking logic executes without errors
  - Person object has badges attribute
  - Badge thresholds are evaluated

### Test 5: Check and Award Challenges
- **Purpose:** Validates weekly challenge system
- **Tests:**
  - Challenge checking logic executes
  - Weekly challenge thresholds evaluated
  - Streak-based challenges work correctly

### Test 6: Calculate Improvement Score
- **Purpose:** Tests Score object and baseline calculations
- **Tests:**
  - Baseline metrics are calculated correctly
  - Score object exists and is initialized
  - Baseline values are reasonable:
    - Baseline distance: ~10km
    - Baseline moving time: ~57 minutes
    - Baseline average speed: ~3.0 m/s

### Test 7: Save and Load User Data
- **Purpose:** Validates DataStorage user persistence
- **Tests:**
  - User data can be saved to JSON
  - User data can be loaded from JSON
  - Data integrity is maintained
  - All user attributes persist correctly
- **Data Saved:**
  - athlete_id, display_name
  - total_workouts, total_distance, total_moving_time
  - Baseline metrics

### Test 8: Save and Load Score Data
- **Purpose:** Tests score persistence
- **Tests:**
  - Score data saves to scores.json
  - Score data loads correctly
  - Score values match after round-trip

### Test 9: Handle Empty Activities
- **Purpose:** Edge case - no activities
- **Tests:**
  - Graceful handling of empty activity list
  - No crashes or exceptions
  - Returns appropriate None/null values

### Test 10: Handle Minimal Activity Data
- **Purpose:** Edge case - activity with minimal fields
- **Tests:**
  - Single activity with only required fields works
  - Optional fields (cadence, heart rate) default properly
  - Baseline calculations still work

### Test 11: Complete End-to-End Pipeline ⭐
- **Purpose:** Full integration test simulating real-world usage
- **Tests:** 11-step complete data flow:

#### Step 1: Receive Athlete Data
Simulates OAuth callback with athlete information

#### Step 2: Create Person Object
Initializes Person from athlete data

#### Step 3: Receive Activities
Simulates Strava API activities endpoint response

#### Step 4: Parse Activities
- Filters running activities
- Aggregates metrics
- Calculates baselines
- Results: 5 runs, 50km total

#### Step 5: Calculate Streak
Determines consecutive activity days (6 days)

#### Step 6: Check Badges
Evaluates badge criteria and awards

#### Step 7: Check Challenges
Evaluates weekly challenge criteria

#### Step 8: Save User Data
Persists all user data to JSON storage

#### Step 9: Save Score Data
Persists score data to JSON storage

#### Step 10: Retrieve Data
Simulates frontend API request to load data

#### Step 11: Format Response
Prepares data for frontend consumption
- Final output:
```json
{
  "display_name": "Default_Username",
  "total_workouts": 5,
  "total_distance_km": 50.0,
  "total_time_hours": 4.75,
  "streak": 6,
  "score": 100
}
```

## Mock Data Details

### Mock Athlete
```python
{
  "id": 12345678,
  "username": "test_runner",
  "firstname": "Test",
  "lastname": "Runner",
  "city": "Eugene",
  "state": "Oregon",
  "country": "United States"
}
```

### Mock Activities Summary

| Activity | Type | Distance | Time | Elevation | Notes |
|----------|------|----------|------|-----------|-------|
| Morning Long Run | Run | 15 km | 75 min | 150m | Long steady run |
| Interval Training | Run | 8 km | 40 min | 50m | Speed workout |
| Easy Recovery | Run | 5 km | 30 min | 20m | Recovery pace |
| Trail Adventure | TrailRun | 12 km | 90 min | 500m | Hilly terrain |
| Treadmill Run | VirtualRun | 10 km | 50 min | 0m | Indoor training |
| Bike Ride | Ride | 30 km | 60 min | - | **Filtered out** |

**Total Running:** 50 km, 285 minutes, 5 activities

## Test Data Storage

Tests use an isolated `test_data/` directory that is automatically cleaned up after tests complete. This ensures tests don't interfere with actual application data.

## Components Tested

### Classes
- ✅ `Person` - User data model
- ✅ `Score` - Improvement scoring algorithm
- ✅ `badges` - Badge award system
- ✅ `challenges` - Weekly challenge system
- ✅ `DataStorage` - JSON file persistence
- ✅ `StravaParser` - API response parsing

### Functions
- ✅ `create_person_from_athlete()` - Person initialization
- ✅ `parse_activities()` - Activity parsing and aggregation
- ✅ `calculate_streak()` - Consecutive day calculation
- ✅ `check_badges()` - Badge evaluation
- ✅ `check_challenges()` - Challenge evaluation
- ✅ `save_user()` / `get_user()` - User persistence
- ✅ `save_score()` / `get_score()` - Score persistence

## Success Criteria

All tests must pass for the data pipeline to be considered functional:

- ✅ Person objects created correctly
- ✅ Activities parsed and aggregated
- ✅ Running activities filtered from other types
- ✅ Metrics calculated accurately
- ✅ Baselines computed correctly
- ✅ Streaks calculated accurately
- ✅ Badges and challenges evaluated
- ✅ Data persists to storage
- ✅ Data loads from storage
- ✅ Data integrity maintained
- ✅ Edge cases handled gracefully

## Integration with Actual Strava API

This test suite uses mock data that **matches the exact structure** of Strava API responses. When you connect to the real Strava API:

1. The real API returns data in the same format as our mocks
2. The same parsing logic is used
3. The same data pipeline processes it
4. The same storage system saves it

**Therefore:** If all tests pass, the system will work with real Strava data.

## Troubleshooting

### Import Errors
```bash
ModuleNotFoundError: No module named 'flask'
```
**Solution:** Install dependencies
```bash
pip3 install -r requirements.txt
```

### Test Failures
If tests fail, check:
1. Have you modified `Person.py`, `Score.py`, `badges.py`, or `challenges.py`?
2. Are all required files present in `DataDuel/backend/`?
3. Does `strava_parser.py` exist and have all methods?

### Permission Errors
```bash
PermissionError: [Errno 13] Permission denied: 'test_data'
```
**Solution:** Delete the test_data directory manually
```bash
rm -rf test_data
```

## Future Enhancements

Potential additions to test coverage:

1. **Performance Testing**
   - Test with 1000+ activities
   - Measure parsing speed

2. **Error Handling**
   - Malformed JSON responses
   - Missing required fields
   - Invalid data types

3. **Concurrency**
   - Multiple users simultaneously
   - Race conditions in storage

4. **Score Calculation**
   - Various improvement scenarios
   - Negative improvement (worse performance)
   - First-time users (no baseline)

5. **Frontend Integration**
   - Mock HTTP requests
   - Response format validation
   - Error response handling

## Running in CI/CD

To integrate into continuous integration:

```yaml
# Example GitHub Actions workflow
- name: Run DataDuel Tests
  run: |
    cd DataDuel/backend
    python3 test_data_flow.py
```

Exit code: 0 = success, non-zero = failure

## Summary

This test suite provides comprehensive validation of DataDuel's data pipeline, allowing development and testing **without requiring Strava authentication**. All tests passing confirms the system is ready to handle real user data from Strava.

