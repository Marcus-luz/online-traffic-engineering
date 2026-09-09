import networkx as nx
import copy

class FaultTester:
    def __init__(self, network, router, engine):
        # Bind core components / Vincula os componentes centrais
        self.net = network
        self.router = router
        self.engine = engine

    def run_link_failure_test(self):
        # Run failure simulation for EACH edge / Roda simulação de falha para CADA enlace
        edges = list(self.net.graph.edges(data=True))
        total_edges = len(edges)
        survived_cases = 0

        print(f"\n--- Link Failure Test / Teste de Falha de Enlace ({total_edges} edges/enlaces) ---")
        
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
            
            # Try to route the lost traffic (Unpacking tuple) / Tenta rotear o tráfego perdido (Desempacotando tupla)
            path, reason = self.engine.process_demand(u, v, traffic_to_relocate, use_smart=True)
            
            if path:
                survived_cases += 1
                print(f"  [+] Edge {u}->{v} failed/falhou. Traffic/Tráfego ({traffic_to_relocate}) successfully relocated via / realocado via: {path}")
            else:
                print(f"  [-] Edge {u}->{v} failed/falhou. Network CRASHED / Rede CAIU (Cannot relocate / Não foi possível realocar {traffic_to_relocate} units).")

            # Restore original network / Restaura rede original
            self.net.graph = original_graph

        print(f"Result/Resultado: Network survived / Rede sobreviveu a {survived_cases}/{total_edges} link failures / falhas de enlace.")
        return survived_cases, total_edges