import unittest
from src.network_manager import Network
from src.router import Router
from src.engine import Engine

class TestEngine(unittest.TestCase):
    def setUp(self):
        # Setup basic network / Configura rede básica
        self.net = Network()
        self.net.load_topology([('A', 'B', 10), ('B', 'C', 10), ('A', 'C', 5)])
        self.router = Router(self.net, config_path='config.json')
        self.engine = Engine(self.net, self.router)

    def test_rejeicao_inviabilidade(self):
        # Demand exceeds capacity / Demanda excede a capacidade (Requisito 6)
        path, reason = self.engine.process_demand('A', 'B', 15)
        self.assertFalse(path)
        self.assertIn("Rejected", reason)

    def test_embaralhamento_prova_online(self):
        # Requisito 1: Prova que a ordem altera o resultado (Strictly Online)
        
        # Ordem 1: Demanda pesada (tamanho 8) chega no final
        demandas_ordem_1 = [
            {'id': 1, 'src': 'A', 'dst': 'C', 'size': 4},
            {'id': 2, 'src': 'A', 'dst': 'C', 'size': 4},
            {'id': 3, 'src': 'A', 'dst': 'C', 'size': 8}
        ]
        
        # Ordem 2: Demanda pesada chega primeiro
        demandas_ordem_2 = [
            demandas_ordem_1[2], 
            demandas_ordem_1[0], 
            demandas_ordem_1[1]
        ]
        
        # Simulacao Ordem 1
        resultado_d3_ordem_1 = None
        for d in demandas_ordem_1:
            path, _ = self.engine.process_demand(d['src'], d['dst'], d['size'])
            if d['id'] == 3:
                resultado_d3_ordem_1 = path # D3 é rejeitada por falta de espaço
                
        # Reseta o estado da rede para a Simulacao Ordem 2
        self.setUp()
        
        resultado_d3_ordem_2 = None
        for d in demandas_ordem_2:
            path, _ = self.engine.process_demand(d['src'], d['dst'], d['size'])
            if d['id'] == 3:
                resultado_d3_ordem_2 = path # D3 é roteada com sucesso (via A->C ou A->B->C)
                
        # Prova formal: A mesma demanda (ID 3) teve destinos fisicamente diferentes apenas por causa da ordem
        self.assertNotEqual(resultado_d3_ordem_1, resultado_d3_ordem_2)

if __name__ == '__main__':
    unittest.main()