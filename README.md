# ⚖️ Lucas Evaristo — Advocacia e Consultoria

Portal institucional com painel administrativo completo.  
Desenvolvido com **FastAPI + fastapi-users + SQLite3**.

---

## 📁 Estrutura do Projeto

```
LE_Advocacia/
│
├── app.py                        ← Ponto de entrada (FastAPI)
├── init_db.py                    ← Script de setup inicial (roda 1 vez)
├── pyproject.toml
│
├── advocacia_app/
│   ├── core/
│   │   ├── config.py             ← Constantes, caminhos, variáveis de ambiente
│   │   ├── content_store.py      ← Dicionário CONTEUDO_PADRAO (seed)
│   │   ├── content_db.py         ← sqlite3 síncrono: conteúdo, cards, imagens, audit
│   │   ├── auth_db.py            ← SQLAlchemy async: modelo User + engine
│   │   └── auth_users.py         ← fastapi-users: UserManager, JWT cookie, dependências
│   │
│   ├── routers/
│   │   ├── site.py               ← GET /  e  GET /login  (páginas públicas)
│   │   ├── admin.py              ← GET /admin  e  POST /admin/update  (painel HTML)
│   │   ├── conteudo.py           ← /api/conteudo/*  (API REST de textos)
│   │   ├── imagens.py            ← /api/imagens/*   (API REST de uploads)
│   │   ├── audit.py              ← /api/audit       (log de auditoria)
│   │   └── health.py             ← /api/health      (health check)
│   │
│   └── schemas/
│       ├── conteudo.py           ← Pydantic: HeroUpdate, CardUpdate, etc.
│       └── users.py              ← Pydantic: UserRead/Create/Update + AlterarSenha
│
├── templates/
│   ├── index.html                ← Site público (Jinja2)
│   ├── login.html                ← Página de login
│   └── admin.html                ← Painel de administração
│
└── static/
    └── img/                      ← Imagens enviadas via upload
```

---

## 🗄️ Arquitetura de Bancos

| Arquivo     | Tecnologia           | Responsabilidade                        |
|-------------|---------------------|-----------------------------------------|
| `auth.db`   | SQLAlchemy async    | Login, sessão JWT, gestão de usuários   |
| `content.db`| sqlite3 (stdlib)    | Textos, cards, imagens, audit_log       |

Dois bancos separados. O `fastapi-users` cuida de tudo que é segurança/auth; o `sqlite3` da stdlib gerencia o CMS — sem dependências extras.

---

## 🚀 Como Iniciar

### 1. Instalar dependências (com Poetry)
```bash
poetry install
```

### 2. (Opcional) Configurar variáveis de ambiente
```bash
export JWT_SECRET="sua_chave_secreta_longa_e_aleatoria"
export ADMIN_EMAIL="contato@lucasevaristo.com.br"
export ADMIN_PASS="Lucas@2026"
```

### 3. Criar o usuário admin e inicializar os bancos
```bash
poetry run python init_db.py
```

### 4. Iniciar o servidor
```bash
poetry run uvicorn app:app --reload --port 8000
```

---

## 🌐 URLs

| URL                          | Descrição                              |
|------------------------------|----------------------------------------|
| `http://localhost:8000/`     | Site público                           |
| `http://localhost:8000/login`| Página de login                        |
| `http://localhost:8000/admin`| Painel administrativo (auth obrigatória)|
| `http://localhost:8000/docs` | Swagger UI — documentação interativa   |
| `http://localhost:8000/redoc`| ReDoc                                  |

---

## 🔐 Autenticação

O projeto usa **fastapi-users com cookie JWT**. O fluxo é:

1. `POST /auth/login` com `{ "username": "email", "password": "senha" }`  
   → Responde com cookie `advocacia_auth` (HTTP-only, 1 hora)

2. Todas as rotas `/admin*` e `/api/*` (exceto `/api/conteudo/publico` e `/api/health`) exigem esse cookie.

---

## 📋 Endpoints da API

### Autenticação
| Método | Rota           | Descrição               |
|--------|---------------|-------------------------|
| POST   | `/auth/login`  | Faz login, seta cookie  |
| POST   | `/auth/logout` | Invalida o cookie       |

### Conteúdo
| Método | Rota                          | Auth | Descrição                  |
|--------|-------------------------------|------|----------------------------|
| GET    | `/api/conteudo/publico`       | ✗    | Todo o conteúdo (público)  |
| GET    | `/api/conteudo`               | ✓    | Todo o conteúdo            |
| PUT    | `/api/conteudo/hero`          | ✓    | Atualiza Hero              |
| PUT    | `/api/conteudo/especialidades`| ✓    | Atualiza cards             |
| PUT    | `/api/conteudo/perfil`        | ✓    | Atualiza perfil            |
| PUT    | `/api/conteudo/contato`       | ✓    | Atualiza contato           |
| PUT    | `/api/conteudo/footer`        | ✓    | Atualiza rodapé            |
| POST   | `/api/conteudo/reset`         | ✓    | Restaura padrão            |

### Imagens
| Método | Rota                     | Auth | Descrição              |
|--------|--------------------------|------|------------------------|
| GET    | `/api/imagens`           | ✓    | Lista imagens          |
| POST   | `/api/imagens/logo`      | ✓    | Upload da logo         |
| POST   | `/api/imagens/perfil`    | ✓    | Upload da foto         |
| POST   | `/api/imagens/background`| ✓    | Upload do background   |

### Sistema
| Método | Rota              | Auth | Descrição         |
|--------|------------------|------|-------------------|
| GET    | `/api/health`    | ✗    | Health check      |
| GET    | `/api/audit`     | ✓    | Log de auditoria  |

---

## ⚠️ Antes de ir para produção

- Defina `JWT_SECRET` via variável de ambiente com valor longo e aleatório
- Mude `cookie_secure=True` em `core/auth_users.py` (requer HTTPS)
- Restrinja `allow_origins` no CORS para o domínio real
- Faça backup periódico dos arquivos `auth.db` e `content.db`