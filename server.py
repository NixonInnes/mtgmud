import asyncio
import mud
import db
import funcs
from channels import channels
from actions import actions

clients = []

def startup():
    session = db.Session()

    # Load rooms
    rooms = session.query(db.Room).all()
    for room in rooms:
        mud.rooms.append(room)
    session.close()

    # Create a lobby if there are no rooms
    if len(mud.rooms) < 1:
        mud.create_lobby()

class Protocol(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport
        self.addr = transport.get_extra_info('peername')
        self.authd = False
        self.session = db.Session()
        self.user = None
        self.room = None

        print("Connected: {}".format(self.addr))
        clients.append(self)
        self.msg_self("\nWelcome to MtGMUD!!\n")

    def data_received(self, data):
        #print("[DEBUG]{}: {}".format(self.addr, data.decode()))
        msg = data.decode().strip()
        args = msg.split()

        if not self.authd:
            funcs.login(self, args)
            return

        if msg:
            if msg[0] in channels:
                self.msg_channel(msg[0], msg[1:])
                self.get_prompt()
                return

            if args[0] in actions:
                actions[args[0]](self, args[1:] if len(args) > 1 else None)
                self.get_prompt()
                return

        self.get_prompt()

    def get_prompt(self):
        self.transport.write("\n>>> ".encode())

    def msg_self(self, msg):
        self.transport.write(msg.encode())

    def msg_channel(self, channel, msg):
        for client in clients:
            if client is self:
                client.transport.write("[{}] You: {}".format(channels[channel], msg).encode())
            else:
                client.transport.write("\n[{}] {}: {}".format(channels[channel], self.addr, msg).encode())

    def connection_lost(self, ex):
        print("Disconnected: {}".format(self.addr))
        mud.users.remove(self)
        clients.remove(self)


if __name__ == '__main__':
    print("Server starting up...")

    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(Protocol, host=mud.HOST, port=mud.PORT)
    server = loop.run_until_complete(coroutine)

    print("Server now listening on {}".format(server.sockets[0].getsockname()))

    print("Running start-up tasks...")
    startup()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Keyboard Interrupt! Exiting...")
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()