import mud
import funcs


def do_chat(client, msg):
    for c in mud.clients:
        if c.user is not None:
            if c is client:
                client.msg_client(c, "\n[chat] You: {}".format(msg))
            else:
                client.msg_client(c, "\n[chat] {}: {}".format(client.user.name, msg))


def do_say(client, msg):
    for c in client.user.room.occupants:
        if c is client:
            client.msg_client(c, "\n[say] You: {}".format(msg))
        else:
            client.msg_client(c, "\n[say] {}: {}".format(client.user.name, msg))


def do_whisper(client, msg):
    args = msg.split()
    recip = args[0]
    msg = ' '.join(args[1:])
    recip = funcs.get_client(recip)
    if recip is None:
        client.msg_self("\nCould not find user {}.".format(args[0]))
        return
    client.msg_client(client, "\n[whisper] You: {}".format(msg))
    client.msg_client(recip, "\n[whisper] {}: {}".format(client.user.name, msg))


channels = {
    '.':  do_chat,
    '\'': do_say,
    '>':  do_whisper
}
