"""Erros próprios da calculadora."""

from __future__ import annotations


class CalcError(Exception):
    """Erro causado pela entrada do usuário (sintaxe, divisão por zero, etc).

    `pos` guarda a posição do caractere problemático, quando existe,
    para que a interface consiga apontar exatamente onde está o erro.
    """

    def __init__(self, message: str, pos: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.pos = pos
