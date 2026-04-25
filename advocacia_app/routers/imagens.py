"""
routers/imagens.py
──────────────────
API REST para upload e listagem de imagens.
Protegida pelo fastapi-users (current_active_user).

  GET  /api/imagens              → lista metadados das imagens
  POST /api/imagens/logo         → substitui a logo/slogan
  POST /api/imagens/perfil       → substitui a foto do advogado
  POST /api/imagens/background   → substitui o fundo do hero
"""

import re
import sqlite3
import unicodedata

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from advocacia_app.core.auth_db import User
from advocacia_app.core.auth_users import current_active_user
from advocacia_app.core.config import ALLOWED_IMAGE_TYPES, IMG_DIR, MAX_IMAGE_SIZE_MB
from advocacia_app.core.content_db import execute, fetchall, get_content_db

router = APIRouter(prefix="/api/imagens", tags=["Imagens API"])

_ALLOWED_EXTS: set[str] = {"jpg", "jpeg", "png", "webp", "gif"}


def _sanitize_filename(name: str) -> str:
    """Normaliza e sanitiza um nome de arquivo, removendo caracteres perigosos."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^a-zA-Z0-9._-]", "", name.strip())
    return name


# ─── Helper ───────────────────────────────────────────────────────────────────
def _salvar_imagem(
    upload: UploadFile,
    nome_canonical: str,
    user: User,
    db: sqlite3.Connection,
) -> str:
    """
    Valida o arquivo, persiste em disco e faz upsert na tabela `imagens`.
    Registra a ação no audit_log.

    Returns:
        URL relativa do arquivo salvo — ex.: /static/img/slogan.png
    """
    if upload.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tipo não permitido: {upload.content_type}. "
                f"Aceitos: {', '.join(sorted(ALLOWED_IMAGE_TYPES))}"
            ),
        )

    conteudo = upload.file.read()
    tamanho_kb = len(conteudo) // 1024

    if len(conteudo) > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo muito grande. Máximo permitido: {MAX_IMAGE_SIZE_MB} MB.",
        )

    raw_name = _sanitize_filename(upload.filename) if upload.filename else "upload.jpg"
    ext = raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else "jpg"
    if ext not in _ALLOWED_EXTS:
        ext = "jpg"
    caminho = IMG_DIR / f"{nome_canonical}.{ext}"

    # Remove versões anteriores com extensões diferentes
    for antigo in IMG_DIR.glob(f"{nome_canonical}.*"):
        antigo.unlink()

    caminho.write_bytes(conteudo)
    url = f"/static/img/{caminho.name}"

    # Upsert na tabela imagens
    execute(
        db,
        """INSERT INTO imagens (nome, url, tamanho_kb, mime_type)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(nome) DO UPDATE
           SET url        = excluded.url,
               tamanho_kb = excluded.tamanho_kb,
               mime_type  = excluded.mime_type,
               enviado_em = datetime('now','localtime')""",
        (nome_canonical, url, tamanho_kb, upload.content_type),
    )

    execute(
        db,
        "INSERT INTO audit_log (usuario, acao, detalhe) VALUES (?, ?, ?)",
        (
            str(user.email),
            f"UPLOAD_{nome_canonical.upper().replace('-', '_')}",
            url,
        ),
    )

    return url


# ─── Rotas ────────────────────────────────────────────────────────────────────

@router.get("", summary="Lista os metadados das imagens registradas")
def listar_imagens(
    _: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> list[dict]:
    return fetchall(
        db,
        "SELECT nome, url, tamanho_kb, mime_type, enviado_em FROM imagens ORDER BY nome",
    )


@router.post("/logo", summary="Upload / substituição da logo do escritório")
def upload_logo(
    file: UploadFile = File(...),
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    url = _salvar_imagem(file, "slogan", user, db)
    return {"ok": True, "url": url, "mensagem": "Logo atualizada com sucesso."}


@router.post("/perfil", summary="Upload / substituição da foto de perfil do advogado")
def upload_perfil(
    file: UploadFile = File(...),
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    url = _salvar_imagem(file, "foto-perfil", user, db)
    return {"ok": True, "url": url, "mensagem": "Foto de perfil atualizada com sucesso."}


@router.post("/background", summary="Upload / substituição da imagem de fundo do hero")
def upload_background(
    file: UploadFile = File(...),
    user: User = Depends(current_active_user),
    db: sqlite3.Connection = Depends(get_content_db),
) -> dict:
    url = _salvar_imagem(file, "background", user, db)
    return {"ok": True, "url": url, "mensagem": "Imagem de fundo atualizada com sucesso."}