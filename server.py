import json
import logging
import time
import uuid
import socket
import threading
import sqlite3

HOST = '127.0.0.1'
PORT = 9999
SERVER_RUNNING = None
lock = threading.Lock()

#============================= ↓ api & db structure assumptions ↓ ===============================#

client_to_server_actions = { 
    
    "action": "login",  # fields: username, password
    "action": "register",  # fields: username, password
    "action": "fetch_crossword",  # fields: crossword_id
    "action": "submit_answer",  # fields: crossword_id, clue_id, answer
    "action": "get_user_stats",  # fields: user_id
    "action": "update_crossword",  # fields: crossword_id, updated_data
    "action": "create_crossword",  # fields: name, gridSize, clues, words
    "action": "get_crossword_list",  # fields: none

}

server_to_client_actions = { 
    
    "action": "login_successful",  # fields: message, user_id
    "action": "login_unsuccessful",  # fields: message
    "action": "registration_successful",  # fields: message
    "action": "registration_unsuccessful",  # fields: message
    "action": "crossword_fetched",  # fields: crossword_id, name, gridSize, clues, visibleSquares
    "action": "crossword_not_found",  # fields: message
    "action": "answer_successful",  # fields: message
    "action": "answer_unsuccessful",  # fields: message
    "action": "user_stats",  # fields: user_id, solved_puzzles, puzzles_posted, total_time
    "action": "crossword_updated",  # fields: message, crossword_id
    "action": "crossword_creation_successful",  # fields: message, crossword_id
    "action": "crossword_creation_unsuccessful",  # fields: message
    "action": "crossword_list",  # fields: crossword_list

}

DB_users_table = {
    "connection": "",
    "address": "",
    "id": "",
    "username": "",
    "password": "",
    "registered": None,
    "stats": {}
}

DB_crosswords_table = {
    "crossWordID": {
        "name": "", # use as identifier
        "gridSize": [],  # dynamic grid size
        "visibleSquares": [], # squares with visible letters in the game
        "words": [], # list of all words for easy retrieval
        "clues": [], # list of clues / questions
        "lateralWords": { 
            "word": {
                "start": (0, 0),
                "end": (0, 0)
            }
        },
        "verticalWords": {
            "word": {
                "start": (0, 0),
                "end": (0, 0)
            }
        }
    }
}

#==================================== ↓ server code ↓ ==========================================#

def InitiateServer():

    print(f"\nInitiating server to run on {HOST} : {PORT} ")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((HOST, PORT))
            server.listen()
            print(f"\nServer running!  Host: {HOST}  Port: {PORT}")

            while True:
                connection, _ = server.accept()
                threading.Thread(target=UserHandler, args=(connection,), daemon=True).start()

    except Exception as e:
        print(f"\nError starting the server: {e}")

def UserHandler(connection):

    # db setup
    con = sqlite3.connect("nonExistent.db")
    cur = con.cursor()

    try:
        while True:

            data = connection.recv(1024).decode()
            communication = json.loads(data)
            action = communication.get("action")

            if not data:
                break

            if action == "login":
                username = communication['username']
                password = communication['password']

                with lock:

                    # check db for user
                    cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                    user_data = cur.fetchone()

                    # check details match
                    if user_data:
                        response = {"action": "login_successful"}
                    else:
                        response = {"action": "login_unsuccessful"}
                    connection.sendall(json.dumps(response).encode())
                    
            if action == "fetch_crossword":
                id = communication['id']

                with lock:

                    # check db for crossword
                    cur.execute("SELECT * FROM crosswords WHERE id = ?", (id))
                    crossword_data = cur.fetchone()

                    if crossword_data:
                        response = {
                            "action": "crossword_fetched",
                            "crossword_id": crossword_data[0],  
                            "name": crossword_data[1],  
                            "gridSize": crossword_data[2],  
                            "visibleSquares": crossword_data[3],  
                            "words": crossword_data[4],  
                            "clues": crossword_data[5],  
                            "lateralWords": json.loads(crossword_data[6]), # format in json in db
                            "verticalWords": json.loads(crossword_data[7]) # format in json in db
                        }

                    else:
                        response = {"action": "failed_to_fetch_crossword"}

                    connection.sendall(json.dumps(response).encode())

    except Exception as e:
        print(f"Error: {e}")

    return

#==============================================================================================#

if __name__ == "__main__":

    InitiateServer()