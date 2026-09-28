from typing import Dict, List
import numpy as np
import random
from .grid import CellType, Position, AgentState, Environment
from .fire import FireModel

class Simulator:
    def __init__(self, env: Environment, fire_model: FireModel, max_turns: int = 1000, cell_capacity: int = 1):
        """
        Orquesta la simulación por turnos y resuelve los cuellos de botella.
        :param cell_capacity: Cantidad máxima de personas que pueden ocupar una celda simultáneamente.
        """
        self.env = env
        self.fire_model = fire_model
        self.max_turns = max_turns
        self.cell_capacity = cell_capacity
        self.current_turn = 0
        
        # Matriz para rastrear cuántas veces se ha transitado/intentado transitar una celda.
        # Los algoritmos leerán esto para penalizar rutas muy saturadas.
        self.congestion_map = np.zeros_like(self.env.grid, dtype=float)

    def _resolve_conflicts(self, intended_moves: Dict[int, Position]) -> Dict[int, Position]:
        """Resuelve embotellamientos si se supera la capacidad física de una celda."""
        actual_moves = {}
        # Agrupar agentes por la celda de destino deseada
        destination_groups: Dict[Tuple[int, int], List[int]] = {}
        
        for agent_id, pos in intended_moves.items():
            coord = (pos.x, pos.y)
            if coord not in destination_groups:
                destination_groups[coord] = []
            destination_groups[coord].append(agent_id)

        # Resolver bloqueos locales
        for coord, agents_requesting in destination_groups.items():
            # Aumentar la penalización en el mapa de congestión por alta demanda
            self.congestion_map[coord[1], coord[0]] += len(agents_requesting)

            if len(agents_requesting) <= self.cell_capacity:
                # No hay bloqueo, todos avanzan
                for a_id in agents_requesting:
                    actual_moves[a_id] = Position(coord[0], coord[1])
            else:
                # Cuello de botella detectado: Seleccionar aleatoriamente quiénes logran pasar
                random.shuffle(agents_requesting)
                winners = agents_requesting[:self.cell_capacity]
                losers = agents_requesting[self.cell_capacity:]
                
                for w_id in winners:
                    actual_moves[w_id] = Position(coord[0], coord[1])
                for l_id in losers:
                    # Los perdedores ejecutan la acción de 'esperar' en su posición actual
                    agent = next(a for a in self.env.agents if a.id == l_id)
                    actual_moves[l_id] = agent.pos

        return actual_moves

    def step(self, agent_actions: Dict[int, Position]) -> bool:
        """
        Ejecuta un turno completo de la simulación.
        :param agent_actions: Diccionario con la posición deseada (ortogonal o actual) por cada agente vivo.
        :return: True si la simulación debe continuar, False si terminó.
        """
        self.current_turn += 1

        # 1. Resolver congestión de movimientos (bloqueos)
        actual_moves = self._resolve_conflicts(agent_actions)

        # 2. Actualizar posiciones de los agentes en el entorno
        for agent in self.env.agents:
            if agent.is_dead or agent.is_evacuated:
                continue
                
            new_pos = actual_moves.get(agent.id, agent.pos)
            
            # Liberar celda anterior (opcional, dependiendo de si quieres visualizar P en la grilla)
            if self.env.grid[agent.pos.y, agent.pos.x] == CellType.PERSON.value:
                self.env.grid[agent.pos.y, agent.pos.x] = CellType.FREE.value
                
            agent.pos = new_pos
            
            # Verificar si alcanzó la salida
            if agent.pos == self.env.exit_pos:
                agent.is_evacuated = True
            else:
                # Marcar nueva posición (si no es salida)
                self.env.grid[agent.pos.y, agent.pos.x] = CellType.PERSON.value

        # 3. Propagar el fuego irreversiblemente
        new_fire_cells = self.fire_model.step()

        # 4. Verificar bajas humanas (si el fuego alcanza a un agente)
        for agent in self.env.agents:
            if not agent.is_evacuated and not agent.is_dead:
                if self.env.grid[agent.pos.y, agent.pos.x] == CellType.FIRE.value:
                    agent.is_dead = True

        # Criterios de parada
        active_agents = sum(1 for a in self.env.agents if not a.is_evacuated and not a.is_dead)
        if active_agents == 0 or self.current_turn >= self.max_turns:
            return False
            
        return True