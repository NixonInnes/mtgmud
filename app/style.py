from textwrap import wrap

FOOTER_80 =        "\n&c||############################################################################||&x"
BLANK_80 =         "\n&c||                                                                            ||&x"
ROW_LINE_80 =      "\n&c||============================================================================||&x"
BLANK_2COL_80=     "\n&c||                                     ||                                     ||&x"
ROW_LINE_2COL_80 = "\n&c||=====================================||=====================================||&x"
BLANK_3COL_80 =    "\n&c||                        ||                        ||                        ||&x"
ROW_LINE_3COL_80 = "\n&c||========================||========================||========================||&x"

FOOTER_40 =        "\n&c||####################################||&x"
BLANK_40 =         "\n&c||                                    ||&x"
ROW_LINE_40 =      "\n&c||====================================||&x"
BLANK_2COL_40 =    "\n&c||                 ||                 ||&x"
ROW_LINE_2COL_40 = "\n&c||=================||=================||&x"

def header_80(title):
    buff = "\n&c||##########################&C[&x &W{:^20}&x &C]&x&c##########################||&x".format(title)
    buff += BLANK_80
    return buff

def body_80(string, align='center'):
    if align == 'left':
        buff = "\n&c||&x {:<74} &c||&x".format(string)
    elif align == 'right':
        buff = "\n&c||&x {:>74} &c||&x".format(string)
    else: # center
        buff = "\n&c||&x {:^74} &c||&x".format(string)
    return buff

def body_2cols_80(stringA, stringB):
    buff = "\n&c||&x {:^35} &c||&x {:^35} &c||&x".format(stringA, stringB)
    return buff

def body_3cols_80(stringA, stringB, stringC):
    buff = "\n&c||&x {:^22} &c||&x {:^22} &c||&x {:^22} &c||&x".format(stringA, stringB, stringC)
    return buff

def header_40(title):
    buff = "\n&c||###########&C[&x &W{:^10}&x &C]&x&c###########||&x".format(title)
    buff += BLANK_40
    return buff

def body_40(string, align='center'):
    if align == 'left':
        buff = "\n&c||&x {:<34} &c||&x".format(string)
    elif align == 'right':
        buff = "\n&c||&x {:>34} &c||&x".format(string)
    else: # center
        buff = "\n&c||&x {:^34} &c||&x".format(string)
    return buff

def body_2cols_40(stringA, stringB):
    buff = "\n&c||&x {:^14} &c||&x {:^14} &c||&x".format(stringA, stringB)
    return buff

def card(card):
    buff = "\n****************************************"
    buff +="\n* {:<29} {:>6} *".format(card.name, str(card.manaCost) if card.manaCost is not None else "")
    buff +="\n****************************************"
    buff +="\n* {:<36} *".format(card.type)
    buff +="\n****************************************"
    buff += "\n*                                      *"
    if card.text is not None:
        textbox = wrap(card.text, width=36)
        for line in textbox:
            buff += "\n* {:<36} *".format(line)
    if card.power is not None:
        buff += "\n*                              {:^3}/{:^3} *".format(str(card.power), str(card.toughness))
    elif card.loyalty is not None:
        buff += "\n*                                   {:^3} *".format(str(card.loyalty))
    else:
        buff += "\n*                                      *"
    buff += "\n****************************************"
    return buff


def room_name(name):
    buff = "\n&y.-~~~~~~~~~~~~~~~~~~~~~~~~~~&Y{{&W {:^20} &Y}}&x&y~~~~~~~~~~~~~~~~~~~~~~~~~~-.&x".format(name)
    return buff

def room_desc(desc):
    buff = ""
    buff += "\n&y:                                                                              &y:&x"
    desc = wrap(desc, width=72)
    for line in desc:
        buff += "\n&y:&x   {:<72}   &y:&x".format(line)
    buff += "\n&y:                                                                              &y:&x"
    return buff

def room_occupants(occs):
    buff = ""
    occs = ', '.join(occs)
    occs = wrap(occs, width=76)
    for line in occs:
        buff += "\n&Y#[&x {:<74} &Y]#&x".format(line)
    return buff

def table_header(name):
    buff = "\n&g===========================&G[[&W {:^20} &G]]&g===========================&x".format(name)
    return buff

def table_user(name):
    buff = "&G|&x&g++++&w {:^28} &g++++&G|&x".format(name)
    return buff

def table_card(index, card):
    buff = "&G|&x ({:2}) [{:1}] {:<27} &G|&x".format(index, "T" if card.tapped else "", card.name)
    return buff

def table_card_blank():
    buff = "&G|                                      |&x"
    return buff