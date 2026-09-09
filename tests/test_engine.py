import unittest
from src.network_manager import Network
from src.router import Router
from src.engine import Engine

class TestEngine(unittest.TestCase):
    def setUp(self):
        # Setup basic network / Configura rede básica
        self.net = Network()
        self.net.load_topology([('A', 'B', 10), ('B', 'C', 10)])
        self.router = Router(self.net, config_path='config.json')
        self.engine = Engine(self.net, self.router)

    def test_rejeicao_inviabilidade(self):
        # Demand exceeds capacity / Demanda excede a capacidade
        path, reason = self.engine.process_demand('A', 'B', 15)
        self.assertFalse(path)
        self.assertIn("Rejected", reason)

    def test_caminho_valido(self):
        # Valid path allocation / Alocação de caminho válido
        path, reason = self.engine.process_demand('A', 'C', 5)
        self.assertEqual(path, ['A', 'B', 'C'])

if __name__ == '__main__':
    unittest.main()