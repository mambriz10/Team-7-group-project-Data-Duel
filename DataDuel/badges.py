class badges:
    def __init__(self):
        # Right now it is assuming that an outside class will change these values after a condition was checked.
        # Maybe in a function that also checks for badges and streaks
        self.moving_time = False
        self.distance = False
        self.max_watts = False
        self.max_speed = False

        self.first_badge = "First"
        self.second_badge = "Second"
        self.third_badge = "Third"

        # They do not have to be the same challenge, it's just default values right now
        self.first_description = "Run 3 miles"
        self.second_description = "Run 5 miles"
        self.third_description = "Run 10 miles"

    # Basic function to get points based on 3 bools. Subject to change
    # assumes the challenge variables have been checked and updated correctly
    def get_points(self):
        points = 0

        points += 5 if self.moving_time else 0
        points += 5 if self.distance else 0
        points += 5 if self.max_watts else 0
        points += 5 if self.max_speed else 0

        return points

