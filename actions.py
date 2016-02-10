import os
from random import shuffle

import mud
import db, models
import funcs
import channels

#TODO: Tidy up the logic of these functions to be more consistent

def do_quit(client, args):
    client.msg_self("\nYou are wracked with uncontrollable pain as you are extracted from the Matrix.\n")
    client.transport.close()


def do_look(client, args):
    if client.user.room is not None:
        client.msg_self(client.user.room.look())


def do_who(client, args):
    buff = "\n||##########################[     USERS ONLINE     ]##########################||"
    buff += "\n||{:^37}||{:^37}||".format('USER', 'ROOM')
    buff += "\n||=====================================||=====================================||"
    for c in mud.clients:
        #TODO: fix formatting
        buff += "\n||{:^37}||{:^37}||".format(c.user.name, c.user.room.name)
    #buff += "|| Online: {}".format(len(mud.clients))
    buff += "\n||############################################################################||"
    client.msg_self(buff)


def do_help(client, args):
    if args is None:
        file = open('help/help', 'r')
    else:
        filename = os.path.join('help/',' '.join(args))
        if os.path.isfile(filename):
            file = open(filename, 'r')
        else:
            file = open('help/help', 'r')
    help_ = file.read()
    file.close()
    client.msg_self(help_)


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

    verbs = {
        'create': create,
        'delete': delete
    }

    if args is not None:
        if args[0] in verbs:
            verbs[args[0]](args[1:] if len(args) > 1 else None)
            return

    client.msg_self("\nRoom what?!")


def do_goto(client, args):
    if args is None:
        client.msg_self("\nGoto where?!")
    else:
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


def do_deck(client, args):
    if args is None:
        if client.user.deck is not None:
            client.msg_self(client.user.deck.show())
            return

    def create(args):
        if args is None:
            client.msg_self("\nPlease specify a deck name.\nUsage: deck new <deck_name>")
        else:
            deck_name = ' '.join(args)
            for d in client.user.decks:
                if d.name == deck_name:
                    client.msg_self("You already have a deck named '{}'.".format(deck_name))
                    return
            new_deck = db.Deck(
                name = deck_name,
                owner_id = client.user.id,
                cards = {}
            )
            db.session.add(new_deck)
            client.user.decks.append(new_deck)
            db.session.commit()
            client.user.deck = new_deck
            client.msg_self("Created new deck '{}'.".format(new_deck.name))

    def set(args):
        if args is None:
            client.msg_self("\nSet what?!\nUsage: deck set <deck_name>")
        else:
            deck_name = ' '.join(args)
            for d in client.user.decks:
                if d.name == deck_name:
                    client.user.deck_id = d.id
                    client.user.deck = d
                    client.msg_self("{} is now your active deck.".format(d.name))
                    return
            client.msg_self("Deck '{}' not found.".format(deck_name))


    def add(args):
        if args is None:
            client.msg_client("\nAdd what?!\nUsage: deck add <card_name>")
            return

        if client.user.deck is None:
            client.msg_self("\nYou do not have an active deck. Use 'deck set <deck_name>' to set an active deck.")
            return

        card_name = ' '.join(args)
        s_card = db.session.query(db.Card).filter_by(name=card_name).first()

        if s_card is None:
            client.msg_self("\nCard '{}' not found.".format(card_name))
            return

        if s_card.id in client.user.deck.cards:
            client.user.deck.cards[s_card.id] += 1
        else:
            client.user.deck.cards[s_card.id] = 1

        db.session.add(client.user.deck)
        db.session.commit()
        client.msg_self("\nAdded '{}' to {}.".format(card_name, client.user.deck.name))



    verbs = {
        'create': create,
        'add': add,
        'set': set
    }

    if args is None:
        if client.user.deck is None:
            client.msg_self("\nYou do not have an active deck. Use 'deck set <deck_name>' to set an active deck.")
        else:
            client.msg_self(client.user.deck.show())
    else:
        if args[0] in verbs:
            verbs[args[0]](args[1:] if len(args) > 1 else None)
        else:
            client.msg_self("\nDeck what?!")


def do_decks(client, args):
    buff = "\n##### Decks #####"
    for deck in client.user.decks:
        buff += "\n{}[{}] {}".format('*' if deck == client.user.deck else '', deck.no_cards, deck.name)
    client.msg_self(buff)


def do_table(client, args):
    def create(args):
        if args is None:
            do_help(client, ['table'])
            return
        table_name = ' '.join(args)
        table_ = models.Table(client, table_name)
        mud.tables.append(table_)
        client.user.table = table_
        client.user.room.tables.append(table_)


    def stack(args):
        if client.user.table is None or client.user.deck is None:
            do_help(client, ['table', 'stack'])
            return
        client.user.table.libraries[client.user] = shuffle(client.user.deck.cards.get())
        channels.do_action(client, "stacked your library.", "stacked their library.")


    verbs = {
        'create': create,
        'stack': stack
    }


    if args is None:
        if client.user.table is None:
            do_help(client, ['table'])
            return
        client.msg_self(client.user.table.show())
        return

    if args[0] in verbs:
        verbs[args[0]](args[1:] if len(args) > 1 else None)
    else:
        do_help(client, ['table'])



actions = {
    'quit':  do_quit,
    'look':  do_look,
    'who':   do_who,
    'help': do_help,
    'rooms': do_rooms,
    'room':  do_room,
    'goto':  do_goto,
    'card':  do_card,
    'deck':  do_deck,
    'decks': do_decks,
    'table': do_table
}

