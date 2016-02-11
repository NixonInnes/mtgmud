FOOTER_80 =        "\n||############################################################################||"
BLANK_80 =         "\n||                                                                            ||"
ROW_LINE_80 =      "\n||============================================================================||"
BLANK_2COL_80=     "\n||                                     ||                                     ||"
ROW_LINE_2COL_80 = "\n||=====================================||=====================================||"
BLANK_3COL_80 =    "\n||                        ||                        ||                        ||"
ROW_LINE_3COL_80 = "\n||========================||========================||========================||"

FOOTER_40 =        "\n||####################################||"
BLANK_40 =         "\n||                                    ||"
ROW_LINE_40 =      "\n||====================================||"
BLANK_2COL_40 =    "\n||                 ||                 ||"
ROW_LINE_2COL_40 = "\n||=================||=================||"

def header_80(title):
    buff = "\n||##########################[ {:^20} ]##########################||".format(title)
    buff += BLANK_80
    return buff

def body_80(string, align='center'):
    if align == 'left':
        buff = "\n|| {:<74} ||".format(string)
    elif align == 'right':
        buff = "\n|| {:>74} ||".format(string)
    else: # center
        buff = "\n|| {:^74} ||".format(string)
    return buff

def body_2cols_80(stringA, stringB):
    buff = "\n|| {:^35} || {:^35} ||".format(stringA, stringB)
    return buff

def body_3cols_80(stringA, stringB, stringC):
    buff = "\n|| {:^22} || {:^22} || {:^22} ||".format(stringA, stringB, stringC)
    return buff

def header_40(title):
    buff = "\n||###########[ {:^10} ]###########||".format(title)
    buff += BLANK_40
    return buff

def body_40(string, align='center'):
    if align == 'left':
        buff = "\n|| {:<34} ||".format(string)
    elif align == 'right':
        buff = "\n|| {:>34} ||".format(string)
    else: # center
        buff = "\n|| {:^34} ||".format(string)
    return buff

def body_2cols_40(stringA, stringB):
    buff = "\n|| {:^14} || {:^14} ||".format(stringA, stringB)
    return buff