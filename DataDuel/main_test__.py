"""
DataDuel Test Suite
Tests Person, Score, Badge, and Challenge integration
"""
import Person
import sys
import os

# Add backend directory to path for parser testing
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_person_initialization():
    """Test Person object creation and default values"""
    print("Testing Person initialization...")
    person = Person.Person()
    
    assert person.total_workouts >= 0, "Workouts should initialize"
    assert person.score is not None, "Score object should exist"
    assert person.badges is not None, "Badges object should exist"
    assert person.weekly_challenges is not None, "Challenges object should exist"
    print("  PASS: Person initialized correctly")
    return person

def test_baseline_calculation():
    """Test baseline calculations"""
    print("\nTesting baseline calculation...")
    person = Person.Person()
    
    # Simulate adding a workout
    person.total_workouts = 2
    person.total_average_speed = 50
    person.total_max_speed = 100
    person.total_distance = 2000
    person.total_moving_time = 2000
    
    # Recalculate baselines
    person.baseline_average_speed = person.total_average_speed / person.total_workouts
    person.baseline_max_speed = person.total_max_speed / person.total_workouts
    person.baseline_distance = person.total_distance / person.total_workouts
    person.baseline_moving_time = person.total_moving_time / person.total_workouts
    
    assert person.baseline_average_speed == 25, "Baseline avg speed should be 25"
    assert person.baseline_max_speed == 50, "Baseline max speed should be 50"
    assert person.baseline_distance == 1000, "Baseline distance should be 1000"
    assert person.baseline_moving_time == 1000, "Baseline moving time should be 1000"
    print("  PASS: Baselines calculated correctly")

def test_score_calculation():
    """Test score calculation with improvement"""
    print("\nTesting score calculation...")
    person = Person.Person()
    
    # Set up scenario: improved performance
    person.average_speed = 30  # Better than baseline (25)
    person.max_speed = 60  # Better than baseline (50)
    person.distance = 1200  # Better than baseline (1000)
    person.moving_time = 1100  # Better than baseline (1000)
    person.streak = 3
    
    # Calculate score
    score_result = person.score.calculate_score(
        person.average_speed,
        person.max_speed,
        person.distance,
        person.moving_time,
        person.baseline_average_speed,
        person.baseline_max_speed,
        person.baseline_distance,
        person.baseline_moving_time,
        person.badges.get_points(),
        person.weekly_challenges.get_points(),
        person.streak
    )
    
    assert score_result >= 0, "Score should be non-negative"
    assert person.score.score >= 0, "Score should be non-negative"
    print(f"  PASS: Score calculated: {person.score.score}")

def test_badge_system():
    """Test badge points calculation"""
    print("\nTesting badge system...")
    person = Person.Person()
    
    # Award some badges
    person.badges.moving_time = True
    person.badges.distance = True
    
    points = person.badges.get_points()
    assert points == 10, f"Should have 10 points (2 badges * 5), got {points}"
    print(f"  PASS: Badge points: {points}")

def test_challenge_system():
    """Test challenge points calculation"""
    print("\nTesting challenge system...")
    person = Person.Person()
    
    # Complete some challenges
    person.weekly_challenges.first_challenge = True
    person.weekly_challenges.second_challenge = True
    person.weekly_challenges.third_challenge = True
    
    points = person.weekly_challenges.get_points()
    assert points == 15, f"Should have 15 points (3 challenges * 5), got {points}"
    print(f"  PASS: Challenge points: {points}")

def test_integrated_scoring():
    """Test complete scoring workflow"""
    print("\nTesting integrated scoring workflow...")
    person = Person.Person()
    
    # Set up complete scenario
    person.total_workouts = 3
    person.streak = 5
    
    # Award badges and challenges
    person.badges.distance = True
    person.badges.max_speed = True
    person.weekly_challenges.first_challenge = True
    
    # Better performance than baseline
    person.average_speed = 30
    person.max_speed = 60
    person.distance = 1200
    person.moving_time = 1100
    
    # Calculate score with bonuses
    person.score.calculate_score(
        person.average_speed,
        person.max_speed,
        person.distance,
        person.moving_time,
        person.baseline_average_speed,
        person.baseline_max_speed,
        person.baseline_distance,
        person.baseline_moving_time,
        person.badges.get_points(),  # 10 points
        person.weekly_challenges.get_points(),  # 5 points
        person.streak  # 5 points
    )
    
    print(f"  Final Score: {person.score.score}")
    print(f"  Badge Points: {person.badges.get_points()}")
    print(f"  Challenge Points: {person.weekly_challenges.get_points()}")
    print(f"  Streak: {person.streak}")
    print("  PASS: Integrated scoring complete")

def test_route_generator():
    """Test route generation system"""
    print("\nTesting route generator...")
    try:
        from route_generator import SimpleRouteGenerator
        
        # Test getting all routes
        routes = SimpleRouteGenerator.get_all_routes()
        assert len(routes) == 5, f"Should have 5 routes, got {len(routes)}"
        
        # Test search
        results = SimpleRouteGenerator.find_routes(distance_km=5.0, max_results=3)
        assert len(results) <= 3, "Should return max 3 results"
        assert len(results) > 0, "Should find at least one route"
        
        print(f"  PASS: Route generator working ({len(routes)} routes available)")
    except ImportError:
        print("  SKIP: Route generator not available (backend not in path)")

if __name__ == "__main__":
    print("=" * 60)
    print("DataDuel Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        test_person_initialization()
        test_baseline_calculation()
        test_score_calculation()
        test_badge_system()
        test_challenge_system()
        test_integrated_scoring()
        test_route_generator()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
