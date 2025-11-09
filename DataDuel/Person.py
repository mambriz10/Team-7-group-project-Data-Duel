# SUBJECT TO CHANGE. This is a main idea, implememntation details will most likely change slightly overtime.

# Assume a person is made when a user first makes an account / connection. Then when they connect to strava, we will
# fill other member variables like the metrics.

# Another way to go is to create this object after a connection to strava has been made and we getc call it with
# data from api call
import Score

class Person:
    def __init__(self):
        # User Information
        self.__name = "Default_Name" # used for profile page and possible leaderboard name
        self.__user_name = "Default_Username" # possible leaderboard name

        self.display_name = self.__user_name # name for leaderboard

        # Metrics
        self.average_speed = 25
        self.max_speed = 50
        self.distance = 1000
        self.moving_time = 1000
        self.cadence = 25
        self.average_watts = 100
        self.elapsed_time = 120
        self.total_elevation = 20

        # Ticked Variables
        self.streak = 0
        self.days_in_league = 0
        self.total_workouts = 1

        self.total_average_speed = self.average_speed
        self.total_max_speed = self.max_speed
        self.total_distance = self.distance
        self.total_moving_time = self.moving_time

        # Baselines used in score calculation
        self.baseline_average_speed = self.total_average_speed / self.total_workouts
        self.baseline_max_speed = self.total_max_speed / self.total_workouts
        self.baseline_distance = self.total_distance / self.total_workouts
        self.baseline_moving_time = self.total_moving_time / self.total_workouts

        # Placeholders for future objects
        self.improvement_score = 10
        self.weekly_challenge = 0
        self.badges = []

    # Setters for user customizable options
    def change_name(self, new_name):
        self.__name = new_name

    def change_username(self, new_user_name):
        self.__user_name = new_user_name

    # Private helper to update totals from currently stored metrics
    def __update_totals(self):
        self.total_average_speed += self.average_speed
        self.total_max_speed += self.max_speed
        self.total_distance += self.distance
        self.total_moving_time += self.moving_time

    def __update_totals_from_args(self, avg_speed, max_speed, distance, moving_time):
        self.total_average_speed += avg_speed
        self.total_max_speed += max_speed
        self.total_distance += distance
        self.total_moving_time += moving_time

    def __recalculate_baselines(self):
        self.baseline_average_speed = self.total_average_speed / self.total_workouts
        self.baseline_max_speed = self.total_max_speed / self.total_workouts
        self.baseline_distance = self.total_distance / self.total_workouts
        self.baseline_moving_time = self.total_moving_time / self.total_workouts

    # REMEMBER to update workouts += 1 before using this method
    def update_baseline_from_current_metrics(self):
        self.__update_totals()
        self.__recalculate_baselines()

    # REMEMBER to update workouts += 1 before using this method
    def update_baseline_from_workout(self, avg_speed, max_speed, distance, moving_time):
        self.__update_totals_from_args(avg_speed, max_speed, distance, moving_time)
        self.__recalculate_baselines()

    # Used in settings to change privacy to change which leaderboard name is shown
    def show_real_name(self, check):
        if check:
            self.display_name = self.__name
        else:
            self.display_name = self.__user_name

    # Adds 1 to total workouts for end of workout easy function call
    def increase_total_workouts(self):
        self.total_workouts += 1