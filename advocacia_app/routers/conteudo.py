"""
routers/conteudo.py
───────────────────
API REST para leitura e edição dos textos do site.
Protegida pelo fastapi-users (current_active_user).

  GET  /api/conteudo            → todo o conteúdo (autenticado)
  GET  /api/conteudo/publico    → todo o conteúdo (sem auth)
  PUT  /api/conteudo/hero
  PUT  /api/conteudo/especialidades
  PUT  /api/conteudo/perfil
  PUT  /api/conteudo/contato
  PUT  /api/conteudo/footer
  PUT  /api/conteudo/sobre-nos
  POST /api/conteudo/reset
"""

import json
import sqlite3
from datetime import datetime

from fastapi import APIRouter, Depends

from advocacia_app.core.auth_db import User
from advocacia_app.core.auth_users import current_active_user
from advocacia_app.core.content_db import get_content_db, fetchall, execute, montar_conteudo, atomic
from advocacia_app.core.content_store import CONTEUDO_PADRAO
from advocacia_app.schemas.conteudo import (
    ContatoUpdate,
    EspecialidadesUpdate,
    FooterUpdate,
    HeroUpdate,
    PerfilUpdate,
    SobreNosUpdate,
)

router = APIRouter(prefix="/api/conteudo", tags=["Conteúdo API"])


_CARD_FIELDS = ("icone", "titulo", "descricao")


def _upsert(
    db: sqlite3.Connection,
    secao: str,
    campos: dict,
    usuario_email: str,
    acao: str,
) -> None:
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for chave, valor in campos.items():
        execute(
            db,
            """INSERT INTO conteudo (secao, chave, valor, atualizado_em)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(secao, chave) DO UPDATE
               SET valor = excluded.valor, atualizado_em = excluded.atualizado_em""",
            (secao, chave, str(valor), agora),
        )
    execute(
        db,
        "INSERT INTO audit_log (usuario, acao, detalhe) VALUES (?, ?, ?)",
        (usuario_email, acao, json.dumps(campos, ensure_ascii=False)),
    )


# ─── Leitura ──────────────────────────────────────────────────────────────────

@router.get("", summary="Todo o conteúdo (autenticado)")
def get_conteudo(
    _: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    return montar_conteudo(db)


@router.get("/publico", summary="Todo o conteúdo (sem autenticação)")
def get_conteudo_publico(db: sqlite3.Connection = Depends(get_content_db)) -> dict:
    return montar_conteudo(db)


# ─── Edição ───────────────────────────────────────────────────────────────────

@router.put("/hero", summary="Atualiza a seção Hero")
def update_hero(
    payload: HeroUpdate,
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    _upsert(db, "hero", payload.model_dump(exclude_none=True), str(user.email), "UPDATE_HERO")
    return {"ok": True, "hero": montar_conteudo(db).get("hero")}


@router.put("/especialidades", summary="Atualiza especialidades e cards")
def update_especialidades(
    payload: EspecialidadesUpdate,
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    updates = payload.model_dump(exclude_none=True)

    campos_secao = {k: v for k, v in updates.items() if k != "cards"}
    if campos_secao:
        _upsert(db, "especialidades", campos_secao, str(user.email), "UPDATE_ESPECIALIDADES")

    if "cards" in updates:
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i, card_upd in enumerate(updates["cards"]):
            set_clauses = []
            params = []
            for campo in _CARD_FIELDS:
                if card_upd.get(campo) is not None:
                    set_clauses.append(f"{campo} = ?")
                    params.append(card_upd[campo])
            if set_clauses:
                set_clauses.append("atualizado_em = ?")
                params.extend([agora, i])
                execute(
                    db,
                    f"UPDATE cards SET {', '.join(set_clauses)} WHERE ordem = ?",
                    tuple(params),
                )
        execute(
            db,
            "INSERT INTO audit_log (usuario, acao, detalhe) VALUES (?, ?, ?)",
            (str(user.email), "UPDATE_CARDS", json.dumps(updates["cards"], ensure_ascii=False)),
        )

    return {"ok": True, "especialidades": montar_conteudo(db).get("especialidades")}


@router.put("/perfil", summary="Atualiza a seção de perfil")
def update_perfil(
    payload: PerfilUpdate,
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    _upsert(db, "perfil", payload.model_dump(exclude_none=True), str(user.email), "UPDATE_PERFIL")
    return {"ok": True, "perfil": montar_conteudo(db).get("perfil")}


@router.put("/contato", summary="Atualiza a seção de contato")
def update_contato(
    payload: ContatoUpdate,
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    _upsert(db, "contato", payload.model_dump(exclude_none=True), str(user.email), "UPDATE_CONTATO")
    return {"ok": True, "contato": montar_conteudo(db).get("contato")}


@router.put("/footer", summary="Atualiza o rodapé")
def update_footer(
    payload: FooterUpdate,
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    _upsert(db, "footer", payload.model_dump(exclude_none=True), str(user.email), "UPDATE_FOOTER")
    return {"ok": True, "footer": montar_conteudo(db).get("footer")}


@router.put("/sobre-nos", summary="Atualiza a página Sobre Nós")
def update_sobre_nos(
    payload: SobreNosUpdate,
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    _upsert(db, "sobre_nos", payload.model_dump(exclude_none=True), str(user.email), "UPDATE_SOBRE_NOS")
    return {"ok": True, "sobre_nos": montar_conteudo(db).get("sobre_nos")}


# ─── Reset ────────────────────────────────────────────────────────────────────

@router.post("/reset", summary="Restaura o conteúdo ao padrão original")
def reset_conteudo(
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    with atomic(db):
        db.execute("DELETE FROM conteudo")
        db.execute("DELETE FROM cards")

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linhas = []
        for secao, campos in CONTEUDO_PADRAO.items():
            if secao == "especialidades":
                for chave, valor in campos.items():
                    if chave != "cards":
                        linhas.append((secao, chave, str(valor), agora))
                continue
            for chave, valor in campos.items():
                linhas.append((secao, chave, str(valor), agora))

        db.executemany(
            "INSERT INTO conteudo (secao, chave, valor, atualizado_em) VALUES (?, ?, ?, ?)",
            linhas,
        )
        db.executemany(
            "INSERT INTO cards (ordem, icone, titulo, descricao, atualizado_em) VALUES (?, ?, ?, ?, ?)",
            [
                (i, c["icone"], c["titulo"], c["descricao"], agora)
                for i, c in enumerate(CONTEUDO_PADRAO["especialidades"]["cards"])
            ],
        )

    execute(
        db,
        "INSERT INTO audit_log (usuario, acao, detalhe) VALUES (?, ?, ?)",
        (str(user.email), "RESET_CONTEUDO", "Conteúdo restaurado ao padrão."),
    )
    return {"ok": True, "mensagem": "Conteúdo restaurado ao padrão."}