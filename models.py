from itertools import zip_longest

class Table(object):
    def __init__(self, client, name):
        self.owner = client
        self.name = name
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


    def show(self):
        buff = "\n||############################################################################||"
        for user in self.battlefields:
            c_list = ["||{:*^25}".format(user.name)]
            for card in self.battlefields[user]:
                c_list.append("||({}) {:<20}|".format(self.battlefields[user].index(card), card.name))
            p_list = [c_list[:]]
        b_list = [zip_longest(*p_list)]
        for lines in b_list:
            for card in lines:
                buff += "\n{}".format("||"+" "*20+"|" if lines[card] is None else lines[card])
        return buff
