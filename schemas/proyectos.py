from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str

class PlanTrabajoIn(BaseModel):
    nombre: str

class EtapaIn(BaseModel):
    nombre: str

class TipoCoberturaIn(BaseModel):
    nombre: str

class PedidoCoberturaIn(BaseModel):
    descripcion: str
    tipo_cobertura: TipoCoberturaIn

class CompromisoIn(BaseModel):
    descripcion: str

class ONGIn(BaseModel):
    nombre: str

class ProyectoFullIn(BaseModel):
    nombre: str
    creador: ONGIn
    ongs_participantes: List[ONGIn] = []
    planes_trabajo: List[PlanTrabajoIn] = []
    etapas: List[EtapaIn] = []
    pedidos_cobertura: List[PedidoCoberturaIn] = []
    compromisos: List[CompromisoIn] = []

# --- Schemas de salida ---
class ONGOut(BaseModel):
    id: int
    nombre: str
    
    class Config:
        orm_mode = True

class ProyectoOut(BaseModel):
    id: int
    nombre: str
    creador_id: Optional[int] = None
    creador: Optional[ONGOut] = None
    # Metadata adicional para debugging
    user_role: Optional[str] = None  # "admin", "ong_owner", "participant", "other"
    user_permissions: Optional[List[str]] = []  # ["read", "write", "delete"]
    
    class Config:
        orm_mode = True

class ProyectosResponse(BaseModel):
    """Response con metadata de usuario para debugging"""
    proyectos: List[ProyectoOut]
    user_info: dict
    total_count: int
    filtered_by: str
