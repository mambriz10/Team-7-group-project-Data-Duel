class badges:
    def __init__(self):
        # Right now it is assuming that an outside class will change these values after a condition was checked.
        # Maybe in a function that also checks for badges and streaks
        self.moving_time = False
        self.distance = False
        self.max_speed = False


        # They do not have to be the same challenge, it's just default values right now
        self.first_description = "Move for 1 hour"
        self.second_description = "Max Speed > 10"
        self.third_description = "Hit Elapse Time > 100"

    # Basic function to get points based on 3 bools. Subject to change
    # assumes the challenge variables have been checked and updated correctly
    def get_points(self):
        points = 0

        points += 5 if self.moving_time else 0
        points += 5 if self.distance else 0
        points += 5 if self.max_speed else 0

        return points

