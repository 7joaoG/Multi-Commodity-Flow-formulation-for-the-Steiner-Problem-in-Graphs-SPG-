# inspect_stp.py
import os

def inspecionar_arquivo(caminho):
    print(f"\n=== INSPECIONANDO: {caminho} ===")
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    # Mostra as primeiras 50 linhas
    for i, linha in enumerate(linhas[:50]):
        print(f"{i+1:3d}: {linha.rstrip()}")

# Inspeciona um arquivo de cada pasta
pastas = [
    "Data/Incidence W/huge_graphs/i320-001.stp",
    "Data/Incidence W/medium_graphs/i160-001.stp",
    "Data/Incidence W/little_graphs/i080-001.stp",
    "Data/Random W/medium_graphs/b01.stp",
]

for pasta in pastas:
    if os.path.exists(pasta):
        inspecionar_arquivo(pasta)
    else:
        print(f"Arquivo não encontrado: {pasta}")