import requests
import mud
import db
from actions import actions


def login(client, args):
    if len(args) == 0:
        client.msg_self("Login error.\nLogin: <username> <password>\nNew Account: register <username> <password> <password>\n")
        return

    if args[0] == 'register':
        if len(args) == 4 and args[2] == args[3]:
            if db.session.query(db.User).filter_by(name=args[1]).first() is None:
                client.user = db.User(name=args[1], password=args[2])
                db.session.add(client.user)
                db.session.commit()
                actions['goto'](client, ['Lobby'])
                client.get_prompt()
                return
            else:
                client.msg_self("Username \"{}\" is already taken, sorry.\n".format(args[1]))

    if len(args) == 2:
        dbuser = db.session.query(db.User).filter_by(name=args[0]).first()
        if dbuser is not None:
            if dbuser.verify_password(args[1]):
                client.user = dbuser
                actions['goto'](client, ['Lobby'])
                client.get_prompt()
                return

    client.msg_self("Login error.\nLogin: <username> <password>\nNew Account: register <username> <password> <password>\n")


def get_room(room_name):
    for room in mud.rooms:
        if room.name == room_name:
            return room
    return None

def get_client(user_name):
    for client in mud.clients:
        if client.user.name == user_name:
            return client
    return None

def update_cards():
    cards = requests.get('http://mtgjson.com/json/AllCards.json').json()
    for c in cards:
        #try:
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
        #except:
        #    print("Card: {} failed to be saved.".format(cards[c]['name']))
    db.session.commit()

