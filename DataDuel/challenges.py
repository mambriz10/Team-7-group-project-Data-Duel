class challenges:
    def __init__(self):
        # Right now it is assuming that an outside class will change these values after a condition was checked.
        # Maybe in a function that also checks for badges and streaks
        self.first_challenge = False
        self.second_challenge = False
        self.third_challenge = False

        self.first_name = "First"
        self.second_name = "Second"
        self.third_name = "Third"

        # They do not have to be the same challenge, it's just default values right now
        self.first_description = "Run 3 miles"
        self.second_description = "Run 5 miles"
        self.third_description = "Run 10 miles"

    # Basic function to get points based on 3 bools. Subject to change
    # assumes the challenge variables have been checked and updated correctly
    def get_points(self):
        points = 0

        points += 5 if self.first_challenge else 0
        points += 5 if self.second_challenge else 0
        points += 5 if self.third_challenge else 0

        return points

