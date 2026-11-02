import pytest

from progcalc import CalcError, calculate

# Expressões só com inteiros: o próprio Python serve de gabarito.
ORACLE_CASES = [
    "1 + 2 * 3",
    "(1 + 2) * 3",
    "10 - 4 - 3",
    "2 ** 3 ** 2",
    "-2 ** 2",
    "2 ** -1",
    "17 // 5",
    "-17 // 5",
    "17 % 5",
    "-17 % 5",
    "0xFF & 0b1010",
    "0xF0 | 0x0F",
    "0b1100 ^ 0b1010",
    "1 << 10",
    "1024 >> 3",
    "~0",
    "~5 & 0xFF",
    "1 | 2 ^ 3 & 4",
    "1 + 2 << 3",
    "- - 4",
    "(1 << 8) - 1",
    "0x1F + 0b11 * 0o7",
    "100 / 4",
]


@pytest.mark.parametrize("text", ORACLE_CASES)
def test_matches_python(text):
    assert calculate(text) == eval(text)  # noqa: S307 (apenas entradas fixas do teste)


def test_exact_division_returns_int():
    result = calculate("10 / 2")
    assert result == 5
    assert isinstance(result, int)


def test_inexact_division_returns_float():
    assert calculate("7 / 2") == 3.5


def test_float_arithmetic():
    assert calculate("1.5 + 2.25") == 3.75


def test_ans_variable():
    assert calculate("ans * 2", {"ans": 21}) == 42


@pytest.mark.parametrize(
    "text",
    [
        "1 / 0",
        "1 // 0",
        "1 % 0",
        "0 ** -1",
        "1.5 & 1",
        "~1.5",
        "1 << -1",
        "1 << 999999",
        "2 ** 999999",
        "(-8) ** 0.5",
        "foo + 1",
        "9.0 ** 999",
        "0x",
        "12abc",
    ],
)
def test_errors_are_reported_as_calc_error(text):
    with pytest.raises(CalcError):
        calculate(text)


def test_deep_nesting_does_not_crash():
    with pytest.raises(CalcError):
        calculate("(" * 5000 + "1" + ")" * 5000)
