from app import mud, db


def send_to_server(msg):
    for user in mud.users:
        user.presenter.show_msg(msg)


def send_to_room(room, msg):
    for user in room.occupants:
        user.presenter.show_msg(msg)


def send_to_table(table, msg):
    for user in table.users:
        user.presenter.show_msg(msg)


# Non-User channels
def do_info(msg):
    send_to_server("&W[&Uinfo&x&W]&x &U{}&x".format(msg))


def do_tinfo(table, msg):
    send_to_table(table, "&W[&Ytable&x&W]&x &Y{}&x".format(msg))


def do_rinfo(room, msg):
    send_to_room(room, "&W[&croom&x&W]&x &c{}&x".format(msg))


# User channels
def send_to_channel(user, channel, msg, do_emote=False):
    args = msg.split()

    if channel.type is 0:
        user_list = [user]
    elif channel.type is 1:
        user_list = mud.users
    elif channel.type is 2:
        user_list = user.room.occupants
    elif channel.type is 3:
        user_list = user.table.users
    elif channel.type is 4:
        user_list = [mud.get_user(args[0])]
        args = args[1:]
        msg = ' '.join(args)
        if msg[0] is '@':
            do_emote = True
            msg = msg[1:]
            args = msg.split()
    else:
        user_list = []

    if do_emote:
        if len(args) > 1:
            if args[1] == "self":
                vict = user
            else:
                vict = None
                for u in user_list:
                    if u.name == args[1]:
                        vict = u
            if vict is None:
                user.presenter.show_msg("{} appears not to be here...".format(args[1]))
                return
        else:
            vict = None
        emote = get_emote(args[0], user, vict)
        if emote is None:
            user.presenter.show_msg("Emote not found.")
            return

        if vict is not None and vict is not user:
            others = [u for u in user_list if u is not user and u is not vict and channel.key in u.db.listening]
            msg_vict = emote['vict']
        else:
            others = [u for u in user_list if u is not user and channel.key in u.db.listening] if emote['others'] is not None else None
        msg_user = emote['user']
        msg_others = emote['others']
    else:
        others = [u for u in user_list if u is not user and channel.key in u.db.listening]
        msg_user = 'You: ' + msg
        msg_others = user.name + ': ' + msg

    user.presenter.show_channel(channel, msg_user)
    if do_emote and vict is not None and vict is not user:
       vict.presenter.show_channel(channel, msg_vict)
    if others is not None:
        for other in others:
            other.presenter.show_channel(channel, msg_others)


def get_emote(emote, user, vict=None):
    emote = db.session.query(db.models.Emote).filter_by(name=emote).first()
    if emote is None:
        return None
    if vict is None:
        return {
            'user': emote.user_no_vict.format(user=user.name),
            'others': emote.others_no_vict.format(user=user.name) if emote.others_no_vict is not None else None
        }
    elif vict is user:
        return {
            'user': emote.user_vict_self.format(user=user.name) if emote.user_vict_self is not None else emote.user_no_vict.format(user=user.name),
            'others': emote.others_vict_self.format(user=user.name) if emote.others_vict_self is not None else emote.others_no_vict.format(user=user.name)
        }

    else:
        return {
            'user': emote.user_vict.format(user=user.name, vict=vict.name) if emote.user_vict is not None else emote.user_no_vict.format(user=user.name),
            'others': emote.others_vict.format(user=user.name, vict=vict.name) if emote.others_vict is not None else emote.others_no_vict.format(user=user.name),
            'vict': emote.vict_vict.format(user=user.name) if emote.vict_vict is not None else None
        }
