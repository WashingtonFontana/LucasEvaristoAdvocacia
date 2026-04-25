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

# ─── Diretórios ───────────────────────────────────────────────────────────────
# BASE_DIR aponta para a raiz do projeto (pai de advocacia_app/)
BASE_DIR: Path = Path(__file__).parent.parent.parent
APP_DIR:  Path = Path(__file__).parent.parent   # advocacia_app/
STATIC_DIR: Path = APP_DIR.parent / "static"
IMG_DIR:  Path = STATIC_DIR / "img"
TEMPLATES_DIR: Path = APP_DIR.parent / "templates"

# Garante que as pastas existam ao importar o módulo
IMG_DIR.mkdir(parents=True, exist_ok=True)

# ─── Banco SQLite de conteúdo (sqlite3 síncrono) ──────────────────────────────
# Separado do banco do fastapi-users para isolar responsabilidades.
CONTENT_DB_PATH: Path = BASE_DIR / "content.db"

# ─── Banco SQLAlchemy async (fastapi-users) ───────────────────────────────────
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{BASE_DIR / 'auth.db'}",
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

# ─── Upload de imagens ────────────────────────────────────────────────────────
ALLOWED_IMAGE_TYPES: set[str] = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE_MB: int = 5