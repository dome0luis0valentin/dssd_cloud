from pydantic import BaseModel
from typing import List

class ONGRequest(BaseModel):
    nombre: str
    usuario_ids: List[int] = []

class ONGOut(BaseModel):
    id: int
    nombre: str

    class Config:
        orm_mode = True
