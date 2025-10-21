from pydantic import BaseModel
from .ong import ONGOut

class CompromisoOut(BaseModel):
    id: int
    realizado: bool
    ong: ONGOut
    pedido_id: int
    
    class Config:
        from_attributes = True