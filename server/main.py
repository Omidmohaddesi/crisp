""" Server builds a flask server to provide APIs for the game """

import datetime
import os

import uuid
import jwt
from flask import Flask, send_from_directory
from flask import request
from flask import abort
from flask_restful import reqparse
from hashids import Hashids
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns

from server.game import build_game
from server.graph import graph
import simulator.agent as agents

PATH = os.path.join(os.path.abspath('..'), 'client/')

APP = Flask(__name__, static_url_path='', static_folder=PATH)
HASHIDS = Hashids(salt="Drug Shortage")

GAMES = {}
HASH_ID_TO_GAME_MAP = {}

parser = reqparse.RequestParser()
parser.add_argument('task')


@APP.after_request
def after_request(response):
    """ after_request """
    response.headers.add(
        'Access-Control-Allow-Origin',
        'http://www.neumadscience.com')
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


def find_first_agent_of_type(game, role):
    """ given a role, find the first agent of a certain role that is not
        controlled by a player user.
    """
    agent_list = None
    if role == 'health-center':
        agent_list = game.simulation.health_centers
    elif role == 'distributor':
        agent_list = game.simulation.distributors
    elif role == 'manufacturer':
        agent_list = game.simulation.manufacturers

    for agent in agent_list:
        for human_player_agent in game.user_id_to_agent_map:
            if not game.user_id_to_agent_map[human_player_agent] is agent:
                continue
        return agent

    return None


@APP.route('/api/create_game', methods=['GET'])
def new_game():
    """ respond to the request from the client to create a new game """

    user_id = str(uuid.uuid4())
    game_id = str(uuid.uuid4())
    start_cycle = int(request.args.get('startCycle'))
    role = request.args.get('role')
    num_human_players = int(request.args.get('numHumanPlayer'))

    game_count = len(GAMES)
    game = build_game()
    game.id = game_id
    game.num_human_players = num_human_players
    GAMES[game_id] = game
    agent = find_first_agent_of_type(game, role)
    game.user_id_to_agent_map[user_id] = agent

    hash_id = HASHIDS.encode(game_count)
    game.hash_id = hash_id
    HASH_ID_TO_GAME_MAP[hash_id] = game

    fast_forward_game(game, start_cycle)

    token_payload = {
        'exp': datetime.datetime.utcnow() +
               datetime.timedelta(days=1, seconds=0),
        'iat': datetime.datetime.utcnow(),
        'gameId': game_id,
        'userId': user_id
    }

    return str(jwt.encode(token_payload, 'SECRET_KEY'))

def fast_forward_game(game, cycle):
    """ Let the default decision maker to run the game for a certain number of
        cyles

        :type game: Game
    """
    for i in range(0, cycle):
        game.runner.next_cycle()

@APP.route('/api/get_game_hash_id', methods=['GET'])
def get_game_hash_id():
    token = request.args.get('token')
    # game, _ = get_game_and_agent_from_token(token)
    game = get_game_and_agent_from_token(token)['game']
    return game.hash_id


@APP.route('/api/is_all_human_player_joined', methods=['GET'])
def is_all_human_player_joined():
    """This function returns true if all the human players in a game joined the game"""

    token = request.args.get('token')
    # game, _ = get_game_and_agent_from_token(token)
    game = get_game_and_agent_from_token(token)['game']

    if game.num_human_players == len(game.user_id_to_agent_map):
        return 'true'

    return 'false'


@APP.route('/api/join_game', methods=['GET'])
def join_game():
    """ This allows a player to join a game """

    hash_id = request.args.get('hashId')
    role = request.args.get('role')

    game = HASH_ID_TO_GAME_MAP[hash_id]
    if game is None:
        abort(404)

    agent = find_first_agent_of_type(game, role)
    if agent is None:
        abort(400)

    user_id = str(uuid.uuid4())
    game.user_id_to_agent_map[user_id] = agent

    token_payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
        'iat': datetime.datetime.utcnow(),
        'gameId': game.id,
        'userId': user_id
    }

    return str(jwt.encode(token_payload, 'SECRET_KEY'))


def get_game_or_401(game_id):
    """ return a game by the game_id or return 401 error"""
    game = GAMES[game_id]
    if game is None:
        abort(401)
    return game


def get_agent_or_401(game, user_id):
    """ return a agent by the user_id in a game or return 401 error"""
    agent = game.user_id_to_agent_map[user_id]
    if agent is None:
        abort(401)
    return agent


def get_game_and_agent_from_token(token):
    """ Return the game and agent from the token string

    :rtype (Game, Agent)
    """
    token_payload = jwt.decode(token, 'SECRET_KEY')

    game_id = token_payload['gameId']
    game = get_game_or_401(game_id)

    user_id = token_payload['userId']
    agent = get_agent_or_401(game, user_id)

    # return (game, agent)
    return {'game': game, 'agent': agent, 'userId': user_id}


@APP.route('/api/get_game_param', methods=['GET'])
def get_game_param():
    """ respond the game parameter value to the client """

    token = request.args.get('token')
    # game, agent = get_game_and_agent_from_token(token)
    game = get_game_and_agent_from_token(token)['game']
    agent = get_game_and_agent_from_token(token)['agent']

    param = request.args.get('paramName')
    if param == 'cycle':
        value = game.simulation.now

    elif param == 'inventory':
        value = agent.inventory_level()

    elif param == "urgent":
        if not isinstance(agent, agents.HealthCenter):
            abort(400)
        value = agent.urgent

    elif param == "non-urgent":
        if not isinstance(agent, agents.HealthCenter):
            abort(400)
        value = agent.non_urgent

    elif param == "lost-urgent":
        if not isinstance(agent, agents.HealthCenter):
            abort(400)
        history_item = agent.get_history_item(game.simulation.now)
        value = history_item['patient_lost'][0]

    elif param == "lost-non-urgent":
        if not isinstance(agent, agents.HealthCenter):
            abort(400)
        history_item = agent.get_history_item(game.simulation.now)
        value = history_item['patient_lost'][1]

    elif param == "order-to-ds1":
        history_item = agent.get_history_item(game.simulation.now - 1)
        value = 0
        for order in history_item['order']:
            if order.dst == game.simulation.distributors[0]:
                value += order.amount

    elif param == "order-to-ds2":
        history_item = agent.get_history_item(game.simulation.now - 1)
        value = 0
        for order in history_item['order']:
            if order.dst == game.simulation.distributors[1]:
                value += order.amount

    elif param == "on-order":
        value = sum(order.amount for order in agent.on_order)

    elif param == 'on-order-ds1':
        value = sum(agent.on_order[j].amount for j in range(0, len(agent.on_order))
                    if agent.on_order[j].dst.id == 2)

    elif param == 'on-order-ds2':
        value = sum(agent.on_order[j].amount for j in range(0, len(agent.on_order))
                    if agent.on_order[j].dst.id == 3)

    elif param == "received-delivery":
        history_item = agent.get_history_item(game.simulation.now)
        value = sum(d['item'].amount for d in history_item['delivery'])

    elif param == "received-delivery-ds1":
        history_item = agent.get_history_item(game.simulation.now)
        value = sum(history_item['delivery'][j]["item"].amount
                    for j in range(0, len(history_item['delivery']))
                    if history_item['delivery'][j]["src"].id == 2)

    elif param == "received-delivery-ds2":
        history_item = agent.get_history_item(game.simulation.now)
        value = sum(history_item['delivery'][j]["item"].amount
                    for j in range(0, len(history_item['delivery']))
                    if history_item['delivery'][j]["src"].id == 3)

    elif param == "in-production":
        value = sum([item.amount for item in agent.in_production])

    elif param == 'backlog-ds1':
        value = 0
        for order in agent.backlog:
            if order.src == game.simulation.distributors[0]:
                value += order.amount

    elif param == 'backlog-ds2':
        value = 0
        for order in agent.backlog:
            if order.src == game.simulation.distributors[1]:
                value += order.amount

    elif param == 'backlog-hc1':
        value = 0
        for order in agent.backlog:
            if order.src == game.simulation.health_centers[0]:
                value += order.amount

    elif param == 'backlog-hc2':
        value = 0
        for order in agent.backlog:
            if order.src == game.simulation.health_centers[1]:
                value += order.amount

    else:
        print "Unsupported parameter type " + param
        abort(400)

    return str(value)


@APP.route('/api/get_game_history_param', methods=['GET'])
def get_game_history_param():
    """ respond the request of querying the value of a simulation parameter. """

    token = request.args.get('token')
    cycle = int(request.args.get('cycle'))
    agent_id = int(request.args.get('agentId'))
    param = request.args.get('paramName')

    # game, _ = get_game_and_agent_from_token(token)
    game = get_game_and_agent_from_token(token)['game']

    agent = game.simulation.agents[agent_id]
    if agent is None:
        abort(404)

    if not agent.is_history_available(cycle):
        abort(404)

    history = agent.get_history_item(cycle)
    try:
        if param == "inventory":
            value = history['inventory']
        elif param == "urgent":
            if not isinstance(agent, agents.HealthCenter):
                abort(400)
            value = history['patient'][0]
        elif param == "non-urgent":
            if not isinstance(agent, agents.HealthCenter):
                abort(400)
            value = history['patient'][1]
        else:
            raise ValueError("Not supported parameter type")
    except ValueError as value_error:
        print value_error
        abort(400)

    return str(value)


@APP.route('/api/make_decision', methods=['GET', 'PUT', 'POST'])
def make_decision():
    """ respond the request of posting the value of a decision parameters. """

    args = parser.parse_args()
    task = args['task']     # StudyCrafter only works with "task" right now for POST call and doesn't
    # accept any other argument
    # token, decision_name, decision_value = task.split(";")

    token = request.args.get('token')
    game = get_game_and_agent_from_token(token)['game']
    agent = get_game_and_agent_from_token(token)['agent']

    decision_name = request.args.get('decisionName')
    decision_value = request.args.get('decisionValue')
    if decision_value is None:
        decision_value = 0

    decision = {
        'agent': agent,
        'decision_name': decision_name,
        'decision_value': int(decision_value),
    }
    game.decisions.append(decision)

    print game.decisions

    return ''


@APP.route("/api/get_user_id", methods=['GET', 'POST'])
def get_user():
    token = request.args.get('token')
    return get_game_and_agent_from_token(token)['userId']


def remove_human_controlled_agents_decisions(game):
    for user_id in game.user_id_to_agent_map:
        agent = game.user_id_to_agent_map[user_id]
        agent.decisions = []


@APP.route('/api/next_period', methods=['GET', 'POST'])
def next_cycle():
    """ respond the request of moving the simulation to the next cycle. """

    token = request.args.get('token')
    # game, agent = get_game_and_agent_from_token(token)
    game = get_game_and_agent_from_token(token)['game']
    agent = get_game_and_agent_from_token(token)['agent']

    game.done_with_current_cycle.append(agent)
    if len(game.done_with_current_cycle) == game.num_human_players:
        game.done_with_current_cycle = []
        do_next_cycle(game)

    return str(game.simulation.now)


def do_next_cycle(game):
    """ Update a game to the next cycle """
    game.runner._make_decision(game.simulation.now)
    remove_human_controlled_agents_decisions(game)
    game.parse_decisions()
    game.runner._apply_decision(game.simulation.now)

    # try:
    #     draw_figures(game)
    # except Exception as e:
    #     print e

    game.simulation.now += 1
    game.runner._update_patient(game.simulation.now)
    game.runner._update_agents(game.simulation.now)
    game.runner._update_network(game.simulation.now)
    game.runner._exogenous_event(game.simulation.now)


def append_data_for_health_center_graph(game, agent):

    now = game.simulation.now
    name = agent.name()
    history = agent.get_history_item(now)
    history_p = agent.get_history_item(game.simulation.now - 1)
    game.data = game.data.append(pd.DataFrame([
        [now, name, 'urgent', agent.urgent, ''],
        [now, name, 'non_urgent', agent.non_urgent, ''],
        [now-1, name, 'order', sum(order.amount for order in history_p['order']), ''],
        [now-1, name, 'order_ds1', sum(order.amount for order in history_p['order']
                                       if order.dst == game.simulation.distributors[0]), ''],
        [now-1, name, 'order_ds2', sum(order.amount for order in history_p['order']
                                       if order.dst == game.simulation.distributors[1]), ''],
        [now, name, 'on_order_ds1', sum(agent.on_order[j].amount for j in range(0, len(agent.on_order))
                                        if agent.on_order[j].dst.id == 2), ''],
        [now, name, 'on_order_ds2', sum(agent.on_order[j].amount for j in range(0, len(agent.on_order))
                                        if agent.on_order[j].dst.id == 3), ''],
        [now, name, 'rec_ds1', sum(history['delivery'][j]["item"].amount
                                   for j in range(0, len(history['delivery']))
                                   if history['delivery'][j]["src"].id == 2), ''],
        [now, name, 'rec_ds2', sum(history['delivery'][j]["item"].amount
                                   for j in range(0, len(history['delivery']))
                                   if history['delivery'][j]["src"].id == 3), '']
    ], columns=game.data_columns))
    # game.data[game.data['now'] == game.simulation.now - 1] =


def draw_figures(game, user_id, agent_name):

    for agent in game.simulation.agents:
        game.data = game.data.append(
            pd.DataFrame(agent.collect_data(game.simulation.now), columns=game.data_columns))
        if agent.agent_type == "hc":
            append_data_for_health_center_graph(game, agent)
    game.data.reset_index()
    print game.data.to_string()

    if game.simulation.now > 9:
        graph(game.data, PATH, user_id=user_id, agent=agent_name)

    # if game.simulation.now > 10:
    #     hc1_data = game.data[game.data['agent'] == 'hc_4']
    #     plt.figure()
    #     sns.tsplot(hc1_data, time='time', condition='item', value='value',
    #                unit='unit').set_title('Health Center 1')
    #     plt.savefig(os.path.join(PATH, 'hc1.png'), dpi=600)
    #
    #     hc2_data = game.data[game.data['agent'] == 'hc_5']
    #     plt.figure()
    #     sns.tsplot(hc2_data, time='time', condition='item', value='value',
    #                unit='unit').set_title('Health Center 2')
    #     plt.savefig(os.path.join(PATH, 'hc2.png'), dpi=600)
    #
    #     ds1_data = game.data[game.data['agent'] == 'ds_2']
    #     plt.figure()
    #     sns.tsplot(ds1_data, time='time', condition='item',
    #                value='value', unit='unit').set_title('Distributor 1')
    #     plt.savefig(os.path.join(PATH, 'ds1.png'), dpi=600)
    #
    #     ds2_data = game.data[game.data['agent'] == 'ds_3']
    #     plt.figure()
    #     sns.tsplot(ds2_data, time='time', condition='item',
    #                value='value', unit='unit').set_title('Distributor 2')
    #     plt.savefig(os.path.join(PATH, 'ds2.png'), dpi=600)
    #
    #     mn1_data = game.data[game.data['agent'] == 'mn_0']
    #     plt.figure()
    #     sns.tsplot(mn1_data, time='time', condition='item',
    #                value='value', unit='unit').set_title('Manufacture 1')
    #     plt.savefig(os.path.join(PATH, 'mn1.png'), dpi=600)
    #
    #     mn2_data = game.data[game.data['agent'] == 'mn_1']
    #     plt.figure()
    #     sns.tsplot(mn2_data, time='time', condition='item',
    #                value='value', unit='unit').set_title('Manufacture 2')
    #     plt.savefig(os.path.join(PATH, 'mn2.png'), dpi=600)
    #     inv_data = game.data[game.data['item'] == 'inventory']
    #     plt.figure()
    #     sns.tsplot(inv_data, time='time', condition='agent',
    #                value='value', unit='unit').set_title('Inventory')
    #     plt.savefig(os.path.join(PATH, 'inventory.png'), dpi=600)


@APP.route("/api/update_graphs", methods=['GET'])
def update():
    """ updates graphs' images for the gamettes for each player. """

    token = request.args.get('token')
    # game, agent = get_game_and_agent_from_token(token)
    game = get_game_and_agent_from_token(token)['game']
    user_id = get_game_and_agent_from_token(token)['userId']
    agent = get_game_and_agent_from_token(token)['agent']

    draw_figures(game, user_id, agent.name())

    # token = request.args.get('token')
    # token_payload = jwt.decode(token, 'SECRET_KEY')
    #
    # game_id = token_payload['game_id']
    # game = GAMES[game_id]
    #
    # user_id = token_payload['user_id']
    #
    # graph(game, PATH, user_id=user_id)

    return "updated!"


@APP.route('/charts/<user_id>/<filename>')
def send_image(user_id, filename):
    return send_from_directory(os.path.join(APP.static_folder + "/" + user_id), filename)


if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)
