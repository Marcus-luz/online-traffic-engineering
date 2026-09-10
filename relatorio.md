# Relatório de Implementação e Resultados

## O que foi construído
Implementei um sistema de roteamento em grafos utilizando duas abordagens comparativas:
1. **Ótimo Offline (Oráculo):** Modelado como *Multi-Commodity Flow* via Programação Linear (PuLP/CBC), em duas fases — Fase 1 maximiza o tráfego total aceito (cada demanda pode ser aceita ou rejeitada, já que nem sempre cabe tudo); Fase 2, entre as soluções que aceitam esse máximo, minimiza o total de saltos. Roteamento indivisível por demanda é *Unsplittable Multicommodity Flow* (NP-difícil); em instâncias pequenas o oráculo resolve o MILP exato, e acima de `ORACLE_EXACT_MAX_VARS` (config.json) ele troca automaticamente para uma relaxação linear (variáveis contínuas), que resolve em tempo polinomial e devolve uma cota superior fracionária. O método usado em cada rodada é sempre reportado.
2. **Roteador Online (Heurística Primal-Dual):** O custo de um cabo cresce exponencialmente à medida que sua utilização se aproxima da capacidade máxima (fórmula base: `exp(3.0 * taxa_de_uso)`). O algoritmo é 100% online, conforme validado pelos testes automatizados de embaralhamento.

## Resultados do Desafio 1 (Trade-off: Saltos vs. Carga)
A execução de todo o *pipeline* se dá pelo comando `python main.py`, que avalia dois cenários (Base e Escala) e imprime, para cada demanda, a rota escolhida e o motivo (Requisito 13).

**Cenário Base (3 nós, MILP exato):**
* **Ótimo Offline:** não cabe 100% da demanda (16 unidades pedidas). O ótimo aceita **12,0/16,0 unidades (75,0%)** com **3 saltos**.
* **Piso de Comparação (Caminho Mínimo):** aceitou só a primeira demanda (4,0 unidades, 1 salto) e rejeitou as duas seguintes por gargalo no enlace direto A→C.
* **Roteador Heurístico:** aceitou 8,0 unidades (o dobro do piso) em 3 saltos, mantendo a carga crítica em 80,0%.
* **Razão contra o ótimo:** tráfego aceito = **66,7%** do que o ótimo aceitaria (8,0/12,0); saltos = **1,00x** os saltos do ótimo (3 vs 3) — a heurística é tão eficiente em saltos quanto o ótimo, mas deixa tráfego aceitável na mesa.
* **Tolerância a Falhas:** a rede sobreviveu a 1/3 das falhas de enlace.

**Cenário de Escala (100 nós, 196 enlaces, 50 demandas — relaxação linear):**
* **Ótimo Offline (cota fracionária):** aceita 200,0/629,0 unidades (31,8%) com 238 saltos.
* **Piso de Comparação:** aceitou 95,0 unidades em 267 saltos, carga crítica 96,0%.
* **Roteador Heurístico:** aceitou 194,0 unidades em 660 saltos, carga crítica 100,0%.
* **Razão contra o ótimo:** tráfego aceito = **97,0%** da cota fracionária (194,0/200,0); saltos = **2,77x** os saltos da cota (660 vs 238) — como a cota é fracionária (permite dividir uma demanda em vários caminhos), ela naturalmente barateia o custo em saltos; ainda assim, o número mostra onde a heurística perde eficiência de caminho para ganhar taxa de aceitação.
* **Tolerância a Falhas:** a rede sobreviveu a **79/196** falhas de enlace testadas.
* **Tempo:** a simulação completa dos dois cenários (Oráculo + Baseline + Heurística + Testes de Falha) rodou em **1,27 segundos** localmente.

## Desafio 2: O Pior Caso e o Teto Matemático
Construí uma topologia adversarial no arquivo `desafio2_pior_caso.py` contendo um caminho de 1 salto competindo contra um caminho de N saltos (instância pequena, oráculo roda em modo exato). Uma demanda "isca" preenche 95% do caminho direto, forçando a heurística a inflar o peso dinâmico.

* **O Afastamento Crescente:** a razão de erro (Saltos da Heurística / Saltos do Oráculo) cresce linearmente conforme o tamanho da rede aumenta, atingindo seu pior caso com **9,00x** de erro quando `N = 17`.
* **O Teto (Platô e Colapso):** em `N = 18`, o erro colapsa instantaneamente de volta para **1,00x** (perfeição) e se mantém assim permanentemente.
* **Argumentação:** o peso de um único enlace superlotado (95%) tem um teto físico definido pela constante `exp(3,0 * 0,95) ≈ 17,3`. Enquanto o desvio de N nós tiver peso somado menor que 17,3, o algoritmo é enganado. A partir de `N = 18` (peso acumulado 18), a heurística conclui que dar a volta é mais "caro" que pagar o pedágio de 17,3 do cabo direto lotado.

## O que não foi feito / limitações conhecidas
* **Falha de Enlaces:** trata o tráfego deslocado de um cabo caído como uma "demanda única agregada" entre os pontos *u* e *v*, em vez de fracionar. Optei por essa simplificação para manter a heurística fiel à regra de não dividir demandas avulsas.
* **Cota do cenário de escala é fracionária, não o ótimo indivisível exato.** O MILP exato (unsplittable) para 50 demandas em 196 enlaces (~9.800 variáveis de rota) não terminou em minutos de busca — é um problema NP-difícil nessa escala. A relaxação linear usada no lugar é uma cota superior válida (nenhuma solução indivisível pode ser melhor que ela), mas não é necessariamente atingível por um roteamento que não fraciona demandas; por isso a razão de saltos no cenário de escala (2,77x) deve ser lida como "distância até uma cota otimista", não como "distância até o ótimo indivisível exato". O cenário base, por ser pequeno, ainda resolve o MILP exato — ali a razão é diretamente comparável.
* **A "razão de saltos" mistura acréscimo por aceitar mais tráfego com acréscimo por caminho pior.** Reportamos tráfego aceito e saltos separadamente (Requisito 4 pede as duas medidas sempre juntas), mas não normalizamos saltos por unidade de tráfego aceito — ficou como um número simples e direto em vez de uma métrica composta, para manter a leitura simples.
