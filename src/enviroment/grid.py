from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List, Optional
import numpy as np

class CellType(Enum):
    """Representación de los tipos de celdas en el mapa para evitar 'cadenas mágicas'."""
    FREE = "."
    WALL = "#"
    EXIT = "E"
    PERSON = "P"
    FIRE = "F"

@dataclass
class Position:
    """Coordenadas (x, y) en la grilla."""
    x: int
    y: int

@dataclass
class AgentState:
    """Estado de una persona durante la evacuación."""
    id: int
    pos: Position
    is_evacuated: bool = False
    is_dead: bool = False
    path: Optional[List[Position]] = None

class Environment:
    """Clase principal que maneja la matriz del mapa y sus reglas."""
    def __init__(self, map_file: str):
        self.grid: np.ndarray = self._load_map(map_file)
        self.exit_pos: Position = self._find_exit()
        self.agents: List[AgentState] = self._find_agents()
        
    def _load_map(self, file_path: str) -> np.ndarray:
        # Lógica para leer el txt y convertirlo a matriz numpy
        pass
        
    def _find_exit(self) -> Position:
        # Lógica para encontrar la coordenada de 'E'
        pass
        
    def _find_agents(self) -> List[AgentState]:
        # Lógica para encontrar las coordenadas de 'P'
        pass