from fastapi import FastAPI
from routers import auth, proyectos, ong, observaciones

app = FastAPI(title="DSSD Cloud Project")

# Routers
app.include_router(auth.router)
app.include_router(proyectos.router)
app.include_router(ong.router)
app.include_router(observaciones.router)
