""" game provides useful data structures to manage games """

import simulation_builder
from simulator.decision import TreatDecision
from simulator.decision import OrderDecision

class GameDecision(object):
    ''' A decision stores the decisions made by user '''

    def __init__(self):
        self.user_id = ''
        self.decision_name = ''
        self.decision_value = 0


class Game(object):
    """ A game is a session that the user plays """

    def __init__(self):
        self.simulation = None
        self.runner = None
        self.cycle = 0
        self.hash_id = ""
        self.user_id_to_agent_map = {}
        self.decisions = []

    def parse_decisions(self):
        for d in self.decisions:
            self.convert_to_simulation_decision(d)

        self.decisions = []

    def convert_to_simulation_decision(self, d):
        """
        :type d: GameDecision
        """

        decision = None

        agent = self.user_id_to_agent_map[d.user_id]
        if d.decision_name == 'satisfy_urgent':
            decision = TreatDecision()
            decision.urgent = d.decision_value
        elif d.decision_name == 'satisfy_non_urgent':
            decision = TreatDecision()
            decision.non_urgent = d.decision_value
        elif d.decision_name == 'order_from_ds1':
            decision = OrderDecision()
            decision.amount = d.decision_value
            decision.upstream = self.simulation.distributors[0]
        elif d.decision_name == 'order_from_ds2':
            decision = OrderDecision()
            decision.amount = d.decision_value
            decision.upstream = self.simulation.distributors[1]
        else:
            print "Decision type " + d.decision_name + " not supported!\n"
            return

        agent.decisions.append(decision)


def build_game():
    """ instantiate a new game """
    simulation, runner = simulation_builder.build_simulation()

    game = Game()
    game.simulation = simulation
    game.runner = runner
    runner._update_patient(0);
    runner._update_agents(0);
    game.cycle = 0

    return game

