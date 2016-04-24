import os

SERVER_NAME = "MtGMUD"

HOST = '127.0.0.1'
PORT = 4000

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = 'sqlite:///' + os.path.join(basedir, 'database.sqlite')

ADMIN = "nix"

LOBBY_ROOM_NAME = "Lobby"
LOBBY_ROOM_DESC = "Welcome to MtGMUD!!\nYou are in the lobby area. Type 'help' to get started!"

BANNED_NAMES = ['admin', 'fuck', 'shit', 'asshole', 'ass', 'nigger']