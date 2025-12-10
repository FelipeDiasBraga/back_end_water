from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterSchema(BaseModel):
    nome: str
    email: EmailStr
    password: str
    telefone: Optional[str] = None
    cpf_cnpj: Optional[str] = None

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    produtor: dict