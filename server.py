import sys
import socketserver

from app import config, mud
from app.player import parser
from app.presenters import presenters


class User(socketserver.BaseRequestHandler):
    """Client connection, an instance per connection."""

    def setup(self):
        print("Connection received from: {}".format(self.client_address))
        self.authd = False
        self.name = None
        self.room = None
        self.table = None
        self.db = None
        self.flags = []
        self.presenter = presenters['text'](self)
        mud.connected.append(self)

    def handle(self):
        while True:
            data = self.request.recv(1024)
            msg = data.decode('utf-8')
            parser.parse(self, msg)

    def load(self, dbUser):
        for user in mud.users:
            if user.db.id is dbUser.id:
                user.presenter.send_msg("You have signed in from another location!")

        self.authd = True
        self.name = str(dbUser.name)
        self.flags = dict(dbUser.flags)
        self.deck = dbUser.deck
        self.decks = dbUser.decks
        self.db = dbUser
        mud.users.append(self)
        lobby = mud.get_room(config.LOBBY_ROOM_NAME)
        self.room = lobby
        lobby.occupants.append(self)

    def send(self, msg):
        self.request.send(msg.encode('utf-8'))

    def disconnect(self):
        self.request.close()


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Main server"""
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address, handler):
        socketserver.TCPServer.__init__(self, server_address, handler)


def main():
    print("Starting server on {}:{} ...".format(config.HOST, config.PORT))
    server = Server((config.HOST, config.PORT), User)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()