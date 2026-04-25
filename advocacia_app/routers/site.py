"""
routers/site.py
───────────────
Rotas públicas do site — renderizam templates Jinja2 com dados do banco.

  GET /           → index.html  (página principal)
  GET /sobre-nos  → sobre-nos.html
  GET /login      → login.html
"""

import sqlite3

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape

from advocacia_app.core.config import TEMPLATES_DIR
from advocacia_app.core.content_db import get_content_db, montar_conteudo

router = APIRouter(tags=["Site Público"])

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)
templates = Jinja2Templates(env=_env)


@router.get("/", response_class=HTMLResponse, summary="Página principal do site")
async def index(
    request: Request,
    db: sqlite3.Connection = Depends(get_content_db),
) -> HTMLResponse:
    dados = montar_conteudo(db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"dados": dados},
    )


@router.get("/sobre-nos", response_class=HTMLResponse, summary="Página Sobre Nós")
async def sobre_nos(
    request: Request,
    db: sqlite3.Connection = Depends(get_content_db),
) -> HTMLResponse:
    dados = montar_conteudo(db)
    return templates.TemplateResponse(
        request=request,
        name="sobre-nos.html",
        context={"dados": dados},
    )


@router.get("/login", response_class=HTMLResponse, summary="Página de login")
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="login.html")