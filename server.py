import json
import logging
import time
import uuid
import socket
import threading

HOST = '127.0.0.1'
PORT = 9999

users = {}
crosswords = {}

#================================ ↓ database assumptions ↓ =================================#

users ["userID"] = {
    "conn": "",
    "addr": "",
    "username": "",
    "stats": {}
}

crosswords = {
    "crossWordID": {
        "name": "", # use as identifier
        "gridSize": [],  # dynamic grid size
        "visibleSquares": [], # squares with visible letters in the game
        "clues": [], # list of clues / questions
        "lateralWords": { 
            "word": {
                "start": (0, 0),
                "end": (0, 4)
            }
        },
        "verticalWords": {
            "word": {
                "start": (0, 0),
                "end": (0, 4)
            }
        }
    }
}

#==================================== ↓ server code ↓ ==========================================#

def InitiateServer():

    print(f"\nInitiating server to run on {HOST}:{PORT}...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()

        while True:
            conn, addr = server.accept()
            users["userID"] = {
                    "conn": conn,
                    "addr": addr,
                    "username": "",
                    "stats": {}
                }

        
# CS5003-P3-Crosswords git init git add README.md git commit -m Add server script (240032527) git branch -M main git remote add origin https://github.com/almightydon7/CS5003-P3-Crosswords.git git push -u origin main
# CS5003-P3-Crosswords git init git add server.py git commit -m Add server script (240032527) git branch -M main git remote add origin https://github.com/almightydon7/CS5003-P3-Crosswords.git git push -u origin main
