"""Etapa 3: percorre a árvore e calcula o valor."""

from __future__ import annotations

import operator
from collections.abc import Callable, Mapping

from .errors import CalcError
from .parser import Binary, Node, Num, Unary, Var

Number = int | float

# Limites para a calculadora não travar com algo como 9 ** 9 ** 9.
MAX_EXPONENT = 10_000
MAX_SHIFT = 10_000

_ARITHMETIC: dict[str, Callable[[Number, Number], Number]] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "//": operator.floordiv,
    "%": operator.mod,
}

_BITWISE: dict[str, Callable[[int, int], int]] = {
    "&": operator.and_,
    "|": operator.or_,
    "^": operator.xor,
    "<<": operator.lshift,
    ">>": operator.rshift,
}


def evaluate(node: Node, variables: Mapping[str, Number] | None = None) -> Number:
    variables = variables or {}

    match node:
        case Num(value):
            return value
        case Var(name):
            if name not in variables:
                raise CalcError(f"variável desconhecida: {name}")
            return variables[name]
        case Unary(op, operand):
            return _unary(op, evaluate(operand, variables))
        case Binary(op, left, right):
            return _binary(op, evaluate(left, variables), evaluate(right, variables))

    raise CalcError("expressão inválida")


def _require_int(op: str, value: Number) -> int:
    if isinstance(value, float):
        raise CalcError(f"o operador {op!r} só funciona com números inteiros")
    return value


def _unary(op: str, value: Number) -> Number:
    if op == "-":
        return -value
    if op == "+":
        return value
    return ~_require_int(op, value)


def _divide(a: Number, b: Number) -> Number:
    if b == 0:
        raise CalcError("divisão por zero")
    # Devolve inteiro quando a divisão é exata, para 10 / 2 mostrar 5 e não 5.0
    if isinstance(a, int) and isinstance(b, int) and a % b == 0:
        return a // b
    return a / b


def _power(a: Number, b: Number) -> Number:
    if isinstance(b, int) and abs(b) > MAX_EXPONENT:
        raise CalcError(f"expoente grande demais (máximo {MAX_EXPONENT})")
    if a == 0 and b < 0:
        raise CalcError("divisão por zero")
    result = a**b
    if isinstance(result, complex):
        raise CalcError("o resultado seria um número complexo")
    return result


def _shift_and_bitwise(op: str, a: Number, b: Number) -> int:
    left = _require_int(op, a)
    right = _require_int(op, b)
    if op in ("<<", ">>"):
        if right < 0:
            raise CalcError("deslocamento negativo")
        if right > MAX_SHIFT:
            raise CalcError(f"deslocamento grande demais (máximo {MAX_SHIFT})")
    return _BITWISE[op](left, right)


def _binary(op: str, a: Number, b: Number) -> Number:
    try:
        if op in _BITWISE:
            return _shift_and_bitwise(op, a, b)
        if op == "/":
            return _divide(a, b)
        if op == "**":
            return _power(a, b)
        if op in ("//", "%") and b == 0:
            raise CalcError("divisão por zero")
        return _ARITHMETIC[op](a, b)
    except OverflowError:
        raise CalcError("o resultado é grande demais") from None
