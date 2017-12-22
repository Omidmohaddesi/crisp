''' Server builds a flask server to provide APIs for the game '''

from flask import Flask, send_from_directory
from flask import request
from flask_restful import Resource, Api
import uuid
import jwt
import datetime

from game import build_game
from simulation_builder import build_simulation

app = Flask(__name__, static_folder='Charts')
api = Api(app)

games = {}
parameters = []
players = {'id0': 0}
decisions = []


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://www.neumadscience.com')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@app.route('/api/create_game', methods=['GET'])
def new_game():
    ''' respond to the request from the client to create a new game '''

    user_id = request.args.get('user_id')
    game_id = request.args.get('game_id')
    start_week = request.args.get('start_week')

    game = build_game(simulation_builder)
    games[game_id] = game

    token_payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
        'iat': datetime.datetime.utcnow(),
        'game_id': game_id,
        'user_id': user_id
    }

    par = {
        "user_id": user_id,
        "game_id": game_id,
        "week": start_week,
        "inventory": 0,
        "urgent": 0,
        "non_urgent": 0,
        "on_order_DS1": 0,
        "on_order_DS2": 0,
        "received_DS1": 0,
        "received_DS2": 0
    }
    parameters.append(par)

    dec = {
        "user_id": user_id,
        "game_id": game_id,
        "week": start_week,
        "order_type": "",
        "allocation_type": "",
        "satisfied_urgent": 0,
        "satisfied_non_urgent": 0,
        "order_amount_DS1": 0,
        "order_amount_DS2": 0,
        "order_amount_total": 0
    }
    decisions.append(dec)

    return jwt.encode(token_payload, 'SECRET_KEY')


@app.route('/api/get_game_param', methods=['GET'])
def get_game_param():
    ''' respond the request of querying the value of a simulation parameter. '''

    token = request.args.get('token')
    token_payload = jwt.decode(token, 'SECRET_KEY')

    game_id = token_payload['game_id']
    game = games[game_id]

    user_id = token_payload['user_id']

    param = request.args.get('param_name')
    value = 0

    if param == 'week':
        value = game.simulation.health_centers[0].time()
        for i in parameters:
            if i['user_id'] == user_id:
                i['week'] = value

    if param == 'inventory':
        value = game.simulation.health_centers[0].inventory()
        for i in parameters:
            if i['user_id'] == user_id:
                i['inventory'] = value

    if param == 'urgent':
        value = game.simulation.health_centers[0].urgent()
        for i in parameters:
            if i['user_id'] == user_id:
                i['urgent'] = value

    if param == 'non_urgent':
        value = game.simulation.health_centers[0].non_urgent()
        for i in parameters:
            if i['user_id'] == user_id:
                i['non_urgent'] = value

    if param == 'on_order_DS1':
        on_order = game.simulation.health_centers[0].on_order()
        value = sum(i['amount'] for i in on_order if i['destination'] == 2)
        for i in parameters:
            if i['user_id'] == user_id:
                i['on_order_DS1'] = value

    if param == 'on_order_DS2':
        on_order = game.simulation.health_centers[0].on_order()
        value = sum(i['amount'] for i in on_order if i['destination'] == 3)
        for i in parameters:
            if i['user_id'] == user_id:
                i['on_order_DS2'] = value

    if param == 'received_DS1':
        delivery = game.simulation.health_centers[0].delivery()
        value = sum(i["item"]["amount"] for i in delivery if i["src"] == 2)
        for i in parameters:
            if i['user_id'] == user_id:
                i['received_DS1'] = value

    if param == 'received_DS2':
        delivery = game.simulation.health_centers[0].delivery()
        value = sum(i["item"]["amount"] for i in delivery if i["src"] == 3)
        for i in parameters:
            if i['user_id'] == user_id:
                i['received_DS2'] = value

    return str(value)


class Decision(Resource):
    @app.route('/api/make_decision', methods=['POST'])
    def make_decision(self):
        ''' respond the request of posting the value of a decision parameters. '''

        token = request.args.get('token')
        token_payload = jwt.decode(token, 'SECRET_KEY')

        game_id = token_payload['game_id']
        game = games[game_id]

        user_id = token_payload['user_id']

        decision_name = request.args.get('decision_name')
        decision_value = request.args.get('decision_value')

        if decision_name == 'order_type':
            for i in decisions:
                if i['user_id'] == user_id:
                    i['order_type'] = decision_value

        if decision_name == 'allocation_type':
            for i in decisions:
                if i['user_id'] == user_id:
                    i['allocation_type'] = decision_value

        if decision_name == 'satisfied_urgent':
            for i in decisions:
                if i['user_id'] == user_id:
                    i['satisfied_urgent'] = decision_value

        if decision_name == 'satisfied_non_urgent':
            for i in decisions:
                if i['user_id'] == user_id:
                    i['satisfied_non_urgent'] = decision_value

        if decision_name == 'order_amount_DS1':
            for i in decisions:
                if i['user_id'] == user_id:
                    i['order_amount_DS1'] = decision_value

        if decision_name == 'order_amount_DS2':
            for i in decisions:
                if i['user_id'] == user_id:
                    i['order_amount_DS2'] = decision_value

        if decision_name == 'order_amount_total':
            for i in decisions:
                if i['user_id'] == user_id:
                    i['order_amount_total'] = decision_value

        return str(decision_value)


@app.route("/api/get_user_id")
def id_generator():
    ''' respond the request from the client to generate a unique user_id '''

    user_id = str(uuid.uuid4())
    player_id = int(list(players)[-1].lstrip('id')) + 1
    player_id = 'id%i' % player_id
    players[player_id] = user_id

    return players[player_id]


@app.route('/Charts/<filename>')
def send_image(filename):
    return send_from_directory(app.static_folder, filename)


api.add_resource(Decision, '/api/make_decision')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
