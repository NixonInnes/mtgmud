class Presenter(object):

    def __init__(self, user):
        self.user = user

    def present(self, buff):
        self.user.send(buff)

    def show_msg(self, msg):
        raise NotImplementedError

    def show_info(self, title, header, info):
        raise NotImplementedError

    def show_info_2col(self, title, header, info):
        raise NotImplementedError

    def show_info_3col(self, title, header, info):
        raise NotImplementedError

    def show_channel(self, channel, msg):
        raise NotImplementedError

    def show_room(self, room):
        raise NotImplementedError

    def show_table(self, table):
        raise NotImplementedError

    def show_card(self, card):
        raise NotImplementedError

    def show_cards(self, cards):
        raise NotImplementedError

    def show_help(self, help_file):
        raise NotImplementedError