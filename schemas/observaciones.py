from pydantic import BaseModel, validator
from typing import Optional

class ObservacionOut(BaseModel):
    id: int
    descripcion: str
    consejo: str

    class Config:
        orm_mode = True

class ObservacionAdminOut(BaseModel):
    id: int
    proyecto: str
    descripcion: str
    consejo: str

    class Config:
        orm_mode = True

class ObservacionCreate(BaseModel):
    descripcion: str
    proyecto_id: Optional[int] = None
    nombre_proyecto: Optional[str] = None

    @validator('proyecto_id', pre=True, always=True)
    def validate_proyecto_identification(cls, v, values):
        proyecto_id = v
        nombre_proyecto = values.get('nombre_proyecto')
        
        if not proyecto_id and not nombre_proyecto:
            raise ValueError('Debe proporcionar proyecto_id o nombre_proyecto')
        
        if proyecto_id and nombre_proyecto:
            raise ValueError('Proporcione solo proyecto_id o nombre_proyecto, no ambos')
        
        return v

    class Config:
        orm_mode = True
