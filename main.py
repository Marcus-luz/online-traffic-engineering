from src.network_manager import Network
from src.router import Router
from src.engine import Engine
from src.oracle import OfflineOracle # <-- NOVO

def main():
    # 1. Setup mock topology and demands
    topology = [
        ('A', 'B', 10),
        ('B', 'C', 10),
        ('A', 'C', 5)
    ]
    demands = [
        {'id': 1, 'src': 'A', 'dst': 'C', 'size': 4},
        {'id': 2, 'src': 'A', 'dst': 'C', 'size': 4},
        {'id': 3, 'src': 'A', 'dst': 'C', 'size': 8} 
    ]

    # 2. RUN ORACLE (Offline) / RODA ORÁCULO (Offline)
    print("--- Offline Optimum (Oracle) ---")
    oracle = OfflineOracle(topology, demands)
    is_possible, best_score = oracle.solve()
    if is_possible:
        print(f"[+] Perfect routing found! Score: {best_score} hops")
    else:
        print("[-] Mathematically impossible to route all demands in this network!")
    print("")

    # 3. Init classes for Online Routing
    net = Network()
    router = Router(net)
    engine = Engine(net, router)
    net.load_topology(topology)

    # 4. Process online
    print("--- Online Routing / Roteamento Online ---")
    for d in demands:
        print(f"Demand {d['id']}: {d['src']}->{d['dst']} (Size: {d['size']})")
        path = engine.process_demand(d['src'], d['dst'], d['size'], use_smart=True)
        if path:
            print(f"  [+] Route: {path}")
        else:
            print("  [-] Rejected (No capacity)")

if __name__ == "__main__":
    main()