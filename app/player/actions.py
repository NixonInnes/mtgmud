import os
import re
from random import randint

from app import config, db, mud, server, style
from . import channels

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

#TODO: Tidy up the logic of these functions to be more consistent

def do_login(user, args):
    """
    Function to register or login an existing user.
    """
    if len(args) == 0:
        user.msg_self("&RLogin Error.&x&GLogin:&x &g<username> <password>&x&CRegister:&x &cregister <username> <password> <password>&c")
        user.get_prompt()
        return

    if args[0] == 'register':
        if len(args) == 4 and args[2] == args[3]:
            if not re.match('^[\w-]', args[1]):
                user.msg_self("Invalid username, please only use alphanumerics.")
                user.get_prompt()
                return
            if len(args[1]) < 3:
                user.msg_self("Username is too short (min. 3).")
                user.get_prompt()
                return
            if len(args[1]) > 20:
                user.msg_self("Username is too long (max. 20).")
                user.get_prompt()
                return
            if str(args[1]).lower() in config.BANNED_NAMES:
                user.msg_self("That name is banned, sorry!")
                user.get_prompt()
                return
            if db.session.query(db.models.User).filter_by(name=args[1]).first() is not None:
                user.msg_self("Username '{}' is already taken, sorry.".format(args[1]))
                user.get_prompt()
                return
            dbUser = db.models.User(name=args[1], password=args[2], aliases={})
            db.session.add(dbUser)
            db.session.commit()
            user.load(dbUser)
            channels.do_info(user, "{} has entered the realm.".format(user.name))
            do_look(user, None)
            user.get_prompt()
            return
    if len(args) == 2:
        dbUser = db.session.query(db.models.User).filter_by(name=args[0]).first()
        if dbUser is not None:
            if dbUser.verify_password(args[1]):
                user.load(dbUser)
                if user.is_banned():
                    user.msg_self("Eeek, it looks like you're banned buddy! Bye!")
                    actions['quit'](user, None)
                    return
                channels.do_info(user, "{} has entered the realm.".format(user.name))
                do_look(user, None)
                user.get_prompt()
                return

    user.msg_self("&RLogin Error.&x&GLogin:&x &g<username> <password>&x&CRegister:&x &cregister <username> <password> <password>&c")
    user.get_prompt()


def do_quit(user, args):
    """
    Closes the user connection.
    """
    user.msg_self("You are wracked with uncontrollable pain as you are extracted from the Matrix.")
    channels.do_info(user, "{} has left the realm.".format(user.name))
    user.transport.close()


def do_look(user, args):
    """
    Sends room information to the user.
    """
    if user.room is None:
        user.msg_self("Umm... something's gone terribly, terribly wrong!")
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


def do_alias(user, args):
    """
    Create or delete aliases for the user.
    """
    if args is None:
        buff = style.header_40('Aliases')
        for alias in user.db.aliases:
            buff += style.body_40("{}: {}".format(alias, user.db.aliases[alias]))
        buff += style.BLANK_40
        buff += style.FOOTER_40
        user.msg_self(buff)
        return
    if args[0] == 'delete' and len(args) > 1:
        if args[1] in user.db.aliases:
            user.db.aliases.pop(args[1])
            user.msg_self("Alias '{}' has been deleted.".format(args[1]))
            return
        user.msg_self("You have no '{}' alias.".format(args[1]))
        return
    if args[1] == 'alias':
        user.msg_self("That's not a good idea...")
        return
    user.db.aliases[args[0]] = ' '.join(args[1:])
    db.session.commit()
    user.msg_self("Alias '{}' for '{}' created.".format(args[0], ' '.join(args[1:])))


def do_make_admin(user, args):
    """
    Set the admin flag for a user.
    """
    if user.name != config.ADMIN:
        user.msg_self("Huh?")
        return
    if args is None:
        user.msg_self("Make who an Admin?")
        return
    user_name = args[0]
    u = server.get_user(user_name)
    if u is None:
        user.msg_self("Could not find user '{}'.".format(user_name))
        return
    if u.is_admin():
        user.msg_self("They are already an Admin!")
        return
    u.flags['admin'] = True
    u.save()
    user.msg_client(u, "&RYou have been made an Admin!&x")
    user.msg_self("&CYou have admin'd {}.&x")

def do_mute(user, args):
    """
    Set mute flag for a user.
    """
    if not user.is_admin():
        user.msg_self("Huh?")
        return
    if args is None:
        user.msg_self("Mute who?")
        return
    user_name = args[0]
    u = server.get_user(user_name)
    if user is None:
        user.msg_self("Could not find user '{}'.".format(user_name))
        return
    u.flags['muted'] = True
    u.save()
    user.msg_client(u, "&RYou have been muted!&x")
    user.msg_self("&CYou have muted {}.&x".format(u.name))
    return


def do_freeze(user, args):
    """
    Set frozen flag for a user
    """
    if not user.is_admin():
        user.msg_self("Huh?")
        return
    if args is None:
        user.msg_self("Freeze who?")
        return
    username = args[0]
    for u in server.users:
        if u.name == username:
            u.flags['frozen'] = True
            u.save()
            user.msg_client(u, "&RYou have been frozen solid!&x")
            user.msg_self("&CYou have frozen {}.&x".format(u.name))

            return
    user.msg_self("Could not find user '{}'.".format(username))


def do_ban(user, args):
    """
    Set banned flag for a user
    """
    if not user.is_admin():
        user.msg_self("Huh?")
        return
    if args is None:
        user.msg_self("Ban who?")
        return
    username = args[0]
    for u in server.users:
        if u.name == username:
            u.flags['banned'] = True
            u.save()
            user.msg_client(u, "&RYou have been banned!&x")
            user.msg_self("&CYou have banned {}.&x".format(u.name))
            actions['quit'](u, None)
            return
    user.msg_self("Could not find user '{}'.".format(username))

def do_card(user, args):
    """
    Queries the card database, and sends results to the user.
    """
    card_name = ' '.join(args)
    cards = db.models.Card.search(card_name)
    if len(cards) < 1:
        user.msg_self("Could not find card: {}".format(card_name))
        return
    buff = ""
    for card in cards:
        buff += style.card(card)
    user.msg_self(buff)


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
            user.msg_self("The room name '{}' is already taken, sorry.".format(room_name))
            return
        room = db.models.Room(name=str(room_name))
        vroom = mud.models.Room.load(room)
        server.rooms.append(vroom)
        db.session.add(room)
        db.session.commit()
        user.msg_self("Room created: {}".format(room_name))

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
                user.msg_user(occupant, "The lights flicker and you are suddenly in {}. Weird...".format(config.LOBBY_ROOM_NAME))
            server.rooms.remove(room)
            db.session.delete(room.db)
            db.session.commit()
            user.msg_self("Room '{}' has been deleted.".format(room.name))
            return
        user.msg_self("Room '{}' was not found.".format(room_name))

    verbs = {
        'create': create,
        'delete': delete
    }

    if args is None:
        do_help(user, ['room'])
        return
    if args[0] in verbs:
        verbs[args[0]](args[1:] if len(args) > 1 else None)
        return
    do_help(user, ['room'])


def do_goto(user, args):
    if user.table is not None:
        user.msg_self("You can't leave now, you're at a table!")
        return
    if args is None:
        do_help(user, ['goto'])
        return
    room_name = ' '.join(args)
    room = server.get_room(room_name)
    if room is None:
        user.msg_self("Goto where?!")
        return
    if user.room is not None:
        user.room.occupants.remove(user)
    user.room = room
    user.room.occupants.append(user)
    do_look(user, None)


def do_deck(user, args):
    def create(args):
        if args is None:
            do_help(user, ['deck'])
            return
        deck_name = mud.colour.strip(' '.join(args))
        for d in user.decks:
            if d.name == deck_name:
                user.msg_self("You already have a deck named '{}'.".format(deck_name))
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
        user.msg_self("Created new deck '{}'.".format(new_deck.name))

    def set_(args):
        if args is None:
            do_help(user, ['deck'])
            return
        deck_name = ' '.join(args)
        for deck in user.decks:
            if deck.name == deck_name:
                user.deck = deck
                db.session.add(user.db)
                db.session.commit()
                print(user.deck)
                user.msg_self("'{}' is now your active deck.".format(deck.name))
                return
        user.msg_self("Deck '{}' not found.".format(deck_name))

    def add(args):
        if args is None:
            do_help(user, ['deck'])
            return
        if user.deck is None:
            do_help(user, ['deck'])
            return
        if not is_int(args[0]):
            num_cards = 1
        else:
            num_cards = int(args[0])
            args = args[1:]
        card_name = ' '.join(args)
        s_cards = db.models.Card.search(card_name)
        if len(s_cards) is 0:
            user.msg_self("Card '{}' not found.".format(card_name))
            return
        if len(s_cards) > 1:
            user.msg_self("Multiple cards called {}: {}Please be more specific.".format(card_name, ', '.join(card.name for card in s_cards)))
            return
        s_card = s_cards[0]
        total_cards = 0
        for card in user.deck.cards:
            total_cards += user.deck.cards[card]
        if total_cards >= 600:
            user.msg_self("Your deck is at the card limit (600).")
        if s_card.id in user.deck.cards:
            user.deck.cards[s_card.id] += num_cards
        else:
            user.deck.cards[s_card.id] = num_cards
        db.session.commit()
        user.msg_self("Added {} x '{}' to '{}'.".format(num_cards, s_card.name, user.deck.name))

    def remove(args):
        if args is None:
            do_help(user, ['deck'])
            return
        if user.deck is None:
            do_help(user, ['deck'])
            return
        if not is_int(args[0]):
            num_cards = 1
        else:
            num_cards = int(args[0])
            args = args[1:]
        card_name = ' '.join(args)
        s_cards = db.models.Card.search(card_name)
        if len(s_cards) is 0:
            user.msg_self("Card '{}' not found.".format(card_name))
            return
        if len(s_cards) > 1:
            user.msg_self("Multiple cards called {}: {}Please be more specific.".format(card_name, ', '.join(card.name for card in s_cards)))
            return
        s_card = s_cards[0]
        for card in user.deck.cards:
            if card == s_card.id:
                user.deck.cards[card] -= num_cards
                if user.deck.cards[card] < 1:
                    user.deck.cards.pop(card, None)
                db.session.commit()
                user.msg_self("Removed {} x '{}' from '{}'.".format(num_cards, s_card.name, user.deck.name))
                return

    verbs = {
        'create': create,
        'add': add,
        'remove': remove,
        'set': set_
    }

    if args is None:
        if user.deck is None:
            do_help(user, ['deck'])
            return
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
    if args[0] in verbs:
        verbs[args[0]](args[1:] if len(args) > 1 else None)
        return
    do_help(user, ['deck'])


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
            do_help(user, ['table', 'create'])
            return
        table_name = mud.colour.strip(' '.join(args))
        table_ = mud.models.Table(user, table_name)
        table_.start_time = int(server.tick_count)
        server.add_tick(table_.round_timer, table_.start_time+50*60, repeat=False)
        server.tables.append(table_)
        user.room.tables.append(table_)
        channels.do_act(user, "have created a table, '{}'.".format(table_.name), "created a table, '{}'.".format(table_.name))
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
                    channels.do_tinfo(user, "joined the table.".format(t.name), "has joined the table.")
                    return
        user.msg_self("Could not find table '{}'.".format(table_name))

    def dice(args):
        if user.table is None:
            do_help(user, ['table', 'dice'])
            return
        if args is not None:
            if str(args[0]).isdigit():
                die_size = int(args[0])
            else:
                do_help(user, ['table', 'dice'])
        else:
            die_size = 6 #Default dice size
        roll = randint(1, die_size)
        channels.do_tinfo(user, "rolled a {} on a {} sided dice.".format(roll, die_size), "rolled a {} on a {} sided dice.".format(roll, die_size))

    def leave(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        channels.do_tinfo(user, "have left the table.", "has left the table.")
        table.leave(user)
        if len(table.users) < 1:
            del table

    def stack(args):
        if user.table is None or user.deck is None:
            do_help(user, ['table', 'stack'])
            return
        user.table.stack(user)
        user.table.shuffle(user)
        channels.do_tinfo(user, "stacked your library.", "stacked their library.")

    def life(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        if args is None:
            user.msg_self("Do what with your life total?")
            return
        if not is_int(args[0]):
            do_help(user, ['table', 'hp'])
            return
        user.table.life_totals[user] += int(args[0])
        channels.do_tinfo(user, "set your life total to {}.".format(user.table.life_totals[user]), "set their life total to {}.".format(user.table.life_totals[user]))

    def draw(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        if len(user.table.libraries[user]) < 1:
            user.msg_self("Your library is empty!")
            return
        if args is None:
            user.table.draw(user)
            channels.do_tinfo(user, "draw a card.", "draws a card.")
            return
        if not is_int(args[0]):
            do_help(user, ['table', 'draw'])
            return
        no_cards = int(args[0])
        if no_cards < 1:
            user.msg_self("Ummm... how would you even... Uhh... I don't... No. Just, no.")
            return
        user.table.draw(user, no_cards)
        channels.do_tinfo(user, "draw {} cards.".format(no_cards), "draws {} cards.".format(no_cards))

    def hand(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        user.msg_self(user.table.hand(user))

    def play(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        if not is_int(args[0]):
            do_help(user, ['table', 'play'])
        card_index = int(args[0])
        if card_index >= len(table.hands[user]):
            user.msg_self("Out of range!")
            return
        card = table.hands[user][int(args[0])]
        table.play(user, card)
        channels.do_tinfo(user, "play {}.".format(card.name), "plays {}.".format(card.name))

    def discard(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        if not is_int(args[0]):
            do_help(user, ['table', 'play'])
        card_index = int(args[0])
        if card_index >= len(table.hands[user]):
            user.msg_self("Out of range!")
            return
        card = table.hands[user][int(args[0])]
        table.discard(user, card)
        channels.do_tinfo(user, "discard {}.".format(card.name), "discards {}.".format(card.name))

    def tap(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        if args is None:
            do_help(user, ['table', 'tap'])
            return
        if is_int(args[0]):
            card_index = int(args[0])
            if card_index >= len(table.battlefields[user]):
                user.msg_self("Out of range!")
                return
            card = table.battlefields[user][card_index]
            if card.tapped:
                user.msg_self("{} is already tapped.".format(card.name))
                return
            card.tap()
            channels.do_tinfo(user, "tap {}.".format(card.name), "taps {}.".format(card.name))
        elif args[0] == "all":
            for card in table.battlefields[user]:
                card.tap()
            channels.do_tinfo(user, "tap all your cards.", "taps all their cards.")
        else:
            do_help(user, ['table', 'tap'])

    def untap(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        if args is None:
            do_help(user, ['table', 'untap'])
            return
        if is_int(args[0]):
            card_index = int(args[0])
            if card_index >= len(table.battlefields[user]):
                user.msg_self("Out of range!")
                return
            card = table.battlefields[user][card_index]
            if not card.tapped:
                user.msg_self("'{}' is not tapped.".format(card.name))
                return
            card.untap()
            channels.do_tinfo(user, "untap {}.".format(card.name), "untaps {}.".format(card.name))
        elif args[0] == "all":
            for card in table.battlefields[user]:
                card.untap()
            channels.do_tinfo(user, "untap all your cards.", "untaps all their cards.")
        else:
            do_help(user, ['table', 'tap'])

    def shuffle(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        user.table.shuffle(user)
        channels.do_tinfo(user, "shuffled your library.", "shuffled their library.")

    def tutor(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        if args is None:
            do_help(user, ['table', 'tutor'])
            return
        card_name = ' '.join(args)
        if user.table.tutor(user, card_name):
            channels.do_tinfo(user, "tutored {} from your library.".format(card_name), "tutored {} from their library.".format(user.name, card_name))
        else:
            user.msg_self("Failed to find '{}' in your library.".format(card_name))

    def destroy(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'destroy'])
            return
        card_index = int(args[0])
        if card_index >= len(table.battlefields[user]):
            user.msg_self("Out of range!")
            return
        card = table.battlefields[user][card_index]
        table.destroy(user, card)
        channels.do_tinfo(user, "destroy your {}.".format(card.name), "destroys their {}.".format(card.name))

    def return_(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'return'])
            return
        card_index = int(args[0])
        if card_index >= len(table.battlefields[user]):
            user.msg_self("Out of range!")
            return
        card = table.battlefields[user][card_index]
        table.return_(user, card)
        channels.do_tinfo(user, "return {} to your hand.".format(card.name), "returns {} to their hand.".format(card.name))

    def greturn(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'greturn'])
            return
        card_index = int(args[0])
        if card_index >= len(table.graveyards[user]):
            user.msg_self("Out of range!")
            return
        card = table.graveyards[user][int(args[0])]
        table.greturn(user, card)
        channels.do_tinfo(user, "return {} from your graveyard to hand.".format(card.name), "returns {} from their graveyard to hand.".format(card.name))

    def unearth(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'unearth'])
            return
        card_index = int(args[0])
        if card_index >= len(table.graveyards[user]):
            user.msg_self("Out of range!")
            return
        card = table.graveyards[user][card_index]
        table.unearth(user, card)
        channels.do_tinfo(user, "unearth your {}.".format(card.name), "unearths their {}.".format(card.name))

    def exile(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'exile'])
            return
        card_index = int(args[0])
        if card_index >= len(table.graveyards[user]):
            user.msg_self("Out of range!")
            return
        card = table.battlefields[user][card_index]
        table.exile(user, card)
        channels.do_tinfo(user, "exile your {}.".format(card.name), "exiles their {}.".format(card.name))

    def grexile(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'grexile'])
            return
        card_index = int(args[0])
        if card_index >= len(table.graveyards[user]):
            user.msg_self("Out of range!")
            return
        card = table.graveyards[user][card_index]
        table.grexile(user, card)
        channels.do_tinfo(user, "exile {} from your graveyard.".format(card.name), "exiles {} from their graveyard.".format(card.name))

    def scoop(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        user.table.scoop(user)
        channels.do_tinfo(user, "scoop it up!", "scoops it up!")

    def time(args):
        if user.table is None:
            user.msg_self("You're not at a table!")
            return
        elapsed = int((server.ticker - user.table.start_time)/60)
        user.msg_self("{} minutes have elapsed.".format(elapsed))

    verbs = {
        'create': create,
        'join': join,
        'leave': leave,
        'dice': dice,
        'stack': stack,
        'draw': draw,
        'life': life,
        'hand': hand,
        'shuffle': shuffle,
        'play': play,
        'tap': tap,
        'untap': untap,
        'discard': discard,
        'tutor': tutor,
        'destroy': destroy,
        'return': return_,
        'greturn': greturn,
        'unearth': unearth,
        'exile': exile,
        'grexile': grexile,
        'scoop': scoop,
        'time': time
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
    'alias': do_alias,
    'freeze': do_freeze,
    'mute': do_mute,
    'make_admin': do_make_admin,
    'rooms': do_rooms,
    'room':  do_room,
    'goto':  do_goto,
    'card':  do_card,
    'deck':  do_deck,
    'decks': do_decks,
    'table': do_table
}

