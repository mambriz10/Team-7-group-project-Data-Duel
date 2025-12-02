"""
Strava Activity Parser
Handles parsing Strava API data and updating Person objects with real activity data
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import Person, Score, etc.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Person import Person


class StravaParser:
    """Utility class for parsing Strava API data"""
    
    @staticmethod
    def create_person_from_athlete(athlete_data):
        """
        Create a Person object from Strava athlete data
        
        Args:
            athlete_data: Athlete info from Strava OAuth response
            
        Returns:
            Person object with basic info populated
        """
        person = Person()
        
        # Set name and username from Strava data
        first_name = athlete_data.get('firstname', '')
        last_name = athlete_data.get('lastname', '')
        full_name = f"{first_name} {last_name}".strip()
        
        person.change_name(full_name if full_name else "Unknown Runner")
        
        # Use Strava username or create from name
        username = athlete_data.get('username')
        if not username:
            username = first_name.lower() if first_name else f"runner{athlete_data.get('id', '')}"
        
        person.change_username(username)
        
        return person
    
    @staticmethod
    def parse_activities(activities_data, person):
        """
        Parse Strava activities and update Person object with metrics
        
        Args:
            activities_data: List of activities from Strava API
            person: Person object to update
            
        Returns:
            Dictionary of aggregated metrics, or None if no running activities
        """
        print(f"      [PARSER] StravaParser.parse_activities() called")
        print(f"         Total activities received: {len(activities_data)}")
        
        # Filter for running activities only
        running_activities = [
            activity for activity in activities_data
            if activity.get('type') in ['Run', 'VirtualRun', 'TrailRun']
        ]
        
        print(f"         Running activities found: {len(running_activities)}")
        if running_activities:
            print(f"         Sample activity types: {[a.get('type') for a in running_activities[:3]]}")
        
        if not running_activities:
            print(f"         [ERROR] No running activities to parse")
            return None
        
        # Reset totals before aggregating
        person.total_workouts = 0
        person.total_distance = 0
        person.total_moving_time = 0
        person.total_average_speed = 0
        person.total_max_speed = 0
        person.total_elevation = 0
        person.average_cadence = 0
        person.average_heartrate = 0
        person.elapsed_time = 0
        
        # Aggregate all running activities
        for activity in running_activities:
            person.total_workouts += 1
            
            # Core metrics (always present)
            distance = activity.get('distance', 0)  # meters
            moving_time = activity.get('moving_time', 0)  # seconds
            average_speed = activity.get('average_speed', 0)  # m/s
            max_speed = activity.get('max_speed', 0)  # m/s
            
            person.total_distance += distance
            person.total_moving_time += moving_time
            person.total_average_speed += average_speed
            person.total_max_speed += max_speed
            
            # Optional metrics (may not be present)
            person.total_elevation += activity.get('total_elevation_gain', 0)
            person.average_cadence += activity.get('average_cadence', 0) or 0
            person.average_heartrate += activity.get('average_heartrate', 0) or 0
            person.elapsed_time += activity.get('elapsed_time', 0) or moving_time
        
        # Calculate baseline averages
        print(f"         [CALC] Calculating baselines...")
        if person.total_workouts > 0:
            person.baseline_average_speed = person.total_average_speed / person.total_workouts
            person.baseline_max_speed = person.total_max_speed / person.total_workouts
            person.baseline_distance = person.total_distance / person.total_workouts
            person.baseline_moving_time = person.total_moving_time / person.total_workouts
            print(f"         [SUCCESS] Baselines calculated:")
            print(f"            Baseline distance: {person.baseline_distance:.0f}m")
            print(f"            Baseline moving time: {person.baseline_moving_time:.0f}s")
            print(f"            Baseline avg speed: {person.baseline_average_speed:.2f}m/s")
            
            # Average optional metrics
            if person.average_cadence > 0:
                person.average_cadence = person.average_cadence / person.total_workouts
            if person.average_heartrate > 0:
                person.average_heartrate = person.average_heartrate / person.total_workouts
            if person.elapsed_time > 0:
                person.elapsed_time = person.elapsed_time / person.total_workouts
            if person.total_elevation > 0:
                person.total_elevation = person.total_elevation / person.total_workouts
        
        # Set current period metrics (same as baseline for now - could be last week only)
        person.average_speed = person.baseline_average_speed
        person.max_speed = person.baseline_max_speed
        person.distance = person.baseline_distance
        person.moving_time = person.baseline_moving_time
        
        return {
            'total_workouts': person.total_workouts,
            'total_distance': person.total_distance,
            'total_moving_time': person.total_moving_time,
            'average_speed': person.average_speed,
            'max_speed': person.max_speed
        }
    
    @staticmethod
    def parse_activities_new(activities_dict, person):
        """
        Parse Strava activities from a weekday-keyed dictionary and update a Person object.
        
        Args:
            activities_dict: Dict with days as keys and list of activities as values
            person: Person instance to update
            
        Returns:
            Aggregated metrics dict or None if no running activities
        """
        # print(activities_dict)

        if not activities_dict or not isinstance(activities_dict, list):
            print("[ERROR] Invalid activities data")
            return None

        # Flatten the dict into a single list of activities
        activities_list = activities_dict

        # Filter for running activities only
        running_activities = [
            activity for activity in activities_list
            if activity.get('type', 'Run') in ['Run', 'VirtualRun', 'TrailRun']  # default 'Run' if no type
        ]

        if not running_activities:
            print("[WARNING] No running activities found")
            return None

        # Reset totals
        person.total_workouts = 0
        person.total_distance = 0
        person.total_moving_time = 0
        person.total_average_speed = 0
        person.total_max_speed = 0
        person.total_elevation = 0
        person.average_cadence = 0
        person.average_heartrate = 0
        person.elapsed_time = 0

        for activity in running_activities:
            person.total_workouts += 1
            distance = activity.get('distance', 0)
            moving_time = activity.get('moving_time', activity.get('elapsed_time', 0))
            average_speed = activity.get('average_speed', 0)
            max_speed = activity.get('max_speed', 0)

            person.total_distance += distance
            person.total_moving_time += moving_time
            person.total_average_speed += average_speed
            person.total_max_speed += max_speed
            person.total_elevation += activity.get('total_elevation_gain', 0)
            person.average_cadence += activity.get('average_cadence', 0) or 0
            person.average_heartrate += activity.get('average_heartrate', 0) or 0
            person.elapsed_time += activity.get('elapsed_time', 0) or moving_time

        # Compute averages
        if person.total_workouts > 0:
            person.baseline_average_speed = person.total_average_speed / person.total_workouts
            person.baseline_max_speed = person.total_max_speed / person.total_workouts
            person.baseline_distance = person.total_distance / person.total_workouts
            person.baseline_moving_time = person.total_moving_time / person.total_workouts
            person.average_cadence /= person.total_workouts
            person.average_heartrate /= person.total_workouts
            person.elapsed_time /= person.total_workouts
            person.total_elevation /= person.total_workouts

        # Current period metrics
        person.average_speed = person.baseline_average_speed
        person.max_speed = person.baseline_max_speed
        person.distance = person.baseline_distance
        person.moving_time = person.baseline_moving_time

        return {
            "total_workouts": person.total_workouts,
            "total_distance": person.total_distance,
            "total_moving_time": person.total_moving_time,
            "average_speed": person.average_speed,
            "max_speed": person.max_speed
        }
    
    @staticmethod
    def calculate_streak(activities_data):
        """
        Calculate consecutive days with activities
        
        Args:
            activities_data: List of activities from Strava API
            
        Returns:
            Number of consecutive days with at least one activity
        """
        if not activities_data:
            return 0
        
        # Extract unique activity dates
        activity_dates = set()
        for activity in activities_data:
            start_date_str = activity.get('start_date_local') or activity.get('start_date')
            if start_date_str:
                # Parse ISO format date
                date_obj = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                activity_dates.add(date_obj.date())
        
        if not activity_dates:
            return 0
        
        # Sort dates in descending order (most recent first)
        sorted_dates = sorted(activity_dates, reverse=True)
        
        # Check if there's an activity today or yesterday
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        if sorted_dates[0] not in [today, yesterday]:
            # Streak is broken if most recent activity is more than 1 day ago
            return 0
        
        # Count consecutive days
        streak = 1
        expected_date = sorted_dates[0] - timedelta(days=1)
        
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            elif sorted_dates[i] < expected_date:
                # Gap found, streak ends
                break
        
        return streak
    
    @staticmethod
    def check_badges(person):
        """
        Check and award badges based on person's metrics
        
        Badges:
        - Moving Time: Average moving time >= 1000 seconds
        - Distance: Average distance >= 5000 meters
        - Max Speed: Max speed >= 4 m/s
        
        Args:
            person: Person object to check badges for
        """
        # Reset badges
        person.badges.moving_time = False
        person.badges.distance = False
        person.badges.max_speed = False
        
        # Moving Time Badge (1000+ seconds average)
        if person.baseline_moving_time >= 1000:
            person.badges.moving_time = True
        
        # Distance Badge (5000+ meters = 5km average)
        if person.baseline_distance >= 5000:
            person.badges.distance = True
        
        # Max Speed Badge (4+ m/s = ~14.4 km/h)
        if person.baseline_max_speed >= 4:
            person.badges.max_speed = True
    
    @staticmethod
    def check_challenges(person, activities_data):
        """
        Check and complete weekly challenges based on recent activities
        
        Challenges:
        1. Run 3+ times this week
        2. Cover 15+ km this week
        3. Maintain 5+ day streak
        
        Args:
            person: Person object to check challenges for
            activities_data: List of activities from Strava API
        """
        # Reset challenges
        person.weekly_challenges.first_challenge = False
        person.weekly_challenges.second_challenge = False
        person.weekly_challenges.third_challenge = False
        
        # Calculate week start (Monday)
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Filter activities from this week
        this_week_activities = []
        this_week_distance = 0
        
        for activity in activities_data:
            start_date_str = activity.get('start_date_local') or activity.get('start_date')
            if start_date_str:
                date_obj = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                
                if date_obj >= week_start:
                    if activity.get('type') in ['Run', 'VirtualRun', 'TrailRun']:
                        this_week_activities.append(activity)
                        this_week_distance += activity.get('distance', 0)
        
        # Challenge 1: 3+ runs this week
        if len(this_week_activities) >= 3:
            person.weekly_challenges.first_challenge = True
        
        # Challenge 2: 15+ km this week
        if this_week_distance >= 15000:  # 15 km in meters
            person.weekly_challenges.second_challenge = True
        
        # Challenge 3: 5+ day streak
        if person.streak >= 5:
            person.weekly_challenges.third_challenge = True

