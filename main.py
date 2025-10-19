from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Union
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import api_project
from database import SessionLocal

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
import os
SECRET_KEY = "clave_super_secreta_para_jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Base de datos en memoria (puedes usar SQLite persistente si quieres)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# ==============================
# MODELOS DE BD
# ==============================
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

Base.metadata.create_all(bind=engine)

# ==============================
# MODELOS DE Pydantic
# ==============================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class ProjectCreate(BaseModel):
    name: str

class ONGRequest(BaseModel):
    nombre: str
    usuario_ids: list[int] = []

# ==============================
# AUTENTICACIÓN
# ==============================
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Usuario de ejemplo
fake_user_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("123"),  # contraseña: 123
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    user_dict = fake_user_db.get(username)
    if user_dict:
        return UserInDB(**user_dict)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return get_user(username)
    except JWTError:
        raise credentials_exception

# ==============================
# APLICACIÓN FASTAPI
# ==============================
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# ==============================
# ENDPOINT DE AUTENTICACIÓN
# ==============================
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# ==============================
# ENDPOINT PARA CREAR PROYECTOS
# ==============================
from models import Base
Base.metadata.create_all(bind=engine)
from models import ONG
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


        
@app.post("/projects")
def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Project).filter(Project.name == project.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="El proyecto ya existe")
    new_project = Project(name=project.name)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {"message": f"Proyecto '{project.name}' creado correctamente"}

# 1. Crear ONG

@app.post("/ongs/")
def crear_ong(request: ONGRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ong = ONG(nombre=request.nombre)
    db.add(ong)
    db.commit()
    db.refresh(ong)
    # Asociar usuarios si se pasan
    # ... (lógica para asociar usuarios)
    return {"id": ong.id, "nombre": ong.nombre}

from models import ONG, Proyecto, PlanTrabajo, Etapa, PedidoCobertura, TipoCobertura, Compromiso
from typing import List, Optional


# Esquemas para requests anidados
class TipoCoberturaIn(BaseModel):
    nombre: str

class PedidoCoberturaIn(BaseModel):
    descripcion: str
    tipo_cobertura: TipoCoberturaIn

class CompromisoIn(BaseModel):
    descripcion: str

class EtapaIn(BaseModel):
    nombre: str

class PlanTrabajoIn(BaseModel):
    nombre: str

class ONGIn(BaseModel):
    nombre: str

class ProyectoFullIn(BaseModel):
    nombre: str
    creador: ONGIn
    ongs_participantes: List[ONGIn] = []
    planes_trabajo: List[PlanTrabajoIn] = []
    etapas: List[EtapaIn] = []
    pedidos_cobertura: List[PedidoCoberturaIn] = []
    compromisos: List[CompromisoIn] = []

# 2. Crear Proyecto con Planes de Trabajo y Pedidos de Cobertura
@app.post("/proyectos/")
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

# 3. Asociar ONG a Proyecto (Participa)
@app.post("/proyectos/{proyecto_id}/participa/")
def agregar_ong_a_proyecto(proyecto_id: int, ong_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    ong = db.query(ONG).filter(ONG.id == ong_id).first()
    if not proyecto or not ong:
        raise HTTPException(status_code=404, detail="Proyecto u ONG no encontrados")
    proyecto.ongs.append(ong)
    db.commit()
    return {"message": "ONG asociada al proyecto"}

# 4. Crear Plan de Trabajo
@app.post("/planes_trabajo/")
def crear_plan_trabajo(nombre: str, proyecto_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    plan = PlanTrabajo(nombre=nombre, proyecto=proyecto)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return {"id": plan.id, "nombre": plan.nombre}

# 5. Crear Etapa
@app.post("/etapas/")
def crear_etapa(nombre: str, proyecto_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    etapa = Etapa(nombre=nombre, proyecto=proyecto)
    db.add(etapa)
    db.commit()
    db.refresh(etapa)
    return {"id": etapa.id, "nombre": etapa.nombre}

# 6. Crear Pedido de Cobertura
@app.post("/pedidos_cobertura/")
def crear_pedido_cobertura(descripcion: str,
                            proyecto_id: int,
                            tipo_id: int,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    tipo = db.query(TipoCobertura).filter(TipoCobertura.id == tipo_id).first()
    pedido = PedidoCobertura(descripcion=descripcion, proyecto=proyecto, tipo_cobertura=tipo)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return {"id": pedido.id, "descripcion": pedido.descripcion}

# 7. Crear Compromiso
@app.post("/compromisos/")
def crear_compromiso(descripcion: str, proyecto_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    compromiso = Compromiso(descripcion=descripcion, proyecto=proyecto)
    db.add(compromiso)
    db.commit()
    db.refresh(compromiso)
    return {"id": compromiso.id, "descripcion": compromiso.descripcion}

# 8. Crear Tipo de Cobertura
@app.post("/tipos_cobertura/")
def crear_tipo_cobertura(nombre: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tipo = TipoCobertura(nombre=nombre)
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return {"id": tipo.id, "nombre": tipo.nombre}

# 9. Crear Proyecto con carga completa
@app.post("/proyectos/full/")
def crear_proyecto_full(data: ProyectoFullIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

@app.get("/ongs/")
def get_ongs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ONG).all()

@app.get("/proyectos/")
def get_proyectos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Proyecto).all()

@app.get("/planes_trabajo/")
def get_planes_trabajo(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(PlanTrabajo).all()

@app.get("/etapas/")
def get_etapas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Etapa).all()

@app.get("/pedidos_cobertura/")
def get_pedidos_cobertura(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(PedidoCobertura).all()

@app.get("/tipos_cobertura/")
def get_tipos_cobertura(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(TipoCobertura).all()

@app.get("/compromisos/")
def get_compromisos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Compromiso).all()

class EtapaOut(BaseModel):
    id: int
    nombre: str
    cumplida: bool

    class Config:
        orm_mode = True


# --- Endpoint para que una ONG participe en un proyecto ---
@app.post("/proyectos/{proyecto_id}/participantes/{ong_id}")
def participar_en_proyecto(
    proyecto_id: int, 
    ong_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
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



@app.put("/proyectos/{proyecto_id}/etapas/{etapa_id}/marcar-cumplida", 
    response_model=EtapaOut,
)
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

    if etapa.cumplida:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La etapa ya está marcada como cumplida"
        )

    etapa.cumplida = True
    db.commit()
    db.refresh(etapa)
    return etapa