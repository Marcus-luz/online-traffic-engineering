import os
from src.network_manager import Network
from src.router import Router
from src.engine import Engine
from src.oracle import OfflineOracle

def generate_adversarial_instance(n_hops):
    # Generates a network to trick the exponential penalty / Gera uma rede para enganar a penalidade exponencial
    topology = []
    
    # Path 1: Direct link (1 hop) / Caminho 1: Direto (1 salto)
    topology.append(('S', 'T', 100))
    
    # Path 2: Long chain (N hops) / Caminho 2: Corrente longa (N saltos)
    for i in range(n_hops):
        u = 'S' if i == 0 else f'M_{i}'
        v = 'T' if i == n_hops - 1 else f'M_{i+1}'
        topology.append((u, v, 100))
        
    # Demands / Demandas
    # Demand 1 (Bait/Isca): Almost fills the direct link / Quase enche o link direto
    # Demand 2 (Payload/Carga): Tricked into the long path / Enganada para o caminho longo
    demands = [
        {'id': 1, 'src': 'S', 'dst': 'T', 'size': 95}, 
        {'id': 2, 'src': 'S', 'dst': 'T', 'size': 5}   
    ]
    
    return topology, demands

def main():
    print("--- DESAFIO 2: O PIOR CASO / WORST CASE ANALYSIS ---")
    print("Metric: Total Hops Used (Online vs Oracle) / Metrica: Total de Saltos\n")
    print(f"{'N_Hops':<10} | {'Online_Hops':<15} | {'Oracle_Hops':<15} | {'Ratio (Online/Oracle)'}")
    print("-" * 65)

    # Test network sizes from 2 to 25 / Testa redes de tamanho 2 a 25
    for n in range(2, 26):
        topology, demands = generate_adversarial_instance(n)
        
        # 1. Oracle (Offline)
        oracle = OfflineOracle(topology, demands)
        oracle_result = oracle.solve()
        oracle_hops = oracle_result['total_hops']
        
        # 2. Online Engine
        net = Network()
        net.load_topology(topology)
        router = Router(net) # Lera automaticamente o config.json
        engine = Engine(net, router)
        
        online_hops = 0
        for d in demands:
            # Unpacking tuple (path, reason) / Desempacotando a tupla
            path, reason = engine.process_demand(d['src'], d['dst'], d['size'], use_smart=True)
            if path:
                online_hops += len(path) - 1 # Number of edges is nodes - 1
                
        # 3. Calculate Ratio / Calcula a Razão
        ratio = (online_hops / oracle_hops) if oracle_hops else float('inf')
        print(f"{n:<10} | {online_hops:<15} | {oracle_hops:<15.1f} | {ratio:.2f}x")

if __name__ == "__main__":
    main()