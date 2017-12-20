''' Server builds a flask server to provide APIs for the game '''

from flask import Flask
from flask import request
import jwt
import datetime

from game import build_game
from simulation_builder import build_simulation

app = Flask(__name__)
games = {}


@app.route('/api/create_game', methods=['POST'])
def new_game():
    ''' respond to the request from the client to create a new game '''

    user_id = request.args.get('user_id')
    game_id = request.args.get('game_id')

    game = build_game(simulation_builder)
    games[game_id] = game

    token_payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
        'iat': datetime.datetime.utcnow(),
        'game_id': game_id,
        'user_id': user_id,
    }

    return jwt.encode(token_payload, 'SECRET_KEY')


@app.route('/api/create_game', methods=['POST'])
def get_game_param():
    ''' respond the request of querying the value of a simulation parameter. '''

    game_id = request.args.get('game_id')
    game = games[game_id]

    param = request.args.get('param_name')
    value = 0
    if param == 'inventory':
        value = game.simulation.health_centers[0].inventory()


    return str(value)
