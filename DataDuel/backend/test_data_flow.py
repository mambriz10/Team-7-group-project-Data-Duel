"""
DataDuel - Comprehensive Data Flow Test Suite

This test suite validates the entire data pipeline from Strava API response
through parsing, processing, storage, and retrieval.

Run with: python3 test_data_flow.py
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Person import Person
from Score import Score
from badges import badges
from challenges import challenges
from data_storage import DataStorage
from strava_parser import StravaParser


class TestDataFlow:
    """Comprehensive test suite for DataDuel data pipeline"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_storage = DataStorage(data_dir="test_data")
        
    def log_test(self, test_name, passed, message=""):
        """Log test results"""
        if passed:
            self.passed += 1
            print(f"[PASS] {test_name}")
            if message:
                print(f"  Detail: {message}")
        else:
            self.failed += 1
            print(f"[FAIL] {test_name}")
            if message:
                print(f"  Error: {message}")
        print()
    
    def cleanup_test_data(self):
        """Clean up test data files"""
        import shutil
        if os.path.exists("test_data"):
            shutil.rmtree("test_data")
        print("[CLEANUP] Test data directory removed\n")
    
    # ==================== MOCK DATA ====================
    
    @staticmethod
    def get_mock_athlete_data():
        """Returns mock athlete data as it would come from Strava API"""
        return {
            "id": 12345678,
            "username": "test_runner",
            "firstname": "Test",
            "lastname": "Runner",
            "profile": "https://dgalywyr863hv.cloudfront.net/pictures/athletes/12345678/test.jpg",
            "city": "Eugene",
            "state": "Oregon",
            "country": "United States"
        }
    
    @staticmethod
    def get_mock_activities_diverse():
        """Returns diverse set of mock activities for comprehensive testing"""
        base_date = datetime.now()
        
        return [
            # Activity 1: Long run
            {
                "id": 1001,
                "name": "Morning Long Run",
                "type": "Run",
                "start_date": (base_date - timedelta(days=0)).isoformat(),
                "distance": 15000.0,  # 15 km
                "moving_time": 4500,  # 75 minutes
                "elapsed_time": 4800,
                "total_elevation_gain": 150.0,
                "average_speed": 3.33,
                "max_speed": 5.0,
                "average_cadence": 168.0,
                "average_heartrate": 155.0
            },
            # Activity 2: Speed workout
            {
                "id": 1002,
                "name": "Interval Training",
                "type": "Run",
                "start_date": (base_date - timedelta(days=1)).isoformat(),
                "distance": 8000.0,
                "moving_time": 2400,
                "average_speed": 3.33,
                "max_speed": 6.0,
                "average_cadence": 180.0,
                "average_heartrate": 165.0
            },
            # Activity 3: Easy recovery run
            {
                "id": 1003,
                "name": "Easy Recovery",
                "type": "Run",
                "start_date": (base_date - timedelta(days=2)).isoformat(),
                "distance": 5000.0,
                "moving_time": 1800,
                "average_speed": 2.78,
                "max_speed": 3.5
            },
            # Activity 4: Trail run
            {
                "id": 1004,
                "name": "Trail Adventure",
                "type": "TrailRun",
                "start_date": (base_date - timedelta(days=3)).isoformat(),
                "distance": 12000.0,
                "moving_time": 5400,
                "total_elevation_gain": 500.0,
                "average_speed": 2.22,
                "max_speed": 4.0
            },
            # Activity 5: Virtual run
            {
                "id": 1005,
                "name": "Treadmill Run",
                "type": "VirtualRun",
                "start_date": (base_date - timedelta(days=4)).isoformat(),
                "distance": 10000.0,
                "moving_time": 3000,
                "average_speed": 3.33,
                "max_speed": 4.5
            },
            # Activity 6: Not a run (should be filtered out)
            {
                "id": 2001,
                "name": "Bike Ride",
                "type": "Ride",
                "start_date": (base_date - timedelta(days=5)).isoformat(),
                "distance": 30000.0,
                "moving_time": 3600
            }
        ]
    
    @staticmethod
    def get_mock_activities_streak():
        """Returns activities designed to test streak calculation"""
        base_date = datetime.now()
        
        return [
            {"id": 3001, "type": "Run", "start_date": (base_date - timedelta(days=0)).isoformat(), "distance": 5000.0, "moving_time": 1800},
            {"id": 3002, "type": "Run", "start_date": (base_date - timedelta(days=1)).isoformat(), "distance": 5000.0, "moving_time": 1800},
            {"id": 3003, "type": "Run", "start_date": (base_date - timedelta(days=2)).isoformat(), "distance": 5000.0, "moving_time": 1800},
            {"id": 3004, "type": "Run", "start_date": (base_date - timedelta(days=3)).isoformat(), "distance": 5000.0, "moving_time": 1800},
            {"id": 3005, "type": "Run", "start_date": (base_date - timedelta(days=4)).isoformat(), "distance": 5000.0, "moving_time": 1800},
            # Gap of 2 days
            {"id": 3006, "type": "Run", "start_date": (base_date - timedelta(days=7)).isoformat(), "distance": 5000.0, "moving_time": 1800}
        ]
    
    @staticmethod
    def get_mock_activities_empty():
        """Returns empty activities list"""
        return []
    
    @staticmethod
    def get_mock_activities_minimal():
        """Returns single minimal activity"""
        return [
            {
                "id": 4001,
                "name": "Single Run",
                "type": "Run",
                "start_date": datetime.now().isoformat(),
                "distance": 5000.0,
                "moving_time": 1800
            }
        ]
    
    # ==================== TEST CASES ====================
    
    def test_1_parse_athlete_data(self):
        """Test 1: Parse athlete data and create Person object"""
        print("="*70)
        print("TEST 1: Parse Athlete Data")
        print("="*70)
        
        athlete_data = self.get_mock_athlete_data()
        print(f"Input: Athlete ID {athlete_data['id']}, Name: {athlete_data['firstname']} {athlete_data['lastname']}")
        
        try:
            person = StravaParser.create_person_from_athlete(athlete_data)
            
            # Validate Person object was created
            assert person is not None, "Person object is None"
            assert hasattr(person, 'total_workouts'), "Person missing total_workouts"
            assert hasattr(person, 'total_distance'), "Person missing total_distance"
            assert hasattr(person, 'display_name'), "Person missing display_name"
            assert person.display_name is not None, "Display name is None"
            
            self.log_test(
                "Parse Athlete Data",
                True,
                f"Person created successfully"
            )
            return person
            
        except Exception as e:
            self.log_test("Parse Athlete Data", False, str(e))
            return None
    
    def test_2_parse_diverse_activities(self):
        """Test 2: Parse diverse set of activities and calculate metrics"""
        print("="*70)
        print("TEST 2: Parse Diverse Activities")
        print("="*70)
        
        athlete_data = self.get_mock_athlete_data()
        activities = self.get_mock_activities_diverse()
        print(f"Input: {len(activities)} activities (including 1 non-run)")
        
        try:
            person = StravaParser.create_person_from_athlete(athlete_data)
            metrics = StravaParser.parse_activities(activities, person)
            
            # Validate filtering (should have 5 runs, not 6 activities)
            assert person.total_workouts == 5, f"Expected 5 runs, got {person.total_workouts}"
            
            # Validate distance calculation (15+8+5+12+10 = 50 km = 50000m)
            expected_distance = 50000.0
            assert abs(person.total_distance - expected_distance) < 100, \
                f"Distance mismatch: expected ~{expected_distance}m, got {person.total_distance}m"
            
            # Validate moving time
            expected_time = 17100  # 4500+2400+1800+5400+3000 seconds
            assert abs(person.total_moving_time - expected_time) < 100, \
                f"Time mismatch: expected ~{expected_time}s, got {person.total_moving_time}s"
            
            # Validate baselines were calculated
            assert person.baseline_distance > 0, "Baseline distance not calculated"
            assert person.baseline_moving_time > 0, "Baseline moving time not calculated"
            
            self.log_test(
                "Parse Diverse Activities",
                True,
                f"Runs: {person.total_workouts}, Distance: {person.total_distance/1000:.1f}km, " +
                f"Time: {person.total_moving_time/60:.0f}min"
            )
            return person
            
        except Exception as e:
            self.log_test("Parse Diverse Activities", False, str(e))
            import traceback
            traceback.print_exc()
            return None
    
    def test_3_calculate_streak(self):
        """Test 3: Calculate activity streak"""
        print("="*70)
        print("TEST 3: Calculate Activity Streak")
        print("="*70)
        
        activities = self.get_mock_activities_streak()
        print(f"Input: {len(activities)} activities over multiple days with gap")
        
        try:
            streak = StravaParser.calculate_streak(activities)
            
            # Should detect 5-day consecutive streak
            expected_streak = 5
            assert streak == expected_streak, \
                f"Streak mismatch: expected {expected_streak} days, got {streak} days"
            
            self.log_test(
                "Calculate Activity Streak",
                True,
                f"Detected {streak}-day consecutive streak"
            )
            return streak
            
        except Exception as e:
            self.log_test("Calculate Activity Streak", False, str(e))
            return None
    
    def test_4_check_badges(self):
        """Test 4: Check and award badges"""
        print("="*70)
        print("TEST 4: Check and Award Badges")
        print("="*70)
        
        athlete_data = self.get_mock_athlete_data()
        activities = self.get_mock_activities_diverse()
        
        try:
            person = StravaParser.create_person_from_athlete(athlete_data)
            StravaParser.parse_activities(activities, person)
            StravaParser.check_badges(person)
            
            # Check if badges object exists
            assert hasattr(person, 'badges'), "Person object missing badges attribute"
            assert person.badges is not None, "Badges is None"
            
            self.log_test(
                "Check and Award Badges",
                True,
                f"Badges checked successfully"
            )
            return person
            
        except Exception as e:
            self.log_test("Check and Award Badges", False, str(e))
            import traceback
            traceback.print_exc()
            return None
    
    def test_5_check_challenges(self):
        """Test 5: Check and award challenges"""
        print("="*70)
        print("TEST 5: Check and Award Challenges")
        print("="*70)
        
        athlete_data = self.get_mock_athlete_data()
        activities = self.get_mock_activities_diverse()
        
        try:
            person = StravaParser.create_person_from_athlete(athlete_data)
            StravaParser.parse_activities(activities, person)
            
            # Calculate streak for challenge checking
            person.streak = StravaParser.calculate_streak(activities)
            
            StravaParser.check_challenges(person, activities)
            
            # Check if challenges object exists
            assert hasattr(person, 'weekly_challenges'), "Person object missing weekly_challenges attribute"
            assert person.weekly_challenges is not None, "Challenges is None"
            
            self.log_test(
                "Check and Award Challenges",
                True,
                f"Challenges checked successfully"
            )
            return person
            
        except Exception as e:
            self.log_test("Check and Award Challenges", False, str(e))
            import traceback
            traceback.print_exc()
            return None
    
    def test_6_calculate_score(self):
        """Test 6: Calculate improvement score"""
        print("="*70)
        print("TEST 6: Calculate Improvement Score")
        print("="*70)
        
        athlete_data = self.get_mock_athlete_data()
        activities = self.get_mock_activities_diverse()
        
        try:
            person = StravaParser.create_person_from_athlete(athlete_data)
            StravaParser.parse_activities(activities, person)
            
            # Check that baseline values were set
            assert person.baseline_moving_time > 0, "Baseline moving time not set"
            assert person.baseline_distance > 0, "Baseline distance not set"
            assert person.baseline_average_speed > 0, "Baseline average speed not set"
            
            # Score object should exist
            assert hasattr(person, 'score'), "Person missing score object"
            assert person.score is not None, "Score object is None"
            
            print(f"Baseline moving time: {person.baseline_moving_time:.0f}s")
            print(f"Baseline distance: {person.baseline_distance/1000:.1f}km")
            print(f"Baseline avg speed: {person.baseline_average_speed:.2f}m/s")
            
            self.log_test(
                "Calculate Improvement Score",
                True,
                "Score object exists and baselines calculated"
            )
            return person.score
            
        except Exception as e:
            self.log_test("Calculate Improvement Score", False, str(e))
            import traceback
            traceback.print_exc()
            return None
    
    def test_7_save_and_load_user(self):
        """Test 7: Save and load user data from storage"""
        print("="*70)
        print("TEST 7: Save and Load User Data")
        print("="*70)
        
        athlete_data = self.get_mock_athlete_data()
        activities = self.get_mock_activities_diverse()
        
        try:
            # Create and process person
            person = StravaParser.create_person_from_athlete(athlete_data)
            StravaParser.parse_activities(activities, person)
            
            athlete_id = str(athlete_data['id'])
            
            # Save to storage
            user_data = {
                "athlete_id": athlete_id,
                "display_name": person.display_name,
                "total_workouts": person.total_workouts,
                "total_distance": person.total_distance,
                "total_moving_time": person.total_moving_time,
                "baseline_distance": person.baseline_distance,
                "baseline_moving_time": person.baseline_moving_time,
                "baseline_average_speed": person.baseline_average_speed
            }
            
            self.test_storage.save_user(athlete_id, user_data)
            print(f"Saved user data for athlete {athlete_id}")
            
            # Load from storage
            loaded_data = self.test_storage.get_user(athlete_id)
            
            # Validate loaded data
            assert loaded_data is not None, "Failed to load user data"
            assert loaded_data['athlete_id'] == athlete_id, "Athlete ID mismatch"
            assert loaded_data['total_workouts'] == person.total_workouts, "Workouts mismatch"
            
            print(f"Loaded user data: {loaded_data['display_name']}, {loaded_data['total_workouts']} runs")
            
            self.log_test(
                "Save and Load User Data",
                True,
                f"Successfully saved and loaded data"
            )
            return loaded_data
            
        except Exception as e:
            self.log_test("Save and Load User Data", False, str(e))
            import traceback
            traceback.print_exc()
            return None
    
    def test_8_save_and_load_score(self):
        """Test 8: Save and load score data from storage"""
        print("="*70)
        print("TEST 8: Save and Load Score Data")
        print("="*70)
        
        athlete_id = "12345678"
        
        try:
            # Create score data
            score_data = {
                "athlete_id": athlete_id,
                "total_score": 150,
                "last_calculated": datetime.now().isoformat()
            }
            
            # Save score
            self.test_storage.save_score(athlete_id, score_data)
            print(f"Saved score data: {score_data['total_score']} points")
            
            # Load score
            loaded_score = self.test_storage.get_score(athlete_id)
            
            # Validate
            assert loaded_score is not None, "Failed to load score"
            assert loaded_score['total_score'] == score_data['total_score'], "Score mismatch"
            
            self.log_test(
                "Save and Load Score Data",
                True,
                f"Score: {loaded_score['total_score']} points"
            )
            return loaded_score
            
        except Exception as e:
            self.log_test("Save and Load Score Data", False, str(e))
            return None
    
    def test_9_empty_activities(self):
        """Test 9: Handle empty activities gracefully"""
        print("="*70)
        print("TEST 9: Handle Empty Activities")
        print("="*70)
        
        athlete_data = self.get_mock_athlete_data()
        activities = self.get_mock_activities_empty()
        print("Input: Empty activities list")
        
        try:
            person = StravaParser.create_person_from_athlete(athlete_data)
            result = StravaParser.parse_activities(activities, person)
            
            # Should return None for empty activities
            assert result is None, "Expected None result for empty activities"
            
            self.log_test(
                "Handle Empty Activities",
                True,
                "Correctly handled empty activities list"
            )
            return True
            
        except Exception as e:
            self.log_test("Handle Empty Activities", False, str(e))
            return False
    
    def test_10_minimal_activity(self):
        """Test 10: Handle minimal activity data"""
        print("="*70)
        print("TEST 10: Handle Minimal Activity Data")
        print("="*70)
        
        athlete_data = self.get_mock_athlete_data()
        activities = self.get_mock_activities_minimal()
        print("Input: Single activity with minimal fields")
        
        try:
            person = StravaParser.create_person_from_athlete(athlete_data)
            metrics = StravaParser.parse_activities(activities, person)
            
            # Should have 1 run
            assert person.total_workouts == 1, f"Expected 1 run, got {person.total_workouts}"
            assert person.total_distance == 5000.0, f"Expected 5000m, got {person.total_distance}m"
            
            self.log_test(
                "Handle Minimal Activity Data",
                True,
                "Correctly parsed minimal activity"
            )
            return True
            
        except Exception as e:
            self.log_test("Handle Minimal Activity Data", False, str(e))
            return False
    
    def test_11_complete_pipeline(self):
        """Test 11: Complete end-to-end data pipeline"""
        print("="*70)
        print("TEST 11: Complete End-to-End Pipeline")
        print("="*70)
        print("This simulates the entire flow from API response to storage retrieval\n")
        
        try:
            # Step 1: Receive athlete data
            print("[STEP 1] Receive athlete data from Strava API")
            athlete_data = self.get_mock_athlete_data()
            athlete_id = str(athlete_data['id'])
            print(f"  -> Athlete: {athlete_data['firstname']} {athlete_data['lastname']}")
            
            # Step 2: Create Person object
            print("[STEP 2] Create Person object")
            person = StravaParser.create_person_from_athlete(athlete_data)
            print(f"  -> Person created")
            
            # Step 3: Fetch activities
            print("[STEP 3] Receive activities from Strava API")
            activities = self.get_mock_activities_diverse()
            print(f"  -> Received {len(activities)} activities")
            
            # Step 4: Parse activities
            print("[STEP 4] Parse activities and calculate metrics")
            metrics = StravaParser.parse_activities(activities, person)
            print(f"  -> Parsed {person.total_workouts} runs, {person.total_distance/1000:.1f}km total")
            
            # Step 5: Calculate streak
            print("[STEP 5] Calculate activity streak")
            person.streak = StravaParser.calculate_streak(activities)
            print(f"  -> Streak: {person.streak} days")
            
            # Step 6: Check badges
            print("[STEP 6] Check and award badges")
            StravaParser.check_badges(person)
            print(f"  -> Badges checked")
            
            # Step 7: Check challenges
            print("[STEP 7] Check and award challenges")
            StravaParser.check_challenges(person, activities)
            print(f"  -> Challenges checked")
            
            # Step 8: Save to storage
            print("[STEP 8] Save user data to storage")
            user_data = {
                "athlete_id": athlete_id,
                "display_name": person.display_name,
                "total_workouts": person.total_workouts,
                "total_distance": person.total_distance,
                "total_moving_time": person.total_moving_time,
                "baseline_distance": person.baseline_distance,
                "baseline_moving_time": person.baseline_moving_time,
                "baseline_average_speed": person.baseline_average_speed,
                "streak": person.streak
            }
            self.test_storage.save_user(athlete_id, user_data)
            print(f"  -> Saved to users.json")
            
            # Step 9: Save score
            print("[STEP 9] Save score data to storage")
            score_data = {
                "athlete_id": athlete_id,
                "total_score": 100,
                "last_calculated": datetime.now().isoformat()
            }
            self.test_storage.save_score(athlete_id, score_data)
            print(f"  -> Saved to scores.json")
            
            # Step 10: Retrieve data
            print("[STEP 10] Retrieve data (simulating frontend API call)")
            loaded_user = self.test_storage.get_user(athlete_id)
            loaded_score = self.test_storage.get_score(athlete_id)
            print(f"  -> User data loaded: {loaded_user['display_name']}")
            print(f"  -> Score data loaded: {loaded_score['total_score']} points")
            
            # Step 11: Format for frontend
            print("[STEP 11] Format response for frontend")
            frontend_response = {
                "display_name": loaded_user['display_name'],
                "total_workouts": loaded_user['total_workouts'],
                "total_distance_km": loaded_user['total_distance'] / 1000,
                "total_time_hours": loaded_user['total_moving_time'] / 3600,
                "streak": loaded_user['streak'],
                "score": loaded_score['total_score']
            }
            print(f"  -> Response ready for frontend\n")
            print("Frontend Response Preview:")
            print(json.dumps(frontend_response, indent=2))
            
            # Validation
            assert loaded_user is not None, "User data not loaded"
            assert loaded_score is not None, "Score data not loaded"
            assert loaded_user['total_workouts'] == person.total_workouts, "Data integrity issue"
            
            self.log_test(
                "Complete End-to-End Pipeline",
                True,
                "All 11 steps completed successfully"
            )
            return True
            
        except Exception as e:
            self.log_test("Complete End-to-End Pipeline", False, str(e))
            import traceback
            traceback.print_exc()
            return False
    
    # ==================== RUN TESTS ====================
    
    def run_all_tests(self):
        """Run all test cases"""
        print("\n")
        print("="*70)
        print(" "*10 + "DataDuel - Data Flow Test Suite")
        print("="*70)
        print("\n")
        
        # Run tests
        self.test_1_parse_athlete_data()
        self.test_2_parse_diverse_activities()
        self.test_3_calculate_streak()
        self.test_4_check_badges()
        self.test_5_check_challenges()
        self.test_6_calculate_score()
        self.test_7_save_and_load_user()
        self.test_8_save_and_load_score()
        self.test_9_empty_activities()
        self.test_10_minimal_activity()
        self.test_11_complete_pipeline()
        
        # Print summary
        print("\n")
        print("="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"PASSED: {self.passed}")
        print(f"FAILED: {self.failed}")
        print(f"TOTAL:  {self.passed + self.failed}")
        print("="*70)
        
        if self.failed == 0:
            print("[SUCCESS] ALL TESTS PASSED!")
        else:
            print(f"[WARNING] {self.failed} TEST(S) FAILED")
        
        print("\n")
        
        # Cleanup
        self.cleanup_test_data()
        
        return self.failed == 0


if __name__ == "__main__":
    print("\nStarting DataDuel Test Suite...")
    print("This will test the complete data pipeline without connecting to Strava.\n")
    
    tester = TestDataFlow()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
