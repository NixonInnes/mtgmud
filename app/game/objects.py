from random import shuffle
from app import db


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
        room.name = str(db_room.name)
        room.description = str(db_room.description)
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
        self.start_time = 0
        self.battlefields = {}
        self.graveyards = {}
        self.exiles = {}
        self.libraries = {}
        self.hands = {}
        self.life_totals = {}
        self.poison_counters = {}
        self.users = []

    # def round_timer(self):
    #     for user in self.users:
    #         user.presenter.send_msg("&W[&x&gtable&x&W]&x &g50 minutes has elapsed.&w\r\n")

    def join(self, user):
        self.users.append(user)
        self.battlefields[user] = []
        self.graveyards[user] = []
        self.exiles[user] = []
        self.libraries[user] = []
        self.hands[user] = []
        self.life_totals[user] = 20
        self.poison_counters[user] = 0

    def leave(self, user):
        self.hands.pop(user)
        self.libraries.pop(user)
        self.exiles.pop(user)
        self.graveyards.pop(user)
        self.battlefields.pop(user)
        self.life_totals.pop(user)
        self.poison_counters.pop(user)
        self.users.remove(user)

    def stack(self, user):
        user.table.libraries[user].clear()
        for card in user.deck.cards:
            dbCard = db.session.query(db.models.Card).get(card)
            for i in range(user.deck.cards[card]):
                self.libraries[user].append(Card.load(dbCard))
        self.life_totals[user] = 20
        self.poison_counters[user] = 0

    def shuffle(self, user):
        shuffle(self.libraries[user])

    def draw(self, user, num=1):
        for i in range(int(num)):
            self.hands[user].append(self.libraries[user][0])
            self.libraries[user].pop(0)

    def play(self, user, card):
        self.battlefields[user].append(card)
        self.hands[user].remove(card)

    def discard(self, user, card):
        self.hands[user].remove(card)
        self.graveyards[user].append(card)

    def tutor(self, user, card_name):
        for card in self.libraries[user]:
            if card.name.lower() == card_name.lower():
                self.hands[user].append(card)
                self.libraries[user].remove(card)
                return True
        return False

    def destroy(self, user, card):
        self.battlefields[user].remove(card)
        self.graveyards[user].append(card)

    def return_(self, user, card):
        self.battlefields[user].remove(card)
        self.hands[user].append(card)

    def greturn(self, user, card):
        self.graveyards[user].remove(card)
        self.hands[user].append(card)

    def unearth(self, user, card):
        self.graveyards[user].remove(card)
        self.battlefields[user].append(card)

    def exile(self, user, card):
        self.battlefields[user].remove(card)
        self.exiles[user].append(card)

    def grexile(self, user, card):
        self.graveyards[user].remove(card)
        self.exiles[user].append(card)

    def hexile(self, user, card):
        self.hands[user].remove(card)
        self.exiles[user].append(card)

    def scoop(self, user):
        self.hands[user].clear()
        self.graveyards[user].clear()
        self.exiles[user].clear()
        self.libraries[user].clear()


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

    def tap(self):
        self.tapped = True

    def untap(self):
        self.tapped = False

    # Not done in __init__ incase we want to create cards on the fly one day... (tokens?)
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