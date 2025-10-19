from pydantic import BaseModel
from typing import Optional

class ObservacionBase(BaseModel):
    descripcion: str
    consejo_nombre: Optional[str] = None  # Nombre del consejo que hizo la observación

class ObservacionOut(ObservacionBase):
    id: int
    proyecto_nombre: Optional[str] = None  # Nombre del proyecto asociado

    class Config:
        orm_mode = True
