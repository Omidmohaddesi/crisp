''' Server builds a flask server to provide APIs for the game '''

from flask import Flask
from flask import request

from game import build_game
from simulation_builder import build_simulation

app = Flask(__name__)
games = []


@app.route('/api/create_game', methods=['POST'])
def new_game():
    ''' respond to the request from the client to create a new game '''

    user_id = request.args.get('user_id')
    game_id = request.args.get('game_id')

    game = build_game(simulation_builder)
    games.append(game)

    return ""


def get_game_param():
    ''' respond the request of querying the value of a simulation parameter. '''

    game_id = request.args.get('game_id')
