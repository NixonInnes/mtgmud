from random import shuffle

class Table(object):
    def __init__(self, client):
        self.owner = client
        self.battlefields = {}
        self.graveyards = {}
        self.exiles = {}
        self.libraries = {}
        self.hands = {}
        self.players = []

        self.add_player(client)


    def add_player(self, client):
        self.players.append(client.user)
        self.battlefields[client.user] = Pile()
        self.graveyards[client.user] = Pile()
        self.exiles[client.user] = Pile()
        self.libraries[client.user] = Pile()
        self.hands[client.user] = Pile()


class Pile(list):
    def __init__(self):
        super().__init__(self)

    def add(self, card, num=1):
        while num > 0:
            self.append(card)
            num -= 1

    def rem(self, card_name, num=1):
        while num > 0:
            for card in self:
                if card.name == card_name:
                    self.remove(card)

    def shuffle(self):
        shuffle(self)