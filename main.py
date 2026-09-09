import os
import time
from src.network_manager import Network
from src.router import Router
from src.engine import Engine
from src.oracle import OfflineOracle
from src.fault_tolerance import FaultTester

def load_demands_from_file(filepath):
    # Load demands from text file / Carrega demandas do arquivo de texto
    demands = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                d_id, src, dst, size = line.split()
                demands.append({'id': int(d_id), 'src': src, 'dst': dst, 'size': float(size)})
    return demands

def get_max_utilization(net):
    # Find the most utilized link / Encontra o enlace mais utilizado
    max_util = 0.0
    for u, v, data in net.graph.edges(data=True):
        util_rate = data['utilization'] / data['capacity']
        if util_rate > max_util:
            max_util = util_rate
    return max_util

def simulate_routing(topo_file, demands, use_smart, label):
    # Setup and simulate routing / Configura e simula o roteamento
    print(f"\n--- {label} ---")
    net = Network()
    net.load_topology_from_file(topo_file)
    router = Router(net)
    engine = Engine(net, router)
    
    total_hops = 0
    for d in demands:
        path, reason = engine.process_demand(d['src'], d['dst'], d['size'], use_smart=use_smart)
        if path:
            total_hops += len(path) - 1
            print(f"Demand/Demanda {d['id']}: Route/Rota {path} | Reason/Motivo: {reason}")
        else:
            print(f"Demand/Demanda {d['id']}: [-] Rejected/Rejeitada | Reason/Motivo: {reason}")
            
    # Calculate and print metrics / Calcula e imprime métricas
    max_util = get_max_utilization(net)
    print(f"-> Summary/Resumo {label}: {total_hops} total hops/saltos totais | Critical Load/Carga Crítica: {max_util*100:.1f}%")
    return net, router, engine

def main():
    # Start timer / Inicia cronômetro
    start_time = time.time()
    
    # Setup paths / Configura caminhos
    topo_file = os.path.join('data', 'rede.txt')
    demands_file = os.path.join('data', 'demandas.txt')

    # Load base network / Carrega rede base
    net_base = Network()
    net_base.load_topology_from_file(topo_file)
    topology_list = [(u, v, data['capacity']) for u, v, data in net_base.graph.edges(data=True)]
    demands = load_demands_from_file(demands_file)

    # 1. Oracle (Offline) / Ótimo Offline
    print("--- 1. Offline Optimum / Ótimo Offline (Oráculo) ---")
    oracle = OfflineOracle(topology_list, demands)
    is_possible, best_score = oracle.solve()
    print(f"Perfect score / Score perfeito: {best_score} hops/saltos" if is_possible else "Mathematically impossible / Matematicamente impossível.")

    # 2. Baseline (Shortest Path) / Piso de Comparação (Caminho Mínimo)
    simulate_routing(topo_file, demands, use_smart=False, label="2. Baseline / Piso de Comparação")
    
    # 3. Smart Router / Roteador Inteligente
    net_smart, router_smart, engine_smart = simulate_routing(topo_file, demands, use_smart=True, label="3. Heuristic Router / Roteador Heurístico")

    # 4. Link Failure Test / Teste de Falhas
    tester = FaultTester(net_smart, router_smart, engine_smart)
    tester.run_link_failure_test()
    
    # Print execution time / Imprime tempo de execução
    print(f"\nExecution Time / Tempo de Execução: {time.time() - start_time:.4f} seconds/segundos")

if __name__ == "__main__":
    main()