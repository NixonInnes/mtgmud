import mud
import db
import funcs


def quit_(client, args):
    if args is None:
        client.msg_self("\nYou are wracked with uncontrollable pain as you are extracted from the Matrix.\n")
        client.transport.close()
        return
    client.msg_self("Quit what?\n")

def look(client, args=None):
    if client.room is not None:
        client.msg_self(client.room.look())


def room_create(client, args):
    if args is None:
        client.msg_self("Create and room and call it what?\nUsage: croom <room name>\n")
        return
    room_name = ' '.join(args)
    if funcs.get_room(room_name) is not None:
        client.msg("The room name \"{}\" is already taken, sorry.".format(room_name))
        return
    room = db.Room(name=str(room_name))
    client.session.add(room)
    client.session.commit()
    mud.rooms.append(room)
    client.msg_self("Room created: {}".format(room.name))


def room_delete(client, args):
    if args is None:
        client.msg_self("Delete which room?\nUsage: droom <room name>\n")
        return
    room_name = ' '.join(args)
    room = funcs.get_room(room_name)
    if room is not None:
        mud.rooms.pop(room)
        if room.permanent:
            client.session.delete(room)
            client.session.commit()
        client.msg("Room \"{}\" has been deleted.\n".format(room.name))
        return
    client.msg("Room \"{}\" was not found.\n".format(room_name))


def room_goto(client, args):
    if args is None:
        client.msg_self("Goto where?\n")
        return
    room_name = ' '.join(args)
    room = funcs.get_room(room_name)
    if room is not None:
        if client.room is not None:
            client.room.occupants.remove(client)
        client.room = room
        client.room.occupants.append(client)
        look(client)


actions = {
    'quit': quit_,
    'look': look,
    'croom': room_create,
    'droom': room_delete,
    'goto': room_goto
}

