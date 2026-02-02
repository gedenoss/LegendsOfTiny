from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class CardModelRead(BaseModel):
    id: int
    name: str
    rarity: str
    image: str

    class Config:
        from_attributes = True


class UserCardRead(BaseModel):
    id: int
    instance_id: str
    obtained_at: float | None = None

    name: str
    rarity: str
    image: str


class CollectionResponse(BaseModel):
    ins: float
    cards: list[UserCardRead]


