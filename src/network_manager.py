import networkx as nx

class Network:
    def __init__(self):
        # Init directed graph / Inicializa grafo direcionado
        self.graph = nx.DiGraph()
        
    def load_topology_from_file(self, filepath):
        # Load links from txt / Carrega enlaces do arquivo txt
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip(): # Ignore empty lines / Ignora linhas vazias
                    u, v, capacity = line.split()
                    self.graph.add_edge(u, v, capacity=float(capacity), utilization=0.0)
            
    def get_remaining_capacity(self, u, v):
        # Get free space / Obtém espaço livre
        edge = self.graph[u][v]
        return edge['capacity'] - edge['utilization']