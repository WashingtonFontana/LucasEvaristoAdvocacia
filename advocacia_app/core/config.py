"""
core/config.py
──────────────
Constantes globais: caminhos, variáveis de ambiente e parâmetros
compartilhados entre todos os módulos.

Regra: nunca importe de outros módulos internos aqui — evita
importações circulares.
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── Data Directory (suporte a volume Railway) ────────────────────────────────
# Desenvolvimento local: DATA_DIR = BASE_DIR (raiz do projeto)
# Produção/Railway     : DATA_DIR = /data (volume persistente)
DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(Path(__file__).parent.parent.parent)))

# ─── Diretórios ───────────────────────────────────────────────────────────────
# BASE_DIR aponta para a raiz do projeto (pai de advocacia_app/)
BASE_DIR: Path = Path(__file__).parent.parent.parent
APP_DIR:  Path = Path(__file__).parent.parent   # advocacia_app/
STATIC_DIR: Path = APP_DIR.parent / "static"
IMG_DIR:  Path = Path(os.getenv("IMG_DIR", str(STATIC_DIR / "img")))
TEMPLATES_DIR: Path = APP_DIR.parent / "templates"

# Garante que as pastas existam ao importar o módulo (falha silenciosa se não gravável)
try:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass

# ─── Banco SQLite de conteúdo (sqlite3 síncrono) ──────────────────────────────
# Separado do banco do fastapi-users para isolar responsabilidades.
CONTENT_DB_PATH: Path = Path(os.getenv("CONTENT_DB_PATH", str(DATA_DIR / "content.db")))

# ─── Banco SQLAlchemy async (fastapi-users) ───────────────────────────────────
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{DATA_DIR / 'auth.db'}",
)

# ─── Segredo JWT ──────────────────────────────────────────────────────────────
# Em produção: defina via variável de ambiente com valor longo e aleatório.
JWT_SECRET: str = os.getenv(
    "JWT_SECRET",
    "CHAVE_ULTRA_SECRETA_DO_LUCAS_EVARISTO_2026",
)
if JWT_SECRET == "CHAVE_ULTRA_SECRETA_DO_LUCAS_EVARISTO_2026":
    logger.warning(
        "JWT_SECRET está usando o valor padrão inseguro. "
        "Defina a variável de ambiente JWT_SECRET em produção."
    )

# ─── Porta (Railway injeta PORT dinamicamente) ────────────────────────────────
PORT: int = int(os.getenv("PORT", "8000"))

# ─── Cookie Secure (deve ser True em produção HTTPS) ──────────────────────────
COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() in ("true", "1", "yes")

# ─── CORS ─────────────────────────────────────────────────────────────────────
_cors_raw: str = os.getenv("CORS_ORIGINS", "*")
CORS_ORIGINS: list[str] = [origin.strip() for origin in _cors_raw.split(",") if origin.strip()]

# ─── Upload de imagens ────────────────────────────────────────────────────────
ALLOWED_IMAGE_TYPES: set[str] = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE_MB: int = 5