class Presenter(object):

    def __init__(self, user):
        self.user = user

    def present(self, buff):
        self.user.send(buff)

    def show_channel(self, channel, msg):
        raise NotImplementedError

    def show_room(self, room):
        raise NotImplementedError

    def show_table(self, table):
        raise NotImplementedError

    def show_card(self, card):
        raise NotImplementedError
