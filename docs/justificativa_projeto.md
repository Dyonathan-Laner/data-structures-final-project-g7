# Justificativa de Projeto — Árvore AVL Aumentada

**Projeto Final de Estruturas de Dados — Grupo 7**
(wiki, θ=0.6, mix 55:15:30, range_agg = contagem, ordem sorted, seed 7)

---

## 1. Por que uma AVL (e não rubro-negra ou treap)

A escolha entre os três balanceamentos permitidos considerou três critérios:
a carga do grupo, a garantia de pior caso e o custo de implementação correta.

| Critério | AVL | Rubro-negra | Treap |
|---|---|---|---|
| Altura garantida | ≤ 1,44·log₂(n) (a mais baixa) | ≤ 2·log₂(n) | O(log n) apenas **em esperança** (randomizada) |
| Custo de inserção | O(log n), ≤ 2 rotações | O(log n), ≤ 2 rotações | O(log n) esperado |
| Custo de remoção | O(log n), até O(log n) rotações | O(log n), ≤ 3 rotações | O(log n) esperado |
| Complexidade de implementação | média (4 casos de rotação) | alta (casos de recoloração + rotação na remoção) | baixa, mas exige prioridade aleatória por nó |
| Manutenção dos campos aumentados | localizada nas rotações e no caminho de volta | idem, mas com mais casos a auditar | idem |

**Decisão.** A carga do Grupo 7 é **55% inserções com ordem `sorted`** — o
caso que mais estressa balanceamento — e **30% buscas**. A AVL é a estrutura
mais rígida das três: mantém a menor altura, o que favorece exatamente a
operação mais frequente depois da inserção (busca). A rubro-negra toleraria
árvores até 2× mais altas para economizar rotações que, na nossa medição,
não são o gargalo (o custo por nível em Python domina — ver relatório
empírico, §5). O treap foi descartado por oferecer apenas garantia
probabilística: com inserção ordenada, um azar nas prioridades produz
regiões localmente degeneradas, e a defesa de corretude passaria a depender
de um argumento probabilístico mais frágil.

**Custo medido da alternativa descartada "não balancear":** a BST ingênua
sob a nossa ordem de inserção degenera para altura = n (4.022 níveis com 10k
operações — uma corrente) e ficou **15,6× mais lenta** já nessa escala
(61,1 µs vs 3,9 µs por operação; relatório empírico, §6), com o fator
crescendo linearmente com n. Esse é o custo, medido na nossa máquina, de
abrir mão do rebalanceamento. O contraponto honesto também foi medido: sob
inserção **aleatória** a ingênua é 2,8–4,9× mais rápida que a AVL na faixa
testada, porque evita todo o custo de manutenção — mas a carga do Grupo 7
não é aleatória, e a garantia de pior caso é exatamente o que se compra com
o balanceamento.

## 2. Invariantes da árvore aumentada

A estrutura mantém, para **todo nó** `x`, quatro invariantes:

- **I1 (ordem de busca).** Toda chave na subárvore esquerda de `x` é menor que
  `x.key`; toda chave na subárvore direita é maior. (Chaves duplicadas são
  ignoradas na inserção, então as chaves são distintas.)
- **I2 (balanceamento AVL).** `|altura(x.left) − altura(x.right)| ≤ 1`, com
  `x.height = 1 + max(altura(x.left), altura(x.right))` correto.
- **I3 (tamanho).** `x.size = 1 + size(x.left) + size(x.right)` — o número de
  nós da subárvore de `x`.
- **I4 (agregado).** `x.aggregate` é o agregado de contagem da subárvore.
  Para o Grupo 7 (contagem), `x.aggregate = x.size` por definição.

Sobre esses invariantes se apoiam as consultas:

- `rank(k)` desce a árvore somando `size(left) + 1` a cada vez que segue para
  a direita — correto se e somente se **I1 e I3** valem em todos os nós do
  caminho.
- `select(i)` usa `size(left)` para decidir o lado da descida — depende de
  **I1 e I3**.
- `range_agg(a, b) = rank(b+1) − rank(a)` conta as chaves em [a, b] — correto
  porque contagem é decomponível por diferença de ranks. (Para agregações
  não-inversíveis como mínimo/máximo seria preciso descer somando agregados
  de subárvores inteiras; com contagem, a formulação por rank é equivalente
  e reutiliza I3.)

## 3. Por que os invariantes se mantêm sob rotação

O ponto crítico do enunciado: *"uma rotação que esquece de recomputar um
agregado quebra todas as consultas subsequentes de forma silenciosa"*.

### 3.1 O argumento

Considere a rotação à esquerda em `x` com filho direito `y` (a rotação à
direita é o caso espelhado):

```
      x                 y
     / \               / \
    A   y     ==>     x   C
       / \           / \
      B   C         A   B
```

- **I1 se mantém** porque a rotação preserva o percurso em-ordem: em ambos os
  lados vale A < x < B < y < C. Nenhuma chave muda de lado relativo.
- **I2, I3 e I4 se mantêm** porque os únicos nós cujas subárvores mudaram são
  `x` e `y` — as subárvores A, B e C são movidas **inteiras**, com seus campos
  internos intactos. O código recomputa os campos exatamente nesses dois nós,
  **na ordem correta** (`_rotate_left` em `src/tree/avl_tree.py`):

  1. `_update(x)` primeiro — `x` agora é filho e seus novos filhos são A e B,
     ambos com campos já corretos;
  2. `_update(y)` depois — `y` agora é a nova raiz local e usa o `x.height`,
     `x.size` recém-recomputados.

  Se a ordem fosse invertida, `y` leria valores obsoletos de `x` e I3/I4
  quebrariam silenciosamente — exatamente o bug que o enunciado descreve.

### 3.2 Propagação no caminho de volta

`_insert` e `_delete` são recursivos e chamam `_update(node)` +
`_rebalance(node)` **em cada nó do caminho de volta à raiz** (busca do ponto
de modificação → folha → raiz). Assim, todo nó cuja subárvore pode ter mudado
tem altura/size/aggregate recomputados de baixo para cima, e I2 é restaurado
no primeiro nó desbalanceado encontrado. Nós fora do caminho de modificação
não têm suas subárvores alteradas, logo seus campos permanecem válidos.

### 3.3 Resposta à pergunta "e se removermos esta rotação?"

Sem a rotação (ou sem o `_update` dentro dela): I2 deixa de valer e a altura
cresce sem limite (no nosso caso sorted, degenera para O(n) — medido no
relatório, §4); ou, pior, I3/I4 ficam inconsistentes e `rank`/`select`/
`range_agg` passam a responder **valores errados sem lançar erro**. O oráculo
do projeto detecta o primeiro caso indiretamente (timeout) e o segundo
diretamente (divergência nas buscas após remoções).

## 4. O `range_agg` de contagem em detalhe

A instância do Grupo 7 define `range_agg(a, b)` = **quantas chaves estão no
intervalo [a, b]**. A implementação (`src/tree/avl_tree.py`) resolve isso em
duas chamadas a `rank`:

```python
def range_agg(self, start: int, end: int) -> int:
    if start > end:
        return 0
    return self.rank(end + 1) - self.rank(start)
```

### 4.1 Por que isso é correto

`rank(k)` devolve o número de chaves **estritamente menores** que `k`. Logo:

- `rank(end + 1)` = nº de chaves ≤ end (todas as menores que end+1);
- `rank(start)` = nº de chaves < start;
- a diferença conta exatamente as chaves `k` com start ≤ k ≤ end.

Exemplo com as chaves {10, 20, 30, 40}: `range_agg(15, 30)` =
`rank(31) − rank(15)` = 3 − 1 = **2** (as chaves 20 e 30). Casos de borda:
intervalo vazio (`start > end`) devolve 0; extremos inexistentes na árvore
funcionam porque `rank` não exige que a chave exista.

### 4.2 Como `rank` usa o campo aumentado

`rank(k)` desce da raiz até uma folha somando, a cada passo para a
**direita**, `size(left) + 1` — todos os nós da subárvore esquerda e o
próprio nó são menores que `k`. É uma única descida: **O(log n)**, e depende
apenas do invariante I3 (`size` correto em todos os nós do caminho). Como a
contagem da subárvore coincide com `size`, o agregado do Grupo 7 reusa o
mesmo campo que já sustenta `select` — uma fonte de verdade, dois usos.

### 4.3 Por que a formulação por diferença só funciona para contagem

Contagem é **inversível**: dá para "subtrair" o prefixo [<start] do prefixo
[≤end]. Agregações como **mínimo/máximo** (de outros grupos) não são — não
existe "min de [a,b] = min(≤b) ⊖ min(<a)". Esses grupos precisariam da
descida clássica que soma agregados de subárvores inteiramente contidas no
intervalo (ainda O(log n), mas com mais código e mais casos de borda). Essa
diferença é exatamente o que a nossa escolha de projeto explora: o par
(contagem, `rank`) dá a resposta com o mínimo de mecanismo novo.

## 5. Decisões de projeto e alternativas descartadas

| Decisão | Escolha | Alternativa descartada e custo |
|---|---|---|
| Balanceamento | AVL | Rubro-negra/treap — ver §1 |
| Agregado de contagem | `aggregate = size` (reuso de I3); `range_agg` por diferença de ranks | Campo separado somado na descida — código extra sem ganho, pois contagem coincide com size |
| Remoção | Por sucessor em-ordem (cópia da chave, remoção recursiva na subárvore direita) | Remoção por fusão — complica a manutenção de I2/I3 |
| Recursão vs iteração | Recursiva na AVL (profundidade ≤ 1,44·log₂(n) ≈ 34 para 10M chaves — segura) | Iterativa — necessária apenas na BST ingênua, onde a profundidade chega a n |
| Baseline | BST ingênua **iterativa** | Recursiva estouraria a pilha do Python com inserção ordenada (limite ~1000 quadros) |
| Derivação da carga | `gen_workload_1.py` com seed 7, `--max-load 2N` chaves reais do wiki | Carregar as 200M chaves — inviável em RAM e desnecessário: o universo efetivo é limitado por `--universe`/N |
| Medição | `perf_counter_ns` por operação, parse fora do laço | Cronometrar o laço inteiro — não permitiria percentis nem separação por operação |

## 6. Corretude verificada

- **Testes unitários** (`tests/test_avl_tree.py`) cobrem inserção, remoção,
  busca, rank, select e range_agg em casos pequenos e dirigidos.
- **Oráculo transitivo**: toda execução de benchmark é conferida com
  `gen_workload_1.py verify`. Como parte das buscas-miss mira chaves já
  removidas, uma remoção incorreta (inclusive um agregado esquecido numa
  rotação que altere a topologia) produz divergência detectável.
- Na maior execução (10M de operações, ordem sorted), **3.000.660 buscas
  foram conferidas com zero divergências**; as 26 execuções da suíte completa
  passaram no oráculo (coluna `oracle` de `benchmark_summary.csv`).
