from itertools import zip_longest
from random import shuffle

from app import db, style


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
    def __init__(self):
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
        return card


class Pile(list):
    def __init__(self):
        super().__init__(self)
        self.name = None

    def shuffle(self):
        shuffle(self)

    def count(self):
        return len(self)