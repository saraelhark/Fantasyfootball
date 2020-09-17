# -*- coding: utf-8 -*-

import requests
import os
from bs4 import BeautifulSoup


class Fantasyfootball:
    """ class representing the game itself """

    def __init__(self):
        print('Welcome to the game!\n')
        self.day = input("Please insert the championship day you're interested in: \n")

    def get_data_from_web(self):
        base_url = "https://www.gazzetta.it/calcio/fantanews/voti/serie-a-2017-18/giornata-" + str(self.day)

        source_code = requests.get(base_url, allow_redirects=False)

        plain_text = source_code.text.encode('ascii', 'replace')

        soup = BeautifulSoup(plain_text, 'html.parser')

        # empty lists to be filled with data gathered from the gazzetta.it website
        # which contains the players' scores
        names = []
        scores = []

        # loop that iterates for all players and create lists with names and final score
        for player in soup.find_all(class_='playerName'):

            player_name = player.find(class_='playerNameIn')
            names.append(player_name.contents[0].contents[0])

            player_points = player.findNext(class_='inParameter fvParameter')
            scores.append(player_points.string)

        # link the two elements as couples and return them as a list --> like a 2D matrix
        all_data = zip(names, scores)

        return list(all_data)

    @staticmethod
    def print_ranking(rank):
        ast = '*'*25
        idx = 1
        print('{:*^25}'.format('RANKING'))
        print(ast)
        for t in rank:
            print('{:<4}  {}'.format(idx, t))
            idx += 1
        print(ast)

    def play_game(self):

        score_data = self.get_data_from_web()
        squads = []

        directory = './teams'

        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)
            squads.append(SoccerTeam(path))

        for team in squads:
            team.create_teams()
            team.assign_data(score_data)
            team.compute_scores()
            team.print_team()

        ranking = sorted(squads, key=lambda x: x.totalScore, reverse=True)

        return ranking


class Player:
    """ class representing a single player """

    def __init__(self, name, pos, stat):
        self.name = name
        self.role = pos
        self.status = stat
        self.score = 0.0

    def __repr__(self):
        return '{:<5} {:<20} {:<6} {:<10} {:<2}'.format(self.role, self.name, str(self.score), self.status, '\n')


class SoccerTeam:
    """ class representing a team """

    teamCount = 0

    def __init__(self, path_file):
        self.players = []
        self.totalScore = 0
        self.playerNum = 0
        SoccerTeam.teamCount += 1
        self.teamNum = SoccerTeam.teamCount
        self.path = path_file

    def __repr__(self):
        return '{} {}: {}\n'.format('Team', self.teamNum, self.totalScore)

    def create_teams(self):
        """ read from file data related to the teams '+str(self.teamNum)+'"""

        with open(self.path, 'r') as open_file:
            all_text = open_file.read()

        # split text in lines
        split_text = all_text.splitlines()

        # skip blank lines
        lines = (line for line in split_text if line)

        # index to distinguish between starting 11 and bench players
        idx = 0

        # take data from the lines, skipping the non relevant lines
        for line in lines:
            if ('TEAM' not in line) & ('STARTING' not in line) & ('SUBSTITUTES' not in line):
                data = line.split(maxsplit=1)
                idx += 1

                if idx < 12:
                    self.players.append(Player(data[1], data[0], 'playing'))
                else:
                    self.players.append(Player(data[1], data[0], 'bench'))

        self.playerNum = idx - 1

    def assign_data(self, zipped_data):
        """ assign data from the internet to players --> scores """

        for names, scores in zipped_data:
            for pl in self.players:

                if (pl.name in names) & (pl.score == 0.0):
                    pl.score = scores

        for pl in self.players:  # check if the player wasn't present at all
            if pl.score == 0.0:
                pl.status = 'not found'
                pl.score = '-'

    def compute_scores(self):

        for pl in self.players[:11]:

            if pl.score != '-':
                self.totalScore += float(pl.score)

            else:
                # handling the no score/not found situation --> choose the first player in the bench
                # with the same role and a valid score
                pl.status = 'no score'
                for pl_bench in self.players[11:]:
                    if (pl_bench.role == pl.role) & (pl_bench.status != 'in ^') & (pl_bench.status != 'not found'):
                        if pl_bench != '-':
                            pl_bench.status = 'in ^'
                            self.totalScore += float(pl_bench.score)
                            break
                        else:
                            continue

    def print_team(self):
        """ print data about the team in a table-like format """
        dash = '-' * 45

        print(dash)
        print('{:<5} {:<20} {:<6} {:<10}'.format('ROLE', 'NAME', 'SCORE', 'STATE'))
        print(dash)

        for pl in self.players:
            print(pl)

        print('{:-^20}{:-^20}'.format('TEAM SCORE', self.totalScore))
        print('\n\n')

    def get_key(self):
        return self.totalScore


if __name__ == "__main__":

    game = Fantasyfootball()

    r = game.play_game()

    game.print_ranking(r)
