from pydantic import BaseModel
from typing import Optional 
from .compromisos import CompromisoOut 


class TipoCoberturaOut(BaseModel):
    id: int
    nombre: str
    class Config:
        from_attributes = True

class PedidoCoberturaOut(BaseModel):
    id: int
    descripcion: str
    tipo_cobertura: TipoCoberturaOut
    compromiso: Optional[CompromisoOut] = None
    class Config:
        from_attributes = True