''' Server builds a flask server to provide APIs for the game '''

import json
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/api/new_game', methods=['GET'])
def new_game():
    ''' respond to the request from the client to create a new game '''
    info_json = request.args.get('info')
    info = json.loads(info_json)
    print info
    return "hello"
