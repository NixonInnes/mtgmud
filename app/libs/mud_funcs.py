from app import config, db
from app.game import objects
from app.libs import db_funcs


def startup(mud):
    print("Checking Room database...")
    if db.session.query(db.models.Room).filter_by(name=config.LOBBY_ROOM_NAME).first() is None:
        print("No lobby found....")
        db_funcs.create_lobby()
    load_rooms(mud)

    print("Checking Card database...")
    if db.session.query(db.models.Card).count() < 1:
        print("Card database is empty. \r\nNow populating...")
        db_funcs.create_cards()
    else:
        print("Cards exist.")

    print("Checking for channels...")
    if db.session.query(db.models.Channel).count() < 1:
        print("No channels found...")
        db_funcs.create_default_channels()
    else:
        print("Channels exist.")
    load_channels(mud)

    print("Checking for emotes...")
    if db.session.query(db.models.Emote).count() < 1:
        print("No emotes found...")
        db_funcs.create_default_emotes()
    else:
        print("Emotes exist.")


def load_rooms(mud):
    print("Loading rooms...")
    if mud.rooms is not None:
        print("Cleaning out existing rooms...")
        for user in mud.users:
            user.room = None
        mud.rooms.clear()
    for i in db.session.query(db.models.Room).all():
        print("Loading room: {}".format(i.name))
        room = objects.Room.load(i)
        mud.rooms.append(room)
    print("Rooms loaded.")


def load_channels(mud):
    print("Loading channels...")
    if mud.channels is not None:
        print("Clearing out existing channels...")
        mud.channels.clear()
    for channel in db.session.query(db.models.Channel).all():
        print("Loading channel: {}".format(channel.name))
        mud.channels[channel.key] = channel
    print("Channels loaded.")
