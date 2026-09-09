import networkx as nx

class Router:
    def __init__(self, network_manager):
        # Bind network / Vincula a rede
        self.net = network_manager

    def route_shortest_path(self, origin, destination):
        # Shortest path ignoring load / Caminho mínimo ignorando carga
        try:
            return nx.shortest_path(self.net.graph, origin, destination)
        except nx.NetworkXNoPath:
            return None # No path / Sem caminho

    def route_smart_path(self, origin, destination, demand_size):
        # Smart routing avoiding congestion / Roteamento inteligente evitando congestionamento
        for u, v, data in self.net.graph.edges(data=True):
            free_space = data['capacity'] - data['utilization']
            
            if free_space < demand_size:
                data['dynamic_weight'] = float('inf') # Full / Lotado
            else:
                # Penalty for high usage / Penalidade por alto uso
                usage_rate = data['utilization'] / data['capacity']
                data['dynamic_weight'] = 1 / (1.001 - usage_rate)

        try:
            return nx.shortest_path(self.net.graph, origin, destination, weight='dynamic_weight')
        except nx.NetworkXNoPath:
            return None # No path / Sem caminho