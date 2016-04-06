import json
import requests
from app import config, db


def create_lobby():
    print("Creating {}...".format(config.LOBBY_ROOM_NAME))
    lobby = db.models.Room(
        name=config.LOBBY_ROOM_NAME,
        description=config.LOBBY_ROOM_DESC
    )
    db.session.add(lobby)
    db.session.commit()
    print("{} created.".format(lobby.name))


def create_default_channels():
    print("Creating default channels...")
    chat = db.models.Channel(
        key=".",
        name="chat",
        colour_token="&G",
        type=1,
        default=True
    )
    db.session.add(chat)
    say = db.models.Channel(
        key="\'",
        name="say",
        colour_token="&C",
        type=2,
        default=True
    )
    db.session.add(say)
    tchat = db.models.Channel(
        key=";",
        name="tchat",
        colour_token="&y",
        type=3,
        default=True
    )
    db.session.add(tchat)
    whisper = db.models.Channel(
        key=">",
        name="whisper",
        colour_token="&M",
        type=4,
        default=True
    )
    db.session.add(whisper)
    db.session.commit()
    print("Created default channels: {}".format(
        ', '.join([channel.name for channel in db.session.query(db.models.Channel).filter_by(default=True).all()])))


def create_emotes(overwrite=False):
    print("Creating default emotes...")
    with open('app/player/emotes.json') as emotes_json:
        emotes = json.load(emotes_json)
    for emote in emotes.values():
        existing_emote = db.session.query(db.models.Emote).filter_by(name=emote['name']).first()
        if existing_emote is not None:
            if overwrite:
                print("Existing emote {} found. Deleting.")
                db.session.remove(existing_emote)
            else:
                print("Emote {} found. Skipping")
                continue
        print("Adding emote: {}".format(emote['name']))
        dbEmote = db.models.Emote(
            name=emote['name'],
            user_no_vict=emote['user_no_vict'],
            others_no_vict=emote['others_no_vict'] if 'others_no_vict' in emote else None,
            user_vict=emote['user_vict'] if 'user_vict' in emote else None,
            others_vict=emote['others_vict'] if 'others_vict' in emote else None,
            vict_vict=emote['vict_vict'] if 'vict_vict' in emote else None,
            user_vict_self=emote['user_vict_self'] if 'user_vict_self' in emote else None,
            others_vict_self=emote['others_vict_self'] if 'others_vict_self' in emote else None
        )
        db.session.add(dbEmote)
    db.session.commit()


def create_cards():
    cards = requests.get('http://mtgjson.com/json/AllCards.json').json()
    for c in cards:
        card = db.models.Card(
            name=cards[c]['name'],
            names=cards[c]['names'] if 'names' in cards[c] else None,
            manaCost=cards[c]['manaCost'] if 'manaCost' in cards[c] else None,
            cmc=cards[c]['cmc'] if 'cmc' in cards[c] else None,
            colors=cards[c]['colors'] if 'colors' in cards[c] else None,
            type=cards[c]['type'],
            supertypes=cards[c]['supertypes'] if 'supertypes' in cards[c] else None,
            types=cards[c]['types'] if 'types' in cards[c] else None,
            subtypes=cards[c]['subtypes'] if 'subtypes' in cards[c] else None,
            rarity=cards[c]['rarity'] if 'rarity' in cards[c] else None,
            text=cards[c]['text'] if 'text' in cards[c] else None,
            power=cards[c]['power'] if 'power' in cards[c] else None,
            toughness=cards[c]['toughness'] if 'toughness' in cards[c] else None,
            loyalty=cards[c]['loyalty'] if 'loyalty' in cards[c] else None
        )
        db.session.add(card)
    db.session.commit()