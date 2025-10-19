from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
from database import get_db
from utils.security import get_current_user
from schemas.observaciones import ObservacionOut

router = APIRouter(prefix="/observaciones", tags=["observaciones"])

# --- Observaciones de un proyecto (Admin) ---
@router.get("/proyectos/{proyecto_id}/admin", response_model=List[ObservacionOut])
def get_observaciones_admin(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.email != "admin@ejemplo.com":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    
    proyecto = db.query(models.Proyecto).filter(models.Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    return [
        ObservacionOut(
            id=obs.id,
            descripcion=obs.descripcion,
            consejo_nombre=obs.consejo.nombre if obs.consejo else None,
            proyecto_nombre=proyecto.nombre
        )
        for obs in proyecto.observaciones
    ]

# --- Todas las observaciones (Admin) ---
@router.get("/all", response_model=List[ObservacionOut])
def get_all_observaciones(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.email != "admin@ejemplo.com":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    
    observaciones = db.query(models.Observacion).all()
    return [
        ObservacionOut(
            id=obs.id,
            descripcion=obs.descripcion,
            consejo_nombre=obs.consejo.nombre if obs.consejo else None,
            proyecto_nombre=obs.proyecto.nombre if obs.proyecto else None
        )
        for obs in observaciones
    ]

# --- Observaciones para responsables de proyecto (ONG creadora) ---
@router.get("/proyectos/{proyecto_id}", response_model=List[ObservacionOut])
def get_observaciones_responsables(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    proyecto = db.query(models.Proyecto).filter(models.Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    if proyecto.creador_id != current_user.ong_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver estas observaciones")
    
    return [
        ObservacionOut(
            id=obs.id,
            descripcion=obs.descripcion,
            consejo_nombre=obs.consejo.nombre if obs.consejo else None,
            proyecto_nombre=proyecto.nombre
        )
        for obs in proyecto.observaciones
    ]
