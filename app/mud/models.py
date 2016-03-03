from itertools import zip_longest
from random import shuffle
from asyncio import Protocol

from app import db, server, style
from app.player import actions, channels


class User(Protocol):

    def connection_made(self, transport):
        self.transport = transport
        self.addr = transport.get_extra_info('peername')
        self.authd = False
        self.name = None
        self.admin = False
        self.room = None
        self.db = None

        self.flags = []

        print("Connected: {}".format(self.addr))
        server.users.append(self)

        #TODO: Add a welcome function
        self.msg_self("\n########## Welcome to MtGMUD!! ##########\n\nLogin: <username> <password>\nRegister: register <username> <password> <password>")
        self.get_prompt()

    def data_received(self, data):
        msg = data.decode().strip()
        args = msg.split()

        if self.authd is False:
            actions['login'](self, args)
            return

        if msg:
            if msg[0] in channels:
                channels[msg[0]](self, msg[1:])
                self.get_prompt()
                return

            if args[0] in actions:
                actions[args[0]](self, args[1:] if len(args) > 1 else None)
                self.get_prompt()
                return

            self.msg_self("\nHuh?")
        self.get_prompt()

    def get_prompt(self):
        # [username]<deck (60)>>>
        buff = "\n"
        if self.username is not None:
            buff += "[{}]".format(self.username)
            if self.deck is not None:
                buff += "<{} ({})>".format(self.deck.name, self.deck.no_cards)
        buff += ">> "
        self.transport.write(buff.encode())

    def msg_self(self, msg):
        self.transport.write(msg.encode())

    @staticmethod
    def msg_client(client, msg):
        client.transport.write(msg.encode())

    @staticmethod
    def load(dbUser):
        user = User()
        user.name = str(dbUser.name)
        user.admin = bool(dbUser.admin)
        user.deck = dbUser.deck
        user.decks = dbUser.decks
        user.db = dbUser
        return user

    def save(self):
        self.db.name = self.name
        self.db.admin = self.admin
        db.session.commit()

    def connection_lost(self, ex):
        print("Disconnected: {}".format(self.addr))
        server.users.remove(self)

        if self.authd:
            self.save()
            self.user.room.occupants.remove(self.user)



class Room(object):
    def __init__(self):
        self.name = None
        self.description = None
        self.db = None

        self.occupants = []
        self.tables = []

    @staticmethod
    def load(db_room):
        room = Room()
        room.name = db_room.name
        room.description = db_room.description
        room.db = db_room
        return room

    def save(self):
        self.db.room.name = self.name
        self.db.description = self.description
        db.session.commit()


class Table(object):
    def __init__(self, user, name):
        self.owner = user
        self.name = name
        self.battlefields = {}
        self.graveyards = {}
        self.exiles = {}
        self.libraries = {}
        self.hands = {}
        self.users = []

    def add_player(self, user):
        self.users.append(user)
        self.battlefields[user] = []
        self.graveyards[user] = Pile()
        self.exiles[user] = Pile()
        self.libraries[user] = Pile()
        self.hands[user] = []

    #TODO: move these functions back into actions
    def stack_library(self, user, card_list):
        for card in card_list:
            self.libraries[user].append(card)

    def shuffle_library(self, user):
        self.libraries[user].shuffle()

    def draw_card(self, user, num=1):
        for i in range(int(num)):
            self.hands[user].append(self.libraries[user][0])
            self.libraries[user].pop(0)

    #TODO: This needs moved into an action
    def show(self):
        buff = style.table_header(self.name)
        for user in self.battlefields:
            card_list = [style.table_user(user.name)]
            for card in self.battlefields[user]:
                card_list.append(style.table_card(self.battlefields[user].index(card), card))
            user_list = [card_list[:]]
        battlefield_list = list(zip_longest(*user_list))
        for lines in battlefield_list:
            for line in lines:
                buff += "\n{}".format("||"+" "*20+"|" if line is None else line)
        return buff


class Card(object):
    def __init__(self, card):
        self.name = None
        self.names = None
        self.manaCost = None
        self.cmc = None
        self.colors = None
        self.type = None
        self.supertypes = None
        self.types = None
        self.subtypes = None
        self.rarity = None
        self.text = None
        self.power = None
        self.toughness = None
        self.loyalty = None

        self.tapped = False
        self.counters = 0

    @staticmethod
    def load(db_card):
        card = Card()
        card.name = db_card.name
        card.names = db_card.names
        card.manaCost = db_card.manaCost
        card.cmc = db_card.cmc
        card.colors = db_card.colors
        card.type = db_card.type
        card.supertypes = db_card.supertypes
        card.types = db_card.types
        card.subtypes = db_card.subtypes
        card.rarity = db_card.rarity
        card.text = db_card.text
        card.power = db_card.power
        card.toughness = db_card.toughness
        card.loyalty = db_card.loyalty


class Pile(list):
    def __init__(self):
        super().__init__(self)
        self.name = None

    def shuffle(self):
        shuffle(self)

    def count(self):
        return len(self)