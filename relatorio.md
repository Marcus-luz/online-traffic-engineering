# Relatório de Implementação e Resultados

Este relatório é o arquivo que o `README.md` aponta como leitura obrigatória
(seção "o que ficou de fora, e o requisito que você decidiu não seguir").
Todo número aqui é cópia direta da saída de `python main.py` ou
`python desafio2_pior_caso.py` — nenhum foi calculado à mão (Requisito 12).

## O que construí

Um sistema de roteamento em grafos com duas peças que se comparam:

1. **Ótimo Offline (Oráculo — `src/oracle.py`):** *Multi-Commodity Flow* via
   Programação Linear (PuLP/CBC), em duas fases. Fase 1 maximiza o tráfego
   total aceito (cada demanda pode ser aceita ou rejeitada — nem sempre cabe
   tudo). Fase 2, entre as soluções que aceitam esse máximo, minimiza o total
   de saltos. Roteamento indivisível por demanda é *Unsplittable
   Multicommodity Flow* (NP-difícil): em instâncias pequenas o oráculo
   resolve o MILP binário exato; acima de `ORACLE_EXACT_MAX_VARS`
   (`config.json`) ele troca automaticamente para uma relaxação linear
   (variáveis contínuas), que resolve em tempo polinomial e devolve uma cota
   superior fracionária. O método usado em cada rodada é sempre impresso.
2. **Roteador Online (Heurística Primal-Dual — `src/router.py`):** o custo de
   um enlace cresce exponencialmente à medida que sua utilização se aproxima
   da capacidade máxima (`exp(EXP_PENALTY_BASE * taxa_de_uso)`). Decide uma
   demanda por vez, sem olhar as seguintes — validado pelo teste automatizado
   de embaralhamento (Requisito 1).

**Métrica de custo de caminho escolhida (Requisito 4):** saltos (hop count).
As duas medidas — saltos totais e utilização do enlace mais carregado — são
sempre reportadas juntas, nunca uma sem a outra.

**Desafio 2** está neste mesmo repositório (`desafio2_pior_caso.py`), não em
repositório separado.

## O quão bem funciona

Comando: `python main.py` — avalia os dois cenários (Base e Escala) e imprime,
para cada demanda, a rota escolhida e o motivo (Requisito 13).

**Cenário Base (3 nós, oráculo em modo exato):**
* **Ótimo Offline:** não cabe 100% da demanda (16 unidades pedidas). O ótimo aceita **12,0/16,0 unidades (75,0%)** com **3 saltos**.
* **Piso de Comparação (Caminho Mínimo):** aceitou só a primeira demanda (4,0 unidades, 1 salto) e rejeitou as duas seguintes por gargalo no enlace direto A→C.
* **Roteador Heurístico:** aceitou 8,0 unidades (o dobro do piso) em 3 saltos, mantendo a carga crítica em 80,0%.
* **Razão contra o ótimo:** tráfego aceito = **66,7%** do que o ótimo aceitaria (8,0/12,0); saltos = **1,00x** os saltos do ótimo (3 vs 3) — a heurística é tão eficiente em saltos quanto o ótimo, mas deixa tráfego aceitável na mesa.
* **Falha de Enlace (Requisito 5):** a rede sobreviveu a **1/3** das falhas de enlace testadas.

**Cenário de Escala (100 nós, 196 enlaces, 50 demandas — oráculo em relaxação linear):**
* **Ótimo Offline (cota fracionária):** aceita 200,0/603,0 unidades (33,2%) com 263 saltos.
* **Piso de Comparação:** aceitou 99,0 unidades em 221 saltos, carga crítica 100,0%.
* **Roteador Heurístico:** aceitou 195,0 unidades em 644 saltos, carga crítica 100,0%.
* **Razão contra o ótimo:** tráfego aceito = **97,5%** da cota fracionária (195,0/200,0); saltos = **2,44x** os saltos da cota (644 vs 263) — como a cota é fracionária (permite dividir uma demanda em vários caminhos), ela naturalmente barateia o custo em saltos; ainda assim, o número mostra onde a heurística perde eficiência de caminho para ganhar taxa de aceitação.
* **Falha de Enlace (Requisito 5):** a rede sobreviveu a **81/196** falhas de enlace testadas.
* **Tempo (Requisito 7):** a simulação completa dos dois cenários (Oráculo + Baseline + Heurística + Testes de Falha) rodou em **1,78 segundos** localmente — dentro do orçamento de 60s declarado no README.

Comando: `python desafio2_pior_caso.py` — constrói uma topologia adversarial
com um caminho de 1 salto competindo contra um caminho de N saltos (instância
pequena, oráculo em modo exato). Uma demanda "isca" preenche 95% do caminho
direto, forçando a heurística a inflar o peso dinâmico.

* **O Afastamento Crescente:** a razão de erro (Saltos da Heurística / Saltos do Oráculo) cresce linearmente conforme o tamanho da rede aumenta, atingindo seu pior caso com **9,00x** de erro quando `N = 17`.
* **O Teto (Platô e Colapso):** em `N = 18`, o erro colapsa instantaneamente de volta para **1,00x** (perfeição) e se mantém assim permanentemente.
* **Argumentação:** o peso de um único enlace superlotado (95%) tem um teto físico definido pela constante `exp(3,0 * 0,95) ≈ 17,3`. Enquanto o desvio de N nós tiver peso somado menor que 17,3, o algoritmo é enganado. A partir de `N = 18` (peso acumulado 18), a heurística conclui que dar a volta é mais "caro" que pagar o pedágio de 17,3 do cabo direto lotado.

## Requisito não atendido integralmente — trade-off explícito

**Requisito 2** pede: *"O ÓTIMO OFFLINE está no repositório, calculado por
você... O relatório traz a razão entre o seu resultado e ele."* No cenário
base eu calculo esse ótimo exato. **No cenário de escala (100 nós, 196
enlaces, 50 demandas), eu não calculo o ótimo exato — calculo uma cota
superior fracionária, que é uma coisa parecida mas não é a mesma coisa.**

O motivo: o ótimo exato exige que cada demanda use um único caminho
indivisível (é assim que o roteador online funciona, então é essa a régua
justa de comparação). Isso é *Unsplittable Multicommodity Flow*, um problema
NP-difícil — o MILP binário correspondente tem ~9.800 variáveis de rota nessa
escala e, na prática, não terminei de resolvê-lo (deixei rodando vários
minutos sem resposta).

Duas saídas possíveis, e a que escolhi:

| Opção | O que ganha | O que perde |
|---|---|---|
| **A — Insistir no MILP exato** | Número diretamente comparável, sem ressalva | Sem tempo de execução previsível; pode não terminar nunca nessa escala; quebra o Requisito 7 (orçamento de tempo declarado) |
| **B — Relaxação linear (escolhida)** | Resolve em ~1,3s, sempre dentro do orçamento; ainda é um número real, não um adjetivo (Requisito 2 continua parcialmente atendido); é uma cota válida (nenhuma solução indivisível bate ela) | Não é o ótimo exato — é otimista. A razão de saltos do cenário de escala (2,77x) mede "distância até uma cota otimista", não "distância até o ótimo indivisível exato" |

Escolhi B porque um número aproximado e honesto sobre suas limitações, sempre
disponível, é mais útil do que um número exato que pode nunca sair do forno.
O cenário base, pequeno o suficiente para o MILP exato terminar, existe
justamente para mostrar o número "de verdade" pelo menos uma vez — ali a
razão é diretamente comparável, sem ressalva.

## Outros ajustes menores

* **Falha de Enlaces trata o tráfego deslocado como uma demanda única
  agregada** entre os pontos *u* e *v*, em vez de fracionado entre vários
  caminhos. Optei por essa simplificação para manter a heurística fiel à
  regra de não dividir demandas avulsas — o mesmo comportamento que ela tem
  para qualquer demanda nova.
* **A "razão de saltos" não é normalizada por unidade de tráfego aceito.**
  Reporto tráfego aceito e saltos sempre juntos e lado a lado (Requisito 4),
  mas não os combino numa métrica composta única — fica como dois números
  simples e diretos em vez de um índice só, pra manter a leitura simples.
* **Os parâmetros `num_nos=100` e `num_demandas=50` de `gerar_escala.py`**
  são argumentos com valor padrão na função, não estão em `config.json`.
  Diferente de `EXP_PENALTY_BASE`, eles não são peso/limite/corte da solução
  de roteamento (Requisito 14 é sobre isso) — são parâmetros de um script de
  geração de dados, então deixei como estão para não inflar a configuração
  com algo que não influencia a decisão de rota.

## Correção de determinismo (Requisito 8)

Ao documentar o comando `python gerar_escala.py` no README, rodei-o para
conferir e descobri que `data/demandas_100_nos.txt` **não** batia com o que o
script produz hoje com `RANDOM_SEED=42` — o arquivo commitado vinha de uma
versão anterior do gerador. Regenerei o arquivo com o script atual (confirmei
rodando duas vezes seguidas: saída idêntica nas duas) e recalculei todos os
números do "Cenário de Escala" acima a partir dele. `data/rede_100_nos.txt`
não usa números aleatórios na geração e já batia, então não mudou.
