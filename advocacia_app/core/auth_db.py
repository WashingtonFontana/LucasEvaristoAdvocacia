"""
core/auth_db.py
───────────────
Configuração do SQLAlchemy async e dos modelos usados pelo fastapi-users.

Separa completamente o banco de autenticação (auth.db) do banco de
conteúdo (content.db), respeitando o princípio de responsabilidade única.

Exporta:
  • Base              — DeclarativeBase para criação de tabelas
  • User              — modelo ORM do usuário admin
  • engine            — AsyncEngine conectado ao DATABASE_URL
  • async_session_maker
  • get_async_session — dependência FastAPI para rotas que precisam do ORM
  • get_user_db       — dependência exigida pelo fastapi-users
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import DATABASE_URL


# ─── Engine e sessão ──────────────────────────────────────────────────────────
engine = create_async_engine(DATABASE_URL, echo=False)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# ─── Base e modelos ───────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class User(Base, SQLAlchemyBaseUserTableUUID):
    """
    Modelo de usuário administrador.
    Herda todos os campos do fastapi-users (email, hashed_password,
    is_active, is_superuser, is_verified).
    """
    __tablename__ = "user"


# ─── Dependências FastAPI ─────────────────────────────────────────────────────
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User)