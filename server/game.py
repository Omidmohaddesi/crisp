""" game provides useful datastructures to manage games """

import simulation_builder


class Game(object):
    """ A game is a session that the user plays """

    def __init__(self):
        self.simulation = None
        self.runner = None


def build_game():
    ''' instantiate a new game '''
    sim = simulation_builder.build_simulation()

    game = Game()
    game.simulation = sim.simulation
    game.runner = sim.runner

    return game


# ------------------------------------
# Testing

game1 = build_game()


for i in range(0, 10):
    game1.runner.next_cycle()
    a = game1.simulation.health_centers[0].inventory_level()
    print(a)