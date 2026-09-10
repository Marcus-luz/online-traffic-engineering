# Desafio de Roteamento Online e Engenharia de Tráfego

Resolve os dois desafios (roteamento online avaliado contra o ótimo offline, e o
pior caso da própria solução) no mesmo repositório.

📄 **Relatório completo:** [`relatorio.md`](relatorio.md) — o que foi construído,
os números de cada cenário, e o que ficou de fora ou foi ajustado. Todo número
que aparece lá sai de um dos comandos desta página (Requisito 12).

⚠️ **Um requisito não é atendido integralmente:** no cenário de 100 nós, o
Requisito 2 (razão contra o ótimo offline exato) usa uma aproximação em vez do
ótimo exato — motivo e trade-off explícito em
[`relatorio.md` → "Requisito não atendido integralmente"](relatorio.md#requisito-não-atendido-integralmente-trade-off-explícito).

## ⚙️ Instalação e Execução

Python 3.10+, dependências fixadas em `requirements.txt`.

1. Clone o repositório e acesse a pasta:
   ```
   git clone <URL_DO_REPO>
   cd online-traffic-engineering
   ```
2. Crie e ative um ambiente virtual:
   ```
   `python -m venv venv`
   `source venv/bin/activate`   # Windows (PowerShell): `.\venv\Scripts\activate`
   ```
3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## 🚀 Como Avaliar

Cada desafio tem um único comando que refaz a avaliação inteira, do dado aos
números (Requisito 11):

* **Desafio 1 — Base + Escala de 100 Nós:**
  `python main.py`
* **Desafio 2 — Pior caso e teto matemático (mesmo repositório do Desafio 1):**
  `python desafio2_pior_caso.py`
* **Testes automatizados (prova de onlineness e de rejeição por inviabilidade):**
  `python -m unittest tests/test_engine.py`
* **Bônus, fora da avaliação principal — cenários de impacto (flash crowd, elefante/rato):**
  `python testes_impacto.py`
* **Reprodução dos dados de escala** (opcional — os arquivos já estão versionados em `data/`; rode só se quiser reconferir que a seed reproduz os mesmos arquivos):
  `python gerar_escala.py`

## ✅ Requisitos do Desafio 1 — onde cada um é atendido

| # | Requisito | Onde |
|---|---|---|
| 1 | Online de verdade, sem olhar demandas futuras | `src/engine.py::Engine.process_demand` decide uma demanda por vez; `tests/test_engine.py::test_embaralhamento_prova_online` embaralha a ordem de chegada e prova que o resultado muda |
| 2 | Ótimo offline no repo; razão como número | `src/oracle.py` (PuLP/CBC); razão (tráfego e saltos) impressa a cada rodada de `main.py`. **Ressalva:** no cenário base é o ótimo exato; no cenário de escala é uma cota superior fracionária, não o ótimo exato — ver trade-off explícito no relatório |
| 3 | Caminho mínimo como piso de comparação | `src/router.py::Router.route_shortest_path`, rodado antes da heurística em `main.py` |
| 4 | Duas medidas sempre juntas | Cada rodada imprime saltos totais **e** carga crítica (utilização do enlace mais carregado). Métrica de custo de caminho escolhida: **saltos (hop count)** |
| 5 | Falha de enlace, reportado em quantos dos \|E\| casos a rede aguenta | `src/fault_tolerance.py::FaultTester.run_link_failure_test`, roda para cada enlace e imprime "sobreviveu a X/\|E\|" |
| 6 | Inviabilidade dita explicitamente, com o ponto de aperto | `Engine.process_demand` rejeita a demanda e nomeia o enlace-gargalo; nunca devolve calada uma rota que estoura capacidade |
| 7 | Escala ≥100 nós, dentro de orçamento declarado | `data/rede_100_nos.txt` (100 nós, 196 enlaces, 50 demandas). Orçamento e medição: ver seção abaixo |
| 8 | Determinismo (mesma entrada, mesma saída) | Nenhuma aleatoriedade na decisão online; geração de dados usa `RANDOM_SEED` fixo em `config.json` |
| 9 | Topologia lida de arquivo | `src/network_manager.py::Network.load_topology_from_file` |
| 10 | Proveniência dos dados declarada | Seção "Proveniência de Dados" abaixo |
| 11 | Um comando só refaz a avaliação inteira | Ver "Como Avaliar" acima |
| 12 | Todo número do relatório sai desse comando | Nenhum número em `relatorio.md` foi calculado à mão — todos são cópia da saída de `main.py` ou `desafio2_pior_caso.py` |
| 13 | Explica por que aquela rota, não só qual | `main.py` imprime rota + motivo para cada demanda; `Router.route_smart_path` monta a explicação a partir dos enlaces da própria rota escolhida (não da rede inteira) |
| 14 | Peso/limite/corte é configuração, não constante escondida | `config.json` — ver tabela de configuração abaixo |
| 15 | Roda localmente, sem chamada paga de API | Só bibliotecas locais (`networkx`, `PuLP` + solver CBC embutido). Nenhuma API externa |
| 16 | Instalação/testes/licença/repo | Ver "Instalação" acima; testes com `python -m unittest tests/test_engine.py`; `LICENSE` MIT; repositório público |

## ⏱️ Orçamento de tempo e medição (Requisito 7)

**Orçamento declarado:** até 60 segundos para o cenário de escala (100 nós,
196 enlaces, 50 demandas), rodando localmente em hardware comum, sem GPU.

**Como medi:** `main.py` cronometra com `time.time()` do início ao fim do
pipeline completo (Oráculo + Baseline + Heurística + Teste de Falhas para os
dois cenários) e imprime `Tempo Total de Execução` ao final. Na prática, a
execução completa leva cerca de **1,3 segundos** nesta máquina — bem dentro do
orçamento.

## 🔧 Configuração (Requisito 14)

Nenhum peso, limite ou ponto de corte está escondido no código — tudo o que
funciona como esse papel está em `config.json`:

| Chave | Efeito | Usado em |
|---|---|---|
| `EXP_PENALTY_BASE` | Base da penalidade exponencial de carga no roteador online (`exp(base * uso)`) | `src/router.py` |
| `RANDOM_SEED` | Semente para a geração determinística da topologia e das demandas de escala | `gerar_escala.py` |
| `ORACLE_EXACT_MAX_VARS` | Nº de variáveis de rota acima do qual o oráculo troca do MILP exato para a relaxação linear | `src/oracle.py` |

## 📁 Proveniência de Dados e Topologias Externas (Requisito 10)

* **Dados Menores (`rede.txt`):** fabricados manualmente para simular gargalos diretos.
* **Escala 100 Nós (`rede_100_nos.txt`):** gerados deterministicamente pelo script `gerar_escala.py`, usando a seed de `config.json`.
* **⚠️ Topologias Externas (Aviso de Grafos):** a arquitetura assume grafos direcionados estritos (cada linha do `.txt` define um único sentido `A -> B`). Para roteamento bidirecional, as duas vias precisam estar declaradas como duas linhas separadas no arquivo.

## 🎯 Ótimo Offline: MILP exato vs. relaxação linear

Roteamento indivisível por demanda (cada demanda usa um único caminho) é um
*Unsplittable Multicommodity Flow*, problema NP-difícil. O oráculo
(`src/oracle.py`) resolve o MILP binário exato quando o número de variáveis de
rota (`demandas × enlaces`) está até `ORACLE_EXACT_MAX_VARS` — cobre o cenário
base. Acima disso — caso do cenário de 100 nós, com ~9.800 variáveis — ele
troca automaticamente para uma relaxação linear (variáveis contínuas), que
resolve em segundos e devolve uma cota superior fracionária válida, em vez de
travar tentando resolver um MILP intratável nessa escala. Qual método foi
usado em cada rodada é sempre impresso, e o `relatorio.md` explica a diferença
e como ler a razão em cada caso.
