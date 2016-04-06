import json
import threading
import time

import requests
from . import objects
from app import config, db


class Ticker(threading.Thread):
    def __init__(self, sleep, func):
        """ execute func() every 'sleep' seconds """
        self.func = func
        self.sleep = sleep
        threading.Thread.__init__(self, name = "Ticker")
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
        self.channels = {}
        # A tick is a list of (function, interval, repeat?)
        self.ticks = []
        self.tick_count = 0
        self.ticker = Ticker(1, self.do_tick)
        self.ticker.start()

        print("Checking Room database...")
        if db.session.query(db.models.Room).filter_by(name=config.LOBBY_ROOM_NAME).first() is None:
            print("No lobby found....")
            self.create_lobby()
        self.load_rooms()

        print("Checking Card database...")
        if db.session.query(db.models.Card).count() < 1:
            print("Card database is empty. \r\nNow populating...")
            self.create_cards()
        else:
            print("Cards exist.")

        print("Checking for channels...")
        if db.session.query(db.models.Channel).count() < 1:
            print("No channels found...")
            self.create_default_channels()
        else:
            print("Channels exist.")
        self.load_channels()

        print("Checking for emotes...")
        if db.session.query(db.models.Emote).count() < 1:
            print("No emotes found...")
            self.create_default_emotes()
        else:
            print("Emotes exist.")

    @staticmethod
    def create_lobby():
        print("Creating {}...".format(config.LOBBY_ROOM_NAME))
        lobby = db.models.Room(
            name=config.LOBBY_ROOM_NAME,
            description=config.LOBBY_ROOM_DESC
        )
        db.session.add(lobby)
        db.session.commit()
        print("{} created.".format(lobby.name))

    def load_rooms(self):
        print("Loading rooms...")
        if self.rooms is not None:
            print("Cleaning out existing rooms...")
            for user in self.users:
                user.room = None
            self.rooms.clear()
        for i in db.session.query(db.models.Room).all():
            print("Loading room: {}".format(i.name))
            room = objects.Room.load(i)
            self.rooms.append(room)
        print("Rooms loaded.")

    def load_channels(self):
        print("Loading channels...")
        if self.channels is not None:
            print("Clearing out existing channels...")
            self.channels.clear()
        for channel in db.session.query(db.models.Channel).all():
            print("Loading channel: {}".format(channel.name))
            self.channels[channel.key] = channel
        print("Channels loaded.")

    def add_tick(self, func, interval, repeat=True):
        self.ticks.append((func, interval, repeat))

    def do_tick(self):
        for tick in self.ticks:
            func, interval, repeat = tick
            if self.tick_count % interval is 0:
                func()
                if not repeat:
                    self.ticks.remove(tick)
        self.tick_count += 1

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

    @staticmethod
    def create_default_channels():
        print("Creating default channels...")
        chat = db.models.Channel(
            key = ".",
            name = "chat",
            colour_token = "&G",
            type = 0,
            default = True
        )
        db.session.add(chat)
        say = db.models.Channel(
            key = "\'",
            name = "say",
            colour_token = "&C",
            type = 1,
            default = True
        )
        db.session.add(say)
        tchat = db.models.Channel(
            key = ";",
            name = "tchat",
            colour_token = "$y",
            type = 2,
            default = True
        )
        db.session.add(tchat)
        whisper = db.models.Channel(
            key = ">",
            name = "whisper",
            colour_token = "&M",
            type = 3,
            default = True
        )
        db.session.add(whisper)
        db.session.commit()
        print("Created default channels: {}".format(', '.join([channel.name for channel in db.session.query(db.models.Channel).filter_by(default=True).all()])))

    @staticmethod
    def create_default_emotes():
        print("Creating default emotes...")
        with open('app/player/emotes.json') as emotes_json:
            emotes = json.load(emotes_json)
        for e in emotes:
            print("Adding emote: {}".format(e))
            emote = db.models.Emote(
                name = emotes[e]['name'],
                user_no_vict = emotes[e]['user_no_vict'],
                others_no_vict = emotes[e]['others_no_vict'] if 'others_no_vict' in emotes[e] else None,
                user_vict = emotes[e]['user_vict'] if 'user_vict' in emotes[e] else None,
                others_vict = emotes[e]['others_vict'] if 'others_vict' in emotes[e] else None,
                vict_vict = emotes[e]['vict_vict'] if 'vict_vict' in emotes[e] else None,
                user_vict_self = emotes[e]['user_vict_self'] if 'user_vict_self' in emotes[e] else None,
                others_vict_self = emotes[e]['others_vict_self'] if 'others_vict_self' in emotes[e] else None
            )
            db.session.add(emote)
        db.session.commit()

    @staticmethod
    def create_cards():
        cards = requests.get('http://mtgjson.com/json/AllCards.json').json()
        for c in cards:
            card = db.models.Card(
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