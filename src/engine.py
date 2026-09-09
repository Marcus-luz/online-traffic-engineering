class Engine:
    def __init__(self, network, router):
        # Bind network and router / Vincula rede e roteador
        self.net = network
        self.router = router

    def process_demand(self, origin, destination, demand_size, use_smart=True):
        # Choose routing method / Escolhe método de roteamento
        if use_smart:
            path = self.router.route_smart_path(origin, destination, demand_size)
        else:
            path = self.router.route_shortest_path(origin, destination)
        
        # Check if path is valid / Verifica se o caminho é válido
        if not path:
            return False # Failed to route / Falhou ao rotear

        # Check capacity for shortest path / Verifica capacidade no caminho curto
        if not use_smart:
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                if self.net.get_remaining_capacity(u, v) < demand_size:
                    return False # Capacity exceeded / Limite excedido

        # Allocate traffic / Aloca o tráfego
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            self.net.graph[u][v]['utilization'] += demand_size
        
        return path # Return allocated route / Retorna rota alocada