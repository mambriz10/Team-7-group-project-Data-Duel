# SUBJECT TO CHANGE. This is a main idea, implememntation details will most likely change slightly overtime.

# Assume a person is made when a user first makes an account / connection. Then when they connect to strava, we will
# fill other member variables like the metrics.

# Another way to go is to create this object after a connection to strava has been made and we getc call it with
# data from api call
import Score
import challenges
import badges
import requests
import json


class Person:
    def __init__(self):
        # User Information
        self.__name = "Default_Name"  # used for profile page and possible leaderboard name
        self.__user_name = "Default_Username"  # possible leaderboard name

        self.display_name = self.__user_name  # name for leaderboard

        # data
        self.player_activities_by_day = {}
        # Metrics
        self.average_speed = 1
        self.max_speed = 1
        self.distance = 1
        self.moving_time = 1

        # These 4 are going to be total averages as well, like the 4 total variables below
        self.average_cadence = 0
        self.average_heartrate = 0
        self.elapsed_time = 0
        self.total_elevation = 0

        # Ticked Variables
        self.streak = 0
        self.days_in_league = 0
        self.total_workouts = 1

        # Metrics
        self.total_average_speed = 0
        self.total_max_speed = 0
        self.total_distance = 0
        self.total_moving_time = 0

        self.total_average_cadence = 0
        self.total_average_heartrate = 0
        self.total_elapsed_time = 0
        self.total_elevation = 0

        # Baselines used in score calculation
        self.baseline_average_speed = 1
        self.baseline_max_speed = 1
        self.baseline_distance = 1
        self.baseline_moving_time = 1

        self.baseline_average_cadence = 0
        self.baseline_average_heartrate = 0
        self.baseline_elapsed_time = 0
        self.baseline_elevation = 0

        # Placeholders for future objects
        self.score = Score.Score()
        self.weekly_challenges = challenges.challenges()
        self.badges = badges.badges()  # dummy value, should be like challenges instead.

        self.rank = 0  # will be their index in leaderboard list + 1

    # Setters for user customizable options
    def change_name(self, new_name):
        self.__name = new_name

    def change_username(self, new_user_name):
        self.__user_name = new_user_name

    # Private helper to update totals from currently stored metrics
    def __update_totals_from_args(self, avg_speed, max_speed, distance, moving_time):
        self.total_average_speed += avg_speed
        self.total_max_speed += max_speed
        self.total_distance += distance
        self.total_moving_time += moving_time

    def update_other_metrics(self, cadence, heartrate, elapsed_time, total_elevation_gain):
        if cadence is not None:
            self.average_cadence += cadence
        if heartrate is not None:
            self.average_heartrate += heartrate
        if elapsed_time is not None:
            self.total_elapsed_time += elapsed_time
        if total_elevation_gain is not None:
            self.total_elevation_gain += total_elevation_gain

    # REMEMBER to update workouts += 1 before using this method
    def update_baseline(self):
        self.baseline_average_speed = self.total_average_speed / self.total_workouts
        self.baseline_max_speed = self.total_max_speed / self.total_workouts
        self.baseline_distance = self.total_distance / self.total_workouts
        self.baseline_moving_time = self.total_moving_time / self.total_workouts

        self.average_cadence = self.average_cadence / self.total_workouts
        self.average_heartrate = self.average_heartrate / self.total_workouts
        self.elapsed_time = self.elapsed_time / self.total_workouts
        self.total_elevation = self.total_elevation / self.total_workouts

    # Used in settings to change privacy to change which leaderboard name is shown
    def show_real_name(self, check):
        if check:
            self.display_name = self.__name
        else:
            self.display_name = self.__user_name

    # Adds 1 to total workouts for end of workout easy function call
    def increase_total_workouts(self):
        self.total_workouts += 1

    def populate_player_activities_by_day(self):
        API_URL = "http://127.0.0.1:5000/strava/activities"
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            self.player_activities_by_day = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching activities: {e}")


    def sum_activities(self):
        # If structure is { "Monday": [act1, act2], "Tuesday": [] }
        for day in self.player_activities_by_day.values():
            # print("Found a day")
            for activity in day:
                # print("Found an activity")
                self.total_workouts += 1

                # If structure of acitvity is the JSON response, it should be a Python dictionary
                # If 'key' is missing, it defaults to 0
                self.__update_totals_from_args(
                    activity.get('average_speed', 0),
                    activity.get('max_speed', 0),
                    activity.get('distance', 0),
                    activity.get('moving_time', 0)
                )

                self.update_other_metrics(
                    activity.get('average_cadence', 0),
                    activity.get('average_heartrate', 0), # only works if user has a heart rate from api call
                    activity.get('elapsed_time', 0),
                    activity.get('total_elevation_gain', 0)
                )

        self.update_baseline()

"""
    def sum_activities(self):
        for weekday, activities in self.player_activities_by_day.items():
            print(f"Processing {weekday}...")
            for activity in activities:

                print(f"Found an activity: {activity['name']}")
                self.total_workouts += 1

                # Update totals — access dict keys instead of attributes
                self.__update_totals_from_args(
                    activity.get("average_speed", 0),
                    activity.get("max_speed", 0),
                    activity.get("distance", 0),
                    activity.get("moving_time", 0)
                )

                self.update_other_metrics(
                    activity.get("average_cadence", 0),
                    activity.get("average_heartrate", 0),
                    activity.get("elapsed_time", 0),
                    activity.get("total_elevation_gain", 0)
                )

        self.update_baseline()
"""