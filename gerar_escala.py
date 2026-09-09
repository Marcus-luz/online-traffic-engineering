import random

def gerar_topologia_e_demandas(num_nos=100, num_demandas=50):
    # Generate 100-node topology / Gera topologia com 100 nós
    with open('data/rede_100_nos.txt', 'w') as f:
        for i in range(1, num_nos):
            f.write(f"N{i} N{i+1} 100\n") # Main chain / Corrente principal
            if i < num_nos - 2:
                f.write(f"N{i} N{i+2} 50\n") # Shortcuts / Atalhos
                
    # Generate random demands / Gera demandas aleatórias
    with open('data/demandas_100_nos.txt', 'w') as f:
        for i in range(1, num_demandas + 1):
            origem = f"N{random.randint(1, num_nos//2)}"
            destino = f"N{random.randint(num_nos//2 + 1, num_nos)}"
            tamanho = random.randint(5, 20)
            f.write(f"{i} {origem} {destino} {tamanho}\n")
            
    print("Scale files generated in data/ folder / Arquivos de escala gerados com sucesso na pasta data/.")

if __name__ == '__main__':
    gerar_topologia_e_demandas()