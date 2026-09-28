from typing import List, Tuple, Optional
from src.environment.grid import Position, CellType, Environment

class DFS:
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
        """Calcula una ruta desde el inicio hasta la salida usando DFS (LIFO)."""
        goal = self.env.exit_pos
        # Pila LIFO nativa de Python (list): Almacena (posición_actual, ruta_hasta_aqui)
        stack = [(start, [start])]
        visited = set()

        while stack:
            # 1. Sacar el último insertado (LIFO)
            current_pos, path = stack.pop()
            current_coord = (current_pos.x, current_pos.y)

            # 2. Test de objetivo al expandir el nodo
            if current_pos == goal:
                return path

            # 3. Verificar y marcar como visitado al momento de expandir
            if current_coord not in visited:
                visited.add(current_coord)

                # 4. Generar hijos
                # Usamos reversed() para que el orden de expansión efectivo 
                # (al sacar de la pila) priorice Arriba, Abajo, Izquierda, Derecha.
                for dy, dx in reversed(self.directions):
                    next_pos = Position(current_pos.x + dx, current_pos.y + dy)
                    next_coord = (next_pos.x, next_pos.y)

                    if next_coord not in visited and self._is_valid(next_pos, self.env.grid):
                        # Se inserta en la pila el nuevo nodo con su ruta acumulada
                        stack.append((next_pos, path + [next_pos]))
                        
        return None # No hay ruta posible (agente atrapado)