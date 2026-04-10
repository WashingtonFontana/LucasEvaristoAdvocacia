"""
init_db.py
──────────
Script de inicialização executado UMA VEZ para criar o usuário
administrador no banco de autenticação (auth.db).

Uso:
    python init_db.py

Variáveis de ambiente opcionais:
    ADMIN_EMAIL  — padrão: contato@lucasevaristo.com.br
    ADMIN_PASS   — padrão: Lucas@2026

Após rodar, inicie normalmente com:
    uvicorn app:app --reload
"""

import asyncio
import os
import uuid

from sqlalchemy import select

from advocacia_app.core.auth_db import Base, User, async_session_maker, engine
from advocacia_app.core.content_db import init_content_db
from fastapi_users.password import PasswordHelper

ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "contato@lucasevaristo.com.br")
ADMIN_PASS:  str = os.getenv("ADMIN_PASS",  "Lucas@2026")

password_helper = PasswordHelper()


async def main() -> None:
    print("=" * 55)
    print("  Inicialização do banco de dados")
    print("=" * 55)

    # ── 1. auth.db — tabela de usuários ─────────────────────────────────────
    print("\n[1/3] Criando tabelas de autenticação (auth.db)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("      ✓ Tabelas verificadas/criadas.")

    # ── 2. Usuário administrador ─────────────────────────────────────────────
    print(f"\n[2/3] Verificando usuário administrador ({ADMIN_EMAIL})...")
    async with async_session_maker() as session:
        resultado = await session.execute(
            select(User).filter_by(email=ADMIN_EMAIL)
        )
        usuario_existente = resultado.scalar_one_or_none()

        if usuario_existente:
            print("      ℹ  Usuário já existe — nenhuma alteração realizada.")
        else:
            novo_usuario = User(
                id=uuid.uuid4(),
                email=ADMIN_EMAIL,
                hashed_password=password_helper.hash(ADMIN_PASS),
                is_active=True,
                is_superuser=True,
                is_verified=True,
            )
            session.add(novo_usuario)
            await session.commit()
            print(f"      ✓ Administrador criado com e-mail: {ADMIN_EMAIL}")

    # ── 3. content.db — textos e cards ───────────────────────────────────────
    print("\n[3/3] Inicializando banco de conteúdo (content.db)...")
    init_content_db()
    print("      ✓ Tabelas e seed verificados.")

    print("\n" + "=" * 55)
    print("  ✅  Tudo pronto! Inicie com:")
    print("      uvicorn app:app --reload")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())