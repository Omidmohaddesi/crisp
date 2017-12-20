""" game provides useful datastructures to manage games """


class Game(object):
    """ A game is a session that the user plays """

    def __init__(self):
        self.simulation = None


def build_game(simulation_builder):
    ''' instantiate a new game '''
    sim = simulation_builder()

    game = Game()
    game.simulation = sim

    return game
