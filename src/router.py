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
        # Precisa recalcular o peso de TODOS os enlaces pra achar o caminho mais
        # barato (Dijkstra precisa dos pesos da rede inteira).
        for u, v, data in self.net.graph.edges(data=True):
            free_space = data['capacity'] - data['utilization']

            if free_space < demand_size:
                # Full link / Enlace lotado
                data['dynamic_weight'] = float('inf')
            else:
                # Exponential penalty for high usage / Penalidade exponencial por alto uso
                usage_rate = data['utilization'] / data['capacity']
                data['dynamic_weight'] = math.exp(self.penalty_base * usage_rate)

        try:
            # Find path using dynamic weights / Encontra caminho usando pesos dinâmicos
            path = nx.shortest_path(self.net.graph, origin, destination, weight='dynamic_weight')
        except nx.NetworkXNoPath:
            return None, "No viable path / Rede sem caminhos viáveis."

        # A explicação olha só pros enlaces que a rota escolhida realmente usa
        # (Requisito 13: por que ESSA rota, não um raio-x da rede inteira).
        details = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            data = self.net.graph[u][v]
            usage_rate = data['utilization'] / data['capacity']
            if usage_rate > 0.5:
                details.append(
                    f"{u}->{v} a {usage_rate*100:.0f}% de uso (peso {data['dynamic_weight']:.1f})"
                )

        if details:
            reason_str = "Desvio por carga em: " + " | ".join(details)
        else:
            reason_str = "Rota livre, sem enlace acima de 50% de uso no caminho."

        return path, reason_str
