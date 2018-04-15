""" Server builds a flask server to provide APIs for the game """

import datetime
import os

import uuid
import jwt
from flask import Flask, send_from_directory
from flask import request
from flask import abort
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
    # start_week = request.args.get('startWeek')
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

    # TODO (Yifan): Fast forward the game to the starting week

    token_payload = {
        'exp': datetime.datetime.utcnow() +
               datetime.timedelta(days=1, seconds=0),
        'iat': datetime.datetime.utcnow(),
        'gameId': game_id,
        'userId': user_id
    }

    return str(jwt.encode(token_payload, 'SECRET_KEY'))


@APP.route('/api/get_game_hash_id', methods=['GET'])
def get_game_hash_id():
    token = request.args.get('token')
    game, _ = get_game_and_agent_from_token(token)
    return game.hash_id


@APP.route('/api/is_all_human_player_joined', methods=['GET'])
def is_all_human_player_joined():
    """This function returns true if all the human players in a game joined the game"""

    token = request.args.get('token')
    game, _ = get_game_and_agent_from_token(token)

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
        'exp': datetime.datetime.utcnow() +
               datetime.timedelta(days=1, seconds=0),
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

    return (game, agent)


@APP.route('/api/get_game_param', methods=['GET'])
def get_game_param():
    """ respond the game parameter value to the client """

    token = request.args.get('token')
    game, agent = get_game_and_agent_from_token(token)

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

    elif param == "on-order":
        value = sum(order.amount for order in agent.on_order)

    elif param == "received-delivery":
        history_item = agent.get_history_item(game.simulation.now)
        value = sum(d['item'].amount for d in history_item['delivery'])

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

    game, _ = get_game_and_agent_from_token(token)

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
            raise ValueError("Not supported paramter type")
    except ValueError as value_error:
        print value_error
        abort(400)

    return str(value)


@APP.route('/api/make_decision', methods=['GET'])
def make_decision():
    """ respond the request of posting the value of a decision parameters. """

    token = request.args.get('token')
    game, agent = get_game_and_agent_from_token(token)

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

# @APP.route("/api/get_user_id")
# def id_generator():
#     """ respond the request from the client to generate a unique user_id """

#     user_id = str(uuid.uuid4())
#     player_id = int(list(players)[-1].lstrip('id')) + 1
#     player_id = 'id%i' % player_id
#     players[player_id] = user_id

#     return players[player_id]

def remove_human_controlled_agents_decisions(game):
    for user_id in game.user_id_to_agent_map:
        agent = game.user_id_to_agent_map[user_id]
        agent.decisions = []

@APP.route('/api/next_period', methods=['GET', 'POST'])
def next_cycle():
    """ respond the request of moving the simulation to the next cycle. """

    token = request.args.get('token')
    game, agent = get_game_and_agent_from_token(token)

    game.done_with_current_cycle.append(agent)
    if (len(game.done_with_current_cycle) == game.num_human_players):
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


def draw_figures(game):

    for agent in game.simulation.agents:
        game.data = game.data.append(
            pd.DataFrame(agent.collect_data(game.simulation.now), columns=game.data_columns))
    game.data.reset_index()
    print game.data.to_string()


    hc1_data = game.data[game.data['agent'] == 'hc_4']
    plt.figure()
    sns.tsplot(hc1_data, time='time', condition='item', value='value',
               unit='unit').set_title('Health Center 1')
    plt.savefig('hc1.png', dpi=600)

    hc2_data = game.data[game.data['agent'] == 'hc_5']
    plt.figure()
    sns.tsplot(hc2_data, time='time', condition='item', value='value',
               unit='unit').set_title('Health Center 2')
    plt.savefig('hc2.png', dpi=600)

    ds1_data = game.data[game.data['agent'] == 'ds_2']
    plt.figure()
    sns.tsplot(ds1_data, time='time', condition='item',
               value='value', unit='unit').set_title('Distributor 1')
    plt.savefig('ds1.png', dpi=600)

    ds2_data = game.data[game.data['agent'] == 'ds_3']
    plt.figure()
    sns.tsplot(ds2_data, time='time', condition='item',
               value='value', unit='unit').set_title('Distributor 2')
    plt.savefig('ds2.png', dpi=600)

    mn1_data = game.data[game.data['agent'] == 'mn_0']
    plt.figure()
    sns.tsplot(mn1_data, time='time', condition='item',
               value='value', unit='unit').set_title('Manufacture 1')
    plt.savefig('mn1.png', dpi=600)

    mn2_data = game.data[game.data['agent'] == 'mn_1']
    plt.figure()
    sns.tsplot(mn2_data, time='time', condition='item',
               value='value', unit='unit').set_title('Manufacture 2')
    plt.savefig('mn2.png', dpi=600)
    inv_data = game.data[game.data['item'] == 'inventory']
    plt.figure()
    sns.tsplot(inv_data, time='time', condition='agent',
               value='value', unit='unit').set_title('Inventory')
    plt.savefig('inventory.png', dpi=600)


@APP.route("/api/update_graphs", methods=['GET'])
def update():
    """ updates graphs' images for the gamettes for each player. """

    token = request.args.get('token')
    token_payload = jwt.decode(token, 'SECRET_KEY')

    game_id = token_payload['game_id']
    game = GAMES[game_id]

    user_id = token_payload['user_id']

    graph(game, PATH, user_id=user_id)

    return "updated!"


@APP.route('/Charts/<filename>')
def send_image(filename):
    return send_from_directory(APP.static_folder, filename)


if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)
