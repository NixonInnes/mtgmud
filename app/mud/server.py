import requests, threading, time

from app import db, config
from app.db import models as db_models
from . import models as v_models

# specify a function to be executed with specified params every n seconds.
class PeriodicExecutor(threading.Thread):
    def __init__(self,sleep,func):
        """ execute func() every 'sleep' seconds """
        self.func = func
        self.sleep = sleep
        threading.Thread.__init__(self,name = "PeriodicExecutor")
        self.setDaemon(True)
    def run(self):
        while 1:
            time.sleep(self.sleep)
            self.func()


class Mud(object):
    def __init__(self):
        self.connected = []
        self.users = []
        self.rooms = []
        self.tables = []
        # A tick is a list of (function, params, interval)
        self.ticks = []
        self.ticker = 0
        self.tick = PeriodicExecutor(1, self.do_tick)
        self.tick.start()


        print("Checking Room database...")
        if db.session.query(db_models.Room).filter_by(name=config.LOBBY_ROOM_NAME).first() is None:
            print("No lobby found, creating...")
            lobby = db_models.Room(
                name=config.LOBBY_ROOM_NAME,
                description=config.LOBBY_ROOM_DESC
            )
            db.session.add(lobby)
            db.session.commit()
            print("Lobby created.")

        print("Loading rooms...")
        for i in db.session.query(db_models.Room).all():
            print("Loading room: {}".format(i.name))
            room = v_models.Room.load(i)
            self.rooms.append(room)
        print("Rooms loaded.")

        print("Checking Card database...")
        if len(db.session.query(db_models.Card).all()) < 1:
            print("Card database is empty. \nNow populating...")
            self.update_cards()
        else:
            print("Cards exist.")

    def add_tick(self, func, interval, repeat=True):
        self.ticks.append((func, interval, repeat))

    def do_tick(self):
        for tick in self.ticks:
            func, interval, repeat = tick
            if self.ticker % interval is 0:
                func()
                if not repeat:
                    self.ticks.remove(tick)
        self.ticker += 1

    def get_room(self, room_name):
        for room in self.rooms:
            if room.name == room_name:
                return room
        return None

    def get_user(self, user_name):
        for user in self.users:
            if user.name == user_name:
                return user
        return None

    def get_lobby(self):
        for room in self.rooms:
            if room.name == config.LOBBY_ROOM_NAME:
                return room
        return None

    def test_tick(self):
        for user in self.users:
            user.msg_self("\n&W[&RANNOUNCEMENT&W]&x Ding-dong. Another hour has gone by...")

    @staticmethod
    def update_cards():
        cards = requests.get('http://mtgjson.com/json/AllCards.json').json()
        for c in cards:
            card = db_models.Card(
                name = cards[c]['name'],
                names = cards[c]['names'] if 'names' in cards[c] else None,
                manaCost = cards[c]['manaCost'] if 'manaCost' in cards[c] else None,
                cmc = cards[c]['cmc'] if 'cmc' in cards[c] else None,
                colors = cards[c]['colors'] if 'colors' in cards[c] else None,
                type = cards[c]['type'],
                supertypes = cards[c]['supertypes'] if 'supertypes' in cards[c] else None,
                types = cards[c]['types'] if 'types' in cards[c] else None,
                subtypes = cards[c]['subtypes'] if 'subtypes' in cards[c] else None,
                rarity = cards[c]['rarity'] if 'rarity' in cards[c] else None,
                text = cards[c]['text'] if 'text' in cards[c] else None,
                power = cards[c]['power'] if 'power' in cards[c] else None,
                toughness = cards[c]['toughness'] if 'toughness' in cards[c] else None,
                loyalty = cards[c]['loyalty'] if 'loyalty' in cards[c] else None
            )
            db.session.add(card)
        db.session.commit()