from progcalc.bases import represent


def test_positive_number():
    rep = represent(255)
    assert rep.dec == "255"
    assert rep.hex == "0xFF"
    assert rep.bin == "0b1111_1111"
    assert rep.oct == "0o377"
    assert rep.note == ""


def test_binary_is_padded_to_nibbles():
    assert represent(5).bin == "0b0101"


def test_hex_is_grouped_by_four_digits():
    assert represent(0xDEADBEEF).hex == "0xDEAD_BEEF"


def test_negative_uses_twos_complement():
    rep = represent(-1, bits=8)
    assert rep.hex == "0xFF"
    assert rep.bin == "0b1111_1111"
    assert "complemento de dois" in rep.note


def test_negative_32_bits():
    assert represent(-10).hex == "0xFFFF_FFF6"


def test_negative_too_big_for_width_falls_back_to_signed():
    rep = represent(-129, bits=8)
    assert rep.hex == "-0x81"
    assert rep.note == ""


def test_float_only_has_decimal():
    rep = represent(3.5)
    assert rep.dec == "3.5"
    assert rep.hex == rep.bin == rep.oct == ""
