import pytest

from progcalc.errors import CalcError
from progcalc.parser import Binary, Num, Unary, parse
from progcalc.tokenizer import tokenize


def tree(text):
    return parse(tokenize(text))


def test_multiplication_binds_tighter_than_addition():
    assert tree("2 + 3 * 4") == Binary("+", Num(2), Binary("*", Num(3), Num(4)))


def test_parentheses_override_precedence():
    assert tree("(2 + 3) * 4") == Binary("*", Binary("+", Num(2), Num(3)), Num(4))


def test_subtraction_is_left_associative():
    assert tree("10 - 3 - 2") == Binary("-", Binary("-", Num(10), Num(3)), Num(2))


def test_power_is_right_associative():
    assert tree("2 ** 3 ** 2") == Binary("**", Num(2), Binary("**", Num(3), Num(2)))


def test_unary_minus_applies_after_power():
    assert tree("-2 ** 2") == Unary("-", Binary("**", Num(2), Num(2)))


def test_bitwise_precedence_matches_python():
    # & é mais forte que ^, que é mais forte que |
    expected = Binary("|", Num(1), Binary("^", Num(2), Binary("&", Num(3), Num(4))))
    assert tree("1 | 2 ^ 3 & 4") == expected


@pytest.mark.parametrize("text", ["", "2 +", "(2 + 3", "2 3", "* 4", "2 + + * 3"])
def test_invalid_syntax(text):
    with pytest.raises(CalcError):
        tree(text)
