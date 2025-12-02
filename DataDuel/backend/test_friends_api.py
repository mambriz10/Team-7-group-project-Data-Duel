"""
Test script for Friends API endpoints
Run this after starting the Flask server to verify friends functionality
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(endpoint, response):
    print(f"\n[{response.status_code}] {endpoint}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)

def test_friends_api():
    print_section("FRIENDS API TEST SUITE")
    print("\nNOTE: You need to be authenticated first!")
    print("1. Open browser and go to http://localhost:5000/auth/strava")
    print("2. Complete authentication")
    print("3. Then run this script\n")
    
    input("Press Enter when ready to test...")
    
    # Test 1: Get current friends (should be empty initially)
    print_section("Test 1: Get Friends List")
    response = requests.get(f"{BASE_URL}/api/friends")
    print_result("GET /api/friends", response)
    
    # Test 2: Get friend requests
    print_section("Test 2: Get Friend Requests")
    response = requests.get(f"{BASE_URL}/api/friends/requests")
    print_result("GET /api/friends/requests", response)
    
    # Test 3: Get sent requests
    print_section("Test 3: Get Sent Requests")
    response = requests.get(f"{BASE_URL}/api/friends/sent")
    print_result("GET /api/friends/sent", response)
    
    # Test 4: Search for users
    print_section("Test 4: Search Users")
    search_query = input("Enter search query (or press Enter to skip): ").strip()
    if search_query:
        response = requests.get(f"{BASE_URL}/api/friends/search?q={search_query}")
        print_result(f"GET /api/friends/search?q={search_query}", response)
    else:
        print("Skipped")
    
    # Test 5: Send friend request (need a real user ID)
    print_section("Test 5: Send Friend Request")
    print("To test this, you need another user's ID")
    friend_id = input("Enter friend user ID (or press Enter to skip): ").strip()
    
    if friend_id:
        response = requests.post(
            f"{BASE_URL}/api/friends/request",
            json={"friend_id": friend_id}
        )
        print_result("POST /api/friends/request", response)
    else:
        print("Skipped")
    
    print_section("TESTS COMPLETE")
    print("\nTo fully test the friends system:")
    print("1. Create 2+ Strava accounts")
    print("2. Authenticate each in the app")
    print("3. Use the frontend to search and add friends")
    print("4. Or use this script with real user IDs")

if __name__ == "__main__":
    try:
        # First check if server is running
        response = requests.get(f"{BASE_URL}/")
        print("✅ Backend server is running!")
        test_friends_api()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Backend server is not running!")
        print(f"   Start it with: cd DataDuel/backend && python app.py")
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

