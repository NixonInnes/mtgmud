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
        self.users = []

        self.add_player(client)


    def add_player(self, client):
        self.users.append(client.user)
        self.battlefields[client.user] = []
        self.graveyards[client.user] = []
        self.exiles[client.user] = Pile()
        self.libraries[client.user] = Pile()
        self.hands[client.user] = Pile()


    def show(self):
        buff = "\n||############################################################################||"
        for user in self.battlefields:
            card_list = ["||{:*^25}".format(user.name)]
            for card in self.battlefields[user]:
                card_list.append("||({}) {:<20}|".format(self.battlefields[user].index(card), card.name))
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

class Pile(list):
    def __init__(self):
        super().__init__(self)
        self.name = None

    def shuffle(self):
        shuffle(self)

    def count(self):
        return len(self)
