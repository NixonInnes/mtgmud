import requests
import mud
import db
import actions

def get_lobby():
    return db.session.query(db.Room).filter_by(name=mud.LOBBY_ROOM_NAME).first()

def login(client, args):
    if len(args) == 0:
        client.msg_self("\nLogin error.\nLogin: <username> <password>\nNew Account: register <username> <password> <password>")
        client.get_prompt()
        return

    if args[0] == 'register':
        if len(args) == 4 and args[2] == args[3]:
            if len(args[1]) > 20:
                client.msg_self("\nUsername is too long (max. 20).")
                client.get_prompt()
                return

            if db.session.query(db.User).filter_by(name=args[1]).first() is not None:
                client.msg_self("\nUsername \"{}\" is already taken, sorry.\n".format(args[1]))
                client.get_prompt()
                return

            new_user = db.User(name=args[1], password=args[2])
            db.session.add(new_user)
            db.session.commit()
            load_user(client, new_user)
            return

    if len(args) == 2:
        dbuser = db.session.query(db.User).filter_by(name=args[0]).first()
        if dbuser is not None:
            if dbuser.verify_password(args[1]):
                load_user(client, dbuser)
                return

    client.msg_self("\nLogin error.\nLogin: <username> <password>\nNew Account: register <username> <password> <password>")
    client.get_prompt()


def load_user(client, user):
    for c in mud.clients:
        if c.user == user:
            client.msg_client(c, "\nYou have signed in from another location!")
            actions.do_quit(c, None)

    client.user = user
    client.user.room = get_lobby()
    client.user.room.occupants.append(client.user)
    actions.do_look(client, None)
    client.get_prompt()

def get_client(user_name):
    for client in mud.clients:
        if client.user.name == user_name:
            return client
    return None

def update_cards():
    cards = requests.get('http://mtgjson.com/json/AllCards.json').json()
    for c in cards:
        card = db.Card(
            name = cards[c]['name'],
            names = cards[c]['names'] if 'names' in cards[c] else None,
            manaCost = cards[c]['manaCost'] if 'manaCost' in cards[c] else None,
            cmc = cards[c]['cmc'] if 'cmc' in cards[c] else None,
            colors = cards[c]['colors'] if 'colors' in cards[c] else None,
            type = cards[c]['type'],
            supertypes = cards[c]['supertypes'] if 'supertypes' in cards[c] else None,
            types = cards[c]['types'] if 'types' in cards[c] else None,
            subtypes = cards[c]['subtypes'] if 'subtypes' in cards[c] else None,
            rarity = cards[c]['rarity'] if 'rarity' in cards[c] else None,
            text = cards[c]['text'] if 'text' in cards[c] else None,
            power = cards[c]['power'] if 'power' in cards[c] else None,
            toughness = cards[c]['toughness'] if 'toughness' in cards[c] else None,
            loyalty = cards[c]['loyalty'] if 'loyalty' in cards[c] else None
        )
        db.session.add(card)
    db.session.commit()

