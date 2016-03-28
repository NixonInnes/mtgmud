from app import mud, db
from app.player.actions import actions
import app.player.channels as channels


def parse(user, msg):
    args = msg.split()

    if user.authd is False:
        actions['login'](user, args)
        return

    if args[0] in user.db.aliases:
        args[0] = str(user.db.aliases[args[0]])
        msg = ' '.join(args)
        args = msg.split()

    if msg[0] in mud.channels:
        ch = db.session.query(db.models.Channel).get(msg[0])
        if msg[1] == '@':
            channels.send_to_channel(user, ch, msg[2:], do_emote=True)
        else:
            channels.send_to_channel(user, ch, msg[1:])
        #user.get_prompt()
        return

    if args[0] in actions:
        if user.is_frozen():
            user.send("You're frozen solid!")
        else:
            actions[args[0]](user, args[1:] if len(args) > 1 else None)
        #user.get_prompt()
        return
    user.send("Huh?")