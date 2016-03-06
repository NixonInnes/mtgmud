import os
from random import randint

from app import config, db, mud, server, style
from . import channels

#TODO: Tidy up the logic of these functions to be more consistent

def do_login(user, args):
    if len(args) == 0:
        user.msg_self("\nLogin error.\nLogin: <username> <password>\nNew Account: register <username> <password> <password>")
        user.get_prompt()
        return

    if args[0] == 'register':
        if len(args) == 4 and args[2] == args[3]:
            if len(args[1]) > 20:
                user.msg_self("\nUsername is too long (max. 20).")
                user.get_prompt()
                return

            if db.session.query(db.models.User).filter_by(name=args[1]).first() is not None:
                user.msg_self("\nUsername \"{}\" is already taken, sorry.\n".format(args[1]))
                user.get_prompt()
                return

            dbUser = db.models.User(name=args[1], password=args[2])
            db.session.add(dbUser)
            db.session.commit()
            user.load(dbUser)
            do_look(user, None)
            user.get_prompt()
            return

    if len(args) == 2:
        dbUser = db.session.query(db.models.User).filter_by(name=args[0]).first()
        if dbUser is not None:
            if dbUser.verify_password(args[1]):
                user.load(dbUser)
                do_look(user, None)
                user.get_prompt()
                return

    user.msg_self("\nLogin error.\nLogin: <username> <password>\nNew Account: register <username> <password> <password>")
    user.get_prompt()

def do_quit(user, args):
    """
    Closes the user connection.

    :param user: server.Protocol
    :param args: None
    :return: None
    """
    user.msg_self("\nYou are wracked with uncontrollable pain as you are extracted from the Matrix.\n")
    user.transport.close()


def do_look(user, args):
    """
    Sends room information to the user.

    :param user: server.Protocol()
    :param args: None
    :return: None
    """
    if user.room is None:
        user.msg_self("\nUmm... something's gone terribly, terribly wrong!")
        return
    buff = style.room_name(user.room.name)
    if user.room.description:
        buff += style.room_desc(user.room.description)
    user_list = ['You']
    for u in user.room.occupants:
        if u is not user:
            user_list.append(u.name)
    buff += style.room_occupants(user_list)
    user.msg_self(buff)



def do_who(user, args):
    """
    Sends a list of connected users to the user.

    :param user:
    :param args:
    :return: None
    """
    buff = style.header_80("ONLINE USERS")
    buff += style.body_2cols_80('USERS', 'ROOM')
    buff += style.ROW_LINE_80
    for u in server.users:
        buff += style.body_2cols_80(u.name, u.room.name)
    buff += style.body_80("Online: {:^3}".format(len(server.users)), align='left')
    buff += style.FOOTER_80
    user.msg_self(buff)


def do_help(user, args):
    """
    Reads a help file and sends the contents to the user.

    :param user: server.Protocol()
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
    user.msg_self(help_)


def do_dice(user, args):
    """
    Simulates a dice roll, and sends results to users on the initiating users table.

    :param user: server.Protocol()
    :param args: Dice size
    :return: None
    """
    if args is None:
        args = [6] #Default dice size
    if user.table is None or not str(args[0]).isdigit():
        do_help(user, ['dice'])
        return
    channels.do_action(user, "rolled a {} on a {} sided dice.".format(randint(1, args[0]), args[0]), "rolled a {} on a {} sided dice.".format(randint(1, args[0]), args[0]))


def do_card(user, args):
    """
    Queries the card database, and sends results to the user.

    :param user: server.Protocol()
    :param args: |find|
    :return: None
    """
    def find(args):
        card_name = ' '.join(args)
        cards = db.models.Card.search(card_name)
        if len(cards) < 1:
            user.msg_self("\nCould not find card: {}".format(card_name))
            return
        buff = ""
        for card in cards:
            buff += style.card(card)
        user.msg_self(buff)

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
    do_help(user, ['card'])


def do_rooms(user, args):
    buff = style.header_80('ROOMS')
    buff += style.body_2cols_80('ROOM', 'USERS')
    buff += style.ROW_LINE_2COL_80
    for room in server.rooms:
        buff += style.body_2cols_80(room.name, ', '.join(user.name for user in room.occupants))
    buff += style.BLANK_80
    buff += style.FOOTER_80
    user.msg_self(buff)


def do_room(user, args):
    def create(args):
        if args is None:
            do_help(user, ['room'])
            return
        room_name = mud.colour.strip(' '.join(args))
        # Check the database for duplicate name, rather than the server.rooms list, as we may not want to load rooms for some reason later
        if db.session.query(db.models.Room).filter_by(name=room_name).first() is not None:
            user.msg_self("\nThe room name '{}' is already taken, sorry.".format(room_name))
            return
        room = db.models.Room(name=str(room_name))
        vroom = mud.models.Room.load(room)
        server.rooms.append(vroom)
        db.session.add(room)
        db.session.commit()
        user.msg_self("\nRoom created: {}".format(room_name))

    def delete(args):
        if args is None:
            do_help(user, ['room'])
            return
        room_name = ' '.join(args)
        for r in server.rooms:
            if r.name == room_name:
                room = r
        if room is not None:
            for occupant in room.occupants:
                do_goto(occupant, config.LOBBY_ROOM_NAME)
                user.msg_user(occupant, "\nThe lights flicker and you are suddenly in {}. Weird...".format(config.LOBBY_ROOM_NAME))
            server.rooms.remove(room)
            db.session.delete(room.db)
            db.session.commit()
            user.msg_self("\nRoom '{}' has been deleted.".format(room.name))
            return
        user.msg_self("\nRoom '{}' was not found.".format(room_name))

    verbs = {
        'create': create,
        'delete': delete
    }

    if args is not None:
        if args[0] in verbs:
            verbs[args[0]](args[1:] if len(args) > 1 else None)
            return
    do_help(user, ['room'])


def do_goto(user, args):
    if args is None:
        do_help(user, ['goto'])
    else:
        room_name = ' '.join(args)
        room = server.get_room(room_name)
        if room is not None:
            if user.room is not None:
                user.room.occupants.remove(user)
            user.room = room
            user.room.occupants.append(user)
            do_look(user, None)
            return
        user.msg_self("\nGoto where?!")


def do_deck(user, args):
    if args is None:
        if user.deck is not None:
            buff = style.header_40(user.deck.name)
            num_cards = 0
            for card in user.deck.cards:
                num_cards += user.deck.cards[card]
                s_card = db.session.query(db.models.Card).get(int(card))
                buff += style.body_40("{:^3} x {:<25}".format(user.deck.cards[card], s_card.name))
            buff += style.body_40(" [{}]".format(num_cards, ''), align='left')
            buff += style.FOOTER_40
            user.msg_self(buff)
            return

    def create(args):
        if args is None:
            do_help(user, ['deck'])
        else:
            deck_name = mud.colour.strip(' '.join(args))
            for d in user.decks:
                if d.name == deck_name:
                    user.msg_self("\nYou already have a deck named '{}'.".format(deck_name))
                    return
            new_deck = db.models.Deck(
                name = deck_name,
                user_id = user.db.id,
                cards = {}
            )
            db.session.add(new_deck)
            user.decks.append(new_deck)
            db.session.commit()
            user.deck = new_deck
            user.msg_self("\nCreated new deck '{}'.".format(new_deck.name))

    def set_(args):
        if args is None:
            do_help(user, ['deck'])
        else:
            deck_name = ' '.join(args)
            for deck in user.decks:
                if deck.name == deck_name:
                    user.deck = deck
                    db.session.add(user.db)
                    db.session.commit()
                    print(user.deck)
                    user.msg_self("\n'{}' is now your active deck.".format(deck.name))
                    return
            user.msg_self("\nDeck '{}' not found.".format(deck_name))


    def add(args):
        if args is None:
            do_help(user, ['deck'])
            return
        if user.deck is None:
            do_help(user, ['deck'])
            return
        if str(args[0]).isdigit():
            num_cards = int(args[0])
            args = args[1:]
        else:
            num_cards = 1
        card_name = ' '.join(args)
        s_cards = db.models.Card.search(card_name)
        if len(s_cards) is 0:
            user.msg_self("\nCard '{}' not found.".format(card_name))
            return
        if len(s_cards) > 1:
            user.msg_self("\nMultiple cards called {}: {}\nPlease be more specific.".format(card_name, ', '.join(card.name for card in s_cards)))
            return
        s_card = s_cards[0]
        total_cards = 0
        for card in user.deck.cards:
            total_cards += user.deck.cards[card]
        if total_cards >= 600:
            user.msg_self("\nYour deck is at the card limit ({}).".format(user.deck.cards['total']))
        if s_card.id in user.deck.cards:
            user.deck.cards[s_card.id] += num_cards
        else:
            user.deck.cards[s_card.id] = num_cards
        db.session.commit()
        user.msg_self("\nAdded {} x '{}' to '{}'.".format(num_cards, s_card.name, user.deck.name))


    def remove(args):
        if args is None:
            do_help(user, ['deck'])
            return
        if user.deck is None:
            do_help(user, ['deck'])
            return
        if str(args[0]).isdigit():
            num_cards = int(args[0])
            args = args[1:]
        else:
            num_cards = 1
        card_name = ' '.join(args)
        s_cards = db.models.Card.search(card_name)
        if len(s_cards) is 0:
            user.msg_self("\nCard '{}' not found.".format(card_name))
            return
        if len(s_cards) > 1:
            user.msg_self("\nMultiple cards called {}: {}\nPlease be more specific.".format(card_name, ', '.join(card.name for card in s_cards)))
            return
        s_card = s_cards[0]
        for card in user.deck.cards:
            if card == s_card.id:
                user.deck.cards[card] -= num_cards
                if user.deck.cards[card] < 1:
                    user.deck.cards.pop(card, None)
                user.deck.cards['total'] -= 1
                db.session.commit()
                user.msg_self("\nRemoved {} x '{}' from '{}'.".format(num_cards, s_card.name, user.deck.name))
                return

    verbs = {
        'create': create,
        'add': add,
        'remove': remove,
        'set': set_
    }

    if args is None:
        if user.deck is None:
            do_help(user, ['room'])
        else:
            user.msg_self(user.deck.show())
    else:
        if args[0] in verbs:
            verbs[args[0]](args[1:] if len(args) > 1 else None)
        else:
            user.msg_self("\nDeck what?!")


def do_decks(user, args):
    buff = style.header_40('Decks')
    for deck in user.decks:
        buff += style.body_40("{:1}[{:^3}] {}".format('*' if deck == user.deck else '', deck.no_cards, deck.name), align='left')
    buff += style.BLANK_40
    buff += style.FOOTER_40
    user.msg_self(buff)


def do_table(user, args):
    def create(args):
        if args is None:
            do_help(user, ['table'])
            return
        table_name = mud.colour.strip(' '.join(args))
        table_ = mud.models.Table(user, table_name)
        server.tables.append(table_)
        user.room.tables.append(table_)
        do_table(user, ['join', table_name])

    def join(args):
        if args is None:
            do_help(user, ['table', 'join'])
            return
        table_name = ' '.join(args)
        for t in user.room.tables:
            if table_name == t.name:
                if len(t.users) < 2 or user in t.users:
                    t.join(user)
                    user.table = t
                    channels.do_action(user, "joined table {}.".format(t.name), "joined the table.")
                    return
        user.msg_self("\nCould not find table '{}".format(table_name))

    def leave(args):
        user.table.leave(user)
        channels.do_action(user, "left the table.", "left the table.")

    def stack(args):
        if user.table is None or user.deck is None:
            do_help(user, ['table', 'stack'])
            return
        user.table.stack(user)
        user.table.shuffle(user)
        channels.do_action(user, "stacked your library.", "stacked their library.")

    def draw(args):
        if args is None:
            user.table.draw(user)
            channels.do_action(user, "draw a card.", "draws a card.")
            return
        if not str(args[0]).isdigit():
            do_help(user, ['table', 'draw'])
            return
        user.table.draw(user, args[0])
        channels.do_action(user, "draw {} cards.".format(args[0]), "draws {} cards.".format(args[0]))

    def hand(args):
        user.msg_self(user.table.hand(user))

    def play(args):
        table = user.table
        if args is None or not str(args[0]).isdigit() or not table.hands[user][int(args[0])]:
            do_help(user, ['table', 'play'])
            return
        card = table.hands[user][int(args[0])]
        table.play(user, card)
        channels.do_action(user, "play {}.".format(card.name), "plays {}.".format(card.name))

    def shuffle(args):
        user.table.shuffle(user)
        channels.do_action(user, "shuffled your library.", "shuffled their library.")

    def tutor(args):
        if args is None:
            do_help(user, ['table', 'tutor'])
            return
        card_name = ' '.join(args)
        if user.table.tutor(user, card_name):
            channels.do_action(user, "tutored {} from your library.".format(card_name), "tutored {} from their library.".format(user.name, card_name))
        else:
            user.msg_self("\nFailed to find '{}' in your library.".format(card_name))

    def destroy(args):
        table = user.table
        if args is None or not str(args[0]).isdigit() or not table.battlefields[user][int(args[0])]:
            do_help(user, ['table', 'destroy'])
            return
        card = table.battlefields[user][int(args[0])]
        table.destroy(user, card)
        channels.do_action(user, "destroy your {}.".format(card.name), "destroys their {}.".format(card.name))

    def return_(args):
        table = user.table
        if args is None or not str(args[0]).isdigit() or not table.battlefields[user][int(args[0])]:
            do_help(user, ['table', 'return'])
            return
        card = table.battlefields[user][int(args[0])]
        table.return_(user, card)
        channels.do_action(user, "return {} to your hand.".format(card.name), "returns {} to their hand.".format(card.name))

    def greturn(args):
        table = user.table
        if args is None or not str(args[0]).isdigit() or not table.graveyards[user][int(args[0])]:
            do_help(user, ['table', 'greturn'])
            return
        card = table.graveyards[user][int(args[0])]
        table.greturn(user, card)
        channels.do_action(user, "return {} from your graveyard to hand.".format(card.name), "returns {} from their graveyard to hand.".format(card.name))

    def unearth(args):
        table = user.table
        if args is None or not str(args[0]).isdigit() or not table.graveyards[user][int(args[0])]:
            do_help(user, ['table', 'unearth'])
            return
        card = table.graveyards[user][int(args[0])]
        table.unearth(user, card)
        channels.do_action(user, "unearth your {}.".format(card.name), "unearths their {}.".format(card.name))

    def exile(args):
        table = user.table
        if args is None or not str(args[0]).isdigit() or not table.battlefields[user][int(args[0])]:
            do_help(user, ['table', 'exile'])
            return
        card = table.battlefields[user][int(args[0])]
        table.exile(user, card)
        channels.do_action(user, "exile your {}.".format(card.name), "exiles their {}.".format(card.name))

    def grexile(args):
        table = user.table
        if args is None or not str(args[0]).isdigit() or not table.graveyards[user][int(args[0])]:
            do_help(user, ['table', 'grexile'])
            return
        card = table.graveyards[user][int(args[0])]
        table.grexile(user, card)
        channels.do_action(user, "exile {} from your graveyard.".format(card.name), "exiles {} from their graveyard.".format(card.name))

    verbs = {
        'create': create,
        'join': join,
        'leave': leave,
        'stack': stack,
        'draw': draw,
        'hand': hand,
        'shuffle': shuffle,
        'play': play,
        'tutor': tutor,
        'destroy': destroy,
        'return': return_,
        'greturn': greturn,
        'unearth': unearth,
        'exile': exile,
        'grexile': grexile
    }


    if args is None:
        if user.table is None:
            do_help(user, ['table'])
            return
        user.msg_self(user.table.show())
        return

    if args[0] in verbs:
        verbs[args[0]](args[1:] if len(args) > 1 else None)
    else:
        do_help(user, ['table'])

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

