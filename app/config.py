import os

HOST = os.environ.get('HOST') or ''
PORT = os.environ.get('PORT') or 4000

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get('DATABASE') or 'sqlite:///' + os.path.join(basedir, 'database.sqlite')

LOBBY_ROOM_NAME = "Lobby"
LOBBY_ROOM_DESC = "Welcome to MtGMUD!!\nYou are in the lobby area. Type 'help' to get started!"