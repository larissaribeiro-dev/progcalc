import pytest

from progcalc.errors import CalcError
from progcalc.tokenizer import Kind, tokenize


def kinds(text):
    return [t.kind for t in tokenize(text)]


def test_simple_expression():
    assert kinds("2 + 3") == [Kind.NUMBER, Kind.OPERATOR, Kind.NUMBER, Kind.END]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("42", 42),
        ("0xFF", 255),
        ("0b1010", 10),
        ("0o17", 15),
        ("1_000", 1000),
        ("0b1111_0000", 240),
        ("3.5", 3.5),
    ],
)
def test_number_formats(text, expected):
    assert tokenize(text)[0].value == expected


def test_two_character_operators_win_over_single():
    texts = [t.text for t in tokenize("2 ** 3 // 4 << 1")]
    assert texts == ["2", "**", "3", "//", "4", "<<", "1", ""]


def test_unknown_character_reports_position():
    with pytest.raises(CalcError) as info:
        tokenize("2 + $")
    assert info.value.pos == 4


def test_hex_prefix_without_digits_is_rejected():
    with pytest.raises(CalcError):
        tokenize("0x_")
