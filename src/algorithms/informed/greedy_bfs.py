import heapq
from typing import List, Optional
from src.environment.grid import Position, CellType, Environment
from src.algorithms.heuristics import manhattan_distance

class GreedyBFS:
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
        """Calcula una ruta hacia la salida minimizando exclusivamente f(n) = h(n)."""
        goal = self.env.exit_pos
        
        # Priority Queue almacena tuplas: (h_score, counter, actual_pos, path)
        pq = []
        counter = 0
        visited = set()
        
        h_score_start = manhattan_distance(start, goal)
        heapq.heappush(pq, (h_score_start, counter, start, [start]))
        visited.add((start.x, start.y))
        
        while pq:
            current_h, _, current_pos, path = heapq.heappop(pq)

            if current_pos == goal:
                return path

            for dy, dx in self.directions:
                next_pos = Position(current_pos.x + dx, current_pos.y + dy)
                next_coord = (next_pos.x, next_pos.y)

                if next_coord not in visited and self._is_valid(next_pos, self.env.grid):
                    visited.add(next_coord)
                    h_score = manhattan_distance(next_pos, goal)
                    
                    counter += 1
                    heapq.heappush(pq, (h_score, counter, next_pos, path + [next_pos]))
                    
        return None