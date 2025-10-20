from pydantic import BaseModel
from typing import List

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
