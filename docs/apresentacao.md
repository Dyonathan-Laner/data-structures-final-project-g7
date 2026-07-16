# Roteiro da Apresentação (5 min, formato do Moodle) — Grupo 7

> Formato definido pelo docente (15/07): **5 minutos**, envio pelo Moodle,
> três blocos — (1) a estrutura de dados, (2) o que foi usado de LLM,
> (3) resultados e porquês. **Todos os integrantes devem apresentar** —
> sugestão de divisão: um bloco por integrante.
> Deck pronto: `docs/apresentacao.pptx`. Números: `benchmark_summary.csv`.

---

## Bloco 1 — A estrutura de dados (1–2 min) · Integrante A

**A intuição.** Uma árvore binária de busca guarda chaves ordenadas, mas só
é rápida se ficar *rasa*. A nossa é uma **AVL aumentada**: (1) rebalanceia
com rotações para garantir altura ≤ 1,44·log₂(n), e (2) cada nó carrega
campos extras — `size` e o agregado da subárvore — que transformam a árvore
numa estrutura de **estatísticas de ordem**.

**O que faz.** Além de `insert`/`delete`/`search`, responde em O(log n):
`rank(k)` (quantas chaves < k), `select(i)` (i-ésima menor) e
`range_agg(a,b)` — na nossa instância, **contagem** de chaves em [a,b],
resolvida como `rank(b+1) − rank(a)` (contagem é inversível por diferença
de prefixos; mín/máx não seriam).

**Qual a diferença / o ponto difícil.** Os campos aumentados precisam
continuar corretos **sob rotação**. A rotação move subárvores inteiras, então
só dois nós mudam — mas a ordem de recomputação importa: atualizamos o filho
antes da nova raiz local, senão `rank`/`select` passam a mentir *sem lançar
erro*. Esse é o bug silencioso que o enunciado descreve, e o oráculo detecta.

**O que utilizamos.** Python 3.14; dados reais do SOSD (`wiki`, timestamps
de edições da Wikipédia); carga gerada com θ=0.6, mix 55:15:30, inserção
**ordenada** (nossa instância), seed 7; oráculo transitivo do professor para
verificar corretude; uma BST ingênua deliberada como linha de base.

## Bloco 2 — O que usamos de LLM (1 min) · Integrante B

**Ferramentas.** [ajustar conforme as sessões reais do grupo — ex.: Claude
Code nas etapas de benchmark/relatório; demais sessões no dump em
`docs/prompts/`].

**Que tipo de prompt funcionou.** Prompts com contexto da *nossa instância*
(Grupo 7: wiki, contagem, sorted, seed 7) e critérios de aceitação
verificáveis — ex.: "instrumente o driver para medir latência **separada por
operação**", "a BST ingênua precisa ser iterativa porque com inserção
ordenada a profundidade chega a n". Iteramos: pedimos explicação dos
invariantes, questionamos resultados estranhos (a inserção sorted mais
rápida que shuffle) antes de aceitá-los.

**O que a LLM implementou vs o que ficou conosco.** A LLM ajudou em código:
driver de benchmark, baseline, automação da suíte e gráficos. A validação
nunca foi delegada: **toda** execução passa pelo oráculo do professor
(26/26 sem divergência, 3.000.660 buscas conferidas na maior) + 12 testes
unitários. A interpretação dos números e as decisões de projeto (por que
AVL, por que rank-diferença) são a parte que defendemos aqui.

**Transparência.** Dump completo e organizado dos chats em `docs/prompts/`,
com índice por sessão e autor.

## Bloco 3 — Resultados e porquês (1–2 min) · Integrante C

**1. O(log n) confirmado em 4 ordens de grandeza — mas com sotaque de
hardware.** Busca: 0,7 µs (10k ops) → 3,3 µs (10M ops). A forma é
logarítmica (altura 13 → 23), mas o custo *por nível* triplicou (52 → 145
ns). **Porquê:** a árvore de 4M de nós não cabe nos 16 MB de L3 — cada nível
vira um cache miss. Teoria dá a forma; o hardware dá a constante.

**2. Balancear é sobrevivência na nossa carga.** Nossa inserção é ordenada:
a BST sem balanceamento degenerou em corrente (altura = nº de chaves: 4.022
em 10k) e ficou **15,6× mais lenta** já em 10k operações. A AVL manteve
altura 23 com 4,08M de chaves — 5% acima do mínimo teórico log₂(n).

**3. O achado que não esperávamos.** Para a AVL, inserção ordenada foi
**mais rápida** que embaralhada (14,7 vs 20,8 µs, −29%). **Porquê:** toda
inserção desce pela espinha direita — caminho curto, fixo, quente no cache —
e as rotações empacotam a árvore quase perfeitamente. O caso "patológico" só
é patológico para quem não balanceia.

**4. Enviesamento ajuda o típico, não a cauda.** Com θ=1.2, o p50 da busca
caiu ~48% (chaves quentes, caminho em cache), mas o **p99 não se moveu** —
as chaves frias continuam pagando a descida inteira. Quem dimensiona por p99
não pode contar com a distribuição de acessos.

**Fechamento (1 frase).** Medimos, verificamos com o oráculo e conseguimos
explicar cada divergência entre teoria e prática — constantes do
interpretador, cache e GC — que é exatamente onde a estrutura aumentada
prova que vale o que promete.

---

## Perguntas prováveis do docente (para quem apresentar ao vivo)

**"O que acontece se removermos esta rotação?"**
→ Dois modos de falha: sem a rotação, a altura degenera (nosso caso sorted
vira O(n) — medido: 15,6× pior em 10k); sem o `_update` *dentro* da rotação,
`size`/`aggregate` ficam obsoletos e `rank`/`select`/`range_agg` respondem
errado **silenciosamente**. O oráculo pega os dois casos.

**"Por que seu p99 cresce aqui?"** (fig2)
→ Cauda = remoções de nó com dois filhos (segunda descida pelo sucessor),
cascatas de rebalanceamento e pausas do GC do CPython; e com N grande, cache
misses por nível empurram a curva inteira.

**"Por que sorted ficou mais rápido que shuffle na AVL?"**
→ Espinha direita: caminho curto/fixo/quente no cache; rotações concentradas
empacotam a árvore (altura 23 vs 26). Shuffle espalha os acessos.

**"Por que rank(b+1) − rank(a) em vez de descer somando agregados?"**
→ Contagem é inversível por diferença de prefixos; mín/máx não são. Reusa o
`size` (I3) que o `select` já exige — menos mecanismo novo para auditar sob
rotação.

**"O delete copia a chave do sucessor — não quebra o size no caminho?"**
→ Não: a remoção recursiva do sucessor atualiza todos os nós daquele caminho
na volta, e o nó que recebeu a chave é atualizado quando a recursão retorna.

**"Por que a BST ingênua é iterativa e a AVL recursiva?"**
→ Profundidade: AVL ≤ ~34 quadros em 10M chaves; a ingênua chega a
profundidade n (4.022 já em 10k) e estouraria o limite de recursão (~1000).
