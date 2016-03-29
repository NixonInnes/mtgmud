class ClientPresenter(object):
    def __init__(self, view):
        self.view = view

        self.view.handle_user_input.append(self.handleInput)

    def start(self):
        self.view.startMainLoop()

    def handleInput(self, val):
        if val.lower() == 'a':
            self._handleA()
        elif val.lower() == 'b':
            self._handleB()
        elif val.lower() == 'q':
            self._handleQ()
        elif val.lower() == 'card':
            self._handleCard()

    def _handleA(self):
        self.view.show('The user typed an A')

    def _handleB(self):
        self.view.show('The user typed a B')

    def _handleQ(self):
        self.view.show('The user typed a Q. Exiting now')
        self.view.exit()

    def _handleCard(self):
        self.view.showCard(1)

if __name__ == '__main__':
    from textView import TextView
    from cursesView import CursesView

    print('----------------------------')
    print('   THIS IS THE TEXTVIEW UI  ')
    print('(hint, type a, b, q, or card')
    print('----------------------------\n\n')
    view = TextView()
    presenter = ClientPresenter(view)
    presenter.start()

    print('\n\n\n\n----------------------------')
    print('   THIS IS THE TEXTVIEW UI  ')
    print('(hint, type a, b, q, or card')
    print('----------------------------\n\n')

    view = CursesView()
    presenter = ClientPresenter(view)
    presenter.start()
