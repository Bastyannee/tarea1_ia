import heapq
from typing import List, Optional
from src.environment.grid import Position, CellType, Environment
from src.algorithms.heuristics import manhattan_distance

class AStar:
    def __init__(self, env: Environment):
        self.env = env
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def _is_valid(self, pos: Position, current_grid) -> bool:
        rows, cols = current_grid.shape
        if 0 <= pos.y < rows and 0 <= pos.x < cols:
            cell = current_grid[pos.y, pos.x]
            return cell in (CellType.FREE.value, CellType.EXIT.value, CellType.PERSON.value)
        return False

    def find_path(self, start: Position) -> Optional[List[Position]]:
        """Calcula la ruta óptima hacia la salida minimizando f(n) = g(n) + h(n)."""
        goal = self.env.exit_pos
        
        # Priority Queue almacena tuplas: (f_score, counter, actual_pos, path)
        # El counter evita empates no comparables entre objetos Position
        pq = []
        counter = 0
        
        g_scores = { (start.x, start.y): 0 }
        f_score_start = manhattan_distance(start, goal)
        
        heapq.heappush(pq, (f_score_start, counter, start, [start]))
        
        while pq:
            current_f, _, current_pos, path = heapq.heappop(pq)
            current_coord = (current_pos.x, current_pos.y)

            if current_pos == goal:
                return path

            for dy, dx in self.directions:
                next_pos = Position(current_pos.x + dx, current_pos.y + dy)
                next_coord = (next_pos.x, next_pos.y)

                if self._is_valid(next_pos, self.env.grid):
                    # El costo de moverse a un nodo adyacente es 1
                    # Aquí se puede sumar self.env.congestion_map[next_pos.y, next_pos.x] si se desea penalizar congestión
                    tentative_g = g_scores[current_coord] + 1 

                    if next_coord not in g_scores or tentative_g < g_scores[next_coord]:
                        g_scores[next_coord] = tentative_g
                        h_score = manhattan_distance(next_pos, goal)
                        f_score = tentative_g + h_score
                        
                        counter += 1
                        heapq.heappush(pq, (f_score, counter, next_pos, path + [next_pos]))
                        
        return None