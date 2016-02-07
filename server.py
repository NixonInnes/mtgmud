import asyncio
import mud
import db
import funcs
from channels import channels
from actions import actions

def startup():
    # Load rooms
    rooms = db.session.query(db.Room).all()
    for room in rooms:
        mud.rooms.append(room)

    # Create a lobby if there are no rooms
    if len(mud.rooms) < 1:
        mud.create_lobby()

    # populate cards if table is empty
    if len(db.session.query(db.Card).all()) < 1:
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
        self.transport.write("\n>>> ".encode())

    def msg_self(self, msg):
        self.transport.write(msg.encode())

    def msg_client(self, client, msg):
        client.transport.write(msg.encode())

    def connection_lost(self, ex):
        print("Disconnected: {}".format(self.addr))
        mud.clients.remove(self)


if __name__ == '__main__':
    print("Server starting up...")

    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(Protocol, host=mud.HOST, port=mud.PORT)
    server = loop.run_until_complete(coroutine)

    print("Server now listening on {}".format(server.sockets[0].getsockname()))

    print("Running start-up tasks...")
    startup()
    print("Completed start-up.")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Keyboard Interrupt! Exiting...")
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
