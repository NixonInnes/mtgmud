from .textStyle import *


def show_room(room):
    buff = "&y.-~~~~~~~~~~~~~~~~~~~~~~~~~~&Y{{&W {:^20} &Y}}&x&y~~~~~~~~~~~~~~~~~~~~~~~~~~-.&x\r\n".format(room.name)
    buff += ""
    buff += "&y:                                                                              &y:&x\r\n"
    desc = wrap(room.desc, width=72)
    for line in desc:
        buff += "&y:&x   {:<72}   &y:&x\r\n".format(line)
    buff += "&y:                                                                              &y:&x\r\n"
    occs = ', '.join([user.name for user in room.occupants].sort())
    occs = wrap(occs, width=76)
    for line in occs:
        buff += "&Y#[&x {:<74} &Y]#&x\r\n".format(line)
    return buff

def show_table(table):
        buff = style.table_header(self.name)
        user_list = []
        for user in self.battlefields:
            card_list = [style.table_user(user.name),
                         style.table_user_stats(self.life_totals[user], len(self.hands[user]),
                                                len(self.libraries[user]), len(self.graveyards[user]),
                                                self.poison_counters[user] if self.poison_counters[user] > 0 else None)]
            lands_list = []
            artifacts_list = []
            enchantments_list = []
            creatures_list = []
            others_list = []
            for card in self.battlefields[user]:
                if 'Land' in card.types:
                    lands_list.append(style.table_card(self.battlefields[user].index(card), card))
                elif 'Artifact' in card.types:
                    artifacts_list.append(style.table_card(self.battlefields[user].index(card), card))
                elif 'Enchantment' in card.types:
                    enchantments_list.append(style.table_card(self.battlefields[user].index(card), card))
                elif 'Creature' in card.types:
                    creatures_list.append(style.table_card(self.battlefields[user].index(card), card))
                else:
                    others_list.append(style.table_card(self.battlefields[user].index(card), card))
            card_list += lands_list+artifacts_list+enchantments_list+creatures_list+others_list
            user_list.append(card_list[:])
        battlefield_list = list(zip_longest(*user_list))
        for lines in battlefield_list:
            for card in lines:
                buff += "{}{}".format("\r\n" if card is lines[0] else "", style.table_card_blank() if card is None else card)
        return buff

def show_card(card):
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
    buff = ""+c_token+"****************************************&x\r\n"
    buff +=""+c_token+"*&x {:<29} {:>6} ".format(card.name, str(card.manaCost) if card.manaCost is not None else "")+c_token+"*&x\r\n"
    buff +=""+c_token+"****************************************&x\r\n"
    buff +=""+c_token+"*&x {:<36} ".format(card.type)+c_token+"*&x\r\n"
    buff += ""+c_token+"****************************************&x\r\n"
    buff += ""+c_token+"*                                      *&x\r\n"
    if card.text is not None:
        textbox = wrap(card.text, width=36)
        for line in textbox:
            buff += ""+c_token+"*&x {:<36} ".format(line)+c_token+"*&x\r\n"
    if card.power is not None:
        buff += ""+c_token+"*&x                              {:^3}/{:^3} ".format(str(card.power), str(card.toughness))+c_token+"*&x\r\n"
    elif card.loyalty is not None:
        buff += ""+c_token+"*&x                                   {:^3} ".format(str(card.loyalty))+c_token+"*&x\r\n"
    else:
        buff += ""+c_token+"*                                      *&x\r\n"
    buff += ""+c_token+"****************************************&x\r\n"
    return buff



def table_header(name):
    buff = "&g===========================&G[[&W {:^20} &G]]&g===========================&x\r\n".format(name)
    return buff

def table_user(name):
    buff = "&G|&x&g++++&w {:^28} &g++++&G|&x".format(name)
    return buff

def table_user_stats(life, hand, library, graveyard, poison=None):
    buff ="&G|&x&g+++&x &RLi&x:&R{:^3}&x &GH&x:&G{:^3}&x &YL&x:&Y{:^3}&x &yG&x:&y{:^3}&x {:^5} &g+++&x&G|&x".format(life, hand, library, graveyard, "&MP&x:&M{:^3}&x".format(poison) if poison is not None else "")
    return buff

def table_card(index, card):
    buff = "&G|&x ({:2}) [{:1}] {:<27} &G|&x".format(index, "T" if card.tapped else "", card.name)
    return buff

def table_card_blank():
    buff = "&G|                                      |&x"
    return buff