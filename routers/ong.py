from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
from utils.security import get_current_user

router = APIRouter(prefix="/ongs", tags=["ongs"])

@router.post("/", response_model=schemas.ONGBase)
def crear_ong(request: schemas.ONGCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ong = models.ONG(nombre=request.nombre)
    db.add(ong)
    db.commit()
    db.refresh(ong)
    # Asignar usuarios
    for user_id in request.usuario_ids:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            user.ong_id = ong.id
    db.commit()
    return schemas.ONGBase(nombre=ong.nombre)

@router.get("/", response_model=List[schemas.ONGBase])
def listar_ongs(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ongs = db.query(models.ONG).all()
    return [schemas.ONGBase(nombre=o.nombre) for o in ongs]
