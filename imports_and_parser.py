import os
import sys
import re
import time
from mip import Model, xsum, minimize, BINARY, CONTINUOUS, OptimizationStatus

def ler_steinlib(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    n, arestas, terminais, secao = 0, [], [], None
    contagem_arestas = 0
    
    for linha in linhas:
        linha = linha.strip()
        
        # Ignora linhas vazias e comentários
        if not linha or linha.startswith('33D32945') or linha.startswith('#'):
            continue
            
        if linha.startswith("SECTION"):
            secao = linha.split()[1] if len(linha.split()) > 1 else None
            continue
            
        if linha == "END":
            continue

        if secao == "Graph":
            if linha.startswith("Nodes"):
                partes = linha.split()
                if len(partes) >= 2:
                    n = int(partes[1])
            elif linha.startswith("Edges"):
                # Apenas ignora a linha de contagem de arestas
                continue
            elif linha.startswith("E"):
                # Formato: E u v c
                partes = linha.split()
                if len(partes) >= 4:  # E + u + v + c
                    try:
                        u = int(partes[1])
                        v = int(partes[2])
                        c = float(partes[3])
                        arestas.append((u, v, c))
                        contagem_arestas += 1
                    except (ValueError, IndexError):
                        pass
            else:
                # Tenta interpretar como aresta no formato "u v c" (sem E)
                partes = linha.split()
                try:
                    if len(partes) >= 3:
                        u = int(partes[0])
                        v = int(partes[1])
                        c = float(partes[2])
                        arestas.append((u, v, c))
                        contagem_arestas += 1
                    elif len(partes) == 2:
                        # Formato sem peso, assume peso 1
                        u = int(partes[0])
                        v = int(partes[1])
                        arestas.append((u, v, 1.0))
                        contagem_arestas += 1
                except (ValueError, IndexError):
                    pass

        elif secao == "Terminals":
            if linha.startswith("T"):
                partes = linha.split()
                if len(partes) >= 2:
                    for p in partes[1:]:
                        if p.isdigit():
                            terminais.append(int(p))
    
    # Se não encontrou terminais, tenta buscar de forma mais flexível
    if not terminais:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            # Procura por "Terminals" e números após
            import re
            padrao_terminal = re.findall(r'Terminals\s+(\d+)', conteudo)
            for t in padrao_terminal:
                terminais.append(int(t))
            
            # Se não achou, procura por linhas com T
            if not terminais:
                padrao_t = re.findall(r'T\s+(\d+)', conteudo)
                for t in padrao_t:
                    terminais.append(int(t))
    
    return n, arestas, terminais