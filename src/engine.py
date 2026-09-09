class Engine:
    def __init__(self, network, router):
        # Bind network and router / Vincula rede e roteador
        self.net = network
        self.router = router

    def process_demand(self, origin, destination, demand_size, use_smart=True):
        # Choose routing method / Escolhe método de roteamento
        if use_smart:
            path, reason = self.router.route_smart_path(origin, destination, demand_size)
        else:
            path = self.router.route_shortest_path(origin, destination)
            reason = "Naive shortest path / Caminho mínimo ingênuo."
        
        # Check if physical path exists / Verifica se existe caminho físico
        if not path:
            return False, "Physical routing failed / Falha de roteamento físico."

        # Validate capacity for ANY path / Valida capacidade para QUALQUER caminho
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            if self.net.get_remaining_capacity(u, v) < demand_size:
                return False, f"Rejected: Bottleneck on link {u}->{v} / Rejeitada: Gargalo excede limite no cabo {u}->{v}."

        # Allocate traffic / Aloca o tráfego
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            self.net.graph[u][v]['utilization'] += demand_size
        
        # Return allocated route and reason / Retorna rota alocada e justificativa
        return path, reason