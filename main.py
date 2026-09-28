import argparse
from typing import Dict, Type
from src.environment.grid import Environment, Position, CellType
from src.environment.fire import FireModel
from src.environment.simulator import Simulator
from src.algorithms.uninformed import BFS, DFS
from src.algorithms.informed import AStar, GreedyBFS

def run_simulation(map_path: str, algo_name: str, algo_class: Type, seed: int = 42, max_turns: int = 200):
    # Foco de fuego inicial (ej. sector superior central del edificio)
    initial_fire = [Position(x=10, y=1)]
    
    env = Environment(map_path, initial_fire=initial_fire)
    fire_model = FireModel(env=env, seed=seed, k_turns=2, spread_prob=0.35)
    simulator = Simulator(env=env, fire_model=fire_model, max_turns=max_turns, cell_capacity=1)
    
    pathfinder = algo_class(env)
    last_clearance_turn = 0
    total_agents = len(env.agents)

    # Rutas calculadas para cada agente
    agent_paths: Dict[int, list] = {}

    while True:
        agent_actions: Dict[int, Position] = {}

        for agent in env.agents:
            if agent.is_dead or agent.is_evacuated:
                continue

            # Replanificar si no tiene ruta o si el siguiente paso se quemó
            needs_replan = (
                agent.id not in agent_paths 
                or not agent_paths[agent.id]
                or env.grid[agent_paths[agent.id][0].y, agent_paths[agent.id][0].x] == CellType.FIRE.value
            )

            if needs_replan:
                new_path = pathfinder.find_path(agent.pos)
                if new_path and len(new_path) > 1:
                    # El primer elemento es la posición actual, el segundo es el próximo paso
                    agent_paths[agent.id] = new_path[1:]
                else:
                    agent_paths[agent.id] = []

            # Determinar la acción deseada (avanzar en la ruta o esperar)
            if agent_paths[agent.id]:
                next_pos = agent_paths[agent.id].pop(0)
                agent_actions[agent.id] = next_pos
            else:
                agent_actions[agent.id] = agent.pos # Esperar en su celda

        # Ejecutar el turno en el simulador
        active = simulator.step(agent_actions)

        # Actualizar tiempo de despeje del último sobreviviente
        survivors_this_turn = [a for a in env.agents if a.is_evacuated]
        if survivors_this_turn:
            last_clearance_turn = simulator.current_turn

        if not active:
            break

    # Recolección de métricas
    survivors = sum(1 for a in env.agents if a.is_evacuated)
    casualties = sum(1 for a in env.agents if a.is_dead)
    survival_rate = (survivors / total_agents) * 100 if total_agents > 0 else 0.0

    return {
        "algoritmo": algo_name,
        "sobrevivientes": f"{survivors}/{total_agents}",
        "tasa_supervivencia": f"{survival_rate:.1f}%",
        "tiempo_despeje": last_clearance_turn,
        "fallecidos": casualties,
        "turnos_totales": simulator.current_turn
    }

def main():
    parser = argparse.ArgumentParser(description="Prueba comparativa de algoritmos de escape.")
    parser.add_argument("--map", type=str, default="data/maps/map1_bottleneck.txt", help="Ruta al mapa")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria")
    args = parser.parse_args()

    algos = {
        "BFS (No informado)": BFS,
        "DFS (No informado)": DFS,
        "A* (Informado)": AStar,
        "Greedy BFS (Informado)": GreedyBFS,
    }

    print(f"\n========================================================")
    print(f" Iniciando simulación en: {args.map} (Seed: {args.seed})")
    print(f"========================================================\n")

    resultados = []
    for name, algo_cls in algos.items():
        res = run_simulation(args.map, name, algo_cls, seed=args.seed)
        resultados.append(res)

    # Imprimir tabla de resultados
    header = f"{'Algoritmo':<24} | {'Evacuados':<10} | {'Supervivencia':<14} | {'Tiempo Despeje':<14}"
    print(header)
    print("-" * len(header))
    for r in resultados:
        print(f"{r['algoritmo']:<24} | {r['sobrevivientes']:<10} | {r['tasa_supervivencia']:<14} | {r['tiempo_despeje']:<14}")
    print()

if __name__ == "__main__":
    main()