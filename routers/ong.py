from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from utils.security import get_db, get_current_user
from schemas.ong import ONGRequest, ONGOut
from models import ONG, User

router = APIRouter(
    prefix="/ongs",
    tags=["ongs"]
)

# Crear ONG
@router.post("/", response_model=ONGOut)
def crear_ong(request: ONGRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    ong = ONG(nombre=request.nombre)
    db.add(ong)
    db.commit()
    db.refresh(ong)
    # Aquí se podría asociar usuarios si se pasan (usuario_ids)
    return ong

# Obtener todas las ONGs
@router.get("/", response_model=List[ONGOut])
def get_ongs(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(ONG).all()
