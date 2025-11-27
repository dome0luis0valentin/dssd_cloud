from pydantic import BaseModel, field_validator, model_validator
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

    @model_validator(mode='before')
    @classmethod
    def validate_proyecto_identification(cls, data):
        if isinstance(data, dict):
            proyecto_id = data.get('proyecto_id')
            nombre_proyecto = data.get('nombre_proyecto')
            
            # Si no hay ninguno de los dos, error
            if not proyecto_id and not nombre_proyecto:
                raise ValueError('Debe proporcionar proyecto_id o nombre_proyecto')
            
            # Si hay ambos, error
            if proyecto_id and nombre_proyecto:
                raise ValueError('Proporcione solo proyecto_id o nombre_proyecto, no ambos')
        
        return data

    class Config:
        orm_mode = True
