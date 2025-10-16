from sqlalchemy import create_engine
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