from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from utils.security import get_db, get_current_user
from schemas.ong import ONGRequest, ONGOut
from schemas.compromisos import CompromisoOut
from models import ONG, User, Proyecto, PedidoCobertura, Compromiso, Etapa
from pydantic import BaseModel

router = APIRouter(
    prefix="/ongs",
    tags=["ongs"]
)

class EtapaOut(BaseModel):
    id: int
    nombre: str
    cumplida: bool

    class Config:
        orm_mode = True

class ProyectoOut(BaseModel): 
    id: int               
    nombre: str           
    
    class Config:
        from_attributes = True # 

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

@router.post(
    "/{proyecto_id}/participar"
)
def participar_en_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    if not current_user.ong_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no está asociado a ninguna ONG y no puede unirse a un proyecto."
        )

    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")

    ong_del_usuario = current_user.ong

    if ong_del_usuario in proyecto.ongs:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tu ONG ya participa en este proyecto")

    proyecto.ongs.append(ong_del_usuario)
    db.commit()
    
    return {"message": f"Tu ONG '{ong_del_usuario.nombre}' ahora participa en el proyecto '{proyecto.nombre}'"}


@router.get(
    "/compromisos",
    response_model=List[CompromisoOut]
)
def obtener_mis_compromisos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.ong_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no está asociado a ninguna ONG."
        )

    return current_user.ong.compromisos


@router.post(
    "/pedidos_colaboracion/{pedido_id}/comprometerse", 
    response_model=CompromisoOut
)
def comprometer_a_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    if not current_user.ong_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no está asociado a ninguna ONG."
        )

    pedido = db.query(PedidoCobertura).filter(PedidoCobertura.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido de colaboración no encontrado.")

    if pedido.compromiso:
        raise HTTPException(status_code=400, detail="Este pedido ya tiene un compromiso asociado.")

    ong_del_usuario = current_user.ong
    proyecto_del_pedido = pedido.proyecto

    if ong_del_usuario not in proyecto_del_pedido.ongs:
        proyecto_del_pedido.ongs.append(ong_del_usuario)

    nuevo_compromiso = Compromiso(ong=ong_del_usuario, pedido=pedido, proyecto=proyecto_del_pedido)
    db.add(nuevo_compromiso)
    db.commit()
    db.refresh(nuevo_compromiso)
    
    return nuevo_compromiso

@router.put(
    "/{compromiso_id}/marcar-realizado",
    response_model=CompromisoOut
)
def marcar_compromiso_realizado(
    compromiso_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    compromiso = db.query(Compromiso).filter(Compromiso.id == compromiso_id).first()
    if not compromiso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El compromiso con ID {compromiso_id} no fue encontrado."
        )
    es_admin = current_user.email == 'admin@ejemplo.com'
    es_propietario = compromiso.ong_id == current_user.ong_id

    if not es_admin and not es_propietario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para modificar este compromiso."
        )
    
    if compromiso.realizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este compromiso ya está marcado como realizado."
        )

    compromiso.realizado = True
    db.commit()
    db.refresh(compromiso)

    return compromiso


@router.put("/{proyecto_id}/etapas/{etapa_id}/marcar-cumplida", response_model=EtapaOut)
def marcar_etapa_de_proyecto_cumplida(
    proyecto_id: int,
    etapa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    etapa = db.query(Etapa).filter(
        Etapa.id == etapa_id,
        Etapa.proyecto_id == proyecto_id
    ).first()

    if not etapa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La etapa con ID {etapa_id} no fue encontrada en el proyecto {proyecto_id}"
        )

    es_admin = current_user.email == 'admin@ejemplo.com'

    es_ong_creadora = (
        current_user.ong_id is not None and 
        etapa.proyecto.creador_id == current_user.ong_id
    )

    if not es_admin and not es_ong_creadora:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para modificar etapas de este proyecto."
        )

    if etapa.cumplida:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La etapa ya está marcada como cumplida"
        )

    etapa.cumplida = True
    db.commit()
    db.refresh(etapa)
    return etapa


@router.get(
    "/proyectos_creados",
    response_model=List[ProyectoOut]
)
def obtener_mis_proyectos_creados(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.ong:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no está asociado a ninguna ONG."
        )

    return current_user.ong.proyectos_creados
