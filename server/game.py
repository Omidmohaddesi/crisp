""" game provides useful data structures to manage games """

import simulation_builder


class Game(object):
    """ A game is a session that the user plays """

    def __init__(self):
        self.simulation = None
        self.runner = None
        self.hash_id = ""


def build_game():
    """ instantiate a new game """
    sim = simulation_builder.build_simulation()

    game = Game()
    game.simulation = sim.simulation
    game.runner = sim.runner

    return game

