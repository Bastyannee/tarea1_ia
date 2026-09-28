from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List, Optional
import numpy as np

class CellType(Enum):
    FREE = "."
    WALL = "#"
    EXIT = "E"
    PERSON = "P"
    FIRE = "F"

@dataclass
class Position:
    x: int
    y: int

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash((self.x, self.y))

@dataclass
class AgentState:
    id: int
    pos: Position
    is_evacuated: bool = False
    is_dead: bool = False
    path: Optional[List[Position]] = None

class Environment:
    def __init__(self, map_file: str, initial_fire: Optional[List[Position]] = None):
        self.map_file = map_file
        self.initial_fire = initial_fire or []
        self.grid: np.ndarray = self._load_map(self.map_file)
        self.exit_pos: Position = self._find_exit()
        self.agents: List[AgentState] = self._find_agents()
        
        # Colocar los focos iniciales de fuego en la grilla
        for f_pos in self.initial_fire:
            if 0 <= f_pos.y < self.grid.shape[0] and 0 <= f_pos.x < self.grid.shape[1]:
                self.grid[f_pos.y, f_pos.x] = CellType.FIRE.value

    def _load_map(self, file_path: str) -> np.ndarray:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [list(line.strip()) for line in f if line.strip()]
        return np.array(lines, dtype=str)

    def _find_exit(self) -> Position:
        y_indices, x_indices = np.where(self.grid == CellType.EXIT.value)
        if len(y_indices) == 0:
            raise ValueError("No se encontró la casilla de salida 'E' en el mapa.")
        return Position(int(x_indices[0]), int(y_indices[0]))

    def _find_agents(self) -> List[AgentState]:
        y_indices, x_indices = np.where(self.grid == CellType.PERSON.value)
        agents = []
        for i, (y, x) in enumerate(zip(y_indices, x_indices)):
            agents.append(AgentState(id=i, pos=Position(int(x), int(y))))
        return agents