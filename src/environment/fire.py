import numpy as np
import random
from typing import List, Tuple
from .grid import CellType, Position, Environment

class FireModel:
    def __init__(self, env: Environment, seed: int, k_turns: int = 2, spread_prob: float = 0.4):
        """
        Modela la propagación estocástica del fuego.
        :param k_turns: Frecuencia de propagación (cada k turnos).
        :param spread_prob: Probabilidad de que el fuego se propague a una celda adyacente.
        """
        self.env = env
        self.seed = seed
        self.k_turns = k_turns
        self.spread_prob = spread_prob
        self.turn_counter = 0
        
        # Fijar semillas para reproducibilidad en el benchmarking
        np.random.seed(self.seed)
        random.seed(self.seed)
        
    def step(self) -> List[Position]:
        """Avanza un turno en el modelo de fuego y retorna las nuevas celdas quemadas."""
        self.turn_counter += 1
        new_fire_cells = []
        
        if self.turn_counter % self.k_turns != 0:
            return new_fire_cells # El fuego no se propaga en este turno

        current_fire = np.argwhere(self.env.grid == CellType.FIRE.value)
        
        for fire_y, fire_x in current_fire:
            # Movimientos ortogonales (arriba, abajo, izquierda, derecha)
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = fire_y + dy, fire_x + dx
                
                # Verificar límites de la matriz
                if 0 <= ny < self.env.grid.shape[0] and 0 <= nx < self.env.grid.shape[1]:
                    target_cell = self.env.grid[ny, nx]
                    
                    # Se propaga solo si está libre o hay una persona (el muro y la salida no arden)
                    if target_cell in (CellType.FREE.value, CellType.PERSON.value):
                        if random.random() < self.spread_prob:
                            self.env.grid[ny, nx] = CellType.FIRE.value
                            new_fire_cells.append(Position(int(nx), int(ny)))
                            
        return new_fire_cells