""" Server builds a flask server to provide APIs for the game """

from flask import Flask, send_from_directory
from flask import request
from flask_restful import Resource, Api
from flask import jsonify
from flask import abort
from hashids import Hashids
import uuid
import jwt
import datetime
import os

from game import build_game
from game import GameDecision
from graph import graph
from simulation_builder import build_simulation
import simulator.agent as agents

path = os.path.join(os.path.abspath('..'), 'client/')

app = Flask(__name__, static_url_path='', static_folder=path)
api = Api(app)
hashids = Hashids(salt="Drug Shortage")

game_count = 0
games = {}
hash_id_to_game_map = {}
parameters = []


@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Origin',
        'http://www.neumadscience.com')
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@app.route('/api/create_game', methods=['GET'])
def new_game():
    """ respond to the request from the client to create a new game """

    user_id = request.args.get('userId')
    game_id = request.args.get('gameId')
    # start_week = request.args.get('startWeek')
    # role = request.args.get('role')

    global game_count
    game_count = game_count + 1
    game = build_game()
    games[game_id] = game
    game.user_id_to_agent_map[user_id] = game.simulation.agents[5]

    hash_id = hashids.encode(game_count)
    game.hash_id = hash_id
    hash_id_to_game_map[hash_id] = game

    # TODO (Yifan): Fast forward the game to the starting week
    # TODO (Yifan): Associate the player with a certain game agent

    token_payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
        'iat': datetime.datetime.utcnow(),
        'gameId': game_id,
        'userId': user_id
    }

    return jsonify({
        'token': jwt.encode(token_payload, 'SECRET_KEY'),
        'hashId': hash_id,
    })


@app.route('/api/get_game_param', methods=['GET'])
def get_game_param():
    """ respond the game parameter value to the client """

    token = request.args.get('token')
    token_payload = jwt.decode(token, 'SECRET_KEY')

    game_id = token_payload['gameId']
    game = games[game_id]
    if game == None:
        abort(401)

    user_id = token_payload['userId']
    agent = game.user_id_to_agent_map[user_id]
    if agent == None:
        abort(401)

    param = request.args.get('paramName')
    if param == 'inventory':
        value = agent.inventory_level()
    elif param == "urgent":
        if not isinstance(agent, agents.HealthCenter):
            abort (400)
        value = agent.urgent
    elif param == "non-urgent":
        if not isinstance(agent, agents.HealthCenter):
            abort (400)
        value = agent.non_urgent
    else:
        print "Unsupported parameter type " + param
        abort(400)

    return str(value)

@app.route('/api/get_game_history_param', methods=['GET'])
def get_game_history_param():
    """ respond the request of querying the value of a simulation parameter. """

    token = request.args.get('token')
    cycle = int(request.args.get('cycle'))
    agent_id = int(request.args.get('agentId'))
    param = request.args.get('paramName')

    token_payload = jwt.decode(token, 'SECRET_KEY')
    game_id = token_payload['gameId']

    game = games[game_id]
    if game == None:
        abort(401)

    agent = game.simulation.agents[agent_id]
    if agent == None:
        abort(404)

    if not agent.is_history_available(cycle):
        abort(404)

    history = agent.get_history_item(cycle)
    try:
        if param == "inventory":
            value = history['inventory']
        elif param == "urgent":
            if not isinstance(agent, agents.HealthCenter):
                abort (400)
            value = history['patient'][0]
        elif param == "non-urgent":
            if not isinstance(agent, agents.HealthCenter):
                abort (400)
            value = history['patient'][1]
        else:
            raise ValueError("Not supported paramter type")
    except Exception as e:
        print e
        abort(400)

    return str(value)


@app.route('/api/make_decision', methods=['GET'])
def make_decision():
    ''' respond the request of posting the value of a decision parameters. '''

    token = request.args.get('token')
    token_payload = jwt.decode(token, 'SECRET_KEY')

    game_id = token_payload['gameId']
    game = games[game_id]

    user_id = token_payload['userId']

    decision_name = request.args.get('decisionName')
    decision_value = request.args.get('decisionValue')

    decision = GameDecision()
    decision.user_id = user_id
    decision.decision_name = decision_name
    decision.decision_value = int(decision_value)
    game.decisions.append(decision)

    print game.decisions

    return '{}'

# @app.route("/api/get_user_id")
# def id_generator():
#     """ respond the request from the client to generate a unique user_id """

#     user_id = str(uuid.uuid4())
#     player_id = int(list(players)[-1].lstrip('id')) + 1
#     player_id = 'id%i' % player_id
#     players[player_id] = user_id

#     return players[player_id]


@app.route('/api/next_period', methods=['GET', 'POST'])
def next_cycle():
    """ respond the request of moving the simulation to the next cycle. """

    token = request.args.get('token')
    token_payload = jwt.decode(token, 'SECRET_KEY')

    game_id = token_payload['gameId']
    game = games[game_id]

    # game.get_current_history_item(game, now=1)

    # game.runner.next_cycle()

    game.runner._make_decision(game.cycle)
    game.simulation.agents[5].decisions = []
    game.parse_decisions()
    game.runner._apply_decision(game.cycle)
    game.cycle = game.cycle + 1
    game.runner._update_patient(game.cycle)
    game.runner._update_agents(game.cycle)
    game.runner._update_network(game.cycle)
    game.runner._exogenous_event(game.cycle)

    week = game.simulation.now
    return str(week)


@app.route("/api/update_graphs", methods=['GET'])
def update():
    ''' updates graphs' images for the gamettes for each player. '''

    token = request.args.get('token')
    token_payload = jwt.decode(token, 'SECRET_KEY')

    game_id = token_payload['game_id']
    game = games[game_id]

    user_id = token_payload['user_id']

    graph(game, path, user_id=user_id)

    return "updated!"


@app.route('/Charts/<filename>')
def send_image(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
