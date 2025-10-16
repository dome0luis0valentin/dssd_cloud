from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Union
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
SECRET_KEY = "clave_super_secreta_para_jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Base de datos en memoria (puedes usar SQLite persistente si quieres)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
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
        "hashed_password": pwd_context.hash("123"),  # contraseña: 1234
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
@app.post("/projects")
def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    existing = db.query(Project).filter(Project.name == project.name).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="El proyecto ya existe")
    new_project = Project(name=project.name)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    db.close()
    return {"message": f"Proyecto '{project.name}' creado correctamente"}
