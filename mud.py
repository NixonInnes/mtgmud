import os


import db

# Import environment variables from .env file
if os.path.exists('.env'):
    print("Importing environment from .env...")
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

users = []
rooms = []



HOST = os.environ.get('HOST') or ''
PORT = os.environ.get('PORT') or 4000


def create_lobby():
    session = db.Session()
    lobby = db.Room(
        name="Lobby",
        description="This is the MtGMUD Lobby."
    )
    session.add(lobby)
    session.commit()
    session.close()
    rooms.append(lobby)


