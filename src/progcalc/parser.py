"""Etapa 2: transforma os tokens em uma árvore (AST) respeitando a precedência.

Parser descendente recursivo. Cada nível de _LEVELS é um nível de precedência,
do mais fraco (|) ao mais forte (* / // %). Acima deles vêm os operadores
unários e a potência, tratados por funções próprias.

    "2 + 3 * 4"  ->  Binary(+, Num(2), Binary(*, Num(3), Num(4)))
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import CalcError
from .tokenizer import Kind, Token

# Mesma ordem de precedência do Python.
_LEVELS: list[tuple[str, ...]] = [
    ("|",),
    ("^",),
    ("&",),
    ("<<", ">>"),
    ("+", "-"),
    ("*", "/", "//", "%"),
]
_UNARY_OPS = ("-", "+", "~")


@dataclass(frozen=True)
class Num:
    value: int | float


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Unary:
    op: str
    operand: Node


@dataclass(frozen=True)
class Binary:
    op: str
    left: Node
    right: Node


Node = Num | Var | Unary | Binary


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._index = 0

    def parse(self) -> Node:
        node = self._parse_level(0)
        token = self._peek()
        if token.kind is not Kind.END:
            raise CalcError(f"token inesperado: {token.text!r}", token.pos)
        return node

    # utilitários

    def _peek(self) -> Token:
        return self._tokens[self._index]

    def _advance(self) -> Token:
        token = self._tokens[self._index]
        self._index += 1
        return token

    def _at_operator(self, operators: tuple[str, ...]) -> bool:
        token = self._peek()
        return token.kind is Kind.OPERATOR and token.text in operators

    # regras da gramática

    def _parse_level(self, level: int) -> Node:
        if level == len(_LEVELS):
            return self._parse_unary()

        node = self._parse_level(level + 1)
        while self._at_operator(_LEVELS[level]):
            op = self._advance().text
            right = self._parse_level(level + 1)
            node = Binary(op, node, right)  # associatividade à esquerda
        return node

    def _parse_unary(self) -> Node:
        if self._at_operator(_UNARY_OPS):
            op = self._advance().text
            return Unary(op, self._parse_unary())
        return self._parse_power()

    def _parse_power(self) -> Node:
        base = self._parse_atom()
        if self._at_operator(("**",)):
            self._advance()
            # associativa à direita: 2 ** 3 ** 2 == 2 ** 9
            return Binary("**", base, self._parse_unary())
        return base

    def _parse_atom(self) -> Node:
        token = self._advance()

        if token.kind is Kind.NUMBER:
            assert token.value is not None
            return Num(token.value)
        if token.kind is Kind.NAME:
            return Var(token.text)
        if token.kind is Kind.LPAREN:
            node = self._parse_level(0)
            closing = self._advance()
            if closing.kind is not Kind.RPAREN:
                raise CalcError("faltou fechar o parêntese", closing.pos)
            return node

        if token.kind is Kind.END:
            raise CalcError("expressão incompleta", token.pos)
        raise CalcError(f"esperava um número ou '(', veio {token.text!r}", token.pos)


def parse(tokens: list[Token]) -> Node:
    return Parser(tokens).parse()
