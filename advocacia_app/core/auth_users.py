"""
core/auth_users.py
──────────────────
Configuração completa do fastapi-users:
  • UserManager — gerencia ciclo de vida dos usuários
  • CookieTransport + JWTStrategy — autenticação via cookie HTTP-only
  • auth_backend — backend registrado na aplicação
  • fastapi_users — instância principal
  • current_active_user — dependência para proteger rotas

A SECRET é lida de core/config.py que por sua vez respeita a variável
de ambiente JWT_SECRET — nunca deixe o valor padrão em produção.
"""

import uuid
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)

from .auth_db import User, get_user_db
from .config import JWT_SECRET


# ─── UserManager ──────────────────────────────────────────────────────────────
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = JWT_SECRET
    verification_token_secret   = JWT_SECRET


async def get_user_manager(
    user_db=Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


# ─── Transporte e estratégia ──────────────────────────────────────────────────
cookie_transport = CookieTransport(
    cookie_name="advocacia_auth",
    cookie_max_age=3600,
    cookie_secure=False,    # True em produção (HTTPS)
    cookie_httponly=True,
    cookie_samesite="lax",
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=JWT_SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt-cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


# ─── Instância principal e dependência de proteção ───────────────────────────
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)