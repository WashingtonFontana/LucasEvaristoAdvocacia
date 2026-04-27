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
    "sobre_nos": {
        "hero_subtitulo":         "Comprometimento, ética e técnica a serviço da justiça desde 2019.",
        "quem_somos_subtitulo":   "QUEM SOMOS",
        "quem_somos_titulo":      "Dr. Lucas Evaristo",
        "quem_somos_texto_1":     "A história do escritório Lucas Evaristo Advocacia e Consultoria é a história de uma vocação."
                                   " Uma escolha deliberada pelo Direito como instrumento de justiça, equilíbrio e proteção — nas"
                                   " causas do trabalho, nas demandas do consumidor, nos processos criminais e nas relações civis"
                                   " que moldam o cotidiano das pessoas.",
        "quem_somos_texto_2":     "Inscrito na Ordem dos Advogados do Brasil desde 2019, o Dr. Lucas Evaristo construiu"
                                   " sua trajetória com método e seriedade, acumulando experiência prática em diferentes"
                                   " frentes do Direito. Com base em Juiz de Fora — MG, atua em audiências, delegacias,"
                                   " varas trabalhistas e juizados especiais, sempre com presença ativa e acompanhamento"
                                   " próximo ao cliente em cada etapa do processo.",
        "quem_somos_texto_3":     "Mais de cinco anos de atuação contínua, com casos nas áreas Criminal, Trabalhista,"
                                   " Cível, do Consumidor e Previdenciária, formaram um profissional versátil e tecnicamente"
                                   " sólido — capaz de traduzir o complexo universo jurídico em soluções claras,"
                                   " eficazes e personalizadas para cada cliente.",
        "trajetoria_subtitulo":   "TRAJETÓRIA",
        "trajetoria_titulo":      "Uma carreira construída com propósito",
        "timeline_ano_1":         "2019",
        "timeline_titulo_1":      "Inscrição na OAB/MG",
        "timeline_desc_1":        "Após a conclusão da graduação em Direito, o Dr. Lucas Evaristo obtém sua inscrição"
                                   " na Ordem dos Advogados do Brasil — seccional Minas Gerais — e inicia sua atuação"
                                   " profissional com foco em causas cíveis e do consumidor.",
        "timeline_ano_2":         "2020",
        "timeline_titulo_2":      "Expansão para o Direito Criminal",
        "timeline_desc_2":        "Amplia sua atuação para o Direito Penal, passando a acompanhar clientes em"
                                   " delegacias, audiências de custódia e processos criminais. Desenvolve expertise"
                                   " em medidas cautelares e sustentações orais perante o Tribunal.",
        "timeline_ano_3":         "2021",
        "timeline_titulo_3":      "Direito Trabalhista e Previdenciário",
        "timeline_desc_3":        "Consolida sua presença nas áreas trabalhista e previdenciária, assessorando"
                                   " tanto empregados quanto empresas em relações de trabalho, além de auxiliar"
                                   " segurados na obtenção de benefícios junto ao INSS.",
        "timeline_ano_4":         "2022 — hoje",
        "timeline_titulo_4":      "Escritório próprio em Juiz de Fora",
        "timeline_desc_4":        "Funda o escritório Lucas Evaristo Advocacia e Consultoria, com sede no centro"
                                   " de Juiz de Fora — MG. Passa a atender clientes de forma personalizada e direta,"
                                   " com acompanhamento próximo em todas as fases processuais e foco em soluções"
                                   " jurídicas eficazes e humanizadas.",
    },
    "footer": {
        "links_titulo":        "Links Rápidos",
        "horarios_titulo":     "Horários",
        "horario_semana":      "Segunda a Sexta: 09:00 - 18:00",
        "horario_fim":         "Sábado e Domingo: Fechado",
        "endereco":            "Av. Brasil, 1975 - Loja 1991 - Centro, Juiz de Fora - MG, 36060-010",
        "conecte_se_titulo":   "CONECTE-SE",
        "conecte_se_instagram": "https://www.instagram.com/advlucasevaristo",
    },
}