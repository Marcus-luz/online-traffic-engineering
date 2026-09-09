import networkx as nx
import copy


class FaultTester:
    def __init__(self, network, router, engine):
        self.net = network
        self.router = router
        self.engine = engine

    def run_link_failure_test(self):
        # Run failure simulation for EACH edge / Roda simulação de falha para CADA enlace
        edges = list(self.net.graph.edges(data=True))
        total_edges = len(edges)
        survived_cases = 0

        print(f"\n--- Link Failure Test ({total_edges} edges) ---")
        
        for u, v, data in edges:
            traffic_to_relocate = data['utilization']
            
            # If edge is empty, network trivially survives / Se cabo está vazio, sobrevive trivialmente
            if traffic_to_relocate == 0:
                survived_cases += 1
                continue

            # Create a parallel reality (deep copy) / Cria uma realidade paralela
            test_graph = copy.deepcopy(self.net.graph)
            
            # Remove the failed edge / Remove o cabo que falhou
            test_graph.remove_edge(u, v)
            
            # Temporarily replace network graph / Substitui grafo temporariamente
            original_graph = self.net.graph
            self.net.graph = test_graph
            
            # Try to route the lost traffic / Tenta rotear o tráfego perdido
            path = self.engine.process_demand(u, v, traffic_to_relocate, use_smart=True)
            
            if path:
                survived_cases += 1
                print(f"  [+] Edge {u}->{v} failed. Traffic ({traffic_to_relocate}) successfully relocated via: {path}")
            else:
                print(f"  [-] Edge {u}->{v} failed. Network CRASHED (Cannot relocate {traffic_to_relocate} units).")

            # Restore original network / Restaura rede original
            self.net.graph = original_graph

        print(f"Result: Network survived {survived_cases}/{total_edges} link failures.")
        return survived_cases, total_edges