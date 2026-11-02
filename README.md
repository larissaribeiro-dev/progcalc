# progcalc

[![CI](https://github.com/larissaribeiro-dev/progcalc/actions/workflows/ci.yml/badge.svg)](https://github.com/larissaribeiro-dev/progcalc/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Calculadora de linha de comando para programadores. Entende operações bitwise, aceita números em binário, hexadecimal e octal, e mostra cada resultado em todas as bases. Negativos aparecem em complemento de dois, do jeito que o hardware guarda.

O mais interessante é que não usa `eval()`. A expressão passa por um tokenizador, um parser descendente recursivo e um avaliador de árvore, escritos do zero e sem dependências externas.

```
$ progcalc "0xFF & 0b1010"
  dec  10
  hex  0xA
  bin  0b1010
  oct  0o12

$ progcalc -10
  dec  -10
  hex  0xFFFF_FFF6
  bin  0b1111_1111_1111_1111_1111_1111_1111_0110
  oct  0o37777777766
  (complemento de dois em 32 bits)
```

## Recursos

- Operadores aritméticos: `+  -  *  /  //  %  **`
- Operadores bitwise: `&  |  ^  ~  <<  >>`
- Parênteses e precedência idêntica à do Python
- Literais em decimal, `0x` (hex), `0b` (binário), `0o` (octal), com separador `_`
- Saída em decimal, hexadecimal, binário e octal, agrupada em blocos de 4
- Complemento de dois configurável (`--bits 8|16|32|64`)
- Modo interativo com a variável `ans` (resultado anterior)
- Mensagens de erro que apontam a posição exata do problema
- Proteção contra entradas que travariam o programa, como `9 ** 9 ** 9`

## Instalação

Requer Python 3.10 ou superior.

```bash
git clone https://github.com/larissaribeiro-dev/progcalc.git
cd progcalc
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

## Uso

### Uma expressão por vez

```bash
progcalc "1 << 10"
progcalc "0xDEADBEEF >> 16"
progcalc --bits 8 "~0x0F"
```

### Modo interativo

Execute `progcalc` sem argumentos:

```
$ progcalc
progcalc 0.1.0. Digite 'ajuda' para ver os comandos.
progcalc> 0xDEADBEEF >> 16
  dec  57005
  hex  0xDEAD
  bin  0b1101_1110_1010_1101
  oct  0o157255
progcalc> ans & 0xFF
  dec  173
  hex  0xAD
  bin  0b1010_1101
  oct  0o255
progcalc> 1 / 0
erro: divisão por zero
```

### Erros apontam a posição

```
$ progcalc "2 + $"
2 + $
    ^
erro: caractere inesperado: '$'
```

### Como biblioteca

```python
from progcalc import calculate

calculate("(1 << 8) - 1")   # 255
calculate("ans * 2", {"ans": 21})   # 42
```

## Precedência dos operadores

Do menor para o maior, igual ao Python:

| Nível | Operadores           | Associatividade |
|-------|----------------------|-----------------|
| 1     | `\|`                 | esquerda        |
| 2     | `^`                  | esquerda        |
| 3     | `&`                  | esquerda        |
| 4     | `<<` `>>`            | esquerda        |
| 5     | `+` `-`              | esquerda        |
| 6     | `*` `/` `//` `%`     | esquerda        |
| 7     | `-x` `+x` `~x`       | direita         |
| 8     | `**`                 | direita         |

## Como funciona

A expressão passa por três etapas independentes:

```
"2 + 3 * 4"
     |
     v
 tokenizer.py   texto  ->  [2] [+] [3] [*] [4]
     |
     v
 parser.py      tokens ->  árvore (AST)
     |                         +
     |                        / \
     |                       2   *
     |                          / \
     |                         3   4
     v
 evaluator.py   árvore ->  14
     |
     v
 bases.py       14     ->  dec, hex, bin, oct
```

Cada módulo tem uma responsabilidade só e pode ser testado sozinho. Um passo a passo detalhado, com um exemplo sendo processado em cada etapa, está em [docs/COMO_FUNCIONA.md](docs/COMO_FUNCIONA.md).

### Estrutura do projeto

```
progcalc/
├── src/progcalc/
│   ├── tokenizer.py     # texto -> tokens
│   ├── parser.py        # tokens -> árvore
│   ├── evaluator.py     # árvore -> valor
│   ├── bases.py         # valor -> dec/hex/bin/oct
│   ├── calculator.py    # junta as etapas
│   ├── cli.py           # linha de comando e modo interativo
│   └── errors.py        # exceção própria
├── tests/
├── docs/
├── .github/workflows/ci.yml
└── pyproject.toml
```

## Decisões de projeto

**Por que não usar `eval()`?** Ele executa qualquer código Python, então uma calculadora baseada nele permitiria `__import__("os").system(...)`. Escrever o parser dá controle total sobre o que é aceito e permite erros claros.

**Por que descendente recursivo?** É a técnica mais direta para ler gramáticas de expressões e o código fica quase idêntico à tabela de precedência. Cada nível chama o seguinte, que é o que garante `2 + 3 * 4 = 14`.

**Por que os limites de expoente e deslocamento?** O Python tem inteiros de tamanho ilimitado. Sem limite, `1 << 10**9` tentaria alocar centenas de megabytes. Os limites (10.000) ficam em constantes no topo de `evaluator.py`.

**Por que `10 / 2` mostra `5` e não `5.0`?** Em uma calculadora de programador, o resultado de uma divisão exata costuma ser usado em máscaras e deslocamentos, que só aceitam inteiros.

## Testes

```bash
pip install -e ".[dev]"
pytest          # roda os testes e mostra a cobertura
ruff check .    # lint
```

Os testes incluem uma bateria que compara o resultado de cada expressão com o do próprio Python, usado como gabarito. A cobertura passa de 95%. O CI roda tudo no GitHub Actions nas versões 3.10 a 3.13.

## Roadmap

- [ ] Funções como `abs()`, `min()`, `max()` e `bin()`
- [ ] Variáveis definidas pelo usuário (`x = 0xFF`)
- [ ] Rotação de bits (`rol`, `ror`) respeitando `--bits`
- [ ] Histórico com setas no modo interativo
- [ ] Publicação no PyPI

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).
