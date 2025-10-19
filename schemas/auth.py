from pydantic import BaseModel
from typing import Union

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class UserBase(BaseModel):
    nombre: str
    apellido: str
    email: str

class UserCreate(UserBase):
    password: str
from pydantic import BaseModel
from typing import Union

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class UserBase(BaseModel):
    nombre: str
    apellido: str
    email: str

class UserCreate(UserBase):
    password: str
