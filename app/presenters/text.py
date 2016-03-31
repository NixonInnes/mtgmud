from itertools import zip_longest
from textwrap import wrap
from app.presenters.base import Presenter


class TextPresenter(Presenter):

    # TODO: write show_channels()
    def show_channel(self, channel, msg):
        self.present("&W[&x{}{}&x&W]&x {}{}&x".format(channel.colour_token, channel.name, channel.colour_token, msg))

    def show_room(self, room):
        buff = "&y.-~~~~~~~~~~~~~~~~~~~~~~~~~~&Y{{&W {:^20} &Y}}&x&y~~~~~~~~~~~~~~~~~~~~~~~~~~-.&x\r\n".format(room.name)
        buff += "&y:                                                                              &y:&x\r\n"
        desc = wrap(room.desc, width=72)
        for line in desc:
            buff += "&y:&x   {:<72}   &y:&x\r\n".format(line)
        buff += "&y:                                                                              &y:&x\r\n"
        occs = ', '.join([user.name for user in room.occupants])
        occs = wrap(occs, width=76)
        for line in occs:
            buff += "&Y#[&x {:<74} &Y]#&x\r\n".format(line)
        self.present(buff)

    def show_table(self, table):
        # TODO: fix this mess
        def table_header(name):
            buff = "&g===========================&G[[&W {:^20} &G]]&g===========================&x\r\n".format(name)
            return buff

        def table_user(name):
            buff = "&G|&x&g++++&w {:^28} &g++++&G|&x".format(name)
            return buff

        def table_user_stats(life, hand, library, graveyard, poison=None):
            buff = "&G|&x&g+++&x &RLi&x:&R{:^3}&x &GH&x:&G{:^3}&x &YL&x:&Y{:^3}&x &yG&x:&y{:^3}&x {:^5} &g+++&x&G|&x".format(
                life, hand, library, graveyard, "&MP&x:&M{:^3}&x".format(poison) if poison is not None else "")
            return buff

        def table_card(index, card):
            buff = "&G|&x ({:2}) [{:1}] {:<27} &G|&x".format(index, "T" if card.tapped else "", card.name)
            return buff

        def table_card_blank():
            buff = "&G|                                      |&x"
            return buff
        buff = table_header(table.name)
        user_list = []
        for user in table.battlefields:
            card_list = [table_user(user.name),
                         table_user_stats(table.life_totals[user], len(table.hands[user]),
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
            card_list += lands_list+artifacts_list+enchantments_list+creatures_list+others_list
            user_list.append(card_list[:])
        battlefield_list = list(zip_longest(*user_list))
        for lines in battlefield_list:
            for card in lines:
                buff += "{}{}".format("\r\n" if card is lines[0] else "", table_card_blank() if card is None else card)
        self.present(buff)

    def show_card(self, card):
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
        buff = c_token+"****************************************&x\r\n"
        buff += c_token+"*&x {:<29} {:>6} ".format(card.name, str(card.manaCost) if card.manaCost is not None else "")+c_token+"*&x\r\n"
        buff += c_token+"****************************************&x\r\n"
        buff += c_token+"*&x {:<36} ".format(card.type)+c_token+"*&x\r\n"
        buff += c_token+"****************************************&x\r\n"
        buff += c_token+"*                                      *&x\r\n"
        if card.text is not None:
            textbox = wrap(card.text, width=36)
            for line in textbox:
                buff += c_token+"*&x {:<36} ".format(line)+c_token+"*&x\r\n"
        if card.power is not None:
            buff += c_token+"*&x                              {:^3}/{:^3} ".format(str(card.power), str(card.toughness))+c_token+"*&x\r\n"
        elif card.loyalty is not None:
            buff += c_token+"*&x                                   {:^3} ".format(str(card.loyalty))+c_token+"*&x\r\n"
        else:
            buff += c_token+"*                                      *&x\r\n"
        buff += c_token+"****************************************&x\r\n"
        self.present(buff)


########################################################################################################################
# Additional functions


COLOUR_TOKENS = {
    '&b': '\033[30m', #black
    '&B': '\033[1;30m', #bright-black
    '&r': '\033[31m', #red
    '&R': '\033[1;31m', #bright-red
    '&g': '\033[32m', #green
    '&G': '\033[1;32m', #bright-green
    '&y': '\033[33m', #yellow
    '&Y': '\033[1;33m', #bright-yellow
    '&u': '\033[34m', #blue
    '&U': '\033[1;34m', #bright-blue
    '&m': '\033[35m', #magenta
    '&M': '\033[1;35m', #bright-magenta
    '&c': '\033[36m', #cyan
    '&C': '\033[1;36m', #bright-cyan
    '&w': '\033[37m', #white
    '&W': '\033[1;37m', #bright-white
    '&x': '\033[0m' #reset
}


def colourify(buff):
    for token in COLOUR_TOKENS:
        buff = buff.replace(token, COLOUR_TOKENS[token])
    return buff


def strip_colours(buff):
    for token in COLOUR_TOKENS:
        buff = buff.replace(token, '')
    return buff


FOOTER_80 =        "&c||############################################################################||&x\r\n"
BLANK_80 =         "&c||                                                                            ||&x\r\n"
ROW_LINE_80 =      "&c||============================================================================||&x\r\n"
BLANK_2COL_80=     "&c||                                     ||                                     ||&x\r\n"
ROW_LINE_2COL_80 = "&c||=====================================||=====================================||&x\r\n"
BLANK_3COL_80 =    "&c||                        ||                        ||                        ||&x\r\n"
ROW_LINE_3COL_80 = "&c||========================||========================||========================||&x\r\n"

FOOTER_40 =        "&c||####################################||&x\r\n"
BLANK_40 =         "&c||                                    ||&x\r\n"
ROW_LINE_40 =      "&c||====================================||&x\r\n"
BLANK_2COL_40 =    "&c||                 ||                 ||&x\r\n"
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
    else: # center
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
    else: # center
        buff = "&c||&x {:^34} &c||&x\r\n".format(string)
    return buff


def body_2cols_40(stringA, stringB):
    buff = "&c||&x {:^14} &c||&x {:^14} &c||&x\r\n".format(stringA, stringB)
    return buff