import os
import time
from src.network_manager import Network
from src.router import Router
from src.engine import Engine
from src.oracle import OfflineOracle
from src.fault_tolerance import FaultTester

def load_demands_from_file(filepath):
    demands = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                d_id, src, dst, size = line.split()
                demands.append({'id': int(d_id), 'src': src, 'dst': dst, 'size': float(size)})
    return demands

def get_max_utilization(net):
    max_util = 0.0
    for u, v, data in net.graph.edges(data=True):
        util_rate = data['utilization'] / data['capacity']
        if util_rate > max_util:
            max_util = util_rate
    return max_util

def simulate_routing(topo_file, demands, use_smart, label):
    net = Network()
    net.load_topology_from_file(topo_file)
    router = Router(net)
    engine = Engine(net, router)

    total_hops = 0
    accepted_traffic = 0.0
    accepted_ids = []
    for d in demands:
        path, reason = engine.process_demand(d['src'], d['dst'], d['size'], use_smart=use_smart)
        status = "ACEITA" if path else "REJEITADA"
        # Requisito 13: pra qualquer demanda, o programa diz por que aquela rota.
        print(f"     D-{d['id']} ({d['src']}->{d['dst']}, {d['size']}): {status} | {reason}")
        if path:
            total_hops += len(path) - 1
            accepted_traffic += d['size']
            accepted_ids.append(d['id'])

    max_util = get_max_utilization(net)
    print(f"-> {label}: {total_hops} saltos totais | {accepted_traffic:.1f} unidades aceitas | Carga Crítica: {max_util*100:.1f}%")
    return {
        'net': net, 'router': router, 'engine': engine,
        'hops': total_hops, 'traffic': accepted_traffic, 'accepted_ids': accepted_ids,
    }

def run_pipeline(topo_file, demands_file, label):
    print(f"\n{'='*60}\n{label}\n{'='*60}")

    net_base = Network()
    net_base.load_topology_from_file(topo_file)
    topology_list = [(u, v, data['capacity']) for u, v, data in net_base.graph.edges(data=True)]
    demands = load_demands_from_file(demands_file)

    # 1. Oracle (Offline) — sempre produz um número, mesmo quando não cabe tudo
    print("--- 1. Offline Optimum / Ótimo Offline ---")
    oracle = OfflineOracle(topology_list, demands)
    result = oracle.solve()
    if result['fully_feasible']:
        print(f"Toda a demanda cabe. Ótimo: {result['total_hops']:.0f} saltos.")
    else:
        pct = result['accepted_traffic'] / result['total_demand'] * 100 if result['total_demand'] else 0.0
        print(f"Não cabe tudo (Infactível para 100%). Ótimo aceita {result['accepted_traffic']:.1f}/"
              f"{result['total_demand']:.1f} unidades ({pct:.1f}%) com {result['total_hops']:.0f} saltos.")

    # 2. Baseline
    print("--- 2. Piso de Comparação (Caminho Mínimo) ---")
    baseline = simulate_routing(topo_file, demands, use_smart=False, label="2. Piso de Comparação (Caminho Mínimo)")

    # 3. Smart Router
    print("--- 3. Roteador Heurístico (Primal-Dual) ---")
    smart = simulate_routing(topo_file, demands, use_smart=True, label="3. Roteador Heurístico (Primal-Dual)")

    # 4. Razão contra o ótimo (Requisito 2: "um número, não um adjetivo")
    print("--- 4. Razão contra o Ótimo Offline (Requisito 2) ---")
    if result['accepted_traffic'] > 0:
        pct_traf = smart['traffic'] / result['accepted_traffic'] * 100
        print(f"   Tráfego: heurística aceitou {pct_traf:.1f}% do que o ótimo aceitaria "
              f"({smart['traffic']:.1f}/{result['accepted_traffic']:.1f} unidades)")
    if result['total_hops'] > 0:
        razao_saltos = smart['hops'] / result['total_hops']
        print(f"   Saltos: heurística usou {razao_saltos:.2f}x os saltos do ótimo "
              f"({smart['hops']} vs {result['total_hops']:.0f})")

    # 5. Link Failure Test
    tester = FaultTester(smart['net'], smart['router'], smart['engine'])
    survived, total_edges = tester.run_link_failure_test()

    return {
        'oracle': result, 'baseline': baseline, 'smart': smart,
        'survived': survived, 'total_edges': total_edges,
    }

def main():
    start_time = time.time()

    # Executa a prova de conceito original (Pequena escala)
    run_pipeline(os.path.join('data', 'rede.txt'), os.path.join('data', 'demandas.txt'), "CENÁRIO 1: REDE BASE (PROVA DE CONCEITO)")

    # Executa a prova de escala (100 nós)
    run_pipeline(os.path.join('data', 'rede_100_nos.txt'), os.path.join('data', 'demandas_100_nos.txt'), "CENÁRIO 2: ESCALA (100 NÓS)")

    print(f"\nTempo Total de Execução (Requisito 7): {time.time() - start_time:.4f} segundos")

if __name__ == "__main__":
    main()
