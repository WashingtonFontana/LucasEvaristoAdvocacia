"""
routers/site.py
───────────────
Rotas públicas do site — renderizam templates Jinja2 com dados do banco.

  GET /          → index.html (site público)
  GET /login     → login.html (página de autenticação)
"""

import sqlite3

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from advocacia_app.core.content_db import get_content_db, fetchall

router = APIRouter(tags=["Site Público"])

# Jinja2 — resolvido em relação ao pacote
import os
_TMPL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
templates = Jinja2Templates(directory=os.path.realpath(_TMPL_DIR))


def _montar_conteudo(db: sqlite3.Connection) -> dict:
    """Reconstrói o dicionário completo de conteúdo a partir do banco."""
    linhas = fetchall(db, "SELECT secao, chave, valor FROM conteudo")
    data: dict = {}
    for row in linhas:
        data.setdefault(row["secao"], {})[row["chave"]] = row["valor"]

    cards = fetchall(db, "SELECT icone, titulo, descricao FROM cards ORDER BY ordem")
    data.setdefault("especialidades", {})["cards"] = cards
    return data


@router.get("/", response_class=HTMLResponse, summary="Página principal do site")
async def index(
    request: Request,
    db: sqlite3.Connection = Depends(get_content_db),
) -> HTMLResponse:
    dados = _montar_conteudo(db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"dados": dados},
    )


@router.get("/login", response_class=HTMLResponse, summary="Página de login")
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="login.html")