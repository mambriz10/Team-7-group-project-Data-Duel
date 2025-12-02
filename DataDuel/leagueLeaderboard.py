import Person

class leagueLeaderboard:
    def sort_players(self):
        # this converts the map to a list after sorted()
        self.players = sorted(self.players.values(), key=lambda player: player.score.score, reverse=True) # sort by highest score

    def __init__(self, size, duration, name, players):
        self.size = size # number of players
        self.duration = duration
        self.name = name

        self.players = players # map of email key to Person object values

        self.sort_players() # converts map into sorted list
        # Set ranks of players from the now converted list
        for player in self.players:
            player.rank = self.players.index(player) + 1 # should change to enumurate on bigger leaderboards



