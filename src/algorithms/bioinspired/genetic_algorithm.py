import random
from typing import List, Tuple, Optional
from src.environment.grid import Position, CellType, Environment
from src.algorithms.heuristics import manhattan_distance

class GeneticAlgorithm:
    def __init__(
        self,
        env: Environment,
        population_size: int = 40,
        generations: int = 50,
        chromosome_len: int = 35,
        mutation_rate: float = 0.08,
        tournament_size: int = 3
    ):
        self.env = env
        self.pop_size = population_size
        self.generations = generations
        self.chrom_len = chromosome_len
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size

        # Acciones: Arriba, Abajo, Izquierda, Derecha, Esperar
        self.actions: List[Tuple[int, int]] = [
            (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)
        ]

    def _generate_individual(self) -> List[Tuple[int, int]]:
        """Crea un cromosoma con una secuencia aleatoria de movimientos."""
        return [random.choice(self.actions) for _ in range(self.chrom_len)]

    def _simulate_path(self, start: Position, chromosome: List[Tuple[int, int]]) -> Tuple[float, List[Position]]:
        """Simula el cromosoma sobre la grilla y calcula su aptitud (fitness)."""
        current = Position(start.x, start.y)
        path = [current]
        reached_exit = False
        steps_taken = 0
        hit_fire = False

        rows, cols = self.env.grid.shape

        for dy, dx in chromosome:
            steps_taken += 1
            nx, ny = current.x + dx, current.y + dy

            # Validación de bordes y obstáculos
            if 0 <= ny < rows and 0 <= nx < cols:
                cell = self.env.grid[ny, nx]
                if cell == CellType.WALL.value:
                    # Choca con pared: no avanza
                    next_pos = current
                elif cell == CellType.FIRE.value:
                    hit_fire = True
                    next_pos = Position(nx, ny)
                else:
                    next_pos = Position(nx, ny)
            else:
                next_pos = current

            current = next_pos
            path.append(current)

            if current == self.env.exit_pos:
                reached_exit = True
                break

        # Función de fitness
        if reached_exit:
            fitness = 1000.0 - (steps_taken * 12.0)
        else:
            final_dist = manhattan_distance(current, self.env.exit_pos)
            fitness = - (final_dist * 20.0) - (steps_taken * 2.0)

        if hit_fire:
            fitness -= 500.0

        return fitness, path

    def _tournament_selection(self, population: List[List[Tuple[int, int]]], fitnesses: List[float]) -> List[Tuple[int, int]]:
        candidates = random.sample(list(range(len(population))), self.tournament_size)
        best_idx = max(candidates, key=lambda idx: fitnesses[idx])
        return list(population[best_idx])

    def _crossover(self, parent1: List[Tuple[int, int]], parent2: List[Tuple[int, int]]) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        if self.chrom_len < 2:
            return list(parent1), list(parent2)
        pt = random.randint(1, self.chrom_len - 1)
        child1 = parent1[:pt] + parent2[pt:]
        child2 = parent2[:pt] + parent1[pt:]
        return child1, child2

    def _mutate(self, chromosome: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        mutated = []
        for gene in chromosome:
            if random.random() < self.mutation_rate:
                mutated.append(random.choice(self.actions))
            else:
                mutated.append(gene)
        return mutated

    def find_path(self, start: Position) -> Optional[List[Position]]:
        """Evoluciona una población de secuencias de acción hacia la salida."""
        population = [self._generate_individual() for _ in range(self.pop_size)]
        best_overall_chrom = population[0]
        best_overall_fitness, best_overall_path = self._simulate_path(start, best_overall_chrom)

        for _ in range(self.generations):
            fitness_scores = []
            paths = []

            for chrom in population:
                fit, p = self._simulate_path(start, chrom)
                fitness_scores.append(fit)
                paths.append(p)
                if fit > best_overall_fitness:
                    best_overall_fitness = fit
                    best_overall_path = p
                    best_overall_chrom = chrom

            # Criterio de término anticipado si encuentra una ruta exitosa a la salida
            if best_overall_fitness > 500.0:
                return best_overall_path

            # Nueva generación con elitismo (preservar el mejor)
            new_population = [best_overall_chrom]

            while len(new_population) < self.pop_size:
                p1 = self._tournament_selection(population, fitness_scores)
                p2 = self._tournament_selection(population, fitness_scores)
                c1, c2 = self._crossover(p1, p2)
                new_population.append(self._mutate(c1))
                if len(new_population) < self.pop_size:
                    new_population.append(self._mutate(c2))

            population = new_population

        return best_overall_path if len(best_overall_path) > 1 else None