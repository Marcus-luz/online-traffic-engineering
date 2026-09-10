import pulp
import json


class OfflineOracle:
    """
    Calcula o ótimo offline conhecendo a lista inteira de demandas.

    Permite rejeitar demandas quando elas não cabem todas na rede sem
    essa válvula o LP fica infactível em qualquer cenário congestionado e
    nunca produz um número comparável ao resultado do roteador online
    (Requisito 2: "a razão entre o seu resultado e ele. Um número, não um
    adjetivo.").

    A otimização é feita em duas fases:
      Fase 1 - maximiza o tráfego total aceito.
      Fase 2 - entre as soluções que aceitam esse máximo de tráfego,
               minimiza o total de saltos.
    """

    def __init__(self, topology, demands, config_path='config.json'):
        self.topology = topology
        self.demands = demands
        self.nodes = set([u for u, v, c in topology] + [v for u, v, c in topology])
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}
        self.exact_max_vars = config.get("ORACLE_EXACT_MAX_VARS", 500)

    def _build_model(self, sense, name, var_cat):
        prob = pulp.LpProblem(name, sense)

        if var_cat == 'Binary':
            bounds = {}
        else:
            bounds = {'lowBound': 0, 'upBound': 1}

        accept_vars = {
            d['id']: pulp.LpVariable(f"accept_{d['id']}", cat=var_cat, **bounds)
            for d in self.demands
        }
        route_vars = {}
        for d in self.demands:
            for u, v, cap in self.topology:
                route_vars[(d['id'], u, v)] = pulp.LpVariable(
                    f"route_{d['id']}_{u}_{v}", cat=var_cat, **bounds
                )

        # Restrição de capacidade / Capacity constraint
        for u, v, cap in self.topology:
            prob += pulp.lpSum(
                [route_vars[(d['id'], u, v)] * d['size'] for d in self.demands]
            ) <= cap, f"Cap_{u}_{v}"

        # Conservação de fluxo, condicionada à aceitação da demanda.
        for d in self.demands:
            for node in self.nodes:
                flow_out = pulp.lpSum(
                    [route_vars[(d['id'], u, v)] for u, v, c in self.topology if u == node]
                )
                flow_in = pulp.lpSum(
                    [route_vars[(d['id'], u, v)] for u, v, c in self.topology if v == node]
                )
                if node == d['src']:
                    prob += (flow_out - flow_in == accept_vars[d['id']])
                elif node == d['dst']:
                    prob += (flow_out - flow_in == -accept_vars[d['id']])
                else:
                    prob += (flow_out - flow_in == 0)

            for u, v, cap in self.topology:
                prob += route_vars[(d['id'], u, v)] <= accept_vars[d['id']]

        return prob, accept_vars, route_vars

    def solve(self):
        total_demand = sum(d['size'] for d in self.demands)
        n_route_vars = len(self.demands) * len(self.topology)

        if n_route_vars <= self.exact_max_vars:
            var_cat = 'Binary'
            method = 'exato (MILP)'
        else:
            # Unsplittable Multicommodity Flow exato é NP-difícil nessa escala;
            # relaxamos para LP (variáveis contínuas) pra continuar em tempo polinomial.
            var_cat = 'Continuous'
            method = 'relaxação linear (cota superior fracionária)'

        # --- Fase 1: maximizar tráfego aceito ---
        prob1, accept1, _ = self._build_model(pulp.LpMaximize, "Fase1_MaxAceito", var_cat)
        prob1 += pulp.lpSum([d['size'] * accept1[d['id']] for d in self.demands])
        prob1.solve(pulp.PULP_CBC_CMD(msg=False))
        best_accepted_traffic = pulp.value(prob1.objective) or 0.0

        # --- Fase 2: entre as soluções que aceitam o máximo, minimizar saltos ---
        prob2, accept2, route2 = self._build_model(pulp.LpMinimize, "Fase2_MinSaltos", var_cat)
        prob2 += pulp.lpSum(
            [d['size'] * accept2[d['id']] for d in self.demands]
        ) >= best_accepted_traffic - 1e-6
        prob2 += pulp.lpSum(
            [route2[(d['id'], u, v)] for d in self.demands for u, v, cap in self.topology]
        )
        prob2.solve(pulp.PULP_CBC_CMD(msg=False))
        total_hops = pulp.value(prob2.objective) or 0.0

        return {
            'accepted_traffic': best_accepted_traffic,
            'total_demand': total_demand,
            'total_hops': total_hops,
            'fully_feasible': best_accepted_traffic >= total_demand - 1e-6,
            'method': method,
        }
