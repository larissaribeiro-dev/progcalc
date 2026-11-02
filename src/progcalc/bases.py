"""Formata um resultado em decimal, hexadecimal, binário e octal."""

from __future__ import annotations

from dataclasses import dataclass

from .evaluator import Number


@dataclass(frozen=True)
class Representation:
    dec: str
    hex: str = ""
    bin: str = ""
    oct: str = ""
    note: str = ""


def _group(digits: str, size: int, pad: bool) -> str:
    """Separa os dígitos em blocos da direita para a esquerda: 11111111 -> 1111_1111."""
    if pad:
        digits = digits.zfill(-(-len(digits) // size) * size)
    blocks = [digits[max(0, end - size) : end] for end in range(len(digits), 0, -size)]
    return "_".join(reversed(blocks))


def represent(value: Number, bits: int = 32) -> Representation:
    """Monta as representações de `value`.

    Negativos que cabem em `bits` aparecem em complemento de dois, que é
    como o hardware realmente guarda o número.
    """
    if isinstance(value, float):
        return Representation(dec=format(value, ".12g"))

    note = ""
    sign = ""
    number = value
    bin_width = hex_width = 0

    if value < 0 and value >= -(1 << (bits - 1)):
        number = value & ((1 << bits) - 1)
        bin_width, hex_width = bits, bits // 4
        note = f"complemento de dois em {bits} bits"
    elif value < 0:
        sign = "-"
        number = -value

    bin_digits = format(number, "b").zfill(bin_width)
    hex_digits = format(number, "X").zfill(hex_width)

    return Representation(
        dec=str(value),
        hex=f"{sign}0x{_group(hex_digits, 4, pad=False)}",
        bin=f"{sign}0b{_group(bin_digits, 4, pad=True)}",
        oct=f"{sign}0o{number:o}",
        note=note,
    )
