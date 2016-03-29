from Event import Event

class TextView(object):
    def __init__(self):
        self.handle_user_input = Event()
        self.loop = True

    def startMainLoop(self):
        while self.loop:
            value = input('What do you want? ')
            ret = self.handle_user_input(value)

    def show(self, value):
        print(value)

    def exit(self):
        self.loop = False

    def showCard(self, card):
        # nothing happens, b/c textView doesn't support this feature
        print('Nothing...')
