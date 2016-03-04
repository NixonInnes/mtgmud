from app import server

# Non-User channels
def do_action(user, msg_self, msg_others):
    for u in user.table.users:
        if u is user:
            user.msg_user(user, "\n[ACT] You {}".format(msg_self))
        else:
            user.msg_user(u, "\n[ACT] {} {}".format(user.user.name, msg_others))

# User channels
def do_chat(user, msg):
    for u in server.users:
        if u.authd:
            if u is user:
                user.msg_self("\n[chat] You: {}".format(msg))
            else:
                user.msg_user(u, "\n[chat] {}: {}".format(user.name, msg))

def do_say(user, msg):
    for u in user.room.occupants:
        if u is user:
            user.msg_self("\n[say] You: {}".format(msg))
        else:
            user.msg_user(u, "\n[say] {}: {}".format(user.name, msg))

def do_tchat(user, msg):
    for u in user.table.users:
        if u is user:
            user.msg_self("\n[table] You: {}".format(msg))
        else:
            user.msg_user(u, "\n[table] {} : {}".format(user.name, msg))

def do_whisper(user, msg):
    args = msg.split()
    recip = args[0]
    msg = ' '.join(args[1:])
    recip = server.get_user(recip)
    if recip is None:
        user.msg_self("\nCould not find user {}.".format(args[0]))
        return
    user.msg_user(user, "\n[whisper] You: {}".format(msg))
    user.msg_user(recip, "\n[whisper] {}: {}".format(user.name, msg))


channels = {
    '.':  do_chat,
    '\'': do_say,
    ':': do_tchat,
    '>':  do_whisper
}
