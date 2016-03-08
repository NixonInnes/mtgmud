#!/usr/bin/env python
import os
# Import environment variables from .env file
if os.path.exists('.env'):
    print("Importing environment from .env...")
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

import asyncio
from app import config
from app.mud.user import User

def main():
    print("Server starting up...")
    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(User, host=config.HOST, port=config.PORT)
    server = loop.run_until_complete(coroutine)

    print("Server now listening on {}".format(server.sockets[0].getsockname()))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Keyboard Interrupt! \nExiting...")
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    main()