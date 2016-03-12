from app import server

# Non-User channels
def do_info(user, msg):
    user.send_to_server("&W[&Uinfo&W]&x &U{}&x".format(msg), "&W[&Uinfo&W]&x &U{}&x".format(msg))

def do_tinfo(user, msg_self, msg_others):
    user.send_to_table("&W[&Ytable&W] &YYou {}&x".format(msg_self), "&W[&Ytable&W] &Y{} {}&x".format(user.name, msg_others))

def do_act(user, msg_self, msg_others):
    user.send_to_room("&cYou {}&x".format(msg_self), "&c{} {}&x".format(user.name, msg_others))

# User channels
def do_chat(user, msg):
    user.send_to_users("&W[&Gchat&W] &xYou: &G{}&x".format(msg), "&W[&Gchat&W] &x{}: &G{}&x".format(user.name, msg))

def do_say(user, msg):
    user.send_to_self("&W[&Csay&W] &xYou: &C{}&x".format(msg))
    others = [u for u in user.room.occupants if u is not user]
    for u in others:
        user.send_to_user(u, "&W[&Csay&W] &x{}: &C{}&x".format(user.name, msg))

def do_tchat(user, msg):
    if user.table is None:
        user.send_to_self("You are not at a table.")
        return
    user.send_to_self("&W[&x&gtchat&W]&x You: &g{}&x".format(msg))
    others = [u for u in user.table.users if u is not user]
    for u in others:
        user.send_to_user(u, "&W[&x&gtchat&W]&x {}: &g{}&x".format(user.name, msg))

def do_whisper(user, msg):
    args = msg.split()
    recip = args[0]
    msg = ' '.join(args[1:])
    recip = server.get_user(recip)
    if recip is None:
        user.send_to_self("Could not find user {}.".format(args[0]))
        return
    user.send_to_self("&W[&Mwhisper&W] &xYou: &M{}&x".format(msg))
    user.send_to_user(recip, "&W[&Mwhisper&W] &x{}: &M{}&x".format(user.name, msg))


channels = {
    '.':  do_chat,
    '\'': do_say,
    ':': do_tchat,
    '>':  do_whisper
}
