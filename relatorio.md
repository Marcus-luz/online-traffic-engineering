# Relatório de Implementação e Resultados

## O que foi construído
Implementei um sistema de roteamento em grafos utilizando duas abordagens comparativas:
1. **Ótimo Offline (Oráculo):** Modelado como *Multi-Commodity Flow* via Programação Linear (PuLP/CBC), retornando a quantidade mínima de saltos matematicamente possível.
2. **Roteador Online (Heurística Primal-Dual):** O custo de um cabo cresce exponencialmente à medida que sua utilização se aproxima da capacidade máxima (fórmula base: `exp(3.0 * taxa_de_uso)`). O algoritmo é 100% online, conforme validado pelos testes automatizados de embaralhamento.

## Resultados do Desafio 1 (Trade-off: Saltos vs. Carga)
A execução de todo o *pipeline* se dá pelo comando `python main.py`, que avalia dois cenários (Base e Escala).

**Cenário Base:**
* **Ótimo Offline:** Inviabilidade matemática confirmada (não cabe tudo).
* **Piso de Comparação (Caminho Mínimo):** Alocou as demandas no menor caminho, mas estourou a capacidade de gargalo, rejeitando demandas massivamente e resultando em apenas 1 salto total (pois alocou apenas o primeiro pacote).
* **Roteador Heurístico:** Aceitou o dobro de tráfego, mitigando o congestionamento ao pagar o custo de 3 saltos totais (distância maior) para manter a carga crítica da rede em seguros 80.0%.
* **Tolerância a Falhas:** Após o roteamento, a heurística provou que a rede sobreviveu a 1/3 das falhas críticas de enlace.

**Cenário de Escala (100 Nós):**
Executado em topologia gerada de 100 nós e 50 demandas agressivas. O Oráculo Offline provou que a rede gerada é matematicamente incapaz de comportar 100% do tráfego (Infactível). O Roteador Heurístico lidou com a inviabilidade graciosamente, roteando o tráfego possível e espalhando a carga pelas rotas alternativas sem estourar limites físicos. O tempo de execução de toda a simulação (Offline + Baseline + Heurística + Teste de Falhas nas centenas de cabos) levou, em média, menos de `1.0 segundo` localmente.

## Desafio 2: O Pior Caso e o Teto Matemático
Construí uma topologia adversarial no arquivo `desafio2_pior_caso.py` contendo um caminho de 1 salto competindo contra um caminho de N saltos. Uma demanda "isca" preenche 95% do caminho direto, forçando a heurística a inflar o peso dinâmico.

* **O Afastamento Crescente:** A razão de erro (Saltos da Heurística / Saltos do Oráculo) cresce linearmente conforme o tamanho da rede aumenta, atingindo seu pior caso com **9.00x** de erro quando `N = 17`.
* **O Teto (Platô e Colapso):** Em `N = 18`, o erro colapsa instantaneamente de volta para **1.00x** (perfeição) e se mantém assim permanentemente. 
* **Argumentação:** Isso ocorre porque o peso de um único enlace superlotado (95%) tem um teto físico definido pela constante matemática `exp(3.0 * 0.95) ≈ 17.3`. Enquanto o desvio de N nós possuía um peso somado menor que 17.3, o algoritmo foi enganado. Assim que o desvio atingiu `N = 18` nós (peso acumulado 18), a heurística deduziu que dar a volta em 18 cidades é, matematicamente, mais "caro" do que pagar o pedágio de `17.3` do cabo direto lotado.

## O que não foi feito (Decisões de Design)
A simulação de Falha de Enlaces adota uma abordagem conservadora: ela trata o tráfego deslocado de um cabo caído como uma "demanda única agregada" entre os pontos *u* e *v*. Em um roteamento altamente fracionado, essa carga poderia ser pulverizada. Optei por esta abordagem para manter a heurística simples e fiel à regra de não dividir demandas avulsas.