from src.network_manager import Network
from src.router import Router
from src.engine import Engine

def main():
    # 1. Init classes / Inicializa as classes
    net = Network()
    router = Router(net)
    engine = Engine(net, router)

    # 2. Setup mock topology / Configura topologia de teste
    # Links: (Origin, Destination, Capacity)
    topology = [
        ('A', 'B', 10),
        ('B', 'C', 10),
        ('A', 'C', 5)
    ]
    net.load_topology(topology)

    # 3. Create mock demands / Cria demandas de teste
    demands = [
        {'id': 1, 'src': 'A', 'dst': 'C', 'size': 4}, # Fits in A->C / Cabe em A->C
        {'id': 2, 'src': 'A', 'dst': 'C', 'size': 4}, # Must detour to A->B->C / Precisa desviar para A->B->C
        {'id': 3, 'src': 'A', 'dst': 'C', 'size': 8}  # Exceeds capacity / Excede a capacidade
    ]

    # 4. Process online / Processa online
    print("--- Online Routing / Roteamento Online ---")
    for d in demands:
        print(f"Demand {d['id']}: {d['src']}->{d['dst']} (Size/Tamanho: {d['size']})")
        path = engine.process_demand(d['src'], d['dst'], d['size'], use_smart=True)
        
        if path:
            print(f"  [+] Route/Rota: {path}")
        else:
            print("  [-] Rejected/Rejeitada (No capacity/Sem capacidade)")

    # 5. Show final status / Mostra status final
    print("\n--- Final Links / Enlaces Finais ---")
    for u, v, data in net.graph.edges(data=True):
        print(f"{u}->{v}: {data['utilization']}/{data['capacity']} used/usado")

if __name__ == "__main__":
    main()