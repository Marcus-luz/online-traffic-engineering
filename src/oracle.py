import pulp

class OfflineOracle:
    def __init__(self, topology, demands):
        self.topology = topology # List of links / Lista de enlaces
        self.demands = demands   # List of demands / Lista de demandas

    def solve(self):
        # Create minimization problem / Cria problema de minimização
        prob = pulp.LpProblem("Offline_Optimum", pulp.LpMinimize)

        # Variables: 1 if demand D uses link (u,v), 0 if not
        # Variáveis: 1 se a demanda D usa o cabo (u,v), 0 se não
        route_vars = {}
        for d in self.demands:
            for u, v, cap in self.topology:
                route_vars[(d['id'], u, v)] = pulp.LpVariable(f"route_{d['id']}_{u}_{v}", cat='Binary')

        # Objective: Minimize total hops / Objetivo: Minimizar total de saltos
        prob += pulp.lpSum([route_vars[(d['id'], u, v)] for d in self.demands for u, v, cap in self.topology])

        # Constraint 1: Link Capacity / Restrição 1: Capacidade do cabo
        for u, v, cap in self.topology:
            prob += pulp.lpSum([route_vars[(d['id'], u, v)] * d['size'] for d in self.demands]) <= cap, f"Cap_{u}_{v}"

        # Constraint 2: Flow Conservation (Waze math) / Restrição 2: Conservação de fluxo
        # What enters a node must leave, except at origin and destination
        nodes = set([u for u, v, c in self.topology] + [v for u, v, c in self.topology])
        for d in self.demands:
            for node in nodes:
                flow_out = pulp.lpSum([route_vars[(d['id'], u, v)] for u, v, c in self.topology if u == node])
                flow_in  = pulp.lpSum([route_vars[(d['id'], u, v)] for u, v, c in self.topology if v == node])
                
                if node == d['src']:
                    prob += (flow_out - flow_in == 1) # Origin / Origem
                elif node == d['dst']:
                    prob += (flow_out - flow_in == -1) # Destination / Destino
                else:
                    prob += (flow_out - flow_in == 0) # Middle nodes / Nós do meio

        # Solve silently / Resolve silenciosamente
        prob.solve(pulp.PULP_CBC_CMD(msg=False))
        
        # Output results / Retorna resultados
        if pulp.LpStatus[prob.status] == 'Optimal':
            return True, pulp.value(prob.objective) # Found perfect route / Achou rota perfeita
        else:
            return False, None # Mathematically impossible / Matematicamente impossível