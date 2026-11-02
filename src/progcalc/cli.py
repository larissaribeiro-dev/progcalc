"""Interface de linha de comando: modo direto e modo interativo (REPL)."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .bases import represent
from .calculator import calculate
from .errors import CalcError
from .evaluator import Number

HELP = """\
Operadores (do menor para o maior nível de precedência):
  |   ^   &   <<  >>   +  -   *  /  //  %   - + ~ (unários)   **

Números aceitos:
  255   0xFF   0b1111_1111   0o377   3.14

Extras:
  ans     resultado da última conta
  ajuda   mostra esta mensagem
  sair    fecha a calculadora
"""

PROMPT = "progcalc> "


def format_result(value: Number, bits: int) -> str:
    rep = represent(value, bits)
    rows = [("dec", rep.dec), ("hex", rep.hex), ("bin", rep.bin), ("oct", rep.oct)]
    lines = [f"  {label}  {text}" for label, text in rows if text]
    if rep.note:
        lines.append(f"  ({rep.note})")
    return "\n".join(lines)


def format_error(text: str, error: CalcError) -> str:
    message = f"erro: {error.message}"
    if error.pos is None:
        return message
    return f"{text}\n{' ' * error.pos}^\n{message}"


def repl(bits: int) -> int:
    print(f"progcalc {__version__}. Digite 'ajuda' para ver os comandos.")
    variables: dict[str, Number] = {}

    while True:
        try:
            line = input(PROMPT).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not line:
            continue
        if line.lower() in ("sair", "exit", "quit"):
            return 0
        if line.lower() in ("ajuda", "help"):
            print(HELP)
            continue

        try:
            value = calculate(line, variables)
        except CalcError as error:
            print(format_error(line, error))
            continue

        variables["ans"] = value
        print(format_result(value, bits))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="progcalc",
        description="Calculadora para programadores: bitwise, hex, binário e octal.",
    )
    parser.add_argument(
        "expression",
        nargs="*",
        help="expressão a calcular. Sem argumentos, abre o modo interativo.",
    )
    parser.add_argument(
        "--bits",
        type=int,
        choices=(8, 16, 32, 64),
        default=32,
        help="largura usada para mostrar negativos em complemento de dois (padrão: 32)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not args.expression:
        return repl(args.bits)

    text = " ".join(args.expression)
    try:
        value = calculate(text)
    except CalcError as error:
        print(format_error(text, error), file=sys.stderr)
        return 1

    print(format_result(value, args.bits))
    return 0
