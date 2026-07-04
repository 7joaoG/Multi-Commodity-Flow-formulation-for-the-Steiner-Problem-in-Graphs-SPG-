import os
import sys
import time
import multiprocessing
from mip import Model, xsum, minimize, BINARY, CONTINUOUS, OptimizationStatus
from imports_and_parser import ler_steinlib
from modeling import construir_e_resolver


INSTANCIAS_SELECIONADAS = {
    "Incidence W/huge_graphs": [
        "i320-001.stp",
        "i320-003.stp",
        "i320-005.stp",
    ],
    "Incidence W/medium_graphs": [
        "i160-001.stp",
        "i160-003.stp",
    ],
    "Incidence W/little_graphs": [
        "i080-001.stp",
    ],
    "Random W/medium_graphs": [
        "b01.stp",
        "b05.stp",
        "b09.stp",
        "b16.stp",
    ],
    "Random W/little_graphs": [
        "design432.stp",
        "w23c23.stp",
    ]
}

# Se você tiver valores ótimos conhecidos para comparação, preencha abaixo.
# Caso contrário, a coluna "Lit." será omitida.
VALORES_OTIMOS = {
    # Exemplo: "i320-001.stp": 1234.0,
}

def get_optimal_threads():
    """Detecta o número ideal de threads com base no hardware."""
    total_cpus = multiprocessing.cpu_count()
    if total_cpus >= 12:
        return int(total_cpus * 0.7)   # ~8 threads para seu i5-1334U
    elif total_cpus >= 8:
        return int(total_cpus * 0.6)
    else:
        return max(1, total_cpus - 1)

def executar_instancia(caminho):
    """Executa o modelo MCF para uma instância e retorna um dicionário com resultados."""
    try:
        n, arestas, terminais = ler_steinlib(caminho)
    except Exception as e:
        return {"erro": f"Falha na leitura: {e}"}

    if not terminais:
        return {"erro": "Sem terminais"}
    if not arestas:
        return {"erro": "Sem arestas"}

    try:
        mdl, inicio = construir_e_resolver(n, arestas, terminais)
        mdl.threads = get_optimal_threads()
        status = mdl.optimize()
        tempo = time.perf_counter() - inicio

        if status == OptimizationStatus.OPTIMAL:
            return {
                "n": n,
                "arestas": len(arestas),
                "terminais": len(terminais),
                "status": "Ótimo",
                "valor": mdl.objective_value,
                "tempo": tempo,
                "threads": mdl.threads
            }
        elif status == OptimizationStatus.FEASIBLE:
            return {
                "n": n,
                "arestas": len(arestas),
                "terminais": len(terminais),
                "status": "Viável",
                "valor": mdl.objective_value,
                "tempo": tempo,
                "threads": mdl.threads
            }
        else:
            return {
                "n": n,
                "arestas": len(arestas),
                "terminais": len(terminais),
                "status": "Não resolvido",
                "valor": None,
                "tempo": tempo,
                "threads": mdl.threads
            }
    except Exception as e:
        return {"erro": f"Erro na otimização: {str(e)}"}

# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    base_dir = "Data"

    print("=" * 110)
    print(" PROBLEMA DE STEINER EM GRAFOS (SPG) – FORMULAÇÃO MCF")
    print(" Baseado em: Koch, T. & Martin, A. (1998).")
    print(" Solving Steiner Tree Problems in Graphs to Optimality.")
    print("=" * 110)

    print("\nConfiguração da execução:")
    print(f"  - Instâncias selecionadas: {sum(len(v) for v in INSTANCIAS_SELECIONADAS.values())}")
    print(f"  - Threads utilizadas: {get_optimal_threads()}")
    print(f"  - Solver: CBC (Coin-or Branch and Cut)")
    print("-" * 110)

    # Cabeçalho da tabela de resultados
    print(f"\n{'Instância':<30} | {'Categoria':<18} | {'Nós':<5} | {'Arestas':<7} | {'Term.':<5} | {'Status':<12} | {'Valor':<10} | {'Tempo (s)':<10}")
    print("-" * 125)

    resultados = []
    total_instancias = 0

    for pasta_relativa, arquivos in INSTANCIAS_SELECIONADAS.items():
        pasta = os.path.join(base_dir, pasta_relativa)
        categoria = pasta_relativa.split('/')[-1]   # ex: huge_graphs
        tipo = pasta_relativa.split('/')[0]         # ex: Incidence W

        for nome_arquivo in arquivos:
            caminho = os.path.join(pasta, nome_arquivo)
            total_instancias += 1

            if not os.path.exists(caminho):
                print(f"{nome_arquivo:<30} | {categoria:<18} | {'N/A':<5} | {'N/A':<7} | {'N/A':<5} | {'Arq. não encontrado':<12} | {'-':<10} | {'-':<10}")
                continue

            print(f"Processando: {nome_arquivo}...", end='', flush=True)
            resultado = executar_instancia(caminho)

            if "erro" in resultado:
                print(" FALHA")
                print(f"{nome_arquivo:<30} | {categoria:<18} | {'-':<5} | {'-':<7} | {'-':<5} | {resultado['erro'][:12]:<12} | {'-':<10} | {'-':<10}")
                continue

            print(f" OK ({resultado['tempo']:.2f}s)")

            valor_str = f"{resultado['valor']:.1f}" if resultado['valor'] is not None else "-"
            print(f"{nome_arquivo:<30} | {categoria:<18} | {resultado['n']:<5} | {resultado['arestas']:<7} | {resultado['terminais']:<5} | {resultado['status']:<12} | {valor_str:<10} | {resultado['tempo']:<10.4f}")
            resultados.append(resultado)

    # =========================================================================
    # ESTATÍSTICAS FINAIS
    # =========================================================================
    print("\n" + "=" * 110)
    print("RESUMO ESTATÍSTICO")
    print("=" * 110)

    if resultados:
        sucessos = [r for r in resultados if r['status'] == 'Ótimo']
        viaveis = [r for r in resultados if r['status'] == 'Viável']
        falhas = [r for r in resultados if r['status'] == 'Não resolvido']

        print(f"\nTotal de instâncias processadas: {len(resultados)}")
        print(f"  - Ótimas: {len(sucessos)}")
        print(f"  - Viáveis: {len(viaveis)}")
        print(f"  - Não resolvidas: {len(falhas)}")

        if sucessos:
            tempos = [r['tempo'] for r in sucessos]
            print(f"\nTempo médio de solução (ótimas): {sum(tempos)/len(tempos):.4f} s")
            print(f"Tempo mínimo: {min(tempos):.4f} s")
            print(f"Tempo máximo: {max(tempos):.4f} s")

            # Melhor e pior caso (em termos de tempo)
            melhor = min(sucessos, key=lambda x: x['tempo'])
            pior = max(sucessos, key=lambda x: x['tempo'])
            print(f"\nMelhor caso: {melhor['n']} nós, {melhor['arestas']} arestas → {melhor['tempo']:.4f} s")
            print(f"Pior caso:  {pior['n']} nós, {pior['arestas']} arestas → {pior['tempo']:.4f} s")

    print("\n" + "=" * 110)
    print("FIM DA EXECUÇÃO – Resultados alinhados com a metodologia de Koch & Martin (1998).")
    print("=" * 110)