import os

# Import environment variables from .env file
if os.path.exists('.env'):
    print("Importing environment from .env...")
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

HOST = os.environ.get('HOST') or ''
PORT = os.environ.get('PORT') or 4000

LOBBY_ROOM_NAME = "Lobby"
LOBBY_ROOM_DESC = "Welcome to MtGMUD!!\nYou are in the lobby area. Type 'help' to get started!"

clients = []
tables = []