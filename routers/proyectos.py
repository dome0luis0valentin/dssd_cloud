from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from utils.security import get_current_user, get_db
from schemas.proyectos import ProjectCreate, ProyectoFullIn
from models import Proyecto, PlanTrabajo, Etapa, PedidoCobertura, TipoCobertura, Compromiso, ONG

router = APIRouter(
    prefix="/proyectos",
    tags=["proyectos"]
)

@router.post("/")
def create_project(project: ProjectCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Proyecto).filter(Proyecto.nombre == project.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="El proyecto ya existe")
    new_project = Proyecto(nombre=project.name)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {"message": f"Proyecto '{project.name}' creado correctamente"}

@router.post("/full/")
def crear_proyecto_full(data: ProyectoFullIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    creador = db.query(ONG).filter(ONG.nombre == data.creador.nombre).first()
    if not creador:
        creador = ONG(nombre=data.creador.nombre)
        db.add(creador)
        db.commit()
        db.refresh(creador)

    proyecto = Proyecto(nombre=data.nombre, creador=creador)
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)

    for ong_in in data.ongs_participantes:
        ong = db.query(ONG).filter(ONG.nombre == ong_in.nombre).first()
        if not ong:
            ong = ONG(nombre=ong_in.nombre)
            db.add(ong)
            db.commit()
            db.refresh(ong)
        proyecto.ongs.append(ong)

    for plan_in in data.planes_trabajo:
        plan = PlanTrabajo(nombre=plan_in.nombre, proyecto=proyecto)
        db.add(plan)
    for etapa_in in data.etapas:
        etapa = Etapa(nombre=etapa_in.nombre, proyecto=proyecto)
        db.add(etapa)
    for pedido_in in data.pedidos_cobertura:
        tipo = db.query(TipoCobertura).filter(TipoCobertura.nombre == pedido_in.tipo_cobertura.nombre).first()
        if not tipo:
            tipo = TipoCobertura(nombre=pedido_in.tipo_cobertura.nombre)
            db.add(tipo)
            db.commit()
            db.refresh(tipo)
        pedido = PedidoCobertura(descripcion=pedido_in.descripcion, proyecto=proyecto, tipo_cobertura=tipo)
        db.add(pedido)
    for compromiso_in in data.compromisos:
        compromiso = Compromiso(descripcion=compromiso_in.descripcion, proyecto=proyecto)
        db.add(compromiso)
    db.commit()
    return {"id": proyecto.id, "nombre": proyecto.nombre}

@router.post("/{proyecto_id}/participantes/{ong_id}")
def participar_en_proyecto(proyecto_id: int, ong_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    ong = db.query(ONG).filter(ONG.id == ong_id).first()
    if not proyecto or not ong:
        raise HTTPException(status_code=404, detail="Proyecto u ONG no encontrados")
    if ong in proyecto.ongs:
        raise HTTPException(status_code=409, detail="La ONG ya participa en este proyecto")
    proyecto.ongs.append(ong)
    db.commit()
    return {"message": f"ONG '{ong.nombre}' ahora participa en el proyecto '{proyecto.nombre}'"}
