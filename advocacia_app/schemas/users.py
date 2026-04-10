"""
schemas/users.py
────────────────
Schemas Pydantic exigidos pelo fastapi-users para as rotas de usuário,
mais schemas próprios para operações do painel (troca de senha/username).
"""

import re
import uuid

from fastapi_users import schemas
from pydantic import BaseModel, field_validator


# ─── Schemas fastapi-users ────────────────────────────────────────────────────
class UserRead(schemas.BaseUser[uuid.UUID]):
    """Dados retornados ao ler um usuário."""
    pass


class UserCreate(schemas.BaseUserCreate):
    """Payload para criação de usuário via /auth/register."""
    pass


class UserUpdate(schemas.BaseUserUpdate):
    """Payload para atualização parcial de usuário."""
    pass


# ─── Schemas do painel admin ──────────────────────────────────────────────────
class AlterarSenhaRequest(BaseModel):
    """Troca de senha — exige a senha atual para confirmação."""
    senha_atual: str
    nova_senha:  str
    confirmar:   str

    @field_validator("nova_senha")
    @classmethod
    def senha_forte(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("A nova senha deve ter pelo menos 8 caracteres.")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("A nova senha deve conter ao menos uma letra.")
        if not re.search(r"[0-9]", v):
            raise ValueError("A nova senha deve conter ao menos um número.")
        return v

    @field_validator("confirmar")
    @classmethod
    def senhas_coincidem(cls, v: str, info) -> str:
        if "nova_senha" in info.data and v != info.data["nova_senha"]:
            raise ValueError("A confirmação não coincide com a nova senha.")
        return v