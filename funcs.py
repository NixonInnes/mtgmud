import mud
import db
from actions import actions


def login(client, args):
    if len(args) == 0:
        client.msg_self("Login error.\nLogin: <username> <password>\nNew Account: register <username> <password> <password>\n")
        return

    if args[0] == 'register':
        if len(args) == 4 and args[2] == args[3]:
            if client.session.query(db.User).filter_by(name=args[1]).first() is None:
                client.user = db.User(name=args[1], password=args[2])
                client.session.add(client.user)
                client.session.commit()
                mud.users.append(client.user)
                client.authd = True
                actions['goto'](client, ['Lobby'])
                return
            else:
                client.msg_self("Username \"{}\" is already taken, sorry.\n".format(args[1]))

    if len(args) == 2:
        dbuser = client.session.query(db.User).filter_by(name=args[0]).first()
        if dbuser is not None:
            if dbuser.verify_password(args[1]):
                client.user = dbuser
                client.authd = True
                actions['goto'](client, ['Lobby'])
                return

    client.msg_self("Login error.\nLogin: <username> <password>\nNew Account: register <username> <password> <password>\n")


def get_room(room_name):
    for room in mud.rooms:
        if room.name == room_name:
            return room
    return None

def get_user(user_name):
    for user in mud.users:
        if user.name == user_name:
            return user
    return None
