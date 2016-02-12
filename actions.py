import os
from random import shuffle

import mud
import db, models
import funcs
import channels
import style

#TODO: Tidy up the logic of these functions to be more consistent

def do_quit(client, args):
    client.msg_self("\nYou are wracked with uncontrollable pain as you are extracted from the Matrix.\n")
    client.transport.close()


def do_look(client, args):
    if client.user.room is not None:
        client.msg_self(client.user.room.look())


def do_who(client, args):
    buff = style.header_80("ONLINE USERS")
    buff += style.body_2cols_80('USERS', 'ROOM')
    buff += style.ROW_LINE_80
    for client in mud.clients:
        buff += style.body_2cols_80(client.user.name, client.user.room.name)
    buff += style.body_80("Online: {:^3}".format(len(mud.clients)), align='left')
    buff += style.FOOTER_80
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
    do_help(client, ['card'])


def do_rooms(client, args):
    buff = style.header_80('ROOMS')
    buff += style.body_2cols_80('ROOM', 'USERS')
    buff += style.ROW_LINE_2COL_80
    for room in mud.rooms:
        buff += style.body_2cols_80(room.name, ', '.join(client.user.name for client in room.occupants))
    buff += style.BLANK_80
    buff += style.FOOTER_80
    client.msg_self(buff)


def do_room(client, args):
    def create(args):
        if args is None:
            do_help(client, ['room'])
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
            do_help(client, ['room'])
            return
        room_name = ' '.join(args)
        room = funcs.get_room(room_name)
        if room is not None:
            mud.rooms.remove(room)
            db.session.delete(room)
            db.session.commit()
            client.msg_self("\nRoom '{}' has been deleted.".format(room.name))
            return
        client.msg_self("\nRoom '{}' was not found.".format(room_name))

    verbs = {
        'create': create,
        'delete': delete
    }

    if args is not None:
        if args[0] in verbs:
            verbs[args[0]](args[1:] if len(args) > 1 else None)
            return

    do_help(client, ['room'])


def do_goto(client, args):
    if args is None:
        do_help(client, ['goto'])
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
            do_help(client, ['deck'])
        else:
            deck_name = ' '.join(args)
            for d in client.user.decks:
                if d.name == deck_name:
                    client.msg_self("\nYou already have a deck named '{}'.".format(deck_name))
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
            client.msg_self("\nCreated new deck '{}'.".format(new_deck.name))

    def set(args):
        if args is None:
            do_help(client, ['deck'])
        else:
            deck_name = ' '.join(args)
            for d in client.user.decks:
                if d.name == deck_name:
                    client.user.deck_id = d.id
                    client.user.deck = d
                    db.session.add(client.user)
                    db.session.commit()
                    print(client.user.deck)
                    client.msg_self("\n{} is now your active deck.".format(d.name))
                    return
            client.msg_self("\nDeck '{}' not found.".format(deck_name))


    def add(args):
        if args is None:
            do_help(client, ['deck'])
            return

        if client.user.deck is None:
            do_help(client, ['room'])
            return

        card_name = ' '.join(args)
        s_card = db.session.query(db.Card).filter_by(name=card_name).first()

        if s_card is None:
            client.msg_self("\nCard '{}' not found.".format(card_name))
            return

        print(client.user.deck.cards)
        if s_card.id in client.user.deck.cards:
            client.user.deck.cards[s_card.id] += 1
        else:
            client.user.deck.cards[s_card.id] = 1
        print(client.user.deck.cards)
        #db.session.add(client.user.deck)
        print(client.user.deck.cards)
        db.session.commit()
        print(client.user.deck.cards)
        client.msg_self("\nAdded '{}' to {}.".format(card_name, client.user.deck.name))

    verbs = {
        'create': create,
        'add': add,
        'set': set
    }

    if args is None:
        if client.user.deck is None:
            do_help(client, ['room'])
        else:
            client.msg_self(client.user.deck.show())
    else:
        if args[0] in verbs:
            verbs[args[0]](args[1:] if len(args) > 1 else None)
        else:
            client.msg_self("\nDeck what?!")


def do_decks(client, args):
    buff = style.header_40('Decks')
    for deck in client.user.decks:
        buff += style.body_40("{:1}[{:^3}] {}".format('*' if deck == client.user.deck else '', deck.no_cards, deck.name), align='left')
    buff += style.BLANK_40
    buff += style.FOOTER_40
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

