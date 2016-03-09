from app import server

# Non-User channels
def do_action(user, msg_self, msg_others):
    for u in user.table.users:
        if u is user:
            user.msg_user(user, "&W[&YACT&W] &YYou {}&x\r\n".format(msg_self))
        else:
            user.msg_user(u, "&W[&YACT&W] &Y{} {}&x\r\n".format(user.name, msg_others))

# User channels
def do_chat(user, msg):
    for u in server.users:
        if u is user:
            user.msg_self("&W[&Gchat&W] &xYou: &G{}&x\r\n".format(msg))
        else:
            user.msg_user(u, "&W[&Gchat&W] &x{}: &G{}&x\r\n".format(user.name, msg))

def do_info(user, msg):
    for u in server.users:
        user.msg_user(u, "&W[&Uinfo&W]&x &U{}&x\r\n".format(msg))

def do_say(user, msg):
    for u in user.room.occupants:
        if u is user:
            user.msg_self("&W[&Csay&W] &xYou: &C{}&x\r\n".format(msg))
        else:
            user.msg_user(u, "&W[&Csay&W] &x{}: &C{}&x\r\n".format(user.name, msg))

def do_tchat(user, msg):
    if user.table is None:
        user.msg_self("You are not at a table.\r\n")
        return
    for u in user.table.users:
        if u is user:
            user.msg_self("&W[&x&gtable&W]&x You: &g{}&x\r\n".format(msg))
        else:
            user.msg_user(u, "&W[&x&gtable&W]&x {}: &g{}&x\r\n".format(user.name, msg))

def do_whisper(user, msg):
    args = msg.split()
    recip = args[0]
    msg = ' '.join(args[1:])
    recip = server.get_user(recip)
    if recip is None:
        user.msg_self("Could not find user {}.\r\n".format(args[0]))
        return
    user.msg_user(user, "&W[&Mwhisper&W] &xYou: &M{}&x\r\n".format(msg))
    user.msg_user(recip, "&W[&Mwhisper&W] &x{}: &M{}&x\r\n".format(user.name, msg))


channels = {
    '.':  do_chat,
    '\'': do_say,
    ':': do_tchat,
    '>':  do_whisper
}
