import os
from src.network_manager import Network
from src.router import Router
from src.engine import Engine
from src.oracle import OfflineOracle
from src.fault_tolerance import FaultTester

def load_demands_from_file(filepath):
    # Load demands from txt / Carrega demandas do arquivo txt
    demands = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                d_id, src, dst, size = line.split()
                demands.append({'id': int(d_id), 'src': src, 'dst': dst, 'size': float(size)})
    return demands

def main():
    # 1. Setup paths / Configura caminhos dos arquivos
    topo_file = os.path.join('data', 'rede.txt')
    demands_file = os.path.join('data', 'demandas.txt')

    # 2. Load Data / Carrega Dados
    net = Network()
    net.load_topology_from_file(topo_file)
    
    # Extract list for Oracle / Extrai lista para o Oráculo
    topology_list = [(u, v, data['capacity']) for u, v, data in net.graph.edges(data=True)]
    demands = load_demands_from_file(demands_file)

    # 3. RUN ORACLE (Offline) / RODA ORÁCULO (Offline)
    print("--- Offline Optimum (Oracle) ---")
    oracle = OfflineOracle(topology_list, demands)
    is_possible, best_score = oracle.solve()
    if is_possible:
        print(f"[+] Perfect routing found! Score: {best_score} hops")
    else:
        print("[-] Mathematically impossible to route all demands!")
    print("")

    # 4. Init Online Routing / Inicia Roteamento Online
    router = Router(net)
    engine = Engine(net, router)

    print("--- Online Routing / Roteamento Online ---")
    for d in demands:
        print(f"Demand {d['id']}: {d['src']}->{d['dst']} (Size: {d['size']})")
        path = engine.process_demand(d['src'], d['dst'], d['size'], use_smart=True)
        if path:
            print(f"  [+] Route: {path}")
        else:
            print("  [-] Rejected (No capacity)")

    # 5. Fault Tolerance Test / Teste de Tolerância a Falhas
    tester = FaultTester(net, router, engine)
    tester.run_link_failure_test()

if __name__ == "__main__":
    main()