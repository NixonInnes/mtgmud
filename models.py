from itertools import zip_longest
from random import shuffle

class Table(object):
    def __init__(self, client, name):
        self.owner = client
        self.name = name
        self.battlefields = {}
        self.graveyards = {}
        self.exiles = {}
        self.libraries = {}
        self.hands = {}
        self.clients = []

    def add_player(self, client):
        self.clients.append(client)
        self.battlefields[client] = []
        self.graveyards[client] = Pile()
        self.exiles[client] = Pile()
        self.libraries[client] = Pile()
        self.hands[client] = []

    #TODO: move these functions back into actions
    def stack_library(self, client, card_list):
        for card in card_list:
            self.libraries[client].append(card)

    def shuffle_library(self, client):
        self.libraries[client].shuffle()

    def draw_card(self, client, num=1):
        for i in range(int(num)):
            self.hands[client].append(self.libraries[client][0])
            self.libraries[client].pop(0)

    #TODO: This needs moved into an action
    def show(self):
        buff = "\n||############################################################################||"
        for client in self.battlefields:
            card_list = ["||{:*^25}".format(client.user.name)]
            for card in self.battlefields[client]:
                card_list.append("||({}) {:<20}|".format(self.battlefields[client].index(card), card.name))
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