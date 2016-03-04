from asyncio import Protocol

from app import db, server

from app.player import actions, channels

class User(Protocol):

    def connection_made(self, transport):
        self.transport = transport
        self.addr = transport.get_extra_info('peername')
        self.authd = False
        self.name = None
        self.admin = False
        self.room = None
        self.db = None

        self.flags = []

        print("Connected: {}".format(self.addr))
        server.connected.append(self)

        #TODO: Add a welcome function
        self.msg_self("\n########## Welcome to MtGMUD!! ##########\n\nLogin: <username> <password>\nRegister: register <username> <password> <password>")
        self.get_prompt()

    def data_received(self, data):
        msg = data.decode().strip()
        args = msg.split()

        if self.authd is False:
            actions['login'](self, args)
            return

        if msg:
            if msg[0] in channels:
                channels[msg[0]](self, msg[1:])
                self.get_prompt()
                return

            if args[0] in actions:
                actions[args[0]](self, args[1:] if len(args) > 1 else None)
                self.get_prompt()
                return

            self.msg_self("\nHuh?")
        self.get_prompt()

    def get_prompt(self):
        # [username]<deck (60)>>>
        buff = "\n"
        if self.name is not None:
            buff += "[{}]".format(self.name)
            if self.deck is not None:
                buff += "<{} ({})>".format(self.deck.name, self.deck.no_cards)
        buff += ">> "
        self.transport.write(buff.encode())

    def msg_self(self, msg):
        self.transport.write(msg.encode())

    @staticmethod
    def msg_user(user, msg):
        user.transport.write(msg.encode())

    def load(self, dbUser):
        for user in server.users:
            if user.db.id is dbUser.id:
                self.msg_user(user, "\nYou have signed in from another location!")
                actions.do_quit(user, None)
        self.authd = True
        self.name = str(dbUser.name)
        self.admin = bool(dbUser.admin)
        self.deck = dbUser.deck
        self.decks = dbUser.decks
        self.db = dbUser
        server.users.append(self)
        lobby = server.get_lobby()
        self.room = lobby
        lobby.occupants.append(self)

    def save(self):
        self.db.name = self.name
        self.db.admin = self.admin
        db.session.commit()

    def connection_lost(self, ex):
        print("Disconnected: {}".format(self.addr))
        server.connected.remove(self)
        server.users.remove(self)

        if self.authd:
            self.save()
            self.user.room.occupants.remove(self.user)