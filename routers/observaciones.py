from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from utils.security import get_db, get_current_user
from schemas.observaciones import ObservacionOut, ObservacionAdminOut, ObservacionCreate
from models import Observacion, Proyecto

router = APIRouter(
    prefix="/observaciones",
    tags=["observaciones"]
)

# Observaciones de un proyecto (solo admin)
@router.get("/proyectos/{proyecto_id}/admin", response_model=List[ObservacionOut])
def get_observaciones_proyecto_admin(proyecto_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.email != "admin@ejemplo.com":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return [{"id": obs.id, "descripcion": obs.descripcion, "consejo": obs.consejo.nombre} for obs in proyecto.observaciones]

# Todas las observaciones (solo admin)
@router.get("/all", response_model=List[ObservacionAdminOut])
def get_all_observaciones(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.email != "admin@ejemplo.com":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    observaciones = db.query(Observacion).all()
    return [
        {
            "id": obs.id,
            "proyecto": obs.proyecto.nombre,
            "descripcion": obs.descripcion,
            "consejo": obs.consejo.nombre
        }
        for obs in observaciones
    ]

# Observaciones para responsables (ONG creadora)
@router.get("/proyectos/{proyecto_id}", response_model=List[ObservacionOut])
def get_observaciones_proyecto_responsables(proyecto_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if proyecto.creador_id != current_user.ong_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver estas observaciones")
    return [{"id": obs.id, "descripcion": obs.descripcion, "consejo": obs.consejo.nombre} for obs in proyecto.observaciones]

@router.post("/", response_model=List[ObservacionOut])
def crear_observacion(data: ObservacionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Solo usuarios del consejo
    if not current_user.consejo_id:
        raise HTTPException(status_code=403, detail="Solo miembros del consejo pueden crear observaciones")
    
    # Validar que el proyecto exista
    proyecto = db.query(Proyecto).filter(Proyecto.id == data.proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    observacion = Observacion(
        descripcion=data.descripcion,
        proyecto_id=proyecto.id,
        consejo_id=current_user.consejo_id
    )
    db.add(observacion)
    db.commit()
    db.refresh(observacion)

    # Retornar la observación en el formato ObservacionOut
    return [
        ObservacionOut(
            id=observacion.id,
            descripcion=observacion.descripcion,
            consejo=observacion.consejo.nombre  # <-- esto es string
        )
    ]
