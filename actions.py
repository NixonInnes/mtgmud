import mud
import db
import funcs


def do_quit(client, args):
    client.msg_self("\nYou are wracked with uncontrollable pain as you are extracted from the Matrix.\n")
    client.transport.close()


def do_look(client, args):
    if client.user.room is not None:
        client.msg_self(client.user.room.look())


def do_who(client, args):
    buff = "\n===== USER ========== ROOM ====="
    for c in mud.clients:
        #TODO: fix formatting
        buff += "\n\t{}\t{}".format(c.user.name, c.user.room.name)
    buff += "\n\nOnline: {}".format(len(mud.clients))
    client.msg_self(buff)


def do_card(client, args):
    def find(args):
        card_name = ' '.join(args)
        card = db.session.query(db.Card).filter_by(name=card_name).first()
        if card is None:
            client.msg_self("\nCould not find card: {}".format(card_name))
            return
        buff = "\n{} \t {}".format(card.name, card.manaCost)
        buff += "\n{}".format(card.type)
        buff += "\n{}".format(card.text)
        if card.loyalty is not None:
            buff += "\n[{}]".format(card.loyalty)
        if card.power is not None and card.toughness is not None:
            buff += "\n[{}/{}]".format(card.power, card.toughness)
        client.msg_self(buff)

    table = { 'find': find }

    if args is not None:
        if args[0] in table:
            table[args[0]](args[1:] if len(args) > 1 else None)
            return
        else:
            find(args)
            return
    client.msg_self("\nCard what??")


def do_rooms(client, args):
    buff = "\n========== ROOMS =========="
    for room in mud.rooms:
        buff += "\n\t{}".format(room.name)
    client.msg_self(buff)


def do_room(client, args):
    def create(args):
        if args is None:
            client.msg_self("\nPlease specify a room name.\nUsage: room create <room name>")
            return
        room_name = ' '.join(args)
        if funcs.get_room(room_name) is not None:
            client.msg("\nThe room name '{}' is already taken, sorry.".format(room_name))
            return
        room = db.Room(name=str(room_name))
        db.session.add(room)
        db.session.commit()
        mud.rooms.append(room)
        client.msg_self("\nRoom created: {}".format(room.name))

    def delete(args):
        if args is None:
            client.msg_self("\nDelete which room?\nUsage: room delete <room name>")
            return
        room_name = ' '.join(args)
        room = funcs.get_room(room_name)
        if room is not None:
            mud.rooms.remove(room)
            db.session.delete(room)
            db.session.commit()
            client.msg_self("Room \"{}\" has been deleted.\n".format(room.name))
            return
        client.msg_self("Room \"{}\" was not found.\n".format(room_name))

    table = {
        'create': create,
        'delete': delete
    }

    if args is not None:
        if args[0] in table:
            table[args[0]](args[1:] if len(args) > 1 else None)
            return

    client.msg_self("\nRoom what?!")


def do_goto(client, args):
    if args is None:
        client.msg_self("\nGoto where?!")
        return
    room_name = ' '.join(args)
    room = funcs.get_room(room_name)
    if room is not None:
        if client.user.room is not None:
            client.user.room.occupants.remove(client)
        client.user.room = room
        client.user.room.occupants.append(client)
        do_look(client, None)
        return
    client.msg_self("\nGoto where?!")


actions = {
    'quit':  do_quit,
    'look':  do_look,
    'who':   do_who,
    'rooms': do_rooms,
    'room':  do_room,
    'goto':  do_goto,
    'card':  do_card
}

