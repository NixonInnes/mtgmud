import threading
import time


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

