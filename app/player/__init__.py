from .acts import *


actions = {
    'login': do_login,
    'quit':  do_quit,
    'look':  do_look,
#    'who':   do_who,
    'help':  do_help,
    'alias': do_alias,
    'freeze': do_freeze,
    'mute': do_mute,
    'make_admin': do_make_admin,
#    'rooms': do_rooms,
    'room':  do_room,
    'goto':  do_goto,
    'card':  do_card,
    'deck':  do_deck,
#    'decks': do_decks,
    'table': do_table
}