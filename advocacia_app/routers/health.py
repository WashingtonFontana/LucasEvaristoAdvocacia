"""
routers/health.py
─────────────────
Health check público da API — sem autenticação.

  GET /api/health
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Sistema"])


@router.get("/health", summary="Verifica se a API está no ar")
def health() -> dict:
    return {
        "status": "ok",
        "servico": "Lucas Evaristo Admin API",
        "versao": "3.0.0",
    }