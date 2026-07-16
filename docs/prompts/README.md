# Dump organizado dos prompts (20% da nota)

O enunciado (§10) avalia "a qualidade dos prompts utilizados — enviar um dump
de todos os chats usados, de maneira organizada. A avaliação foca no
raciocínio e na iteração demonstrados, não no volume."

## Como organizar

Um arquivo por sessão de chat, nomeado `NN-tema.md` (ou `.pdf`/`.txt`
conforme a exportação da ferramenta), na ordem cronológica do projeto.
Preencher o índice abaixo à medida que os dumps forem adicionados.

## Índice das sessões

| # | Arquivo | Ferramenta | Tema / o que foi feito | Autor da sessão |
|---|---|---|---|---|
| 01 | `01-implementacao-avl.md` | [preencher] | Implementação inicial da AVL aumentada (insert/delete/rotações) | [preencher] |
| 02 | `02-workload-e-oraculo.md` | [preencher] | Integração com gen_workload e verificação | [preencher] |
| 03 | [`prompts.md`](prompts.md) | Claude Code | Instrumentação por operação, baseline BST ingênua, suíte de benchmarks (escala + θ), geração de gráficos, relatório empírico e justificativa — prompts anotados com contexto e resultado | Lucas |
| … | | | | |

> **Exportar a sessão do Claude Code (nº 03):** o transcript completo fica
> no histórico da ferramenta; exportar como texto/markdown e salvar nesta
> pasta. O mesmo vale para sessões de outros integrantes em outras
> ferramentas (ChatGPT: Settings → Data Controls → Export; Claude.ai:
> menu da conversa → compartilhar/exportar).

## O que o docente procura (checklist por sessão)

- [ ] O prompt inicial dá contexto e restrições (não só "faça X")?
- [ ] Há **iteração**: correções, pedidos de explicação, decisões revisadas?
- [ ] O grupo questiona/valida o que a ferramenta produz (ex.: rodar o
      oráculo, testes, conferir números)?
- [ ] Fica claro o que é autoria da ferramenta vs decisão do grupo?
      (obrigatório também identificar isso no relatório — regras §11)
