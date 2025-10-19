from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
from utils.security import get_current_user

router = APIRouter(prefix="/proyectos", tags=["proyectos"])

# --- Crear Proyecto simple ---
@router.post("/", response_model=schemas.ProyectoFullIn)  # Podés definir un schema simplificado si querés
def crear_proyecto(nombre: str, creador_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    creador = db.query(models.ONG).filter(models.ONG.id == creador_id).first()
    if not creador:
        raise HTTPException(status_code=404, detail="ONG creadora no encontrada")
    proyecto = models.Proyecto(nombre=nombre, creador=creador)
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return schemas.ProyectoFullIn(
        nombre=proyecto.nombre,
        creador=schemas.ONGIn(nombre=creador.nombre)
    )

# --- Crear Proyecto Full ---
@router.post("/full/", response_model=schemas.ProyectoFullIn)
def crear_proyecto_full(data: schemas.ProyectoFullIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # ONG creadora
    creador = db.query(models.ONG).filter(models.ONG.nombre == data.creador.nombre).first()
    if not creador:
        creador = models.ONG(nombre=data.creador.nombre)
        db.add(creador)
        db.commit()
        db.refresh(creador)

    proyecto = models.Proyecto(nombre=data.nombre, creador=creador)
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)

    # ONGs participantes
    for ong_in in data.ongs_participantes:
        ong = db.query(models.ONG).filter(models.ONG.nombre == ong_in.nombre).first()
        if not ong:
            ong = models.ONG(nombre=ong_in.nombre)
            db.add(ong)
            db.commit()
            db.refresh(ong)
        proyecto.ongs.append(ong)

    # Planes de trabajo
    for plan_in in data.planes_trabajo:
        plan = models.PlanTrabajo(nombre=plan_in.nombre, proyecto=proyecto)
        db.add(plan)

    # Etapas
    for etapa_in in data.etapas:
        etapa = models.Etapa(nombre=etapa_in.nombre, proyecto=proyecto)
        db.add(etapa)

    # Pedidos de cobertura
    for pedido_in in data.pedidos_cobertura:
        tipo = db.query(models.TipoCobertura).filter(models.TipoCobertura.nombre == pedido_in.tipo_cobertura.nombre).first()
        if not tipo:
            tipo = models.TipoCobertura(nombre=pedido_in.tipo_cobertura.nombre)
            db.add(tipo)
            db.commit()
            db.refresh(tipo)
        pedido = models.PedidoCobertura(descripcion=pedido_in.descripcion, proyecto=proyecto, tipo_cobertura=tipo)
        db.add(pedido)

    # Compromisos
    for compromiso_in in data.compromisos:
        compromiso = models.Compromiso(descripcion=compromiso_in.descripcion, proyecto=proyecto)
        db.add(compromiso)

    db.commit()
    return data  # devolvemos el mismo schema que recibimos

# --- Listar Proyectos ---
@router.get("/", response_model=List[schemas.ProyectoFullIn])
def listar_proyectos(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    proyectos = db.query(models.Proyecto).all()
    result = []
    for p in proyectos:
        result.append(
            schemas.ProyectoFullIn(
                nombre=p.nombre,
                creador=schemas.ONGIn(nombre=p.creador.nombre),
                ongs_participantes=[schemas.ONGIn(nombre=o.nombre) for o in p.ongs],
                planes_trabajo=[schemas.PlanTrabajoIn(nombre=pl.nombre) for pl in p.planes_trabajo],
                etapas=[schemas.EtapaIn(nombre=e.nombre) for e in p.etapas],
                pedidos_cobertura=[
                    schemas.PedidoCoberturaIn(
                        descripcion=pc.descripcion,
                        tipo_cobertura=schemas.TipoCoberturaIn(nombre=pc.tipo_cobertura.nombre)
                    )
                    for pc in p.pedidos_cobertura
                ],
                compromisos=[schemas.CompromisoIn(descripcion=c.descripcion) for c in p.compromisos]
            )
        )
    return result
