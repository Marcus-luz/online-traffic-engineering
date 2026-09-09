import networkx as nx
import math
import json

class Router:
    def __init__(self, network_manager, config_path='config.json'):
        # Bind network and load config / Vincula rede e carrega configuração
        self.net = network_manager
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Load exponential penalty base / Carrega base da penalidade exponencial
        self.penalty_base = self.config.get("EXP_PENALTY_BASE", 3.0)

    def route_shortest_path(self, origin, destination):
        # Shortest path ignoring load / Caminho mínimo ignorando carga
        try:
            return nx.shortest_path(self.net.graph, origin, destination)
        except nx.NetworkXNoPath:
            return None

    def route_smart_path(self, origin, destination, demand_size):
        # Smart routing avoiding congestion / Roteamento inteligente evitando congestionamento
        reasoning = []
        for u, v, data in self.net.graph.edges(data=True):
            free_space = data['capacity'] - data['utilization']
            
            if free_space < demand_size:
                # Full link / Enlace lotado
                data['dynamic_weight'] = float('inf')
                reasoning.append(f"Link {u}->{v} no capacity / Cabo {u}->{v} sem capacidade.")
            else:
                # Exponential penalty for high usage / Penalidade exponencial por alto uso
                usage_rate = data['utilization'] / data['capacity']
                data['dynamic_weight'] = math.exp(self.penalty_base * usage_rate)
                
                # Log high usage links / Registra enlaces com alto uso
                if usage_rate > 0.5:
                    reasoning.append(f"{u}->{v} usage/uso {usage_rate*100:.0f}% (weight/peso {data['dynamic_weight']:.1f})")

        try:
            # Find path using dynamic weights / Encontra caminho usando pesos dinâmicos
            path = nx.shortest_path(self.net.graph, origin, destination, weight='dynamic_weight')
            reason_str = "Detour via / Desvio por: " + " | ".join(reasoning) if reasoning else "Ideal path free / Rota ideal livre."
            return path, reason_str
        except nx.NetworkXNoPath:
            return None, "No viable path / Rede sem caminhos viáveis."