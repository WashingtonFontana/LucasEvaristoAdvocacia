"""
schemas/conteudo.py
───────────────────
Modelos Pydantic que validam os payloads dos endpoints de conteúdo.
Todos os campos são Optional para suportar atualizações parciais (PATCH).
"""

from typing import Optional
from pydantic import BaseModel


class HeroUpdate(BaseModel):
    welcome_text:  Optional[str] = None
    titulo_linha1: Optional[str] = None
    titulo_linha2: Optional[str] = None
    subtitulo:     Optional[str] = None
    btn_texto:     Optional[str] = None

    model_config = {"json_schema_extra": {"example": {
        "welcome_text":  "SEJA BEM-VINDO!",
        "titulo_linha1": "Lucas Evaristo -",
        "titulo_linha2": "Advocacia e Consultoria",
        "subtitulo":     "Soluções jurídicas eficazes",
        "btn_texto":     "ENTRE EM CONTATO",
    }}}


class CardUpdate(BaseModel):
    icone:     Optional[str] = None
    titulo:    Optional[str] = None
    descricao: Optional[str] = None


class EspecialidadesUpdate(BaseModel):
    subtitulo: Optional[str] = None
    titulo:    Optional[str] = None
    cards:     Optional[list[CardUpdate]] = None


class PerfilUpdate(BaseModel):
    titulo_secao: Optional[str] = None
    nome:         Optional[str] = None
    cargo:        Optional[str] = None


class ContatoUpdate(BaseModel):
    titulo:               Optional[str] = None
    placeholder_nome:     Optional[str] = None
    placeholder_telefone: Optional[str] = None
    placeholder_mensagem: Optional[str] = None
    btn_texto:            Optional[str] = None
    whatsapp_numero:      Optional[str] = None


class FooterUpdate(BaseModel):
    links_titulo:    Optional[str] = None
    horarios_titulo: Optional[str] = None
    horario_semana:  Optional[str] = None
    horario_fim:     Optional[str] = None
    endereco:        Optional[str] = None