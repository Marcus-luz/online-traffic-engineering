# Desafio de Roteamento Online e Engenharia de Tráfego

Este projeto resolve o problema de roteamento online através de uma heurística Primal-Dual baseada em penalidade exponencial.

## ⚙️ Instalação e Execução

O projeto foi construído em Python e as dependências estão fixadas. Siga os passos exatos:

1. Clone o repositório e acesse a pasta:
   git clone <URL_DO_REPO>
   cd online-traffic-engineering-main

2. Crie e ative um ambiente virtual:
   python -m venv venv
   # No Linux/Mac: source venv/bin/activate
   # No Windows (PowerShell): .\venv\Scripts\activate

3. Instale as dependências:
   pip install -r requirements.txt

## 🚀 Como Avaliar (Comandos Únicos)

Toda a avaliação técnica ocorre através de comandos únicos.

* **Avaliação Geral (Desafio 1 - Base + Escala de 100 Nós):**
  `python main.py`
* **Testes Automatizados (Prova de Onlineness e Inviabilidade):**
  `python -m unittest tests/test_engine.py`
* **Análise Adversarial de Pior Caso e Teto (Desafio 2):**
  `python desafio2_pior_caso.py`
* **Cenários de Impacto (Flash Crowd e Elefante/Ratos):**
  `python testes_impacto.py`

## 📁 Proveniência de Dados e Topologias Externas
* **Dados Menores (`rede.txt`):** Fabricados manualmente para simular gargalos diretos.
* **Escala 100 Nós (`rede_100_nos.txt`):** Gerados deterministicamente pelo script `gerar_escala.py` utilizando seed controlada via `config.json`.
* **⚠️ Topologias Externas (Aviso de Grafos):** A arquitetura assume grafos direcionados estritos (cada linha do `.txt` define apenas um sentido `A -> B`). Para roteamento externo bidirecional, deve-se declarar as vias de ida e volta separadamente no arquivo.

## 🎯 Ótimo Offline: MILP exato vs. relaxação linear
Roteamento indivisível por demanda (cada demanda usa um único caminho) é um *Unsplittable Multicommodity Flow*, problema NP-difícil. O oráculo (`src/oracle.py`) resolve o MILP binário exato quando o número de variáveis de rota (`demandas × enlaces`) está até `ORACLE_EXACT_MAX_VARS` (config.json, padrão 500) — cobre o cenário base. Acima disso — caso do cenário de 100 nós, com ~9.800 variáveis — ele troca automaticamente para uma relaxação linear (variáveis contínuas), que resolve em segundos e devolve uma cota superior fracionária válida, em vez de travar tentando resolver um MILP intratável nessa escala. Qual método foi usado é sempre impresso e vai para o relatório (`relatorio.md` detalha a diferença).