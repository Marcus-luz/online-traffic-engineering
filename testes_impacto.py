import os
from src.network_manager import Network
from src.router import Router
from src.engine import Engine

def run_scenario(topology, demands, use_smart, title):
    # Executa a simulacao e imprime os resultados comparativos
    print(f"\n>>> {title} <<<")
    net = Network()
    net.load_topology(topology)
    router = Router(net) 
    engine = Engine(net, router)
    
    accepted = 0
    rejected = 0
    for d in demands:
        path, reason = engine.process_demand(d['src'], d['dst'], d['size'], use_smart)
        if path:
            accepted += 1
            if d['size'] >= 50: # Destaca a rota do Elefante
                print(f"  [ELEPHANT/ELEFANTE] D-{d['id']} routed via / roteado via: {path}")
        else:
            rejected += 1
            if d['size'] >= 50: # Destaca a falha do Elefante
                print(f"  [ELEPHANT/ELEFANTE] D-{d['id']} REJECTED / REJEITADA! Reason/Motivo: {reason}")
                
    print(f"-> Result/Resultado: {accepted} Aceitas | {rejected} Rejeitadas")
    print("-> Load/Carga nos cabos principais:")
    for u, v, data in net.graph.edges(data=True):
        if data['utilization'] > 0:
            print(f"     Link {u}->{v}: {data['utilization']}/{data['capacity']}")

def teste_elefante_rato():
    print("\n" + "="*60)
    print("TESTE 1: FLUXOS ELEFANTE VS RATO (Elephant vs Mice)")
    print("="*60)
    
    # Rota direta (cap 100) vs Rota de desvio (cap 100)
    topology = [
        ('A', 'B', 100), 
        ('A', 'C', 100), 
        ('C', 'B', 100)
    ]
    
    demands = []
    # 80 Ratos (Tamanho 1) inundando a rede
    for i in range(1, 81):
        demands.append({'id': i, 'src': 'A', 'dst': 'B', 'size': 1})
    # 1 Elefante (Tamanho 50) chegando de surpresa
    demands.append({'id': 81, 'src': 'A', 'dst': 'B', 'size': 50})
    
    run_scenario(topology, demands, False, "Baseline (Caminho Mínimo)")
    run_scenario(topology, demands, True, "Heurística Primal-Dual (A Nossa Solução)")

def teste_flash_crowd():
    print("\n" + "="*60)
    print("TESTE 2: EFEITO FLASH CROWD (Hotspot / Sorvedouro)")
    print("="*60)
    
    # 2 Origens tentam acessar o mesmo alvo 'T' através de 3 Roteadores do Meio (M1, M2, M3)
    topology = [
        ('S1', 'M1', 100), ('S2', 'M1', 100),
        ('S1', 'M2', 100), ('S2', 'M2', 100),
        ('S1', 'M3', 100), ('S2', 'M3', 100),
        ('M1', 'T', 20), # Gargalo 1 (Entrada do Servidor)
        ('M2', 'T', 20), # Gargalo 2
        ('M3', 'T', 20)  # Gargalo 3
    ]
    
    demands = []
    # 6 Requisições simultâneas de tamanho 10 para o alvo "T" (Total: 60)
    for i in range(1, 4):
        demands.append({'id': i, 'src': 'S1', 'dst': 'T', 'size': 10})
        demands.append({'id': i+3, 'src': 'S2', 'dst': 'T', 'size': 10})
        
    run_scenario(topology, demands, False, "Baseline (Caminho Mínimo)")
    run_scenario(topology, demands, True, "Heurística Primal-Dual (A Nossa Solução)")

if __name__ == '__main__':
    teste_elefante_rato()
    teste_flash_crowd()