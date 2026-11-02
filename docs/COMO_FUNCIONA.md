# Como o progcalc funciona, passo a passo

Este documento segue uma única expressão por todas as etapas: `2 + 3 * 4`.

A ideia central é que o computador não "enxerga" uma conta como nós. Para ele, a entrada é só uma sequência de caracteres. Para calcular, precisamos reconhecer as partes (etapa 1), entender a estrutura (etapa 2) e só então calcular (etapa 3).

## Etapa 1: Tokenizador (`tokenizer.py`)

Quebra o texto em pedaços com significado, chamados tokens.

```
"2 + 3 * 4"  ->  NUMBER(2)  OPERATOR(+)  NUMBER(3)  OPERATOR(*)  NUMBER(4)  END
```

Isso é feito com uma expressão regular que reconhece, nesta ordem: espaços, números, nomes, operadores e parênteses. A ordem importa por dois motivos:

- `0xFF` precisa ser testado antes de `0`, senão leríamos o número `0` seguido do nome `xFF`.
- `**` precisa ser testado antes de `*`, senão `2 ** 3` viraria dois asteriscos separados.

Cada token também guarda a posição onde apareceu no texto. É isso que permite mostrar o `^` apontando o erro.

## Etapa 2: Parser (`parser.py`)

Recebe os tokens em fila e monta uma árvore que representa a estrutura da conta.

```
        +
       / \
      2   *
         / \
        3   4
```

A multiplicação ficou mais "embaixo" na árvore porque será calculada primeiro. Isso é a precedência de operadores aparecendo na estrutura.

Como o parser consegue isso? Cada nível de precedência é uma função que chama a do nível acima (mais forte). Em `_parse_level`:

1. O nível `+ -` pede ao nível `* / // %` para ler uma "parcela".
2. O nível `* / // %` lê `3`, vê o `*`, lê `4` e devolve `3 * 4`.
3. De volta ao nível `+ -`, ele já tem `2` à esquerda e `3 * 4` à direita, e monta a soma.

Quem fica mais perto das folhas da árvore ganha prioridade. Os níveis estão listados na constante `_LEVELS`, do mais fraco ao mais forte.

Os parênteses entram em `_parse_atom`: ao ver `(`, o parser volta para o nível mais fraco e lê uma expressão inteira até achar o `)`. Por isso `(2 + 3) * 4` funciona.

### Associatividade

- `10 - 3 - 2` deve ser `(10 - 3) - 2 = 5`. O `while` em `_parse_level` vai empilhando operações à esquerda.
- `2 ** 3 ** 2` deve ser `2 ** (3 ** 2) = 512`. Em `_parse_power`, depois do `**` chamamos a regra de novo, o que agrupa à direita.

## Etapa 3: Avaliador (`evaluator.py`)

Percorre a árvore de baixo para cima:

```
evaluate(+)
  evaluate(2)        -> 2
  evaluate(*)
    evaluate(3)      -> 3
    evaluate(4)      -> 4
    3 * 4            -> 12
  2 + 12             -> 14
```

Um `match` separa os quatro tipos de nó: número, variável, operação unária e operação binária. Aqui também ficam as regras de negócio: divisão por zero, bitwise só com inteiros, limites de expoente e deslocamento.

## Etapa 4: Formatação (`bases.py`)

Pega o 14 e produz as quatro representações.

Para números negativos, usamos o complemento de dois. Em 8 bits, o `-1` é guardado como `11111111`. A conta é `valor & (2**bits - 1)`: a máscara descarta os bits acima da largura escolhida e sobra o padrão de bits que o hardware usaria.

## Etapa 5: Interface (`cli.py`)

Liga tudo ao terminal. O modo direto calcula uma expressão e sai. O modo interativo é um laço que lê uma linha, calcula e imprime, guardando o último resultado em `ans`.

Todos os erros previstos são `CalcError`. A interface captura só esse tipo, então um bug real do programa continua aparecendo como erro de verdade em vez de ser escondido.

## Para estudar mais

Se quiser se aprofundar nesse assunto, os termos para pesquisar são: análise léxica, gramática livre de contexto, parser descendente recursivo, árvore sintática abstrata (AST) e complemento de dois. São temas das disciplinas de Compiladores e Arquitetura de Computadores.
