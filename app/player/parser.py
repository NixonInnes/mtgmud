from app import db, game, mud, player


def parse(user, msg):
    args = msg.split()

    if user.authd is False:
        player.acts.do_login(user, args)
        return

    if args[0] in user.db.aliases:
        args[0] = str(user.db.aliases[args[0]])
        msg = ' '.join(args)
        args = msg.split()

    if msg[0] in mud.channels:
        ch = db.session.query(db.models.Channel).get(msg[0])
        if msg[1] == '@':
            game.channels.send_to_channel(user, ch, msg[2:], do_emote=True)
        else:
            game.channels.send_to_channel(user, ch, msg[1:])
        return

    if args[0] in player.actions:
        # if user.is_frozen():
        #     user.send("You're frozen solid!")
        # else:
        #     actions[args[0]](user, args[1:] if len(args) > 1 else None)
        player.actions[args[0]](user, args[1:] if len(args) > 1 else None)
        return
    user.presenter.show_msg("Huh?")