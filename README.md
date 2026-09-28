# Tarea 1: Escape de la Torre - Inteligencia Artificial

## 1. Información General
* **Asignatura:** Inteligencia Artificial.
* **Actividad:** Tarea 1: Escape de la Torre.
* **Autor / Integrante:** Bastián Antonio Pérez Aguayo.
* **Fecha:** Septiembre 2026.

---

## 2. Descripción del Problema
Este proyecto implementa y evalúa un sistema de evacuación de emergencia ante un incendio dinámico dentro de una infraestructura con pasillos estrechos y una **única salida de escape**. El objetivo central es modelar la toma de decisiones y navegación de los agentes atrapados para maximizar la tasa de supervivencia y minimizar el tiempo de despeje, mitigando los cuellos de botella y bloqueos locales generados por la alta densidad de personas.

El entorno cuenta con:
* Modelado matricial 2D del edificio y obstáculos fijos.
* Propagación estocástica e irreversible del fuego controlada por semilla (`seed`).
* Resolución de conflictos de congestión y capacidad física de las celdas.

---

## 3. Algoritmos Implementados
La navegación se resuelve bajo tres paradigmas:

1. **Búsqueda No Informada:**
   * **BFS (Breadth-First Search):** Garantiza la ruta más corta en cantidad de pasos uniformes mediante una cola FIFO (`collections.deque`).
   * **DFS (Depth-First Search):** Explora trayectorias en profundidad mediante una pila LIFO sin garantías de optimalidad.
2. **Búsqueda Informada:**
   * **A\* (A-Estrella):** Optimiza la función $f(n) = g(n) + h(n)$ utilizando distancias acumuladas y cola de prioridad (`heapq`).
   * **Greedy Best-First Search:** Búsqueda voraz guiada exclusivamente por $f(n) = h(n)$ hacia la salida.
   * *Heurística implementada:* **Distancia Manhattan**, admisible y consistente para grillas con movimientos ortogonales en 4 direcciones.
3. **Optimización Bioinspirada:**
   * **Algoritmo Genético:** Implementación metaheurística propia. Modela secuencias de acciones como cromosomas, optimizados mediante selección por torneo, cruce en un punto (*crossover*), mutación aleatoria y elitismo con función de aptitud (*fitness*) penalizada por turnos y fuego.

---

## 4. Estructura del Repositorio
```text
tarea1_ia/
├── data/
│   └── maps/                         # Escenarios matriciales de prueba
│       ├── map1_bottleneck.txt       # Cuello de botella / Alta congestión
│       ├── map2_maze.txt             # Laberinto / Pasillos ciegos
│       └── map3_open.txt             # Espacio semiabierto
├── resultados/                       # Salidas de simulaciones
│   ├── graficos/                     # Figuras generadas (barras y boxplots)
│   ├── metricas_detalladas.csv       # Registro por iteración
│   └── metricas_resumen.csv          # Media, std, min y max
├── src/
│   ├── algorithms/                   # Implementaciones de búsqueda
│   │   ├── bioinspired/              # Algoritmo Genético
│   │   ├── informed/                 # A* y Greedy BFS
│   │   ├── uninformed/               # BFS y DFS
│   │   └── heuristics.py             # Distancia Manhattan
│   └── environment/                  # Motor de simulación
│       ├── fire.py                   # Modelo estocástico del fuego
│       ├── grid.py                   # Carga de mapa y entidades
│       └── simulator.py              # Ciclo de turnos y congestión
├── main.py                           # Simulación comparativa individual
├── run_experiments.py                # Benchmarking automatizado (80-200 iter)
├── requirements.txt                  # Dependencias del proyecto
└── README.md                         # Documentación del proyecto

```

---

## 5. Instalación y Configuración del Entorno

### Requisitos Previos

* **Python 3.10 o superior** (probado en entornos Linux / macOS / Windows).
* Gestor de paquetes `pip`.

### Paso 1: Clonar el repositorio

```bash
git clone [https://github.com/Bastyannee/tarea1_ia.git](https://github.com/Bastyannee/tarea1_ia.git)
cd tarea1_ia

```

### Paso 2: Crear y activar el entorno virtual

* **En Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate

```


* **En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

```



### Paso 3: Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt

```

---

## 6. Instrucciones de Ejecución

### A. Simulación Individual y Comparativa (`main.py`)

Permite ejecutar un turno completo de evaluación para los 5 algoritmos en un mapa específico:

```bash
# Ejecutar en el Mapa 1 por defecto (Bottleneck)
python main.py

# Ejecutar en otros escenarios y configurar semilla
python main.py --map data/maps/map2_maze.txt --seed 123
python main.py --map data/maps/map3_open.txt --seed 42

```

### B. Benchmarking Estadístico Automatizado (`run_experiments.py`)

Ejecuta la batería experimental requerida (mínimo 80 iteraciones por configuración de mapa y algoritmo) variando las semillas estocásticas:

```bash
# Ejecutar con 80 iteraciones (1200 simulaciones totales)
python run_experiments.py --iterations 80

# Ejecutar con 200 iteraciones (máxima significancia estadística)
python run_experiments.py --iterations 200

```

---

## 7. Métricas y Salidas Generadas

El script de benchmarking procesa los experimentos y exporta de forma automática:

1. **`resultados/metricas_resumen.csv`:** Tabla estadística agregada con **media, desviación estándar, valor mínimo y valor máximo** de:


* **Tasa de supervivencia:** Porcentaje de agentes que logran evacuar ($N_{\text{sobrevivientes}} / N_{\text{total}}$).


* **Tiempo de despeje:** Turnos consumidos hasta la salida del último sobreviviente.




2. **`resultados/graficos/supervivencia_comparativa.png`:** Gráfico de barras comparativo de supervivencia con barras de error por desviación estándar.
3. **`resultados/graficos/tiempo_despeje_boxplot.png`:** Diagramas de caja (*boxplots*) con la distribución y dispersión del tiempo de evacuación.

---

## 8. Declaración de Uso de Herramientas Externas e IA

En conformidad con las directrices académicas y el syllabus de la asignatura:

* Se utilizaron herramientas de inteligencia artificial generativa como apoyo durante el diseño conceptual de la arquitectura modular de software, la estructuración de scripts y la resolución de errores de compatibilidad de dependencias.


* Todo el código fuente, la lógica de los algoritmos de búsqueda (BFS, DFS, A*, Greedy BFS y Algoritmo Genético) y el análisis de resultados fueron revisados, adaptados e integrados de forma personalizada por el autor.
