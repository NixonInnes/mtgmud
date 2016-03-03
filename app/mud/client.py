from asyncio import Protocol

from app import server
from app.player import actions, channels


class Client(Protocol):

    def connection_made(self, transport):
        self.transport = transport
        self.addr = transport.get_extra_info('peername')
        self.user = None

        print("Connected: {}".format(self.addr))
        server.clients.append(self)
        #TODO: Add a welcome function
        self.msg_self("\n########## Welcome to MtGMUD!! ##########\n\nLogin: <username> <password>\nRegister: register <username> <password> <password>")
        self.get_prompt()

    def data_received(self, data):
        msg = data.decode().strip()
        args = msg.split()

        if self.user is None:
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
        if self.user is not None:
            buff += "[{}]".format(self.user.name)
            if self.user.deck is not None:
                buff += "<{} ({})>".format(self.user.deck.name, self.user.deck.no_cards)
        buff += ">> "
        self.transport.write(buff.encode())

    def msg_self(self, msg):
        self.transport.write(msg.encode())

    def msg_client(self, client, msg):
        client.transport.write(msg.encode())

    def connection_lost(self, ex):
        print("Disconnected: {}".format(self.addr))
        server.clients.remove(self)

        if self.user:
            self.user.room.occupants.remove(self.user)
            server.users.remove(self.user)


