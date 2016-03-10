from textwrap import wrap

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

def card(card):
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

def room_name(name):
    buff = "&y.-~~~~~~~~~~~~~~~~~~~~~~~~~~&Y{{&W {:^20} &Y}}&x&y~~~~~~~~~~~~~~~~~~~~~~~~~~-.&x\r\n".format(name)
    return buff

def room_desc(desc):
    buff = ""
    buff += "&y:                                                                              &y:&x\r\n"
    desc = wrap(desc, width=72)
    for line in desc:
        buff += "&y:&x   {:<72}   &y:&x\r\n".format(line)
    buff += "&y:                                                                              &y:&x\r\n"
    return buff

def room_occupants(occs):
    buff = ""
    occs = ', '.join(occs)
    occs = wrap(occs, width=76)
    for line in occs:
        buff += "&Y#[&x {:<74} &Y]#&x\r\n".format(line)
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