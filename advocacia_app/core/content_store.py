"""
core/content_store.py
─────────────────────
Define o CONTEUDO_PADRAO — dicionário com os textos originais do site.

Este módulo não tem dependências internas, apenas fornece a constante
usada em dois lugares:
  • core/content_db.py  → seed inicial do banco de conteúdo
  • routers/conteudo.py → endpoint POST /api/conteudo/reset
"""

from typing import TypedDict


class CardPadrao(TypedDict):
    icone: str
    titulo: str
    descricao: str


CONTEUDO_PADRAO: dict[str, dict[str, str | list[CardPadrao]]] = {
    "hero": {
        "welcome_text":  "SEJA BEM-VINDO!",
        "titulo_linha1": "Lucas Evaristo -",
        "titulo_linha2": "Advocacia e Consultoria",
        "subtitulo":     "Transformando desafios jurídicos complexos em soluções eficazes e personalizadas",
        "btn_texto":     "ENTRE EM CONTATO",
    },
    "especialidades": {
        "subtitulo": "NOSSAS ESPECIALIDADES",
        "titulo":    "Áreas de atuação",
        "cards": [
            {
                "icone":     "⚖️",
                "titulo":    "Criminal",
                "descricao": "Atuação em Audiências, Sustentações Orais, Acompanhamento em "
                             "Delegacias, Processos Penais e Medidas Cautelares.",
            },
            {
                "icone":     "💼",
                "titulo":    "Trabalhista",
                "descricao": "Consultoria e litígio em relações de trabalho para empregados e empresas.",
            },
            {
                "icone":     "🏛️",
                "titulo":    "Cível",
                "descricao": "O Direito Civil protege a dignidade humana ao regular relações, "
                             "garantir propriedades e assegurar a justiça nas escolhas individuais.",
            },
            {
                "icone":     "🛒",
                "titulo":    "Consumidor",
                "descricao": "Proteção contra práticas abusivas e defesa dos direitos do consumidor.",
            },
            {
                "icone":     "👵",
                "titulo":    "Previdenciário",
                "descricao": "Auxílio na obtenção de aposentadorias, auxílios e benefícios do INSS.",
            },
        ],
    },
    "perfil": {
        "titulo_secao": "Nosso Corpo Jurídico",
        "nome":         "Lucas Evaristo",
        "cargo":        "Advogado",
    },
    "contato": {
        "titulo":                "Fale Conosco",
        "placeholder_nome":      "Seu Nome",
        "placeholder_telefone":  "Seu Telefone",
        "placeholder_mensagem":  "Sua Mensagem",
        "btn_texto":             "Enviar Mensagem",
        "whatsapp_numero":       "5532988134080",
    },
    "footer": {
        "links_titulo":    "Links Rápidos",
        "horarios_titulo": "Horários",
        "horario_semana":  "Segunda a Sexta: 09:00 - 18:00",
        "horario_fim":     "Sábado e Domingo: Fechado",
        "endereco":        "Av. Brasil, 1975 - Loja 1991 - Centro, Juiz de Fora - MG, 36060-010",
    },
}