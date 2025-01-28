# Define los modelos de entrada y salida de datos

from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str
    role: str
    
class DatasetCreate(BaseModel):
    dataset_name: str
    n_rows: int
    n_columns: int    
    selected: bool

class UserRead(BaseModel):
    id: int
    username: str
    full_name: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    id: int
    access_token: str
    token_type: str
    username: str
    fullname: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None
