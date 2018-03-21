import requests
import uuid
import sys

server_url = "http://127.0.0.1:5000/api/"
token = ""


def main():
    start_game()
    play_game()


def start_game():
    while True:
        print("Menu:")
        print("1. Start a new game")
        print("2. Join a game")
        choice = raw_input("# ")

        if choice == '1':
            new_game()
            return
        elif choice == '2':
            join_game()
            return
        else:
            print("No such option. Please try again.\n")


def new_game():
    global token
    num_human_players = take_integer_user_input('Number of human players (1 - 6)?', (1, 6))

    req = requests.get(server_url + 'create_game', {
        'user_id': str(uuid.uuid4()),
        'game_id': str(uuid.uuid4()),
        'start_week': 0,
        'num_human_players': num_human_players,
    })
    response = req.json()

    if req.status_code == 200:
        print("OK, Let your partners join game with token \"" + response['hash_id'] + "\".")
        token = response['token']
        return
    else:
        raise Exception("Failed, server returns " + str(req.status_code))


def join_game():
    pass


def play_game():
    while True:
        retrieve_game_param()
        make_decision()

def retrieve_game_param():
    cycle = take_integer_user_input('\nWhich cycle?')
    agent_id = take_integer_user_input('\nWhich agent (1 - 6)?')
    param = take_integer_user_input(
        '\nWhich parameter?\n'
        '\t1. inventory\n'
        '\t0. Done! Go to make a decision.\n'
    )

    if param = 0:
        return

    req = requests.get(server_url + 'create_game', {
        'token': token,
        'cycle': cycle,
        'agent': agent_id,
        'param': param,
    })


def make_decision():
    pass

def take_integer_user_input(prompt, range=(-sys.maxint - 1, sys.maxint)):
    while True:
        print(prompt)
        choice = raw_input('# ')

        try:
            integer = int(choice)
        except ValueError:
            print('Invalid input. Please try again.')
            continue

        if integer < range[0] or integer > range[1]:
            print('Invalid input. Please try again.')
            continue

        return integer


if __name__ == '__main__':
    main()
