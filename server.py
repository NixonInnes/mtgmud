import sys
import socketserver
import ssl

from app import config, db, mud
from app.player import parser, acts
from app.presenters import presenters


class User(socketserver.BaseRequestHandler):
    """Client connection, an instance per connection."""

    def setup(self):
        print("Connection received: {}".format(self.client_address))
        self.authd = False
        self.name = None
        self.room = None
        self.table = None
        self.db = None
        self.flags = []
        self.presenter = presenters['text'](self)
        mud.connected.append(self)

    def handle(self):
        acts.do_help(self, ['welcome'])
        while True:
            data = self.request.recv(1024)
            msg = data.decode('utf-8')
            parser.parse(self, msg)

    def load(self, dbUser):
        other = mud.get_user(dbUser.name)
        if other:
            other.presenter.show_msg("You have signed in from another location!")
            other.disconnect()

        self.authd = True
        self.name = str(dbUser.name)
        self.flags = dict(dbUser.flags)
        self.deck = dbUser.deck
        self.decks = dbUser.decks
        self.db = dbUser
        mud.add_user(self)
        self.room = mud.get_room(config.LOBBY_ROOM_NAME)
        self.room.occupants.append(self)

    def save(self):
        self.db.name = self.name
        self.db.flags = self.flags
        db.session.commit()

    def send(self, msg):
        self.request.send(msg.encode('utf-8'))

    def disconnect(self):
        self.save()
        self.request.close()

    def finish(self):
        print("Connection closed: {}".format(self.client_address))
        if self in mud.users:
            mud.rem_user(self)


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Main server"""
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address, handler):
        socketserver.TCPServer.__init__(self, server_address, handler)
    
    def get_request(self):
        (sock, addr) = socketserver.TCPServer.get_request(self)
        return ssl.wrap_socket(sock, server_side=True, certfile="app/certs/cert.pem"), addr


def main():
    print("Starting server on {}:{} ...".format(config.HOST, config.PORT))
    server = Server((config.HOST, config.PORT), User)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
