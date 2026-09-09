import networkx as nx

class Network:
    def __init__(self):
        # Init directed graph / Inicializa grafo direcionado
        self.graph = nx.DiGraph()
        
    def load_topology(self, links_data):
        # Load links (u, v, capacity) / Carrega enlaces (u, v, capacidade)
        for u, v, capacity in links_data:
            self.graph.add_edge(u, v, capacity=capacity, utilization=0.0)
            
    def get_remaining_capacity(self, u, v):
        # Get free space / Obtém espaço livre
        edge = self.graph[u][v]
        return edge['capacity'] - edge['utilization']