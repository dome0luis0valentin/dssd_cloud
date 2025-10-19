from pydantic import BaseModel

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
