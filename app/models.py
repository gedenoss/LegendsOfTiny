from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .db import Base


class GameState(Base):
    __tablename__ = "game_state"
    
    id = Column(Integer, primary_key=True, default=1)
    ins = Column(Float, default=50.0)


class CardModel(Base):
    __tablename__ = "card_models"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    rarity = Column(String(50), nullable=False)
    image = Column(String(255), nullable=False)

    user_cards = relationship("UserCard", back_populates="model")


class UserCard(Base):
    __tablename__ = "user_cards"

    id = Column(Integer, primary_key=True)
    card_model_id = Column(Integer, ForeignKey("card_models.id", ondelete="RESTRICT"), nullable=False)
    obtained_at = Column(DateTime(timezone=True), server_default=func.now())
    instance_id = Column(String(64), unique=True, nullable=False)

    model = relationship("CardModel", back_populates="user_cards")


