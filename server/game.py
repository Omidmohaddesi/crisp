""" game provides useful data structures to manage games """

import pandas as pd

from server import simulation_builder
from simulator.decision import TreatDecision
from simulator.decision import OrderDecision
from simulator.decision import ProduceDecision
from simulator.decision import AllocateDecision


class Game(object):
    """ A game is a session that the user plays """

    def __init__(self):
        self.id = ''
        self.simulation = None
        self.runner = None
        self.num_human_players = 1
        self.hash_id = ""
        self.user_id_to_agent_map = {}
        self.decisions = []
        self.done_with_current_cycle = []
        self.study_name = ""

        self.data_columns = ['time', 'agent', 'item', 'value', 'unit']
        self.data = pd.DataFrame(columns=self.data_columns)

    def parse_decisions(self):
        """ convert the game decision to simulator desicion """
        for decision in self.decisions:
            self.convert_to_simulation_decision(decision)

        self.decisions = []

    def convert_to_simulation_decision(self, game_decision):
        """
        :type d: GameDecision
        """

        if game_decision['decision_name'] == 'satisfy_urgent':
            decision = TreatDecision()
            decision.urgent = game_decision['decision_value']
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'satisfy_non_urgent':
            decision = TreatDecision()
            decision.non_urgent = game_decision['decision_value']
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'order_from_ds1':
            decision = OrderDecision()
            decision.amount = game_decision['decision_value']
            # decision.upstream = self.simulation.distributors[0]
            decision.upstream = [k for k in self.simulation.distributors if k.agent_name == 'DS'][0]
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'order_from_ds2':
            decision = OrderDecision()
            decision.amount = game_decision['decision_value']
            # decision.upstream = self.simulation.distributors[1]
            decision.upstream = [k for k in self.simulation.distributors if k.agent_name == 'DS'][1]
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'order_from_mn1':
            decision = OrderDecision()
            decision.amount = game_decision['decision_value']
            decision.upstream = self.simulation.manufacturers[0]
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'order_from_mn2':
            decision = OrderDecision()
            decision.amount = game_decision['decision_value']
            decision.upstream = self.simulation.manufacturers[1]
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'produce':
            decision = ProduceDecision()
            decision.amount = game_decision['decision_value']
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'satisfy_ds1':
            decision = AllocateDecision()
            decision.amount = game_decision['decision_value']
            decision.downstream_node = self.simulation.distributors[0]
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'satisfy_ds2':
            decision = AllocateDecision()
            decision.amount = game_decision['decision_value']
            decision.downstream_node = self.simulation.distributors[1]
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'satisfy_hc1':
            decision = AllocateDecision()
            decision.amount = game_decision['decision_value']
            decision.downstream_node = self.simulation.health_centers[0]
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'satisfy_hc2':
            decision = AllocateDecision()
            decision.amount = game_decision['decision_value']
            decision.downstream_node = self.simulation.health_centers[1]
            game_decision['agent'].decisions.append(decision)

        else:
            print "Decision type " + game_decision['decision_name'] \
                  + " not supported!\n"
            return


def build_game(study_name=None):
    """ instantiate a new game """
    game = Game()
    game.study_name = study_name
    if game.study_name == 'beerGame':
        simulation, runner = simulation_builder.build_simulation_beer_game()
    else:
        simulation, runner = simulation_builder.build_simulation()

    game.simulation = simulation
    game.runner = runner
    runner._update_patient(0)
    runner._update_agents(0)

    return game
