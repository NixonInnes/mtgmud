from Event import Event

class CursesView(object):
    def __init__(self):
        self.handle_user_input = Event()
        self.loop = True

    def startMainLoop(self):
        while self.loop:
            value = input('What do you want? ')
            ret = self.handle_user_input(value)

    def show(self, value):
        # curses.show something
        print(value)

    def exit(self):
        self.loop = False

    def showCard(self, card):
        print('this is a card')
        print('|-------------|')
        print('| o         o |')
        print('|      --     |')
        print('|-------------|')
        print(' Golem: hp 120 ')
        print(' mp 400, spd 1 ')
