import os
import re
from app import config, db, mud
from app.libs import colour
from app.game import channels, objects
from random import randint


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class d_user_has(object):
    def __init__(self, user, attrib, error_msg='Huh?'):
        self.user = user
        self.attrib = attrib
        self.error_msg = error_msg

    def __call__(self, func):
        def wrapper(*args):
            if hasattr(self.user, self.attrib) and getattr(self.user, self.attrib) is not None:
                func(*args)
            else:
                self.user.presenter.show_msg(self.error_msg)
        return wrapper


# TODO: Tidy up the logic of these functions to be more consistent

def do_login(user, args):
    """
    Function to register or login an existing user.
    """
    if len(args) == 0:
        user.presenter.show_msg("&RLogin Error.&x\r\n&GLogin:&x &g<username> <password>&x\r\n&CRegister:&x &cregister <username> <password> <password>&c")
        return

    if args[0] == 'register':
        if len(args) == 4 and args[2] == args[3]:
            if not re.match('^[\w-]', args[1]):
                user.presenter.show_msg("Invalid username, please only use alphanumerics.")
                return
            if len(args[1]) < 3:
                user.presenter.show_msg("Username is too short (min. 3).")
                return
            if len(args[1]) > 20:
                user.presenter.show_msg("Username is too long (max. 20).")
                return
            if str(args[1]).lower() in config.BANNED_NAMES:
                user.presenter.show_msg("That name is banned, sorry!")
                return
            if db.session.query(db.models.User).filter_by(name=args[1]).first() is not None:
                user.presenter.show_msg("Username '{}' is already taken, sorry.".format(args[1]))
                return
            dbUser = db.models.User(
                name = args[1],
                password = args[2],
                aliases = {},
                listening = ''.join([channel.key for channel in db.session.query(db.models.Channel).filter_by(default=True).all()])
            )
            db.session.add(dbUser)
            db.session.commit()
            user.load(dbUser)
            channels.do_info("{} has entered the realm.".format(user.name))
            do_look(user, None)
            return

    if len(args) == 2:
        dbUser = db.session.query(db.models.User).filter_by(name=args[0]).first()
        if dbUser is not None:
            if dbUser.verify_password(args[1]):
                user.load(dbUser)
                # TODO: Move this to user.flags
                if user.flags['banned']:
                    user.presenter.show_msg("Eeek! It looks like you're banned, buddy! Bye!")
                    do_quit(user, None)
                    return
                channels.do_info("{} has entered the realm.".format(user.name))
                do_look(user, None)
                return

    user.presenter.show_msg("&RLogin Error.&x\r\n&GLogin:&x &g<username> <password>&x\r\n&CRegister:&x &cregister <username> <password> <password>&c")


def do_quit(user, args):
    """
    Closes the user connection.
    """
    user.presenter.show_msg("&gYou are wracked with uncontrollable pain as you are extracted from the Matrix.&x")
    channels.do_info("{} has left the realm.".format(user.name))
    user.disconnect()


def do_look(user, args):
    """
    Sends room information to the user.
    """
    user.presenter.show_room(user.room)


def do_who(user, args):
    """
    Sends a list of connected users to the user.
    """
    headers = ('User', 'Room')
    info = [(u.name, u.room.name) for u in mud.users]
    user.presenter.show_info_2col('USERS', headers, info)


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
    user.presenter.show_help(file)
    file.close()


def do_alias(user, args):
    """
    Create or delete aliases for the user.
    """
    if args is None:
        header = 'My Aliases'
        info = []
        for alias in user.db.aliases:
            info.append("{}: {}".format(alias, user.db.aliases[alias]))
        user.presenter.show_info('ALIASES', header, info)
        return
    if args[0] == 'delete' and len(args) > 1:
        if args[1] in user.db.aliases:
            user.db.aliases.pop(args[1])
            user.presenter.show_msg("Alias '{}' has been deleted.".format(args[1]))
            return
        user.presenter.show_msg("You have no '{}' alias.".format(args[1]))
        return
    if args[1] == 'alias':
        user.presenter.show_msg("That's not a good idea...")
        return
    user.db.aliases[args[0]] = ' '.join(args[1:])
    db.session.commit()
    user.presenter.show_msg("Alias '{}' for '{}' created.".format(args[0], ' '.join(args[1:])))


def do_make_admin(user, args):
    """
    Set the admin flag for a user.
    """
    if user.name != config.ADMIN:
        user.presenter.show_msg("Huh?")
        return
    if args is None:
        user.presenter.show_msg("Make who an Admin?")
        return
    user_name = args[0]
    u = mud.get_user(user_name)
    if u is None:
        user.presenter.show_msg("Could not find user '{}'.".format(user_name))
        return
    if u.is_admin():
        user.presenter.show_msg("They are already an Admin!")
        return
    u.flags['admin'] = True
    u.save()
    u.presenter.show_msg("&RYou have been made an Admin!&x")
    user.presenter.show_msg("&CYou have admin'd {}.&x")


def do_mute(user, args):
    """
    Set mute flag for a user.
    """
    if not user.is_admin():
        user.presenter.show_msg("Huh?")
        return
    if args is None:
        user.presenter.show_msg("Mute who?")
        return
    user_name = args[0]
    victim = mud.get_user(user_name)
    if user is None:
        user.presenter.show_msg("Could not find user '{}'.".format(user_name))
        return
    victim.flags['muted'] = True
    victim.save()
    victim.presenter.show_msg("&RYou have been muted!&x")
    user.presenter.show_msg("&CYou have muted {}.&x".format(victim.name))
    return


def do_freeze(user, args):
    """
    Set frozen flag for a user
    """
    if not user.is_admin():
        user.presenter.show_msg("Huh?")
        return
    if args is None:
        user.presenter.show_msg("Freeze who?")
        return
    username = args[0]
    victim = mud.get_user(username)
    if victim is None:
        user.presenter.show_msg("Could not find user '{}'.".format(username))
        return
    victim.flags['frozen'] = True
    victim.save()
    victim.presenter.show_msg("&RYou have been frozen solid!&x")
    user.presenter.show_msg("&CYou have frozen {}.&x".format(victim.name))


def do_ban(user, args):
    """
    Set banned flag for a user
    """
    if not user.is_admin():
        user.presenter.show_msg("Huh?")
        return
    if args is None:
        user.presenter.show_msg("Ban who?")
        return
    username = args[0]
    victim = mud.get_user(username)
    if victim is None:
        user.presenter.show_msg("Could not find user '{}'.".format(username))
        return
    victim.flags['banned'] = True
    victim.save()
    victim.presenter.show_msg("&RYou have been banned!&x")
    user.presenter.show_msg("&CYou have banned {}.&x".format(victim.name))
    do_quit(victim, None)


def do_card(user, args):
    """
    Queries the card database, and sends results to the user.
    """
    card_name = ' '.join(args)
    card = db.session.query(db.models.Card).filter(db.models.Card.name.like(card_name)).first()
    if card is None:
        user.presenter.show_msg("Could not find card: {}".format(card_name))
        return
    user.presenter.show_card(card)


def do_rooms(user, args):
    headers = ('Room', 'Users')
    info = [(room.name, ', '.join(user.name for user in room.occupants)) for room in mud.rooms]
    user.presenter.show_info_2col('ROOMS', headers, info)


def do_room(user, args):
    def create(args):
        if args is None:
            do_help(user, ['room'])
            return
        room_name = colour.strip_tokens(' '.join(args))
        # Check the database for duplicate name, rather than the server.rooms list,
        # as we may not want to load rooms for some reason later
        if db.session.query(db.models.Room).filter_by(name=room_name).first() is not None:
            user.presenter.show_msg("The room name '{}' is already taken, sorry.".format(room_name))
            return
        room = db.models.Room(name=str(room_name))
        vroom = objects.Room.load(room)
        mud.rooms.append(vroom)
        db.session.add(room)
        db.session.commit()
        user.presenter.show_msg("Room created: {}".format(room_name))

    def delete(args):
        if args is None:
            do_help(user, ['room'])
            return
        room_name = ' '.join(args)
        room = mud.get_room(room_name)
        if room is None:
            user.presenter.show_msg("Room '{}' was not found.".format(room_name))
            return
        for occupant in room.occupants:
            do_goto(occupant, config.LOBBY_ROOM_NAME)
            occupant.presenter.show_msg(
                "The lights flicker and you are suddenly in {}. Weird...".format(config.LOBBY_ROOM_NAME))
        mud.rooms.remove(room)
        db.session.delete(room.db)
        db.session.commit()
        user.presenter.show_msg("Room '{}' has been deleted.".format(room.name))

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
        user.presenter.show_msg("You can't leave now, you're at a table!")
        return
    if args is None:
        do_help(user, ['goto'])
        return
    room_name = ' '.join(args)
    room = mud.get_room(room_name)
    if room is None:
        user.presenter.show_msg("Goto where?!")
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
        deck_name = colour.strip_tokens(' '.join(args))
        for d in user.decks:
            if d.name == deck_name:
                user.presenter.show_msg("You already have a deck named '{}'.".format(deck_name))
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
        user.presenter.show_msg("Created new deck '{}'.".format(new_deck.name))

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
                user.presenter.show_msg("'{}' is now your active deck.".format(deck.name))
                return
        user.presenter.show_msg("Deck '{}' not found.".format(deck_name))

    @d_user_has(user, 'deck', "You don't have a deck!")
    def add(args):
        if args is None:
            do_help(user, ['deck'])
            return
        if not is_int(args[0]):
            num_cards = 1
        else:
            num_cards = int(args[0])
            args = args[1:]
        card_name = ' '.join(args)
        s_card = db.session.query(db.models.Card).filter(db.models.Card.name.like(card_name)).first()
        if s_card is None:
            user.presenter.show_msg("Card '{}' not found.".format(card_name))
            return
        total_cards = 0
        for card in user.deck.cards:
            total_cards += user.deck.cards[card]
        if total_cards >= 600:
            user.presenter.show_msg("Your deck is at the card limit (600).")
        if s_card.id in user.deck.cards:
            user.deck.cards[s_card.id] += num_cards
        else:
            user.deck.cards[s_card.id] = num_cards
        db.session.commit()
        user.presenter.show_msg("Added {} x '{}' to '{}'.".format(num_cards, s_card.name, user.deck.name))

    @d_user_has(user, 'deck', "You don't have a deck!")
    def remove(args):
        if args is None:
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
            user.presenter.show_msg("Card '{}' not found.".format(card_name))
            return
        if len(s_cards) > 1:
            user.presenter.show_msg("Multiple cards called {}: {}Please be more specific.".format(card_name, ', '.join(card.name for card in s_cards)))
            return
        s_card = s_cards[0]
        for card in user.deck.cards:
            if card == s_card.id:
                user.deck.cards[card] -= num_cards
                if user.deck.cards[card] < 1:
                    user.deck.cards.pop(card, None)
                db.session.commit()
                user.presenter.show_msg("Removed {} x '{}' from '{}'.".format(num_cards, s_card.name, user.deck.name))
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
        header = user.deck.name
        info = []
        num_cards = 0
        for card in user.deck.cards:
            num_cards += user.deck.cards[card]
            s_card = db.session.query(db.models.Card).get(int(card))
            info.append("{:^3} x {:<25}".format(user.deck.cards[card], s_card.name))
        user.presenter.show_info('DECK', header, info)
        return
    if args[0] in verbs:
        verbs[args[0]](args[1:] if len(args) > 1 else None)
        return
    do_help(user, ['deck'])


def do_decks(user, args):
    info = ["{:1}[{:^3}] {}".format('*' if deck == user.deck else '', deck.no_cards, deck.name) for deck in user.deck]
    user.presenter.show_info('DECKS', 'decks', info)


def do_table(user, args):
    def create(args):
        if args is None:
            do_help(user, ['table', 'create'])
            return
        table_name = colour.strip_tokens(' '.join(args))
        table_ = objects.Table(user, table_name)
        table_.start_time = int(mud.tick_count)
        #mud.add_tick(table_.round_timer, table_.start_time+50*60, repeat=False)
        mud.tables.append(table_)
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
                    channels.do_tinfo(user.table, "{} has joined the table.".format(t.name))
                    return
        user.presenter.show_msg("Could not find table '{}'.".format(table_name))

    @d_user_has(user, 'table')
    def dice(args):
        if args is not None:
            if str(args[0]).isdigit():
                die_size = int(args[0])
            else:
                do_help(user, ['table', 'dice'])
                return
        else:
            die_size = 6 # Default dice size
        roll = randint(1, die_size)
        channels.do_tinfo(user.table, "{} rolled {} on a {} sided dice.".format(user.name, roll, die_size))

    @d_user_has(user, 'table')
    def leave(args):
        table = user.table
        table.leave(user)
        channels.do_tinfo(table, "{} has left the table.".format(user.name))
        user.table = None
        if len(table.users) < 1:
            del table

    @d_user_has(user, 'table')
    def stack(args):
        user.table.stack(user)
        user.table.shuffle(user)
        channels.do_tinfo(user.table, "{} stacked their library.".format(user.name))

    @d_user_has(user, 'table')
    def life(args):
        if args is None:
            user.presenter.show_msg("Do what with your life total?")
            return
        if not is_int(args[0]):
            do_help(user, ['table', 'hp'])
            return
        user.table.life_totals[user] += int(args[0])
        channels.do_tinfo(user.table, "{} set their life total to {}.".format(user.name, user.table.life_totals[user]))

    @d_user_has(user, 'table')
    def draw(args):
        if len(user.table.libraries[user]) < 1:
            user.presenter.show_msg("Your library is empty!")
            return
        if args is None:
            user.table.draw(user)
            channels.do_tinfo(user.table, "{} draws a card.".format(user.name))
            return
        if not is_int(args[0]):
            do_help(user, ['table', 'draw'])
            return
        no_cards = int(args[0])
        if no_cards < 1:
            user.presenter.show_msg("Ummm... how would you even... Uhh... I don't... No. Just, no.")
            return
        user.table.draw(user, no_cards)
        channels.do_tinfo(user.table, "{} draws {} cards.".format(user.name, no_cards))

    @d_user_has(user, 'table')
    def hand(args):
        user.presenter.show_cards(user.table.hands[user])

    @d_user_has(user, 'table')
    def play(args):
        table = user.table
        if not is_int(args[0]):
            do_help(user, ['table', 'play'])
        card_index = int(args[0])
        if card_index >= len(table.hands[user]):
            user.presenter.show_msg("Out of range!")
            return
        card = table.hands[user][int(args[0])]
        table.play(user, card)
        channels.do_tinfo(user.table, "{} plays {}.".format(user.name, card.name))

    @d_user_has(user, 'table')
    def discard(args):
        table = user.table
        if not is_int(args[0]):
            do_help(user, ['table', 'play'])
        card_index = int(args[0])
        if card_index >= len(table.hands[user]):
            user.presenter.show_msg("Out of range!")
            return
        card = table.hands[user][int(args[0])]
        table.discard(user, card)
        channels.do_tinfo(user.table, "{} discards {}.".format(user.name, card.name))

    @d_user_has(user, 'table')
    def tap(args):
        table = user.table
        if args is None:
            do_help(user, ['table', 'tap'])
            return
        if is_int(args[0]):
            card_index = int(args[0])
            if card_index >= len(table.battlefields[user]):
                user.presenter.show_msg("Out of range!")
                return
            card = table.battlefields[user][card_index]
            if card.tapped:
                user.presenter.show_msg("{} is already tapped.".format(card.name))
                return
            card.tap()
            channels.do_tinfo(user.table, "{} taps {}.".format(user.name, card.name))
        elif args[0] == "all":
            for card in table.battlefields[user]:
                card.tap()
            channels.do_tinfo(user.table, "{} taps all their cards.".format(user.name))
        else:
            do_help(user, ['table', 'tap'])

    @d_user_has(user, 'table')
    def untap(args):
        table = user.table
        if args is None:
            do_help(user, ['table', 'untap'])
            return
        if is_int(args[0]):
            card_index = int(args[0])
            if card_index >= len(table.battlefields[user]):
                user.presenter.show_msg("Out of range!")
                return
            card = table.battlefields[user][card_index]
            if not card.tapped:
                user.presenter.show_msg("'{}' is not tapped.".format(card.name))
                return
            card.untap()
            channels.do_tinfo(user.table, "{} untaps {}.".format(user.name, card.name))
        elif args[0] == "all":
            for card in table.battlefields[user]:
                card.untap()
            channels.do_tinfo(user.table, "{} untaps all their cards.".format(user.name))
        else:
            do_help(user, ['table', 'tap'])

    @d_user_has(user, 'table')
    def shuffle(args):
        user.table.shuffle(user)
        channels.do_tinfo(user.table, "{} shuffled their library.".format(user.name))

    @d_user_has(user, 'table')
    def tutor(args):
        if args is None:
            do_help(user, ['table', 'tutor'])
            return
        card_name = ' '.join(args)
        if user.table.tutor(user, card_name):
            channels.do_tinfo(user.table, "{} tutored {} from their library.".format(user.name, card_name))
        else:
            user.presenter.show_msg("Failed to find '{}' in your library.".format(card_name))

    @d_user_has(user, 'table')
    def destroy(args):
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'destroy'])
            return
        card_index = int(args[0])
        if card_index >= len(table.battlefields[user]):
            user.presenter.show_msg("Out of range!")
            return
        card = table.battlefields[user][card_index]
        table.destroy(user, card)
        channels.do_tinfo(user.table, "{} destroys their {}.".format(user.name, card.name))

    @d_user_has(user, 'table')
    def return_(args):
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'return'])
            return
        card_index = int(args[0])
        if card_index >= len(table.battlefields[user]):
            user.presenter.show_msg("Out of range!")
            return
        card = table.battlefields[user][card_index]
        table.return_(user, card)
        channels.do_tinfo(user.table, "{} returns {} to their hand.".format(user.name, card.name))

    @d_user_has(user, 'table')
    def greturn(args):
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'greturn'])
            return
        card_index = int(args[0])
        if card_index >= len(table.graveyards[user]):
            user.presenter.show_msg("Out of range!")
            return
        card = table.graveyards[user][int(args[0])]
        table.greturn(user, card)
        channels.do_tinfo(user.table, "{} returns {} from their graveyard to hand.".format(user.name, card.name))

    @d_user_has(user, 'table')
    def unearth(args):
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'unearth'])
            return
        card_index = int(args[0])
        if card_index >= len(table.graveyards[user]):
            user.presenter.show_msg("Out of range!")
            return
        card = table.graveyards[user][card_index]
        table.unearth(user, card)
        channels.do_tinfo(user.table, "{} unearths their {}.".format(user.name, card.name))

    @d_user_has(user, 'table')
    def exile(args):
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'exile'])
            return
        card_index = int(args[0])
        if card_index >= len(table.graveyards[user]):
            user.presenter.show_msg("Out of range!")
            return
        card = table.battlefields[user][card_index]
        table.exile(user, card)
        channels.do_tinfo(user.table, "{} exiles their {}.".format(user.name, card.name))

    @d_user_has(user, 'table')
    def grexile(args):
        table = user.table
        if args is None or not is_int(args[0]):
            do_help(user, ['table', 'grexile'])
            return
        card_index = int(args[0])
        if card_index >= len(table.graveyards[user]):
            user.presenter.show_msg("Out of range!")
            return
        card = table.graveyards[user][card_index]
        table.grexile(user, card)
        channels.do_tinfo(user.table, "exiles {} from their graveyard.".format(user.name, card.name))

    @d_user_has(user, 'table')
    def scoop(args):
        if user.table is None:
            user.presenter.show_msg("You're not at a table!")
            return
        user.table.scoop(user)
        channels.do_tinfo(user.table, "{} scoops it up!".format(user.name))

    @d_user_has(user, 'table')
    def time(args):
        elapsed = int((mud.ticker - user.table.start_time)/60)
        user.presenter.show_msg("{} minutes have elapsed.".format(elapsed))

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
        user.presenter.show_msg(user.table.show())
        return

    if args[0] in verbs:
        verbs[args[0]](args[1:] if len(args) > 1 else None)
    else:
        do_help(user, ['table'])
