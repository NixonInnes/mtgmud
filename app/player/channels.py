from app import server

# Non-User channels
def do_action(user, msg_self, msg_others):
    for u in user.table.users:
        if u is user:
            user.msg_user(user, "\n&W[&YACT&W] &YYou {}&x".format(msg_self))
        else:
            user.msg_user(u, "\n&W[&YACT&W] &Y{} {}&x".format(user.name, msg_others))

# User channels
def do_chat(user, msg):
    for u in server.users:
        if u.authd:
            if u is user:
                user.msg_self("\n&W[&Gchat&W] &xYou: &G{}&x".format(msg))
            else:
                user.msg_user(u, "\n&W[&Gchat&W] &x{}: &G{}&x".format(user.name, msg))

def do_say(user, msg):
    for u in user.room.occupants:
        if u is user:
            user.msg_self("\n&W[&Csay&W] &xYou: &C{}&x".format(msg))
        else:
            user.msg_user(u, "\n&W[&Csay&W] &x{}: &C{}&x".format(user.name, msg))

def do_tchat(user, msg):
    if user.table is None:
        user.msg_self("\nYou are not at a table.")
        return
    for u in user.table.users:
        if u is user:
            user.msg_self("\n&W[&gtable&W] &xYou: &g{}&x".format(msg))
        else:
            user.msg_user(u, "\n&W[&gtable&W] &x{}: &g{}&x".format(user.name, msg))

def do_whisper(user, msg):
    args = msg.split()
    recip = args[0]
    msg = ' '.join(args[1:])
    recip = server.get_user(recip)
    if recip is None:
        user.msg_self("\nCould not find user {}.".format(args[0]))
        return
    user.msg_user(user, "\n&W[&Mwhisper&W] &xYou: &M{}&x".format(msg))
    user.msg_user(recip, "\n&W[&Mwhisper&W] &x{}: &M{}&x".format(user.name, msg))


channels = {
    '.':  do_chat,
    '\'': do_say,
    ':': do_tchat,
    '>':  do_whisper
}
