from pydantic import BaseModel
from typing import List

class ONGBase(BaseModel):
    nombre: str

class ONGCreate(ONGBase):
    usuario_ids: List[int] = []
