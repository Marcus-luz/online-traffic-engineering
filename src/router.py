import networkx as nx
import math

class Router:
    def __init__(self, network_manager):
        # Bind network / Vincula a rede
        self.net = network_manager

    def route_shortest_path(self, origin, destination):
        # Shortest path ignoring load / Caminho mínimo ignorando carga
        try:
            return nx.shortest_path(self.net.graph, origin, destination)
        except nx.NetworkXNoPath:
            return None 

    def route_smart_path(self, origin, destination, demand_size):
        # Exponential Penalty Routing (Primal-Dual approach) 
        # Roteamento de Penalidade Exponencial (Abordagem Primal-Dual)
        for u, v, data in self.net.graph.edges(data=True):
            free_space = data['capacity'] - data['utilization']
            
            if free_space < demand_size:
                data['dynamic_weight'] = float('inf') # Full / Lotado
            else:
                # Literature standard: exponential growth / Padrão da literatura: crescimento exponencial
                # Base is an arbitrary constant (e.g., 2 or e) / A base é uma constante arbitrária (ex: 2 ou e)
                usage_rate = data['utilization'] / data['capacity']
                data['dynamic_weight'] = math.exp(3 * usage_rate) # e^(3 * usage)

        try:
            return nx.shortest_path(self.net.graph, origin, destination, weight='dynamic_weight')
        except nx.NetworkXNoPath:
            return None