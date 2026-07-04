import time
from mip import Model, xsum, minimize, BINARY, CONTINUOUS, OptimizationStatus

def construir_e_resolver(n, arestas, terminais):
    inicio = time.perf_counter()
    
    # Usando CBC que é mais estável no Windows
    mdl = Model(solver_name='CBC')
    mdl.verbose = 0

    mdl.threads = 8  # Usar múltiplas threads

    # Variáveis y: indica se a aresta é usada na solução
    y = {}
    for e in arestas:
        y[e] = mdl.add_var(var_type=BINARY)

    # Cria arcos bidirecionais para o fluxo
    arcos = []
    for u, v, c in arestas:
        arcos.append((u, v, (u, v, c)))  # (origem, destino, aresta_original)
        arcos.append((v, u, (u, v, c)))

    raiz = terminais[0]
    mercadorias = [t for t in terminais if t != raiz]

    # Variáveis de fluxo f[u, v, k]
    f = {}
    for k in mercadorias:
        for u, v, e in arcos:
            f[(u, v, k)] = mdl.add_var(var_type=CONTINUOUS, lb=0, ub=1)

    # Restrições de conservação de fluxo para cada mercadoria
    for k in mercadorias:
        for i in range(1, n + 1):
            saida = xsum(f[(i, j, k)] for i_u, j, e in arcos if i_u == i)
            entrada = xsum(f[(j, i, k)] for j, i_u, e in arcos if i_u == i)

            if i == raiz:
                mdl += saida - entrada == 1
            elif i == k:
                mdl += saida - entrada == -1
            else:
                mdl += saida - entrada == 0

    # Restrições de acoplamento: fluxo só passa por arestas selecionadas
    for k in mercadorias:
        for u, v, e in arcos:
            mdl += f[(u, v, k)] <= y[e]

    # Função objetivo: minimizar custo total das arestas selecionadas
    mdl.objective = minimize(
        xsum(c * y[(u, v, c)] for u, v, c in arestas)
    )

    return mdl, inicio