# Sessão: benchmarks, medições e relatório empírico

**Ferramenta:** Claude Code · **Autor da sessão:** Lucas Kaue Ribeiro Weber
**Data:** 15/07/2026 · **Etapa do projeto:** estudo empírico (§7) e entregáveis escritos (§8)

Prompts do integrante, na ordem em que foram enviados, até a fase de geração
do documento final. Cada prompt vem com o contexto do que ele disparou, para
evidenciar o raciocínio e a iteração (critério de avaliação do §10).

---

## Prompt 1 — abertura da sessão

> *(anexos: captura de tela do download do dataset `wiki_ts_200M_uint64` em
> andamento + PDF do enunciado do projeto)*
>
> seguinte, eu preciso fazer a parte de relatórios/artigo deste trabalho,
> pode me ajudar, estou baixando o arquivo necessario, como faço isso?

**Contexto/resultado:** a ferramenta leu o enunciado (PDF), identificou a
instância do Grupo 7 (wiki, θ=0.6, mix 55:15:30, contagem, sorted, seed 7),
auditou o código existente do repositório contra as exigências do §7 e
apontou as lacunas de medição que impediriam o relatório: sem latência por
tipo de operação, sem varredura de θ, sem baseline ingênua, sem verificação
automática pelo oráculo, faixa de N insuficiente. Propôs um plano em 3
etapas (instrumentação → esqueletos dos documentos → execução com dados
reais) antes de escrever qualquer coisa.

## Prompt 2 — aprovação do plano

> sim

**Contexto/resultado:** autorização para executar o plano enquanto o
dataset baixava. Foram implementados: latências separadas por operação no
driver, BST ingênua iterativa como baseline, suíte de 26 cenários (escala
1k–10M × sorted/shuffle + varredura θ ∈ {0.0, 0.6, 0.99, 1.2}) com
verificação automática pelo oráculo, script de gráficos e os esqueletos do
relatório e da justificativa. Tudo validado com chaves sintéticas antes dos
dados reais (12 testes unitários + oráculo OK).

## Prompt 3 — questionamento de custo/execução

> tá, como vai funcionar? tu vai botar para rodar e vai comer tokens nesse
> meio tempo?

**Contexto/resultado:** iteração sobre o *processo*, não sobre o código —
esclarecemos que o benchmark rodaria em segundo plano na nossa máquina (sem
custo enquanto executa) e avaliamos alternativas (rodar manualmente e
retomar depois). Decisão: execução em background disparada pela ferramenta.

## Prompt 4 — validação de pré-condição

> verifica se o caminho do arquivo tá correto

**Contexto/resultado:** antes de rodar a suíte, conferimos o dataset:
caminho exato esperado pelo `benchmark_manager.py`, tamanho byte a byte
(1.600.000.008 = 8 de cabeçalho + 200M × 8), cabeçalho SOSD declarando 200M
de chaves e primeira chave plausível como timestamp (jan/2001, início da
Wikipédia). Download íntegro confirmado.

## Prompt 5 — autorização da execução

> pode

**Contexto/resultado:** suíte completa executada (~13 min): 26 cenários,
todos aprovados pelo oráculo (3.000.660 buscas conferidas na maior
execução, zero divergências). Na sequência, os gráficos foram gerados e o
relatório empírico e a justificativa foram preenchidos com os números reais
da máquina do grupo.

---

*Prompts posteriores desta mesma sessão (geração do .docx, conformidade com
o checklist da Pessoa 3, adaptação da apresentação ao formato de 5 min do
Moodle) constam do transcript completo exportado da ferramenta.*
