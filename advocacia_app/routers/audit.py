"""
routers/audit.py
────────────────
Consulta ao log de auditoria — todas as ações do painel ficam registradas.
Protegida pelo fastapi-users (current_active_user).

  GET /api/audit               → registros mais recentes
  GET /api/audit?usuario=x     → filtra por e-mail do usuário
  GET /api/audit?acao=x        → filtra por tipo de ação
  GET /api/audit?limite=100    → controla o máximo de registros (padrão: 50)
"""

import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, Query

from advocacia_app.core.auth_db import User
from advocacia_app.core.auth_users import current_active_user
from advocacia_app.core.content_db import fetchall, get_content_db

router = APIRouter(prefix="/api/audit", tags=["Auditoria API"])


@router.get("", summary="Lista o log de auditoria das ações no painel")
def listar_audit(
    usuario: Optional[str] = Query(None, description="Filtra pelo e-mail do usuário"),
    acao:    Optional[str] = Query(None, description="Filtra pelo tipo de ação"),
    limite:  int           = Query(50, ge=1, le=200, description="Máximo de registros"),
    _: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> list[dict]:
    sql    = "SELECT id, usuario, acao, detalhe, ip, criado_em FROM audit_log WHERE 1=1"
    params: list = []

    if usuario:
        sql += " AND usuario = ?"
        params.append(usuario)
    if acao:
        sql += " AND acao = ?"
        params.append(acao.upper())

    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limite)

    return fetchall(db, sql, tuple(params))