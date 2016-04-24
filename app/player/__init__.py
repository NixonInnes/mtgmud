from . import acts


actions = {
    'login': acts.do_login,
    'quit':  acts.do_quit,
    'look':  acts.do_look,
    'who':   acts.do_who,
    'help':  acts.do_help,
    'alias': acts.do_alias,
    'freeze': acts.do_freeze,
    'mute': acts.do_mute,
    'make_admin': acts.do_make_admin,
    'rooms': acts.do_rooms,
    'room':  acts.do_room,
    'goto':  acts.do_goto,
    'card':  acts.do_card,
    'deck':  acts.do_deck,
    'decks': acts.do_decks,
    'table': acts.do_table
}
