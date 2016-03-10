from app import server

# Non-User channels
def do_info(user, msg):
    for u in server.users:
        user.msg_user(u, "&W[&Uinfo&W]&x &U{}&x".format(msg))

def do_tinfo(user, msg_self, msg_others):
    user.msg_self("&W[&Ytable&W] &YYou {}&x".format(msg_self))
    others = [u for u in user.table.users if u is not user]
    for u in others:
        user.msg_user(u, "&W[&Ytable&W] &Y{} {}&x".format(user.name, msg_others))

def do_act(user, actionee_msg, others_msg):
    user.msg_self("&cYou {}&x".format(actionee_msg))
    others = [u for u in user.room.occupants if u is not user]
    for u in others:
        user.msg_user(u, "&c{} {}&x".format(user.name, others_msg))

# User channels
def do_chat(user, msg):
    user.msg_self("&W[&Gchat&W] &xYou: &G{}&x".format(msg))
    others = [u for u in server.users if u is not user]
    for u in others:
        user.msg_user(u, "&W[&Gchat&W] &x{}: &G{}&x".format(user.name, msg))

def do_say(user, msg):
    user.msg_self("&W[&Csay&W] &xYou: &C{}&x".format(msg))
    others = [u for u in user.room.occupants if u is not user]
    for u in others:
        user.msg_user(u, "&W[&Csay&W] &x{}: &C{}&x".format(user.name, msg))

def do_tchat(user, msg):
    if user.table is None:
        user.msg_self("You are not at a table.")
        return
    user.msg_self("&W[&x&gtchat&W]&x You: &g{}&x".format(msg))
    others = [u for u in user.table.users if u is not user]
    for u in others:
        user.msg_user(u, "&W[&x&gtchat&W]&x {}: &g{}&x".format(user.name, msg))

def do_whisper(user, msg):
    args = msg.split()
    recip = args[0]
    msg = ' '.join(args[1:])
    recip = server.get_user(recip)
    if recip is None:
        user.msg_self("Could not find user {}.".format(args[0]))
        return
    user.msg_self("&W[&Mwhisper&W] &xYou: &M{}&x".format(msg))
    user.msg_user(recip, "&W[&Mwhisper&W] &x{}: &M{}&x".format(user.name, msg))


channels = {
    '.':  do_chat,
    '\'': do_say,
    ':': do_tchat,
    '>':  do_whisper
}
