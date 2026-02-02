from sqlalchemy.orm import Session

from . import models
from .models import CardModel, UserCard
from datetime import datetime, timezone
import random
import uuid


BASE_CARDS = [
    {"name": "Common Hero", "rarity": "common", "image": "/static/images/common/common.JPG"},
    {"name": "Uncommon Hero", "rarity": "uncommon", "image": "/static/images/uncommon/uncommon.JPG"},
    {"name": "Rare Hero", "rarity": "rare", "image": "/static/images/rare/rare.JPG"},
    {"name": "Epic Hero", "rarity": "epic", "image": "/static/images/epic/epic.JPG"},
    {"name": "Legendary Hero", "rarity": "legendary", "image": "/static/images/legendary/legendary.JPG"},
]

CARD_DEFS = []
card_id = 1
for base_card in BASE_CARDS:
    CARD_DEFS.append({
        "id": card_id,
        "name": base_card["name"],
        "rarity": base_card["rarity"],
        "image": base_card["image"],
    })
    card_id += 1

RARITIES = ["common", "uncommon", "rare", "epic", "legendary"]
WEIGHTS = [58, 25.4, 15.5, 1, 0.1]


def seed_card_models(db: Session):
    for c in CARD_DEFS:
        if not db.get(CardModel, c["id"]):
            db.add(CardModel(**c))
    db.commit()


def booster_open(db: Session):
    new_cards: list[UserCard] = []
    for _ in range(2):
        rarity = random.choices(RARITIES, weights=WEIGHTS)[0]
        model = db.query(CardModel).filter(CardModel.rarity == rarity).first()
        uc = UserCard(
            card_model_id=model.id,
            instance_id=str(uuid.uuid4()),
            obtained_at=datetime.now(timezone.utc),
        )
        db.add(uc)
        new_cards.append(uc)
    db.commit()
    for uc in new_cards:
        db.refresh(uc)
    return new_cards


def get_collection(db: Session):
    cards = []
    for uc in db.query(UserCard).all():
        cards.append({
            "id": uc.id,
            "instance_id": uc.instance_id,
            "obtained_at": uc.obtained_at.timestamp() if uc.obtained_at else None,
            "name": uc.model.name,
            "rarity": uc.model.rarity,
            "image": uc.model.image,
        })
    return {
        "cards": cards,
    }



