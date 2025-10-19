from fastapi import FastAPI
from database import Base, engine
from routers import auth, proyectos, ong, observaciones

# --- Crear tablas si no existen ---
Base.metadata.create_all(bind=engine)

# --- Instancia de FastAPI ---
app = FastAPI(
    title="DSSD Cloud API",
    description="API para gestión de proyectos y ONGs",
    version="1.0.0"
)

# --- Routers ---
app.include_router(auth.router)
app.include_router(proyectos.router)
app.include_router(ong.router)
app.include_router(observaciones.router)

# --- Endpoint raíz ---
@app.get("/", tags=["Root"])
def root():
    return {"message": "API DSSD Cloud funcionando 🚀"}
