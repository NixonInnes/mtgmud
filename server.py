import asyncio
import mud
import db
import funcs
from channels import channels
from actions import actions

def startup():
    # Check for Lobby & create one if not
    if funcs.get_lobby() is None:
        print("No lobby found, creating...")
        lobby = db.Room(
            name=mud.LOBBY_ROOM_NAME,
            description=mud.LOBBY_ROOM_DESC
        )
        db.session.add(lobby)
        db.session.commit()

    # Clean rooms if the server shutdown unexpectedly
    for room in db.session.query(db.Room).all():
        room.occupants.clear()

    # Populate cards if table is empty
    if len(db.session.query(db.Card).all()) < 1:
        print("Card database is empty. \nNow populating...")
        funcs.update_cards()


class Protocol(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport
        self.addr = transport.get_extra_info('peername')
        self.user = None

        print("Connected: {}".format(self.addr))
        mud.clients.append(self)
        #TODO: Add a welcome function
        self.msg_self("\n########## Welcome to MtGMUD!! ##########\n\nLogin: <username> <password>\nRegister: register <username> <password> <password>")
        self.get_prompt()

    def data_received(self, data):
        msg = data.decode().strip()
        args = msg.split()

        if self.user is None:
            funcs.login(self, args)
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
        mud.clients.remove(self)
        if self.user.room:
            self.user.room.occupants.remove(self.user)


if __name__ == '__main__':
    print("Server starting up...")

    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(Protocol, host=mud.HOST, port=mud.PORT)
    server = loop.run_until_complete(coroutine)

    print("Running start-up tasks...")
    startup()
    print("Completed start-up.")
    print("Server now listening on {}".format(server.sockets[0].getsockname()))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Keyboard Interrupt! \nExiting...")
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
