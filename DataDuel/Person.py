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
        self.__name = "Default_Name" # used for profile page and possible leaderboard name
        self.__user_name = "Default_Username" # possible leaderboard name

        self.display_name = self.__user_name # name for leaderboard

        #data
        self.player_activities_by_day = {}
        # Metrics
        self.average_speed = 0
        self.max_speed = 0
        self.distance = 0
        self.moving_time = 0

        # These 4 are going to be total averages as well, like the 4 total variables below
        self.average_cadence = 0
        self.average_heartrate = 0
        self.elapsed_time = 0
        self.total_elevation = 0

        # Ticked Variables
        self.streak = 0
        self.days_in_league = 0
        self.total_workouts = 0

        self.total_average_speed = self.average_speed
        self.total_max_speed = self.max_speed
        self.total_distance = self.distance
        self.total_moving_time = self.moving_time

        # Baselines used in score calculation
        self.baseline_average_speed = 0
        self.baseline_max_speed = 0
        self.baseline_distance = 0
        self.baseline_moving_time = 0

        # Placeholders for future objects
        self.score = Score.Score()
        self.weekly_challenges = challenges.challenges()
        self.badges = badges.badges() # dummy value, should be like challenges instead.

        self.rank = 0 # will be their index in leaderboard list + 1

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

    def update_other_metrics(self, cadence, heartrate, time, elevation):
        self.avegage_cadence += cadence
        self.average_heartrate += heartrate
        self.elapsed_time += time
        self.total_elevation += elevation

    # REMEMBER to update workouts += 1 before using this method
    def update_baseline(self):
        self.baseline_average_speed = self.total_average_speed / self.total_workouts
        self.baseline_max_speed = self.total_max_speed / self.total_workouts
        self.baseline_distance = self.total_distance / self.total_workouts
        self.baseline_moving_time = self.total_moving_time / self.total_workouts

        self.average_cadence = self.avegage_cadence / self.total_workouts
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

    #
    def populate_player_activities_by_day(self):
        API_URL = "http://localhost:5000/strava/activities"
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            self.player_activities_by_day = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching activities: {e}")
            

    def sum_activities(self):
        for day in self.player_activities_by_day.values():
            for activity in day:
                self.total_workouts += 1
                self.__update_totals_from_args(activity.average_speed, activity.max_speed, activity.distance, activity.moving_time)
                self.update_other_metrics(activity.average_cadence, activity.heartrate, activity.elapsed_time, activity.total_elevation_gain)

        self.update_baseline()