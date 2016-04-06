from itertools import zip_longest
from textwrap import wrap
from app.libs import colour
from app.presenters.base import Presenter


class TextPresenter(Presenter):
    def present(self, buff):
        self.user.send(colour.colourify('\r\n' + buff + '\r\n' + self.draw_prompt()))

    def show_msg(self, msg):
        self.present(msg)

    def show_channel(self, channel, msg):
        self.present("&W[&x{}{}&x&W]&x {}{}&\r\n".format(channel.colour_token, channel.name, channel.colour_token, msg))

    def show_room(self, room):
        buff = "&y.-~~~~~~~~~~~~~~~~~~~~~~~~~~&Y{{&W {:^20} &Y}}&x&y~~~~~~~~~~~~~~~~~~~~~~~~~~-.&x\r\n".format(
                room.name)
        buff += "&y:                                                                              &y:&x\r\n"
        desc = wrap(room.description, width=72)
        for line in desc:
            buff += "&y:&x   {:<72}   &y:&x\r\n".format(line)
        buff += "&y:                                                                              &y:&x\r\n"
        occs = ', '.join(['You']+[user.name for user in room.occupants if user is not self.user])
        occs = wrap(occs, width=76)
        for line in occs:
            buff += "&Y#[&x {:<74} &Y]#&x\r\n".format(line)
        self.present(buff)

    def show_table(self, table):

        def table_card(index, card):
            buff = "&G|&x ({:2}) [{:1}] {:<27} &G|&x".format(index, "T" if card.tapped else "", card.name)
            return buff

        buff = "&g===========================&G[[&W {:^20} &G]]&g===========================&x\r\n".format(table.name)
        user_list = []
        for user in table.battlefields:
            card_list = ["&G|&x&g++++&w {:^28} &g++++&G|&x".format(user.name),
                         "&G|&x&g+++&x &RLi&x:&R{:^3}&x &GH&x:&G{:^3}&x &YL&x:&Y{:^3}&x &yG&x:&y{:^3}&x {:^5} &g+++&x&G|&x".format(
                                 table.life_totals[user], len(table.hands[user]),
                                 len(table.libraries[user]), len(table.graveyards[user]),
                                 table.poison_counters[user] if table.poison_counters[user] > 0 else None)]
            lands_list = []
            artifacts_list = []
            enchantments_list = []
            creatures_list = []
            others_list = []
            for card in table.battlefields[user]:
                if 'Land' in card.types:
                    lands_list.append(table_card(table.battlefields[user].index(card), card))
                elif 'Artifact' in card.types:
                    artifacts_list.append(table_card(table.battlefields[user].index(card), card))
                elif 'Enchantment' in card.types:
                    enchantments_list.append(table_card(table.battlefields[user].index(card), card))
                elif 'Creature' in card.types:
                    creatures_list.append(table_card(table.battlefields[user].index(card), card))
                else:
                    others_list.append(table_card(table.battlefields[user].index(card), card))
            card_list += lands_list + artifacts_list + enchantments_list + creatures_list + others_list
            user_list.append(card_list[:])
        battlefield_list = list(zip_longest(*user_list))
        for lines in battlefield_list:
            for card in lines:
                buff += "{}{}".format("\r\n" if card is lines[0] else "",
                                      "&G|                                      |&x" if card is None else card)
        self.present(buff)

    def show_card(self, card):
        self.present(draw_card(card))

    def show_cards(self, cards):
        buff = ""
        for card in cards:
            buff += draw_card(card)
        self.present(buff)

    def draw_prompt(self):
        buff = ""
        if self.user.name is not None:
            buff += "&B<&x &c{}&x ".format(self.user.name)
            if self.user.deck is not None:
                buff += "&B||&x &c{}&x &C(&x&c{}&x&C)&x ".format(self.user.deck.name, self.user.deck.no_cards)
            if self.user.table is not None:
                buff += "&B||&x &GH&x:&G{}&x &YL&x:&Y{}&x &yG&x:&y{}&x ".format(len(self.user.table.hands[self]),
                                                                                len(self.user.table.libraries[self]),
                                                                                len(self.user.table.graveyards[self]))
        buff += "&B>&x&w>> &x"
        return buff


########################################################################################################################
# Additional functions



def draw_card(card):
    if card.colors is None:
        c_token = "&w"
    elif len(card.colors) > 1:
        c_token = "&Y"
    elif 'White' in card.colors:
        c_token = "&W"
    elif 'Blue' in card.colors:
        c_token = "&U"
    elif 'Black' in card.colors:
        c_token = "&B"
    elif 'Red' in card.colors:
        c_token = "&R"
    elif 'Green' in card.colors:
        c_token = "&G"
    else:
        c_token = "&w"
    buff = c_token + "****************************************&x\r\n"
    buff += c_token + "*&x {:<29} {:>6} ".format(card.name, str(
        card.manaCost) if card.manaCost is not None else "") + c_token + "*&x\r\n"
    buff += c_token + "****************************************&x\r\n"
    buff += c_token + "*&x {:<36} ".format(card.type) + c_token + "*&x\r\n"
    buff += c_token + "****************************************&x\r\n"
    buff += c_token + "*                                      *&x\r\n"
    if card.text is not None:
        textbox = wrap(card.text, width=36)
        for line in textbox:
            buff += c_token + "*&x {:<36} ".format(line) + c_token + "*&x\r\n"
    if card.power is not None:
        buff += c_token + "*&x                              {:^3}/{:^3} ".format(str(card.power), str(
            card.toughness)) + c_token + "*&x\r\n"
    elif card.loyalty is not None:
        buff += c_token + "*&x                                   {:^3} ".format(
            str(card.loyalty)) + c_token + "*&x\r\n"
    else:
        buff += c_token + "*                                      *&x\r\n"
    buff += c_token + "****************************************&x\r\n"
    return buff


FOOTER_80 = "&c||############################################################################||&x\r\n"
BLANK_80 = "&c||                                                                            ||&x\r\n"
ROW_LINE_80 = "&c||============================================================================||&x\r\n"
BLANK_2COL_80 = "&c||                                     ||                                     ||&x\r\n"
ROW_LINE_2COL_80 = "&c||=====================================||=====================================||&x\r\n"
BLANK_3COL_80 = "&c||                        ||                        ||                        ||&x\r\n"
ROW_LINE_3COL_80 = "&c||========================||========================||========================||&x\r\n"

FOOTER_40 = "&c||####################################||&x\r\n"
BLANK_40 = "&c||                                    ||&x\r\n"
ROW_LINE_40 = "&c||====================================||&x\r\n"
BLANK_2COL_40 = "&c||                 ||                 ||&x\r\n"
ROW_LINE_2COL_40 = "&c||=================||=================||&x\r\n"


def header_80(title):
    buff = "&c||##########################&C[&x &W{:^20}&x &C]&x&c##########################||&x\r\n".format(title)
    buff += BLANK_80
    return buff


def body_80(string, align='center'):
    if align == 'left':
        buff = "&c||&x {:<74} &c||&x\r\n".format(string)
    elif align == 'right':
        buff = "&c||&x {:>74} &c||&x\r\n".format(string)
    else:  # center
        buff = "&c||&x {:^74} &c||&x\r\n".format(string)
    return buff


def body_2cols_80(stringA, stringB):
    buff = "&c||&x {:^35} &c||&x {:^35} &c||&x\r\n".format(stringA, stringB)
    return buff


def body_3cols_80(stringA, stringB, stringC):
    buff = "&c||&x {:^22} &c||&x {:^22} &c||&x {:^22} &c||&x\r\n".format(stringA, stringB, stringC)
    return buff


def header_40(title):
    buff = "&c||###########&C[&x &W{:^10}&x &C]&x&c###########||&x\r\n".format(title)
    buff += BLANK_40
    return buff


def body_40(string, align='center'):
    if align == 'left':
        buff = "&c||&x {:<34} &c||&x\r\n".format(string)
    elif align == 'right':
        buff = "&c||&x {:>34} &c||&x\r\n".format(string)
    else:  # center
        buff = "&c||&x {:^34} &c||&x\r\n".format(string)
    return buff


def body_2cols_40(stringA, stringB):
    buff = "&c||&x {:^14} &c||&x {:^14} &c||&x\r\n".format(stringA, stringB)
    return buff
