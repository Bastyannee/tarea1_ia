from src.environment.grid import Position

def manhattan_distance(pos1: Position, pos2: Position) -> float:
    """
    Calcula la distancia Manhattan entre dos posiciones.
    Ideal para movimientos en 4 direcciones en una grilla.
    """
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)