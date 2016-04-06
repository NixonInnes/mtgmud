import threading
import time
from app import config, db
from app.game import objects
from app.libs import db_funcs


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
        self.startup()

    def startup(self):
        print("Checking Room database...")
        if db.session.query(db.models.Room).filter_by(name=config.LOBBY_ROOM_NAME).first() is None:
            print("No lobby found....")
            db_funcs.create_lobby()
        self.load_rooms()

        print("Checking Card database...")
        if db.session.query(db.models.Card).count() < 1:
            print("Card database is empty. \r\nNow populating...")
            db_funcs.create_cards()
        else:
            print("Cards exist.")

        print("Checking for channels...")
        if db.session.query(db.models.Channel).count() < 1:
            print("No channels found...")
            db_funcs.create_default_channels()
        else:
            print("Channels exist.")
        self.load_channels()

        print("Checking for emotes...")
        if db.session.query(db.models.Emote).count() < 1:
            print("No emotes found...")
            db_funcs.create_emotes()
        else:
            print("Emotes exist.")

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

