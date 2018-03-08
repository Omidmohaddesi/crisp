import requests
import uuid

server_url = "http://127.0.0.1:5000/api/"


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
    while True:
        print("How many human players (1 - 6)?:")
        choice = raw_input("# ")

        try:
            num_human_players = int(choice)
        except ValueError:
            print "Invalid input. Please try again."
            continue

        if num_human_players > 6 or num_human_players < 1:
            print("Number of players must be between 1 to 6. Please try again.")
            continue

        req = requests.get(server_url + 'create_game', {
            'user_id': str(uuid.uuid4()),
            'game_id': str(uuid.uuid4()),
            'start_week': 0,
            'num_human_players': num_human_players,
        })

        print req



def join_game():
    pass


def play_game():
    pass


if __name__ == '__main__':
    main()
