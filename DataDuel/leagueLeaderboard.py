import Person

class leagueLeaderboard:
    def sort_players(self):
        self.players = sorted(self.players, key=lambda player: player.score.score, reverse=True) # sort by highest score

    def __init__(self, size, duration, name, players):
        self.size = size # number of players
        self.duration = duration
        self.name = name

        self.players = players # list of players
        self.sort_players()

        # Set ranks of players
        for player in self.players:
            player.rank = self.players.index(player) + 1



