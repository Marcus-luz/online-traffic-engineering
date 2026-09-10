import unittest
from src.network_manager import Network
from src.router import Router
from src.engine import Engine

class TestEngine(unittest.TestCase):
    def setUp(self):
        # Setup basic network / Configura rede basica
        self.net = Network()
        self.net.load_topology([('A', 'B', 10), ('B', 'C', 10), ('A', 'C', 5)])
        self.router = Router(self.net, config_path='config.json')
        self.engine = Engine(self.net, self.router)

    def test_rejeicao_inviabilidade(self):
        """
        Requirement 6: Blocks traffic greater than the bottleneck capacity.
        Requisito 6: Bloqueia trafego maior que a capacidade do gargalo.
        """
        print("\n[TEST 1] Verifying rejection of infeasible demand (Bottleneck) / [TESTE 1] Verificando rejeicao de demanda inviavel (Gargalo)...")
        path, reason = self.engine.process_demand('A', 'B', 15)
        
        self.assertFalse(path)
        self.assertIn("Rejected", reason)
        print("  -> SUCCESS/SUCESSO: Network blocked traffic of 15 on a link of 10 and emitted the reason correctly / A rede bloqueou o trafego de 15 num enlace de 10 e emitiu o motivo corretamente.")

    def test_embaralhamento_prova_online(self):
        """
        Requirement 1: Proves strictly online nature (Shuffling Test).
        Requisito 1: Prova natureza estritamente online (Teste de Embaralhamento).
        """
        print("\n[TEST 2] Proving strictly online nature (Shuffling) / [TESTE 2] Comprovando natureza estritamente Online (Embaralhamento)...")
        
        # Order 1: Heavy demand (size 8) arrives last / Ordem 1: Demanda pesada (tamanho 8) chega no final
        demandas_ordem_1 = [
            {'id': 1, 'src': 'A', 'dst': 'C', 'size': 4},
            {'id': 2, 'src': 'A', 'dst': 'C', 'size': 4},
            {'id': 3, 'src': 'A', 'dst': 'C', 'size': 8}
        ]
        
        # Order 2: Heavy demand arrives first / Ordem 2: Demanda pesada chega primeiro
        demandas_ordem_2 = [
            demandas_ordem_1[2], 
            demandas_ordem_1[0], 
            demandas_ordem_1[1]
        ]
        
        # Simulate Order 1 / Simulacao Ordem 1
        resultado_d3_ordem_1 = None
        for d in demandas_ordem_1:
            path, _ = self.engine.process_demand(d['src'], d['dst'], d['size'])
            if d['id'] == 3:
                resultado_d3_ordem_1 = path # D3 is rejected / D3 e rejeitada
                
        # Reset network state for Order 2 / Reseta o estado da rede para a Simulacao Ordem 2
        self.setUp()
        
        resultado_d3_ordem_2 = None
        for d in demandas_ordem_2:
            path, _ = self.engine.process_demand(d['src'], d['dst'], d['size'])
            if d['id'] == 3:
                resultado_d3_ordem_2 = path # D3 is successfully routed / D3 e roteada com sucesso
                
        # Formal proof: The same demand had different physical destinations just because of the order
        # Prova formal: A mesma demanda teve destinos diferentes apenas pela ordem
        self.assertNotEqual(resultado_d3_ordem_1, resultado_d3_ordem_2)
        print("  -> SUCCESS/SUCESSO: Demand 3 destination changed physically based solely on who arrived first / O destino da Demanda 3 mudou fisicamente baseando-se apenas em quem chegou antes.")
        print(f"     Result in Original Order / Resultado na Ordem Original.......: {resultado_d3_ordem_1}")
        print(f"     Result in Shuffled Order / Resultado na Ordem Embaralhada..: {resultado_d3_ordem_2}")

if __name__ == '__main__':
    unittest.main()