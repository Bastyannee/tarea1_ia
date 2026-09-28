import argparse
import os
from typing import Dict, List, Type
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.algorithms.bioinspired import GeneticAlgorithm
from src.algorithms.informed import AStar, GreedyBFS
from src.algorithms.uninformed import BFS, DFS
from src.environment.fire import FireModel
from src.environment.grid import CellType, Environment, Position
from src.environment.simulator import Simulator


def run_single_simulation(
    map_path: str,
    algo_class: Type,
    seed: int,
    max_turns: int = 150
) -> Dict[str, float]:
    """Ejecuta una corrida estocástica individual y retorna sus métricas."""
    initial_fire = [Position(x=10, y=1)]
    env = Environment(map_path, initial_fire=initial_fire)
    fire_model = FireModel(env=env, seed=seed, k_turns=2, spread_prob=0.35)
    simulator = Simulator(
        env=env,
        fire_model=fire_model,
        max_turns=max_turns,
        cell_capacity=1
    )

    pathfinder = algo_class(env)
    total_agents = len(env.agents)
    last_clearance_turn = 0
    agent_paths: Dict[int, list] = {}

    while True:
        agent_actions: Dict[int, Position] = {}

        for agent in env.agents:
            if agent.is_dead or agent.is_evacuated:
                continue

            needs_replan = (
                agent.id not in agent_paths
                or not agent_paths[agent.id]
                or env.grid[
                    agent_paths[agent.id][0].y,
                    agent_paths[agent.id][0].x
                ] == CellType.FIRE.value
            )

            if needs_replan:
                new_path = pathfinder.find_path(agent.pos)
                if new_path and len(new_path) > 1:
                    agent_paths[agent.id] = new_path[1:]
                else:
                    agent_paths[agent.id] = []

            if agent_paths[agent.id]:
                agent_actions[agent.id] = agent_paths[agent.id].pop(0)
            else:
                agent_actions[agent.id] = agent.pos

        active = simulator.step(agent_actions)

        # Registrar el turno del último sobreviviente que logra escapar
        if any(a.is_evacuated for a in env.agents):
            last_clearance_turn = simulator.current_turn

        if not active:
            break

    survivors = sum(1 for a in env.agents if a.is_evacuated)
    survival_rate = (survivors / total_agents) if total_agents > 0 else 0.0

    return {
        "survival_rate": survival_rate * 100.0,
        "clearance_time": last_clearance_turn,
    }


def execute_benchmarks(
    maps: List[str],
    iterations: int = 80,
    seed_base: int = 1000
):
    algorithms = {
        "BFS": BFS,
        "DFS": DFS,
        "A*": AStar,
        "Greedy BFS": GreedyBFS,
        "Genético": GeneticAlgorithm,
    }

    os.makedirs("resultados/graficos", exist_ok=True)
    raw_results = []

    total_runs = len(maps) * len(algorithms) * iterations
    current_run = 0

    print(f"\nIniciando benchmarking de {total_runs} simulaciones en total...")

    for map_path in maps:
        map_name = os.path.splitext(os.path.basename(map_path))[0]
        print(f"\n--- Evaluando Mapa: {map_name} ---")

        for algo_name, algo_cls in algorithms.items():
            print(f"-> Ejecutando {algo_name} ({iterations} iteraciones)...")

            for i in range(iterations):
                seed = seed_base + i
                metrics = run_single_simulation(map_path, algo_cls, seed=seed)

                raw_results.append({
                    "mapa": map_name,
                    "algoritmo": algo_name,
                    "iteracion": i + 1,
                    "semilla": seed,
                    "tasa_supervivencia": metrics["survival_rate"],
                    "tiempo_despeje": metrics["clearance_time"],
                })

                current_run += 1
                if current_run % 20 == 0 or current_run == total_runs:
                    progreso = (current_run / total_runs) * 100.0
                    print(
                        f"   Progreso global: {progreso:.1f}% "
                        f"({current_run}/{total_runs})"
                    )

    # Convertir a DataFrame
    df_raw = pd.DataFrame(raw_results)
    df_raw.to_csv("resultados/metricas_detalladas.csv", index=False)

    # Calcular estadísticos descriptivos obligatorios
    summary = df_raw.groupby(["mapa", "algoritmo"]).agg(
        supervivencia_media=("tasa_supervivencia", "mean"),
        supervivencia_std=("tasa_supervivencia", "std"),
        supervivencia_min=("tasa_supervivencia", "min"),
        supervivencia_max=("tasa_supervivencia", "max"),
        despeje_media=("tiempo_despeje", "mean"),
        despeje_std=("tiempo_despeje", "std"),
        despeje_min=("tiempo_despeje", "min"),
        despeje_max=("tiempo_despeje", "max"),
    ).reset_index()

    summary.to_csv("resultados/metricas_resumen.csv", index=False)
    print("\n✓ Resumen de métricas guardado en 'resultados/metricas_resumen.csv'")

    # Generación de gráficos para el informe
    generate_figures(df_raw)


def generate_figures(df: pd.DataFrame):
    sns.set_theme(style="whitegrid")

    # 1. Gráfico de Tasa de Supervivencia por Algoritmo y Mapa
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=df,
        x="mapa",
        y="tasa_supervivencia",
        hue="algoritmo",
        errorbar="sd",
        palette="viridis"
    )
    plt.title(
        "Tasa de Supervivencia Promedio por Escenario (con Desviación Estándar)",
        fontsize=13,
        pad=15
    )
    plt.xlabel("Escenario (Mapa)", fontsize=11)
    plt.ylabel("Supervivencia (%)", fontsize=11)
    plt.ylim(0, 105)
    plt.legend(title="Algoritmo", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("resultados/graficos/supervivencia_comparativa.png", dpi=300)
    plt.close()

    # 2. Boxplot de Tiempo de Despeje del Último Sobreviviente
    plt.figure(figsize=(11, 6))
    sns.boxplot(
        data=df,
        x="mapa",
        y="tiempo_despeje",
        hue="algoritmo",
        palette="Set2"
    )
    plt.title(
        "Distribución del Tiempo de Despeje del Último Sobreviviente (Turnos)",
        fontsize=13,
        pad=15
    )
    plt.xlabel("Escenario (Mapa)", fontsize=11)
    plt.ylabel("Turnos para Despeje", fontsize=11)
    plt.legend(title="Algoritmo", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("resultados/graficos/tiempo_despeje_boxplot.png", dpi=300)
    plt.close()

    print("✓ Gráficos generados exitosamente en 'resultados/graficos/'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Suite de benchmarking para Escape de la Torre."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=80,
        help="Número de iteraciones por experimento (mínimo 80, recomendado 200)"
    )
    args = parser.parse_args()

    test_maps = [
        "data/maps/map1_bottleneck.txt",
        "data/maps/map2_maze.txt",
        "data/maps/map3_open.txt"
    ]

    execute_benchmarks(maps=test_maps, iterations=args.iterations)