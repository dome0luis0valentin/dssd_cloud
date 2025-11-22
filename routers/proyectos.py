from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from utils.security import get_current_user, get_db
from schemas.proyectos import ProjectCreate, ProyectoFullIn
from schemas.compromisos import CompromisoOut
from schemas.pedidos import PedidoCoberturaOut
from models import Proyecto, PlanTrabajo, Etapa, PedidoCobertura, TipoCobertura, Compromiso, ONG, User 

router = APIRouter(
    prefix="/proyectos",
    tags=["proyectos"]
)

#creo que lo podemos borrar
# ------- Mantener la versión con ProjectCreate (pydantic) -------
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

# ------- 2. Crear Proyecto con Planes de Trabajo y Pedidos de Cobertura (firma alternativa) -------
@router.post("/crear_con_params/")
def crear_proyecto(
    nombre: str,
    creador_id: int,
    planes_trabajo: list[str] = [],
    pedidos_cobertura: list[dict] = [],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    creador = db.query(ONG).filter(ONG.id == creador_id).first()
    if not creador:
        raise HTTPException(status_code=404, detail="ONG creadora no encontrada")
    proyecto = Proyecto(nombre=nombre, creador=creador)
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    # Cargar planes de trabajo
    for nombre_plan in planes_trabajo:
        plan = PlanTrabajo(nombre=nombre_plan, proyecto=proyecto)
        db.add(plan)
    # Cargar pedidos de cobertura
    for pedido in pedidos_cobertura:
        tipo = db.query(TipoCobertura).filter(TipoCobertura.id == pedido["tipo_id"]).first()
        pedido_obj = PedidoCobertura(descripcion=pedido["descripcion"], proyecto=proyecto, tipo_cobertura=tipo)
        db.add(pedido_obj)
    db.commit()
    return {"id": proyecto.id, "nombre": proyecto.nombre}

# ------- 4. Crear Plan de Trabajo -------
@router.post("/planes_trabajo/")
def crear_plan_trabajo(nombre: str, proyecto_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    plan = PlanTrabajo(nombre=nombre, proyecto=proyecto)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return {"id": plan.id, "nombre": plan.nombre}

# ------- 5. Crear Etapa -------
@router.post("/etapas/")
def crear_etapa(nombre: str, proyecto_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    etapa = Etapa(nombre=nombre, proyecto=proyecto)
    db.add(etapa)
    db.commit()
    db.refresh(etapa)
    return {"id": etapa.id, "nombre": etapa.nombre}

# ------- 6. Crear Pedido de Cobertura -------
@router.post("/pedidos_cobertura/")
def crear_pedido_cobertura(descripcion: str,
                            proyecto_id: int,
                            tipo_id: int,
                            db: Session = Depends(get_db),
                            current_user = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    tipo = db.query(TipoCobertura).filter(TipoCobertura.id == tipo_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de cobertura no encontrado")
    pedido = PedidoCobertura(descripcion=descripcion, proyecto=proyecto, tipo_cobertura=tipo)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return {"id": pedido.id, "descripcion": pedido.descripcion}

# ------- 7. Crear Compromiso -------
@router.post("/compromisos/")
def crear_compromiso(descripcion: str, proyecto_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    compromiso = Compromiso(descripcion=descripcion, proyecto=proyecto)
    db.add(compromiso)
    db.commit()
    db.refresh(compromiso)
    return {"id": compromiso.id, "descripcion": compromiso.descripcion}

# ------- 8. Crear Tipo de Cobertura -------
@router.post("/tipos_cobertura/")
def crear_tipo_cobertura(nombre: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    tipo = TipoCobertura(nombre=nombre)
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return {"id": tipo.id, "nombre": tipo.nombre}

# ------- 9. Crear Proyecto con carga completa -------
@router.post("/full/")
def crear_proyecto_full(data: ProyectoFullIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # ONG creadora
    creador = db.query(ONG).filter(ONG.nombre == data.creador.nombre).first()
    if not creador:
        creador = ONG(nombre=data.creador.nombre)
        db.add(creador)
        db.commit()
        db.refresh(creador)
    # Proyecto
    proyecto = Proyecto(nombre=data.nombre, creador=creador)
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    # ONGs participantes
    for ong_in in data.ongs_participantes:
        ong = db.query(ONG).filter(ONG.nombre == ong_in.nombre).first()
        if not ong:
            ong = ONG(nombre=ong_in.nombre)
            db.add(ong)
            db.commit()
            db.refresh(ong)
        proyecto.ongs.append(ong)
    # Planes de trabajo
    for plan_in in data.planes_trabajo:
        plan = PlanTrabajo(nombre=plan_in.nombre, proyecto=proyecto)
        db.add(plan)
    # Etapas
    for etapa_in in data.etapas:
        etapa = Etapa(nombre=etapa_in.nombre, proyecto=proyecto)
        db.add(etapa)
    # Pedidos de cobertura
    for pedido_in in data.pedidos_cobertura:
        tipo = db.query(TipoCobertura).filter(TipoCobertura.nombre == pedido_in.tipo_cobertura.nombre).first()
        if not tipo:
            tipo = TipoCobertura(nombre=pedido_in.tipo_cobertura.nombre)
            db.add(tipo)
            db.commit()
            db.refresh(tipo)
        pedido = PedidoCobertura(descripcion=pedido_in.descripcion, proyecto=proyecto, tipo_cobertura=tipo)
        db.add(pedido)
    # Compromisos
    for compromiso_in in data.compromisos:
        compromiso = Compromiso(descripcion=compromiso_in.descripcion, proyecto=proyecto)
        db.add(compromiso)
    db.commit()
    return {"id": proyecto.id, "nombre": proyecto.nombre}

# ------- GETs (listas) -------
@router.get("/ongs/")
def get_ongs(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(ONG).all()

@router.get("/")
def get_proyectos(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Proyecto).all()

@router.get("/planes_trabajo/")
def get_planes_trabajo(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(PlanTrabajo).all()

@router.get("/etapas/")
def get_etapas(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Etapa).all()

@router.get("/pedidos_cobertura/")
def get_pedidos_cobertura(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(PedidoCobertura).all()

@router.get("/tipos_cobertura/")
def get_tipos_cobertura(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(TipoCobertura).all()

@router.get("/compromisos/")
def get_compromisos(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Compromiso).all()

# ------- Endpoint para que una ONG participe en un proyecto (otra ruta con formato distinto) -------
@router.post("/{proyecto_id}/participantes/{ong_id}")
def participar_en_proyecto(
    proyecto_id: int,
    ong_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.email != "admin@ejemplo.com":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")

    ong = db.query(ONG).filter(ONG.id == ong_id).first()
    if not ong:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONG no encontrada")

    if ong in proyecto.ongs:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La ONG ya participa en este proyecto")

    proyecto.ongs.append(ong)
    db.commit()
    return {"message": f"ONG '{ong.nombre}' ahora participa en el proyecto '{proyecto.nombre}'"}


from pydantic import BaseModel
class EtapaOut(BaseModel):
    id: int
    nombre: str
    cumplida: bool

    class Config:
        orm_mode = True

@router.get(
    "/{proyecto_id}/etapas"
)
def obtener_etapas_de_proyecto(
    proyecto_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
  
    # Primero, verificamos que el proyecto exista
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proyecto con ID {proyecto_id} no fue encontrado."
        )
    
    return proyecto.etapas

@router.get(
    "/{proyecto_id}/pedidos_colaboracion",
    response_model=List[PedidoCoberturaOut],
)
def obtener_pedidos_de_colaboracion_por_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proyecto con ID {proyecto_id} no fue encontrado."
        )
    
    return proyecto.pedidos_cobertura

@router.post(
    "/pedidos_colaboracion/{pedido_id}/comprometerse/{ong_id}",
    response_model=CompromisoOut,
)
def comprometer_ong_a_pedido(
    pedido_id: int,
    ong_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.email != "admin@ejemplo.com":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    pedido = db.query(PedidoCobertura).filter(PedidoCobertura.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido de colaboración no encontrado")

    if pedido.compromiso:
        raise HTTPException(status_code=400, detail="Este pedido ya tiene un compromiso asociado")

    ong = db.query(ONG).filter(ONG.id == ong_id).first()
    if not ong:
        raise HTTPException(status_code=404, detail="ONG no encontrada")

    nuevo_compromiso = Compromiso(ong=ong, pedido=pedido)
    db.add(nuevo_compromiso)
    db.commit()
    db.refresh(nuevo_compromiso)
    
    return nuevo_compromiso


@router.get(
    "/{ong_id}/compromisos",
    response_model=List[CompromisoOut] 
)
def obtener_compromisos_de_ong(
    ong_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    ong = db.query(ONG).filter(ONG.id == ong_id).first()
    if not ong:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La ONG con ID {ong_id} no fue encontrada."
        )


    return ong.compromisos


@router.get(
    "/pedidos_colaboracion/pendientes",
    response_model=List[PedidoCoberturaOut],
)
def obtener_pedidos_pendientes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pedidos_pendientes = db.query(PedidoCobertura).filter(
        PedidoCobertura.compromiso == None
    ).all()
    
    return pedidos_pendientes

@router.get(
    "/{proyecto_id}/pedidos_colaboracion",
    response_model=List[PedidoCoberturaOut],
)
def obtener_pedidos_de_colaboracion_por_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proyecto con ID {proyecto_id} no fue encontrado."
        )
    
    return proyecto.pedidos_cobertura

# En: routers/proyectos.py
from schemas.ong import ONGOut # Importa el schema

@router.get(
    "/{proyecto_id}/participantes",
    response_model=List[ONGOut],
)
def obtener_ongs_participantes(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene y devuelve una lista de todas las ONGs que participan
    en un proyecto específico.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El proyecto con ID {proyecto_id} no fue encontrado."
        )

    # Devolvemos la lista de ONGs participantes a través de la relación
    return proyecto.ongs