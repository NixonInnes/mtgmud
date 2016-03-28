from app import db
from app import mud


def send_to_server(msg):
    for u in mud.users:
        u.send_to_self(msg)


def send_to_room(room, msg):
    for user in room.occupants:
        user.send_to_self(msg)


def send_to_table(table, msg):
    for user in table.users:
        user.send_to_self(msg)


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
        user_list = mud.users
    if channel.type is 1:
        user_list = user.room.occupants
    if channel.type is 2:
        user_list = user.table.users
    if channel.type is 3:
        user_list = [mud.get_user(args[0])]
        args = args[1:]
        msg = ' '.join(args)
        if msg[0] is '@':
            do_emote = True
            msg = msg[1:]
            args = msg.split()

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
                user.send_to_self("{} appears not to be here...".format(args[1]))
                return
        else:
            vict = None
        emote = get_emote(user, args[0], vict)
        if emote is None:
            user.send_to_self("Emote not found.")
            return

        if vict is not None and vict is not user:
            others = [u for u in user_list if u is not user and u is not vict and channel.key in u.db.listening]
            msg_vict = "&W[&x{}{}&x&W]&x {}{}&x".format(channel.colour_token, channel.name, channel.colour_token, emote['vict'])
        else:
            others = [u for u in user_list if u is not user and channel.key in u.db.listening] if emote['others'] is not None else None
        msg_user = "&W[&x{}{}&x&W]&x {}{}&x".format(channel.colour_token, channel.name, channel.colour_token, emote['user'])
        msg_others = "&W[&x{}{}&x&W]&x {}{}&x".format(channel.colour_token, channel.name, channel.colour_token, emote['others']) if emote['others'] is not None else None
    else:
        others = [u for u in user_list if u is not user and channel.key in u.db.listening]
        msg_user = "&W[&x{}{}&x&W]&x You{}: {}{}&x".format(channel.colour_token, channel.name, " to {}".format(others[0].name) if channel.type is 3 else "", channel.colour_token, msg)
        msg_others = "&W[&x{}{}&x&W]&x {}: {}{}&x".format(channel.colour_token, channel.name, user.name, channel.colour_token, msg)

    user.send_to_self(msg_user)
    if do_emote and vict is not None and vict is not user:
        user.send_to_user(vict, msg_vict)
    if others is not None:
        user.send_to_users(others, msg_others)


def get_emote(user, emote, vict=None):
    emote = db.session.query(db.models.Emote).filter_by(name=emote).first()
    if emote is None:
        return None
    if vict is not None:
        if vict is user:
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
    else:
        return {
            'user': emote.user_no_vict.format(user=user.name),
            'others': emote.others_no_vict.format(user=user.name) if emote.others_no_vict is not None else None
        }