# strava_parser.py
from Person import Person

class StravaParser:
    @staticmethod
    def create_person_from_athlete(athlete_json):
        """
        Create a Person object from Strava athlete JSON
        """
        person = Person()
        person.change_name(athlete_json.get("firstname", "") + " " + athlete_json.get("lastname", ""))
        person.change_username(athlete_json.get("username", athlete_json.get("id", "unknown")))
        person.display_name = athlete_json.get("firstname", "Unknown")
        person.avatar_url = athlete_json.get("profile", "")
        return person

    @staticmethod
    def parse_activities(activities, person):
        """
        Map Strava activities to Person object metrics
        Only simple example: total distance, average speed, total workouts
        """
        total_distance = 0
        total_time = 0
        max_speed = 0
        total_workouts = len(activities)

        for activity in activities:
            # distance in meters
            dist = activity.get("distance", 0)
            total_distance += dist

            # moving time in seconds
            moving_time = activity.get("moving_time", 0)
            total_time += moving_time

            # max speed in m/s
            max_s = activity.get("max_speed", 0)
            if max_s > max_speed:
                max_speed = max_s

        person.total_workouts = total_workouts
        person.total_distance = total_distance
        person.total_moving_time = total_time
        person.average_speed = total_distance / total_time if total_time > 0 else 0
        person.max_speed = max_speed

        return {
            "total_workouts": person.total_workouts,
            "total_distance": person.total_distance,
            "total_moving_time": person.total_moving_time,
            "average_speed": person.average_speed,
            "max_speed": person.max_speed
        }

    @staticmethod
    def calculate_streak(activities):
        """
        Placeholder: calculate consecutive days with activities
        """
        # In a real implementation, you would check activity start dates
        return len(activities)  # simplistic example

    @staticmethod
    def check_badges(person):
        """Placeholder: update badges"""
        person.badges = type("Badges", (), {"get_points": lambda: 0})()

    @staticmethod
    def check_challenges(person, activities):
        """Placeholder: update weekly challenges"""
        person.weekly_challenges = type("Challenges", (), {"get_points": lambda: 0})()
