"""
routers/admin.py
────────────────
Rotas HTML do painel administrativo — protegidas pelo fastapi-users.

  GET  /admin          → exibe formulário com dados atuais
  POST /admin/update   → salva textos + foto de perfil via multipart form
"""

import os
import sqlite3

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from advocacia_app.core.auth_db import User
from advocacia_app.core.auth_users import current_active_user
from advocacia_app.core.config import IMG_DIR, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE_MB
from advocacia_app.core.content_db import get_content_db, fetchall, execute

router = APIRouter(tags=["Painel Admin"])

import os as _os
_TMPL_DIR = _os.path.join(_os.path.dirname(__file__), "..", "..", "templates")
templates = Jinja2Templates(directory=_os.path.realpath(_TMPL_DIR))


def _montar_conteudo(db: sqlite3.Connection) -> dict:
    linhas = fetchall(db, "SELECT secao, chave, valor FROM conteudo")
    data: dict = {}
    for row in linhas:
        data.setdefault(row["secao"], {})[row["chave"]] = row["valor"]
    cards = fetchall(db, "SELECT icone, titulo, descricao FROM cards ORDER BY ordem")
    data.setdefault("especialidades", {})["cards"] = cards
    return data


@router.get("/admin", response_class=HTMLResponse, summary="Painel de administração")
async def admin_panel(
    request: Request,
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> HTMLResponse:
    """Exibe o formulário com todos os dados atuais do banco para edição."""
    dados = _montar_conteudo(db)
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"user": user, "dados": dados},
    )


@router.post("/admin/update", summary="Salva alterações do formulário do painel")
async def update_site(
    request:          Request,
    # ── Campos do formulário ──────────────────────────────────────────────────
    hero_welcome:     str = Form(None),
    hero_titulo1:     str = Form(None),
    hero_titulo2:     str = Form(None),
    hero_subtitulo:   str = Form(None),
    hero_btn:         str = Form(None),
    perfil_nome:      str = Form(None),
    perfil_cargo:     str = Form(None),
    contato_whatsapp: str = Form(None),
    footer_semana:    str = Form(None),
    footer_fimde:     str = Form(None),
    footer_endereco:  str = Form(None),
    nova_foto:        UploadFile = File(None),
    # ── Dependências ─────────────────────────────────────────────────────────
    user: User = Depends(current_active_user),
    db:   sqlite3.Connection = Depends(get_content_db),
) -> RedirectResponse:
    """
    Recebe os campos do formulário HTML, faz upsert no banco de conteúdo
    e registra a ação no audit_log.
    """
    atualizacoes = {
        ("hero",   "welcome_text"):  hero_welcome,
        ("hero",   "titulo_linha1"): hero_titulo1,
        ("hero",   "titulo_linha2"): hero_titulo2,
        ("hero",   "subtitulo"):     hero_subtitulo,
        ("hero",   "btn_texto"):     hero_btn,
        ("perfil", "nome"):          perfil_nome,
        ("perfil", "cargo"):         perfil_cargo,
        ("contato","whatsapp_numero"): contato_whatsapp,
        ("footer", "horario_semana"): footer_semana,
        ("footer", "horario_fim"):    footer_fimde,
        ("footer", "endereco"):       footer_endereco,
    }

    for (secao, chave), valor in atualizacoes.items():
        if valor is not None:
            execute(
                db,
                """INSERT INTO conteudo (secao, chave, valor)
                   VALUES (?, ?, ?)
                   ON CONFLICT(secao, chave) DO UPDATE
                   SET valor = excluded.valor,
                       atualizado_em = datetime('now','localtime')""",
                (secao, chave, valor),
            )

    # Foto de perfil
    if nova_foto and nova_foto.filename:
        if nova_foto.content_type in ALLOWED_IMAGE_TYPES:
            conteudo_foto = await nova_foto.read()
            if len(conteudo_foto) <= MAX_IMAGE_SIZE_MB * 1024 * 1024:
                ext = nova_foto.filename.rsplit(".", 1)[-1].lower()
                destino = IMG_DIR / f"perfil_lucas.{ext}"
                # Remove versão anterior com extensão diferente
                for old in IMG_DIR.glob("perfil_lucas.*"):
                    old.unlink()
                destino.write_bytes(conteudo_foto)

                execute(
                    db,
                    """INSERT INTO imagens (nome, url, tamanho_kb, mime_type)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(nome) DO UPDATE
                       SET url       = excluded.url,
                           tamanho_kb= excluded.tamanho_kb,
                           mime_type = excluded.mime_type,
                           enviado_em= datetime('now','localtime')""",
                    (
                        "foto-perfil",
                        f"/static/img/{destino.name}",
                        len(conteudo_foto) // 1024,
                        nova_foto.content_type,
                    ),
                )

    # Audit log
    execute(
        db,
        "INSERT INTO audit_log (usuario, acao, detalhe) VALUES (?, ?, ?)",
        (str(user.email), "UPDATE_PAINEL_HTML", "Atualização via formulário HTML."),
    )

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)