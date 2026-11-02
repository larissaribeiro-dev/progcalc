"""Junta as três etapas: tokenizar, interpretar e calcular."""

from __future__ import annotations

from collections.abc import Mapping

from .errors import CalcError
from .evaluator import Number, evaluate
from .parser import parse
from .tokenizer import tokenize


def calculate(text: str, variables: Mapping[str, Number] | None = None) -> Number:
    """Calcula uma expressão e devolve o resultado.

    >>> calculate("0xFF & 0b1010")
    10
    """
    try:
        tree = parse(tokenize(text))
        return evaluate(tree, variables)
    except RecursionError:
        raise CalcError("expressão aninhada demais") from None
