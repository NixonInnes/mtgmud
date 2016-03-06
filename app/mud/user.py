from asyncio import Protocol

from .colour import colourify
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
        self.table = None
        self.db = None

        self.flags = []

        print("Connected: {}".format(self.addr))
        server.connected.append(self)

        #TODO: Add a welcome function
        actions['help'](self, ['welcome'])
        self.get_prompt()

    def data_received(self, data):
        msg = data.decode().strip()
        args = msg.split()

        if self.authd is False:
            actions['login'](self, args)
            return

        if len(args) > 0 and not args[0] == 'alias':
            for alias in self.aliases:
                if alias in args:
                    args[args.index(alias)] = str(self.aliases[alias])
            args = str(' '.join(args)).split()

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
        else:
            if self.table is not None:
                actions['table'](self, None)
            elif self.room is not None:
                actions['look'](self, None)

        self.get_prompt()

    def get_prompt(self):
        buff = "\n\n"
        if self.name is not None:
            buff += "&B<&x &c{}&x".format(self.name)
            if self.deck is not None:
                buff += " &B||&x &c{}&x &C(&x&c{}&x&C) &B>&x".format(self.deck.name, self.deck.no_cards)
            if self.table is not None:
                buff += " &B||&x &YH&x:&Y{}&x &GL&x:&G{}&x ".format(len(self.table.hands[self]), len(self.table.libraries[self]))
        buff += "&w>> &x"
        self.msg_self(buff)

    def msg_self(self, msg):
        self.msg_user(self, msg)

    @staticmethod
    def msg_user(user, msg):
        msg = colourify(msg)
        user.transport.write(msg.encode())

    def load(self, dbUser):
        for user in server.users:
            if user.db.id is dbUser.id:
                self.msg_user(user, "\nYou have signed in from another location!")
                actions['quit'](user, None)
        self.authd = True
        self.name = str(dbUser.name)
        self.aliases = dbUser.aliases
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
        
        if self.authd:
            self.save()
            server.users.remove(self)
            self.room.occupants.remove(self)
