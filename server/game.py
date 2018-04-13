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
        self.simulation = None
        self.runner = None
        self.cycle = 0
        self.hash_id = ""
        self.user_id_to_agent_map = {}
        self.decisions = []

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
            decision.upstream = self.simulation.distributors[0]
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'order_from_ds2':
            decision = OrderDecision()
            decision.amount = game_decision['decision_value']
            decision.upstream = self.simulation.distributors[1]
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'produce':
            decision = ProduceDecision()
            decision.amount = game_decision['decision_value']
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'satisfy_ds1':
            # decisions = self._construct_allocation_decision(
            #     game_decision['agent'],
            #     self.simulation.distributors[0],
            #     game_decision['decision_value'])
            # game_decision['agent'].decisions.extend(decisions)
            decision = AllocateDecision()
            decision.amount = game_decision['decision_value']
            decision.downstream_node = self.simulation.distributors[0]
            game_decision['agent'].decisions.append(decision)

        elif game_decision['decision_name'] == 'satisfy_ds2':
            # decisions = self._construct_allocation_decision(
            #     game_decision['agent'],
            #     self.simulation.distributors[1],
            #     game_decision['decision_value'])
            # game_decision['agent'].decisions.extend(decisions)
            decision = AllocateDecision()
            decision.amount = game_decision['decision_value']
            decision.downstream_node = self.simulation.distributors[1]
            game_decision['agent'].decisions.append(decision)

        else:
            print "Decision type " + game_decision['decision_name'] \
                  + " not supported!\n"
            return

    # def _construct_allocation_decision(self, agent, downstream_node, amount):
    #     amount_left = amount
    #     decisions = []
    #     orders = [order for order in agent.backlog if order.src is downstream_node]
    #
    #     if not orders or not agent.inventory:
    #         return []
    #
    #     order_index = 0
    #     item_index = 0
    #     order = orders[order_index]
    #     item = agent.inventory[item_index]
    #     order_left = order.amount
    #     item_left = item.amount
    #
    #     while amount_left > 0:
    #
    #         decision = AllocateDecision()
    #         decision.order = order
    #         decision.item = item
    #         decisions.append(decision)
    #
    #         if order_left < item_left:
    #             if order_left < amount_left:
    #                 decision.amount = order_left
    #                 order_index += 1
    #                 order = orders[order_index]
    #                 order_left = order.amount
    #                 amount_left -= decision.amount
    #             else:
    #                 decision.amount = amount_left
    #                 amount_left = 0
    #         else:
    #             if item_left < amount_left:
    #                 decision.amount = item_left
    #                 item_index += 1
    #                 item = agent.inventory[item_index]
    #                 item_left = item.amount
    #                 amount_left -= decision.amount
    #             else:
    #                 decision.amount = amount_left
    #                 amount_left = 0
    #
    #     return decisions


def build_game():
    """ instantiate a new game """
    simulation, runner = simulation_builder.build_simulation()

    game = Game()
    game.simulation = simulation
    game.runner = runner
    runner._update_patient(0)
    runner._update_agents(0)
    game.cycle = 0

    return game
