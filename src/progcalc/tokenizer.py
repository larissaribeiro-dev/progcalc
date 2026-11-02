"""Etapa 1: transforma o texto digitado em uma lista de tokens.

Exemplo: "2 + 0xFF" vira [NUMBER(2), OPERATOR(+), NUMBER(255), END].
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto

from .errors import CalcError


class Kind(Enum):
    NUMBER = auto()
    NAME = auto()
    OPERATOR = auto()
    LPAREN = auto()
    RPAREN = auto()
    END = auto()


@dataclass(frozen=True)
class Token:
    kind: Kind
    text: str
    value: int | float | None
    pos: int


# A ordem importa: "0x1F" precisa ser testado antes de "0", e "**" antes de "*".
_PATTERN = re.compile(
    r"""
    (?P<space>\s+)
  | (?P<number>0[xX][0-9a-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+|\d[\d_]*(?:\.\d+)?)
  | (?P<name>[A-Za-z_]\w*)
  | (?P<op>\*\*|//|<<|>>|[-+*/%&|^~])
  | (?P<lparen>\()
  | (?P<rparen>\))
    """,
    re.VERBOSE,
)


def _to_number(lexeme: str, pos: int) -> int | float:
    clean = lexeme.replace("_", "")
    try:
        if clean[:2].lower() in ("0x", "0b", "0o"):
            return int(clean, 0)  # base 0 deixa o Python ler o prefixo
        if "." in clean:
            return float(clean)
        return int(clean)
    except ValueError:
        raise CalcError(f"número inválido: {lexeme!r}", pos) from None


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    while pos < len(text):
        match = _PATTERN.match(text, pos)
        if match is None:
            raise CalcError(f"caractere inesperado: {text[pos]!r}", pos)

        group = match.lastgroup
        lexeme = match.group()

        if group == "number":
            tokens.append(Token(Kind.NUMBER, lexeme, _to_number(lexeme, pos), pos))
        elif group == "name":
            tokens.append(Token(Kind.NAME, lexeme, None, pos))
        elif group == "op":
            tokens.append(Token(Kind.OPERATOR, lexeme, None, pos))
        elif group == "lparen":
            tokens.append(Token(Kind.LPAREN, lexeme, None, pos))
        elif group == "rparen":
            tokens.append(Token(Kind.RPAREN, lexeme, None, pos))
        # espaços em branco são apenas ignorados

        pos = match.end()

    tokens.append(Token(Kind.END, "", None, len(text)))
    return tokens
