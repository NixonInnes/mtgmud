from itertools import zip_longest
from random import shuffle
import style

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
        self.name = card.name
        self.names = card.names
        self.manaCost = card.manaCost
        self.cmc = card.cmc
        self.colors = card.colors
        self.type = card.type
        self.supertypes = card.supertypes
        self.types = card.types
        self.subtypes = card.subtypes
        self.rarity = card.rarity
        self.text = card.text
        self.power = card.power
        self.toughness = card.toughness
        self.loyalty = card.loyalty

        self.tapped = False
        self.counters = 0


class Pile(list):
    def __init__(self):
        super().__init__(self)
        self.name = None

    def shuffle(self):
        shuffle(self)

    def count(self):
        return len(self)