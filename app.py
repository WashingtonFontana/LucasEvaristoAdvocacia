"""
app.py
──────
Ponto de entrada da aplicação. Responsabilidades:

  1. Inicializar os dois bancos via lifespan
       • auth.db  (SQLAlchemy async — tabela de usuários fastapi-users)
       • content.db (sqlite3 síncrono — textos, cards, imagens, audit_log)
  2. Registrar middlewares (CORS)
  3. Incluir todos os routers
  4. Montar arquivos estáticos POR ÚLTIMO (mount é greedy — engole prefixos)

Toda lógica de negócio, autenticação e persistência vive nos
submódulos correspondentes (core/, routers/, schemas/).
"""

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from advocacia_app.core.auth_db import Base, engine
from advocacia_app.core.auth_users import auth_backend, fastapi_users
from advocacia_app.core.config import STATIC_DIR
from advocacia_app.core.content_db import init_content_db
from advocacia_app.routers import admin, audit, conteudo, health, imagens, site
from advocacia_app.schemas.users import UserRead, UserUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─── Lifespan — inicializa ambos os bancos antes de aceitar requisições ───────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. auth.db — cria tabela `user` via SQLAlchemy async
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. content.db — cria tabelas de conteúdo e executa seed (síncrono)
    init_content_db()

    yield  # aplicação rodando


# ─── Aplicação ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Lucas Evaristo — Advocacia e Consultoria",
    version="3.0.0",
    description=(
        "Portal institucional e painel administrativo do escritório "
        "Lucas Evaristo Advocacia e Consultoria."
    ),
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # restrinja ao domínio real em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Rotas fastapi-users (auth) ───────────────────────────────────────────────
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Autenticação"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/users",
    tags=["Usuários"],
)

# ─── Routers da aplicação ─────────────────────────────────────────────────────
# IMPORTANTE: todos os include_router() ANTES de qualquer app.mount()
# O mount() tem prioridade sobre routers e engole prefixos de forma greedy.
app.include_router(health.router)
app.include_router(site.router)
app.include_router(admin.router)
app.include_router(conteudo.router)
app.include_router(imagens.router)
app.include_router(audit.router)

# ─── Arquivos estáticos — SEMPRE POR ÚLTIMO ───────────────────────────────────
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")