from progcalc.cli import main


def test_one_shot_expression(capsys):
    assert main(["0xFF", "&", "0b1010"]) == 0
    out = capsys.readouterr().out
    assert "dec  10" in out
    assert "0xA" in out
    assert "0b1010" in out


def test_error_returns_nonzero_and_points_at_problem(capsys):
    assert main(["2 + $"]) == 1
    err = capsys.readouterr().err
    assert "erro:" in err
    assert "    ^" in err


def test_bits_option(capsys):
    assert main(["--bits", "8", "-1"]) == 0
    assert "0xFF" in capsys.readouterr().out


def test_repl_keeps_last_result(monkeypatch, capsys):
    inputs = iter(["6 * 7", "ans + 1", "sair"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "dec  42" in out
    assert "dec  43" in out


def test_repl_survives_errors(monkeypatch, capsys):
    inputs = iter(["1 / 0", "2 + 2", "sair"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "divisão por zero" in out
    assert "dec  4" in out
