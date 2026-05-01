# ⚖️ Lucas Evaristo - Advocacia e Consultoria

Este é um site institucional funcional desenvolvido para o meu
projeto acadêmico, com foco em apresentar o trabalho jurídico do
escritório de advocacia parceiro.

---

## 🚀 Tecnologias Utilizadas

- **Python 3.13** — linguagem principal do projeto
- **FastAPI com Poetry** — framework web assíncrono e gerenciamento de dependências
- **Jinja2** — templates HTML server-side
- **SQLite3 nativo (stdlib)** — banco de conteúdo síncrono
- **SQLAlchemy async + aiosqlite** — banco de autenticação
- **fastapi-users** — autenticação JWT com cookie HTTP-only
- **HTML5** — estruturação semântica
- **CSS3** — layouts com Grid e Flexbox
- **JavaScript** — interatividade e formulário WhatsApp
- **python-multipart** — upload de imagens
- **python-dotenv** — variáveis de ambiente

---

## 🛠️ Funcionalidades

- [x] Cabeçalho fixo com menu responsivo (hamburguer mobile)
- [x] Hero section com imagem de fundo e overlay
- [x] Grade de áreas de atuação: Criminal, Trabalhista, Cível, Consumidor e Previdenciário
- [x] Página Sobre Nós com linha do tempo da trajetória do advogado
- [x] Seção de perfil do advogado responsável
- [x] Formulário de contato com envio direto via WhatsApp
- [x] Rodapé com horários de funcionamento e endereço
- [x] Painel administrativo protegido por autenticação JWT
- [x] CMS para edição de textos do site via API REST
- [x] Upload de imagens: logo, foto de perfil e background
- [x] Log de auditoria de todas as ações do painel
- [x] API REST documentada via Swagger UI

---

## 📁 Estrutura do Projeto

```
advocacia_app/ (raiz do projeto)
├── app.py                  — Ponto de entrada da aplicação FastAPI
├── init_db.py              — Script de criação do usuário admin e seed dos bancos
├── pyproject.toml          — Configuração do Poetry e dependências
├── requirements.txt        — Dependências para pip/Docker
├── railway.toml            — Configuração de deploy no Railway
├── README.md                — Documentação do projeto
├── advocacia_app/
│   ├── core/
│   │   ├── config.py           — Constantes, caminhos e variáveis de ambiente
│   │   ├── content_store.py    — Dicionário CONTEUDO_PADRAO (seed)
│   │   ├── content_db.py       — sqlite3 síncrono: conteúdo, cards, imagens, audit
│   │   ├── auth_db.py          — SQLAlchemy async: modelo User + engine
│   │   └── auth_users.py       — fastapi-users: UserManager, JWT cookie, dependências
│   ├── routers/
│   │   ├── site.py             — Rotas públicas: / e /sobre-nos
│   │   ├── admin.py            — Painel HTML: GET /admin, POST /admin/update
│   │   ├── conteudo.py         — API REST: /api/conteudo/*
│   │   ├── imagens.py          — API REST: /api/imagens/*
│   │   ├── audit.py            — API REST: /api/audit
│   │   └── health.py           — Health check: /api/health
│   └── schemas/
│       ├── conteudo.py         — Modelos Pydantic: HeroUpdate, CardUpdate, etc.
│       └── users.py            — Modelos Pydantic: UserRead, AlterarSenhaRequest
├── templates/
│   ├── index.html          — Site público (página principal)
│   ├── sobre-nos.html      — Página Sobre Nós
│   ├── login.html           — Página de login
│   └── admin.html           — Painel de administração
└── static/
    ├── style.css             — Estilos do site e painel
    └── img/                  — Imagens enviadas via upload
```

---

## 🗄️ Arquitetura de Banco de Dados

Dois bancos SQLite3 separados por responsabilidade:

| Arquivo | Tecnologia | Tabelas | Responsabilidade |
|---------|-----------|---------|-----------------|
| `auth.db` | SQLAlchemy async + aiosqlite | `user` | Login, sessão JWT, gestão de usuários |
| `content.db` | sqlite3 (stdlib) síncrono | `conteudo`, `cards`, `imagens`, `audit_log` | Textos, cards, imagens e log de auditoria |

---

## 🚀 Como Iniciar o Projeto

**Dependências principais:** Python 3.13, Poetry

```bash
poetry install
```

```bash
poetry run python init_db.py
```

```bash
poetry run fastapi dev app.py
```

| URL | Descrição |
|-----|-----------|
| `http://localhost:8000` | Site público |
| `http://localhost:8000/admin` | Painel administrativo (requer login) |
| `http://localhost:8000/docs` | Swagger UI — documentação interativa |

---

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Valor padrão |
|----------|-----------|-------------|
| `JWT_SECRET` | Chave secreta para tokens JWT | Valor inseguro embutido (definir em produção) |
| `ADMIN_EMAIL` | E-mail do administrador | `contato@lucasevaristo.com.br` |
| `ADMIN_PASS` | Senha do administrador | `xxxxxxxxxx` |

---

## 📋 Endpoints da API

### Autenticação

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/auth/login` | ✗ | Login, seta cookie JWT |
| POST | `/auth/logout` | ✗ | Invalida cookie |

### Site Público

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/` | ✗ | Página principal |
| GET | `/sobre-nos` | ✗ | Página Sobre Nós |
| GET | `/login` | ✗ | Página de login |

### Painel Admin (HTML)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/admin` | ✓ | Painel de administração |
| POST | `/admin/update` | ✓ | Salva alterações do formulário |

### Conteúdo (API REST)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/conteudo/publico` | ✗ | Todo o conteúdo (público) |
| GET | `/api/conteudo` | ✓ | Todo o conteúdo |
| PUT | `/api/conteudo/hero` | ✓ | Atualiza Hero |
| PUT | `/api/conteudo/especialidades` | ✓ | Atualiza cards |
| PUT | `/api/conteudo/perfil` | ✓ | Atualiza perfil |
| PUT | `/api/conteudo/contato` | ✓ | Atualiza contato |
| PUT | `/api/conteudo/footer` | ✓ | Atualiza rodapé |
| PUT | `/api/conteudo/sobre-nos` | ✓ | Atualiza Sobre Nós |
| POST | `/api/conteudo/reset` | ✓ | Restaura padrão |

### Imagens (API REST)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/imagens` | ✓ | Lista imagens |
| POST | `/api/imagens/logo` | ✓ | Upload da logo |
| POST | `/api/imagens/perfil` | ✓ | Upload da foto |
| POST | `/api/imagens/background` | ✓ | Upload do background |

### Sistema

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/health` | ✗ | Health check público |
| GET | `/api/audit` | ✓ | Log de auditoria |

---

## 🌐 Deploy

**Plataforma:** Railway

**Comando de start:**

```bash
python init_db.py && uvicorn app:app --host 0.0.0.0 --port $PORT
```

> **Nota:** O banco SQLite3 é armazenado no filesystem do container. Em caso de redeploy, os dados persistem apenas se um volume for configurado.

---

## 🌍 Impacto Social (ODS)

Este projeto está alinhado com o ODS 16 (Paz, Justiça e Instituições
Eficazes) da ONU, visando facilitar o acesso democrático à informação
jurídica e promover um canal direto e eficiente entre o cidadão e
a justiça.

---

## ✍️ Créditos
Este projeto foi desenvolvido integralmente por:

#### Washington Fontana Netto

#### ⭐ Desenvolvido para fins acadêmicos.
