from collections import deque
from typing import List, Tuple, Optional
from src.environment.grid import Position, CellType, Environment

class BFS:
    def __init__(self, env: Environment):
        self.env = env
        # Movimientos ortogonales permitidos (Arriba, Abajo, Izquierda, Derecha)
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def _is_valid(self, pos: Position, current_grid) -> bool:
        """Verifica si una celda está dentro del mapa y no es un obstáculo ni fuego."""
        rows, cols = current_grid.shape
        if 0 <= pos.y < rows and 0 <= pos.x < cols:
            cell = current_grid[pos.y, pos.x]
            # Es válido si está libre, es la salida, o es otra persona (para permitir encolamientos)
            return cell in (CellType.FREE.value, CellType.EXIT.value, CellType.PERSON.value)
        return False

    def find_path(self, start: Position) -> Optional[List[Position]]:
        """Calcula la ruta más corta desde el inicio hasta la salida usando BFS."""
        goal = self.env.exit_pos
        queue = deque([(start, [start])]) # Almacena (posición_actual, ruta_hasta_aqui)
        visited = { (start.x, start.y) }

        while queue:
            current_pos, path = queue.popleft()

            if current_pos == goal:
                return path

            for dy, dx in self.directions:
                next_pos = Position(current_pos.x + dx, current_pos.y + dy)
                next_coord = (next_pos.x, next_pos.y)

                if next_coord not in visited and self._is_valid(next_pos, self.env.grid):
                    visited.add(next_coord)
                    # Se encola la nueva posición y la ruta acumulada
                    queue.append((next_pos, path + [next_pos]))
                    
        return None # No hay ruta posible