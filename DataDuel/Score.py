from math import ceil

class Score:
    def __init__(self):
        self.score = 0
        self.previous_score = 0
        self.improvement = 0

    def get_score(self):
        return self.score

    def fix_negative_score(self):
        if self.score < 0:
            self.score = 0

    def calculate_improvement_bonus(self):
        return ceil(self.improvement * .01) * 5

    def calculate_score(self, average_speed, max_speed, distance, moving_time,
                        base_average_speed, base_max_speed, base_distance, base_moving_time,
                        badge_points, challenge_points, streak):
        self.previous_score = self.score
        scale = 0

        scale += 1 if average_speed >= base_average_speed else -1
        scale += 1 if max_speed >= base_max_speed else -1
        scale += 1 if distance >= base_distance else -1
        scale += 1 if moving_time >= base_moving_time else -1

        if scale > 0:
            print("DEBUG: IN SCALE > 0")
            self.score += (scale + badge_points + challenge_points + streak)

            if self.score - self.previous_score > 0:
                self.improvement += self.score - self.previous_score

            self.score += self.calculate_improvement_bonus()

        elif scale < 0:
            print("DEBUG: IN SCALE <>> 0")

            self.score -= scale * scale
            self.score += ceil((badge_points + challenge_points + streak) * .5)

            if self.score - self.previous_score > 0:
                self.improvement += self.score - self.previous_score

            self.score += ceil(self.calculate_improvement_bonus() * .5)

        else:
            print("DEBUG: IN SCALE == 0")

            self.score += (badge_points + challenge_points + streak)

            if self.score - self.previous_score > 0:
                self.improvement += self.score - self.previous_score

            self.score += ceil(self.calculate_improvement_bonus() * .5)

        self.fix_negative_score()
        return self.score