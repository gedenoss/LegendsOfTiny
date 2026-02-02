from fastapi import FastAPI, Request, Depends, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from . import crud, models

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)
with Session(bind=engine) as _db:
    try:
        crud.seed_card_models(_db)
        if not _db.query(models.GameState).first():
            _db.add(models.GameState(id=1, ins=50.0))
            _db.commit()
    except Exception:
        pass


def get_game_state(db: Session = Depends(get_db)) -> models.GameState:
    state = db.query(models.GameState).filter(models.GameState.id == 1).first()
    if not state:
        state = models.GameState(id=1, ins=50.0)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/booster/open")
def open_booster(db: Session = Depends(get_db), state: models.GameState = Depends(get_game_state)):
    if state.ins < 10:
        raise HTTPException(status_code=400, detail="Not enough INS")
    
    state.ins -= 10
    db.add(state)
    db.commit()
    db.refresh(state)
    
    new_cards = crud.booster_open(db)
    
    payload = []
    for uc in new_cards:
        payload.append({
            "id": uc.id,
            "instance_id": uc.instance_id,
            "obtained_at": uc.obtained_at.timestamp() if uc.obtained_at else None,
            "name": uc.model.name,
            "rarity": uc.model.rarity,
            "image": uc.model.image,
        })
    return {"cards": payload, "ins_balance": state.ins}


@app.get("/collection")
def get_collection(db: Session = Depends(get_db), state: models.GameState = Depends(get_game_state)):
    collection = crud.get_collection(db)
    collection["ins"] = state.ins
    return collection


@app.post("/ins/add")
def add_ins(db: Session = Depends(get_db), state: models.GameState = Depends(get_game_state)):
    state.ins += 10
    db.add(state)
    db.commit()
    db.refresh(state)
    return {"ins": state.ins}

