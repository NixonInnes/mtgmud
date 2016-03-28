from textwrap import wrap

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

def colourify(string):
    for token in COLOUR_TOKENS:
        string = string.replace(token, COLOUR_TOKENS[token])
    return string

def strip_colours(string):
    for token in COLOUR_TOKENS:
        string = string.replace(token, '')
    return string


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

