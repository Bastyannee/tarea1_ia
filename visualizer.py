import sys
import pygame
from typing import Dict, Type
from src.environment.grid import Environment, Position, CellType
from src.environment.fire import FireModel
from src.environment.simulator import Simulator
from src.algorithms.uninformed import BFS, DFS
from src.algorithms.informed import AStar, GreedyBFS
from src.algorithms.bioinspired import GeneticAlgorithm

# --- CONFIGURACIÓN RETRO (Paleta Arcade) ---
CELL_SIZE = 30
COLOR_BG = (15, 15, 20)           # Fondo oscuro CRT
COLOR_WALL = (30, 30, 200)        # Muros azul neón (estilo laberinto)
COLOR_FREE = (20, 20, 25)         # Suelo
COLOR_EXIT = (57, 255, 20)        # Salida verde fosforescente
COLOR_FIRE = (255, 69, 0)         # Fuego naranja/rojo vibrante
COLOR_AGENT = (255, 255, 0)       # Agentes amarillo Pac-Man
COLOR_GRID = (40, 40, 60)         # Líneas de la cuadrícula
COLOR_TEXT = (200, 200, 200)

ALGORITHMS = {
    "1": ("BFS", BFS),
    "2": ("DFS", DFS),
    "3": ("A-Star", AStar),
    "4": ("Greedy", GreedyBFS),
    "5": ("Genetico", GeneticAlgorithm)
}

def draw_menu(screen, font, selected_algo: str, delay_ms: int):
    """Renderiza el menú de selección superior."""
    menu_surface = pygame.Surface((screen.get_width(), 60))
    menu_surface.fill((30, 30, 40))
    
    text_algo = font.render(f"Algoritmo: [ {ALGORITHMS[selected_algo][0]} ] (Usa 1-5 para cambiar)", True, COLOR_TEXT)
    text_speed = font.render(f"Velocidad: {delay_ms} ms/turno (Usa FLECHAS para cambiar)", True, COLOR_TEXT)
    text_start = font.render("Presiona ENTER para iniciar/reiniciar simulación", True, COLOR_TEXT)
    
    menu_surface.blit(text_algo, (10, 5))
    menu_surface.blit(text_speed, (10, 25))
    menu_surface.blit(text_start, (10, 45))
    screen.blit(menu_surface, (0, 0))

def draw_grid(screen, env: Environment, offset_y: int):
    """Renderiza el estado actual del mapa y el fuego."""
    rows, cols = env.grid.shape

    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE + offset_y, CELL_SIZE, CELL_SIZE)
            cell_value = env.grid[y, x]

            if cell_value == CellType.WALL.value:
                pygame.draw.rect(screen, COLOR_WALL, rect)
            elif cell_value == CellType.EXIT.value:
                pygame.draw.rect(screen, COLOR_EXIT, rect)
            elif cell_value == CellType.FIRE.value:
                pygame.draw.rect(screen, COLOR_FIRE, rect)
                inner_rect = rect.inflate(-8, -8)
                pygame.draw.rect(screen, (255, 200, 0), inner_rect)
            else:
                pygame.draw.rect(screen, COLOR_FREE, rect)

            pygame.draw.rect(screen, COLOR_GRID, rect, 1)

    for agent in env.agents:
        if not agent.is_dead and not agent.is_evacuated:
            center_x = agent.pos.x * CELL_SIZE + CELL_SIZE // 2
            center_y = agent.pos.y * CELL_SIZE + offset_y + CELL_SIZE // 2
            pygame.draw.circle(screen, COLOR_AGENT, (center_x, center_y), CELL_SIZE // 2 - 4)

def run_simulation_step(env, pathfinder, agent_paths, simulator):
    """Avanza un turno en el motor de simulación."""
    agent_actions: Dict[int, Position] = {}
    for agent in env.agents:
        if agent.is_dead or agent.is_evacuated:
            continue

        needs_replan = (
            agent.id not in agent_paths 
            or not agent_paths[agent.id]
            or env.grid[agent_paths[agent.id][0].y, agent_paths[agent.id][0].x] == CellType.FIRE.value
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

    return simulator.step(agent_actions)

def main():
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("consolas", 14)

    # Configuración inicial
    map_path = "data/maps/map1_bottleneck.txt"
    initial_fire = [Position(x=10, y=1)]
    
    # Dimensiones basadas en el mapa
    temp_env = Environment(map_path, initial_fire=[])
    rows, cols = temp_env.grid.shape
    MENU_HEIGHT = 70
    width = max(cols * CELL_SIZE, 500)
    height = rows * CELL_SIZE + MENU_HEIGHT
    
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Escape de la Torre - Retro AI Simulator")

    # Estado de la UI
    selected_algo_key = "1"
    delay_ms = 150  # Pausa entre turnos en milisegundos
    running = True
    simulation_active = False
    
    # Variables del motor
    env = None
    simulator = None
    pathfinder = None
    agent_paths = {}

    # Renderizado inicial vacío
    screen.fill(COLOR_BG)
    draw_menu(screen, font, selected_algo_key, delay_ms)
    draw_grid(screen, temp_env, MENU_HEIGHT)
    pygame.display.flip()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                # Controles de Algoritmo
                if event.unicode in ALGORITHMS:
                    selected_algo_key = event.unicode
                    
                # Controles de Velocidad
                elif event.key == pygame.K_UP:
                    delay_ms = min(2000, delay_ms + 50)
                elif event.key == pygame.K_DOWN:
                    delay_ms = max(50, delay_ms - 50)
                    
                # Reiniciar / Iniciar Simulación
                elif event.key == pygame.K_RETURN:
                    env = Environment(map_path, initial_fire=initial_fire)
                    fire_model = FireModel(env=env, seed=42, k_turns=2, spread_prob=0.35)
                    simulator = Simulator(env=env, fire_model=fire_model, max_turns=150, cell_capacity=1)
                    
                    algo_class = ALGORITHMS[selected_algo_key][1]
                    pathfinder = algo_class(env)
                    agent_paths = {}
                    simulation_active = True

        screen.fill(COLOR_BG)
        draw_menu(screen, font, selected_algo_key, delay_ms)

        if simulation_active and env is not None:
            simulation_active = run_simulation_step(env, pathfinder, agent_paths, simulator)
            draw_grid(screen, env, MENU_HEIGHT)
            pygame.display.flip()
            pygame.time.delay(delay_ms) # Ralentiza la simulación según configuración
        else:
            # Si terminó o aún no inicia, dibujar el estado estático
            if env is not None:
                draw_grid(screen, env, MENU_HEIGHT)
            else:
                draw_grid(screen, temp_env, MENU_HEIGHT)
            pygame.display.flip()
            pygame.time.delay(50) # Bajo uso de CPU mientras está en el menú

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()