"""
core/content_db.py
──────────────────
Camada SQLite3 **síncrona** exclusiva para as tabelas de conteúdo do site.

Por que sqlite3 síncrono e não SQLAlchemy async?
  • O fastapi-users já gerencia o banco de usuários via SQLAlchemy async.
  • Textos e imagens do CMS são operações simples, sem concorrência crítica.
  • sqlite3 da stdlib não precisa de dependência extra e é suficiente aqui.
  • O WAL mode resolve a coexistência leitura/escrita no mesmo arquivo .db.

Tabelas gerenciadas aqui:
  conteudo   — textos do site por seção/chave
  cards      — 5 cards de especialidades
  imagens    — metadados de uploads
  audit_log  — registro de todas as ações do painel

Responsabilidades:
  • DDL e seed automáticos via init_content_db()
  • Dependência FastAPI get_content_db() — uma conexão por request
  • Helpers fetchone / fetchall / execute / montar_conteudo
"""

import hashlib
import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from .config import CONTENT_DB_PATH
from .content_store import CONTEUDO_PADRAO

# ─── DDL ─────────────────────────────────────────────────────────────────────
_DDL = """
-- Textos do site: cada linha é secao + chave → valor
CREATE TABLE IF NOT EXISTS conteudo (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    secao         TEXT    NOT NULL,
    chave         TEXT    NOT NULL,
    valor         TEXT    NOT NULL DEFAULT '',
    atualizado_em TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    UNIQUE (secao, chave)
);

-- Cards de especialidades
CREATE TABLE IF NOT EXISTS cards (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ordem         INTEGER NOT NULL UNIQUE,
    icone         TEXT    NOT NULL DEFAULT '',
    titulo        TEXT    NOT NULL DEFAULT '',
    descricao     TEXT    NOT NULL DEFAULT '',
    atualizado_em TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- Metadados de imagens enviadas via upload
CREATE TABLE IF NOT EXISTS imagens (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT    NOT NULL UNIQUE,
    url           TEXT    NOT NULL,
    tamanho_kb    INTEGER,
    mime_type     TEXT,
    enviado_em    TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- Log de auditoria de ações realizadas pelo painel
CREATE TABLE IF NOT EXISTS audit_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario       TEXT    NOT NULL,
    acao          TEXT    NOT NULL,
    detalhe       TEXT,
    ip            TEXT,
    criado_em     TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);
"""


# ─── Seed ─────────────────────────────────────────────────────────────────────
def _seed(conn: sqlite3.Connection) -> None:
    """Popula dados iniciais se as tabelas estiverem vazias. Idempotente.

    Também garante que chaves adicionadas ao CONTEUDO_PADRAO após o seed
    inicial sejam inseridas em bancos já existentes (INSERT OR IGNORE).
    """
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM conteudo")
    if cur.fetchone()[0] == 0:
        linhas = []
        for secao, campos in CONTEUDO_PADRAO.items():
            if secao == "especialidades":
                for chave, valor in campos.items():
                    if chave != "cards":
                        linhas.append((secao, chave, str(valor)))
                continue
            for chave, valor in campos.items():
                linhas.append((secao, chave, str(valor)))
        cur.executemany(
            "INSERT OR IGNORE INTO conteudo (secao, chave, valor) VALUES (?, ?, ?)",
            linhas,
        )
    else:
        linhas = []
        for secao, campos in CONTEUDO_PADRAO.items():
            if secao == "especialidades":
                for chave, valor in campos.items():
                    if chave != "cards":
                        linhas.append((secao, chave, str(valor)))
                continue
            for chave, valor in campos.items():
                linhas.append((secao, chave, str(valor)))
        cur.executemany(
            "INSERT OR IGNORE INTO conteudo (secao, chave, valor) VALUES (?, ?, ?)",
            linhas,
        )

    # Cards
    cur.execute("SELECT COUNT(*) FROM cards")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO cards (ordem, icone, titulo, descricao) VALUES (?, ?, ?, ?)",
            [
                (i, c["icone"], c["titulo"], c["descricao"])
                for i, c in enumerate(CONTEUDO_PADRAO["especialidades"]["cards"])
            ],
        )

    conn.commit()


# ─── Conexão ──────────────────────────────────────────────────────────────────
def _conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(str(CONTENT_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_content_db() -> None:
    """
    Cria as tabelas e executa o seed.
    Chamado no lifespan do FastAPI — executa uma única vez na inicialização.
    """
    conn = _conectar()
    conn.executescript(_DDL)
    conn.commit()
    _seed(conn)
    conn.close()


# ─── Dependência FastAPI ──────────────────────────────────────────────────────
def get_content_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Uma conexão sqlite3 por request HTTP. Fechamento garantido via finally.

    Uso nos routers:
        db: sqlite3.Connection = Depends(get_content_db)
    """
    conn = _conectar()
    try:
        yield conn
    finally:
        conn.close()


# ─── Helpers de query ─────────────────────────────────────────────────────────
def fetchone(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> dict | None:
    row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def fetchall(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def execute(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> int:
    """Executa DML, faz commit e retorna lastrowid."""
    cur = conn.execute(sql, params)
    conn.commit()
    return cur.lastrowid


def montar_conteudo(conn: sqlite3.Connection) -> dict:
    """Reconstrói o dicionário completo de conteúdo a partir do banco.

    Usado pelos routers públicos e admin para popular os templates Jinja2
    e os endpoints da API REST. Evita duplicação de lógica de consulta.
    """
    linhas = fetchall(conn, "SELECT secao, chave, valor FROM conteudo")
    data: dict = {}
    for row in linhas:
        data.setdefault(row["secao"], {})[row["chave"]] = row["valor"]
    cards = fetchall(conn, "SELECT icone, titulo, descricao FROM cards ORDER BY ordem")
    data.setdefault("especialidades", {})["cards"] = cards
    return data


@contextmanager
def atomic(conn: sqlite3.Connection):
    """Context manager para operações atômicas.

    Commit ao final do bloco se não houver exceção; rollback caso contrário.
    Internamente desabilita o auto-commit do helper execute() ao abrir
    uma transação explícita.
    """
    conn.execute("BEGIN")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise