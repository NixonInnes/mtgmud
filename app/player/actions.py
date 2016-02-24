import os
from random import randint

from app import config, db, mud, server, style
from . import channels

#TODO: Tidy up the logic of these functions to be more consistent

def do_login(client, args):
    if len(args) == 0:
        client.msg_self("\nLogin error.\nLogin: <username> <password>\nNew Account: register <username> <password> <password>")
        client.get_prompt()
        return

    if args[0] == 'register':
        if len(args) == 4 and args[2] == args[3]:
            if len(args[1]) > 20:
                client.msg_self("\nUsername is too long (max. 20).")
                client.get_prompt()
                return

            if db.session.query(db.models.User).filter_by(name=args[1]).first() is not None:
                client.msg_self("\nUsername \"{}\" is already taken, sorry.\n".format(args[1]))
                client.get_prompt()
                return

            new_user = db.models.User(name=args[1], password=args[2])
            db.session.add(new_user)
            db.session.commit()
            client.user = new_user
            client.user.room = server.get_lobby()
            do_look(client, '')
            client.get_prompt()
            return

    if len(args) == 2:
        dbuser = db.session.query(db.models.User).filter_by(name=args[0]).first()
        if dbuser is not None:
            if dbuser.verify_password(args[1]):
                client.user = dbuser
                client.user.room = server.get_lobby()
                do_look(client, '')
                client.get_prompt()
                return

    client.msg_self("\nLogin error.\nLogin: <username> <password>\nNew Account: register <username> <password> <password>")
    client.get_prompt()

def do_quit(client, args):
    """
    Closes the client connection.

    :param client: server.Protocol
    :param args: None
    :return: None
    """
    client.msg_self("\nYou are wracked with uncontrollable pain as you are extracted from the Matrix.\n")
    client.transport.close()


def do_look(client, args):
    """
    Sends room information to the client.

    :param client: server.Protocol()
    :param args: None
    :return: None
    """
    if client.user.room is None:
        client.msg_self("\nUmm... something's gone terribly, terribly wrong!")
        return
    buff = style.room_name(client.user.room.name)
    if client.user.room.description:
        buff += style.room_desc(client.user.room.description)
    user_list = ['You']
    for u in client.user.room.occupants:
        if u is not client.user:
            user_list.append(u.name)
    buff += style.room_occupants(user_list)
    client.msg_self(buff)



def do_who(client, args):
    """
    Sends a list of connected users to the client.

    :param client:
    :param args:
    :return: None
    """
    buff = style.header_80("ONLINE USERS")
    buff += style.body_2cols_80('USERS', 'ROOM')
    buff += style.ROW_LINE_80
    for c in server.clients:
        buff += style.body_2cols_80(c.user.name, c.user.room.name)
    buff += style.body_80("Online: {:^3}".format(len(server.clients)), align='left')
    buff += style.FOOTER_80
    client.msg_self(buff)


def do_help(client, args):
    """
    Reads a help file and sends the contents to the client.

    :param client: server.Protocol()
    :param args: help filename
    :return: None
    """
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


def do_dice(client, args):
    """
    Simulates a dice roll, and sends results to clients on the initiating clients table.

    :param client: server.Protocol()
    :param args: Dice size
    :return: None
    """
    if args is None:
        args = [6] #Default dice size
    if client.user.table is None or not str(args[0]).isdigit():
        do_help(client, ['dice'])
        return
    channels.do_action(client, "rolled a {} on a {} sided dice.".format(randint(1, args[0]), args[0]), "rolled a {} on a {} sided dice.".format(randint(1, args[0]), args[0]))


def do_card(client, args):
    """
    Queries the card database, and sends results to the client.

    :param client: server.Protocol()
    :param args: |find|
    :return: None
    """
    def find(args):
        card_name = ' '.join(args)
        cards = db.models.Card.search(card_name)
        if len(cards) < 1:
            client.msg_self("\nCould not find card: {}".format(card_name))
            return
        buff = ""
        for card in cards:
            buff += style.card(card)
        client.msg_self(buff)

    verbs = {
        'find': find
    }

    if args is not None:
        if args[0] in verbs:
            verbs[args[0]](args[1:] if len(args) > 1 else None)
            return
        else:
            find(args)
            return
    do_help(client, ['card'])


def do_rooms(client, args):
    buff = style.header_80('ROOMS')
    buff += style.body_2cols_80('ROOM', 'USERS')
    buff += style.ROW_LINE_2COL_80
    for room in db.session.query(db.models.Room).all():
        buff += style.body_2cols_80(room.name, ', '.join(user.name for user in room.occupants))
    buff += style.BLANK_80
    buff += style.FOOTER_80
    client.msg_self(buff)


def do_room(client, args):
    def create(args):
        if args is None:
            do_help(client, ['room'])
            return
        room_name = ' '.join(args)
        if db.session.query(db.models.Room).filter_by(name=room_name).first() is not None:
            client.msg_self("\nThe room name '{}' is already taken, sorry.".format(room_name))
            return
        room = db.models.Room(name=str(room_name))
        vroom = mud.models.Room.load(room)
        server.rooms.append(vroom)
        db.session.add(room)
        db.session.commit()
        client.msg_self("\nRoom created: {}".format(room_name))

    def delete(args):
        if args is None:
            do_help(client, ['room'])
            return
        room_name = ' '.join(args)
        for r in server.rooms:
            if r.name == room_name:
                room = r
        if room is not None:
            for occupant in room.occupants:
                do_goto(occupant, config.LOBBY_ROOM_NAME)
                client.msg_client(occupant, "\nThe lights flicker and you are suddenly in {}. Weird...".format(config.LOBBY_ROOM_NAME))
            server.rooms.remove(room)
            db.session.delete(room.db)
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
        room = db.session.query(db.models.Room).filter_by(name=room_name).first()
        if room is not None:
            if client.user.room is not None:
                client.user.room.occupants.remove(client.user)
            client.user.room = room
            db.session.commit()
            do_look(client, None)
            return
        client.msg_self("\nGoto where?!")


def do_deck(client, args):
    if args is None:
        if client.user.deck is not None:
            buff = style.header_40(client.user.deck.name)
            num_cards = 0
            for card in client.user.deck.cards:
                num_cards += client.user.deck.cards[card]
                s_card = db.session.query(db.models.Card).get(card)
                buff += style.body_40("{:^3} x {:<25}".format(client.user.deck.cards[card], s_card.name))
            buff += style.body_40(" [{}]".format(num_cards, ''), align='left')
            buff += style.FOOTER_40
            client.msg_self(buff)
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
            new_deck = db.models.Deck(
                name = deck_name,
                user_id = client.user.id,
                cards = {}
            )
            db.session.add(new_deck)
            client.user.decks.append(new_deck)
            db.session.commit()
            client.user.deck = new_deck
            client.msg_self("\nCreated new deck '{}'.".format(new_deck.name))

    def set_(args):
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
                    client.msg_self("\n'{}' is now your active deck.".format(d.name))
                    return
            client.msg_self("\nDeck '{}' not found.".format(deck_name))


    def add(args):
        if args is None:
            do_help(client, ['deck'])
            return
        if client.user.deck is None:
            do_help(client, ['deck'])
            return
        if str(args[0]).isdigit():
            num_cards = int(args[0])
            args = args[1:]
        else:
            num_cards = 1
        card_name = ' '.join(args)
        s_cards = db.models.Card.search(card_name)
        if len(s_cards) == 0:
            client.msg_self("\nCard '{}' not found.".format(card_name))
            return
        if len(s_cards) > 1:
            client.msg_self("\nMultiple cards called {}: {}\nPlease be more specific.".format(card_name, ', '.join(card.name for card in s_cards)))
            return
        s_card = s_cards[0]
        card_count = 0
        for card in client.user.deck.cards:
            card_count += int(client.user.deck.cards[card])
        if card_count >= 600:
            client.msg_self("\nYour deck is at the card limit ({}).".format(card_count))
        if s_card.id in client.user.deck.cards:
            client.user.deck.cards[s_card.id] += num_cards
        else:
            client.user.deck.cards[s_card.id] = num_cards
        db.session.commit()
        client.msg_self("\nAdded {} x '{}' to '{}'.".format(num_cards, s_card.name, client.user.deck.name))


    def remove(args):
        if args is None:
            do_help(client, ['deck'])
            return
        if client.user.deck is None:
            do_help(client, ['deck'])
            return
        if str(args[0]).isdigit():
            num_cards = int(args[0])
            args = args[1:]
        else:
            num_cards = 1
        card_name = ' '.join(args)
        s_cards = db.models.Card.search(card_name)
        if len(s_cards) == 0:
            client.msg_self("\nCard '{}' not found.".format(card_name))
            return
        if len(s_cards) > 1:
            client.msg_self("\nMultiple cards called {}: {}\nPlease be more specific.".format(card_name, ', '.join(card.name for card in s_cards)))
            return
        s_card = s_cards[0]
        for card in client.user.deck.cards:
            if card == s_card.id:
                client.user.deck.cards[card] -= num_cards
                if client.user.deck.cards[card] < 1:
                    client.user.deck.cards.pop(card, None)
                db.session.commit()
                client.msg_self("\nRemoved {} x '{}' from '{}'.".format(num_cards, s_card.name, client.user.deck.name))
                return

    verbs = {
        'create': create,
        'add': add,
        'remove': remove,
        'set': set_
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
        table_ = db.models.Table(client.user, table_name)
        server.tables.append(table_)
        client.user.room.tables.append(table_)
        do_table(client, ['join', table_name])

    def join(args):
        if args is None:
            do_help(client, ['table', 'join'])
            return
        table_name = ' '.join(args)
        for t in client.user.room.tables:
            if table_name == t.name:
                if len(t.clients) < 2 or client.user in t.users:
                    t.add_player(client.user)
                    client.user.table = t
                    channels.do_action(client, "joined table {}.".format(t.name), "joined the table.")
                    return
        client.msg_self("\nCould not find table '{}".format(table_name))

    def stack(args):
        if client.user.table is None or client.user.deck is None:
            do_help(client, ['table', 'stack'])
            return
        client.user.table.stack_library(client, client.user.deck.get())
        client.user.table.shuffle_library(client)
        channels.do_action(client, "stacked your library.", "stacked their library.")

    def draw(args):
        if args is None:
            client.user.table.draw_card(client)
            channels.do_action(client, "draw a card.", "draws a card.")
            return
        if not str(args[0]).isdigit():
            do_help(client, ['table', 'draw'])
            return
        client.user.table.draw_card(client, args[0])
        channels.do_action(client, "draw {} cards.".format(args[0]), "draws {} cards.".format(client.user.name, args[0]))

    def hand(args):
        buff = style.header_40("Hand")
        for card in client.user.table.hands[client]:
            buff += style.body_40("({:2}) {:<25}".format(client.user.table.hands[client].index(card), card.name))
        buff += style.FOOTER_40
        client.msg_self(buff)

    def play(args):
        if args is None or not str(args[0]).isdigit():
            do_help(client ['table', 'play'])
            return
        if not client.user.table.hands[client][int(args[0])]:
            do_help(client ['table', 'play'])
            return
        client.user.table.battlefields[client].append(client.user.table.hands[client][int(args[0])])
        channels.do_action(client, "play {}.".format(client.user.table.hands[client][int(args[0])].name), "plays {}.".format(client.user.table.hands[client][int(args[0])].name))
        client.user.table.hands[client].pop(int(args[0]))

    verbs = {
        'create': create,
        'join': join,
        'stack': stack,
        'draw': draw,
        'hand': hand,
        'play': play
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
    'login': do_login,
    'quit':  do_quit,
    'look':  do_look,
    'who':   do_who,
    'help':  do_help,
    'dice':  do_dice,
    'rooms': do_rooms,
    'room':  do_room,
    'goto':  do_goto,
    'card':  do_card,
    'deck':  do_deck,
    'decks': do_decks,
    'table': do_table
}

