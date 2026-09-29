# Informe Técnico: Tarea 1 - Escape de la Torre

## 1. Descripción y Funcionamiento de los Algoritmos

El objetivo principal de esta implementación es modelar la toma de decisiones de agentes en un entorno adverso, buscando minimizar las pérdidas humanas y mitigar la congestión durante una evacuación. Para ello, se evaluaron tres paradigmas de búsqueda:

### Búsqueda No Informada

Estos métodos exploran el espacio de estados sin información adicional sobre la ubicación de la meta.

* **Búsqueda en Amplitud (BFS):** Opera mediante una estructura de datos de tipo cola (FIFO), expandiendo los nodos nivel por nivel al momento de generarlos. Este algoritmo garantiza encontrar la ruta óptima siempre que el costo de cada paso sea uniforme.


* **Búsqueda en Profundidad (DFS):** Utiliza una estructura de pila (LIFO) para expandir los nodos, explorando una rama hasta su máxima profundidad antes de retroceder. No es un algoritmo óptimo ni completo en espacios infinitos o con ciclos, lo que significa que puede generar rutas innecesariamente largas.



### Búsqueda Informada

Estos algoritmos utilizan funciones heurísticas para estimar el costo hacia la meta y priorizar la exploración.

* **Búsqueda Voraz (Greedy Best-First):** Selecciona el siguiente paso basándose exclusivamente en la heurística, evaluando $f(n) = h(n)$. Aunque suele ser rápido, no es óptimo y puede caer en bucles al ignorar el costo acumulado de la ruta.


* **Búsqueda A* (A-Star):** Combina el costo acumulado desde el inicio con la estimación hacia la meta mediante la función $f(n) = g(n) + h(n)$. Es un algoritmo completo y óptimo siempre que la heurística utilizada sea admisible o consistente.



### Optimización Bioinspirada

* **Algoritmo Genético:** Es un método metaheurístico inspirado en la evolución biológica que trabaja con una población de estados. El algoritmo optimiza las rutas a través de tres fases clave: **Selección** de los individuos más aptos, **Cruce** para combinar características de rutas exitosas, y **Mutación**, que introduce cambios aleatorios para evitar que la población se estanque en óptimos locales (convergencia prematura).



---

## 2. Justificación de Heurísticas

### Admisibilidad de la Distancia Manhattan

Para la búsqueda informada (A* y Greedy BFS), se requiere una heurística admisible, es decir, una función que nunca sobreestime el costo real para alcanzar la meta. En esta simulación, los agentes se desplazan a través de una cuadrícula donde solo se permiten movimientos ortogonales (arriba, abajo, izquierda, derecha). Bajo esta restricción geométrica, la Distancia Manhattan calcula exactamente el número mínimo de pasos necesarios para llegar a la salida si no existieran obstáculos. Por lo tanto, cumple con las propiedades de consistencia y admisibilidad, garantizando que A* encuentre la ruta óptima.

### Función de Aptitud (*Fitness*) del Algoritmo Genético

La función de evaluación para el Algoritmo Genético fue diseñada para reflejar las restricciones críticas del entorno de emergencia. Para maximizar la supervivencia y reducir el tiempo de exposición, el *fitness* otorga una alta bonificación por alcanzar la coordenada de escape y penaliza proporcionalmente la cantidad de turnos invertidos. Adicionalmente, aplica una penalización drástica si la ruta atraviesa celdas con fuego, forzando a la población a priorizar caminos despejados y seguros a lo largo de las generaciones.

---

## 3. Análisis Comparativo de Resultados

*(Nota para el documento: Inserta aquí la imagen `resultados/graficos/supervivencia_comparativa.png`)*

*(Nota para el documento: Inserta aquí la imagen `resultados/graficos/tiempo_despeje_boxplot.png`)*

De acuerdo con las restricciones del proyecto, el análisis se centra en la tasa de supervivencia, definida como el porcentaje de agentes que logran evacuar con éxito respecto al total inicial, y en los estadísticos descriptivos del tiempo total de despeje (media, desviación estándar, valor mínimo y valor máximo) correspondiente al número de turnos que le tomó al último sobreviviente en alcanzar la salida.

Al contrastar los datos exportados en `resultados/metricas_resumen.csv`, se observa una clara segmentación en el rendimiento de los paradigmas:

* **Efectividad de Evacuación:** Los algoritmos BFS y A* presentan consistentemente la mayor tasa de supervivencia media, logrando ratios cercanos al 100% en mapas abiertos y con cuellos de botella simples. Por el contrario, DFS muestra la mayor varianza (desviación estándar) y los valores mínimos más críticos en la tasa de supervivencia.
* **Tiempos de Despeje:** Los estadísticos de tiempo revelan que A* y BFS mantienen las medias de turnos más bajas y con menor dispersión. El Algoritmo Genético presenta tiempos de despeje competitivos, aunque con una dispersión ligeramente mayor debido a su naturaleza estocástica.



---

## 4. Conclusiones

La simulación de evacuación bajo condiciones de fuego dinámico demuestra que la elección del algoritmo de navegación es un factor determinante para la supervivencia. Algoritmos como BFS y A* preservan un mayor índice de supervivencia frente a DFS debido a sus garantías teóricas: BFS es óptimo asumiendo costos uniformes, y A* es óptimo gracias a su heurística admisible. Al calcular consistentemente la ruta más corta, ambos métodos minimizan el número de turnos que los agentes pasan transitando por la infraestructura, reduciendo significativamente la ventana de tiempo en la que pueden ser alcanzados por la propagación del incendio.

Por otro lado, DFS expande nodos en profundidad al momento de insertarlos en su pila (LIFO) y no garantiza la ruta más corta. En escenarios complejos como laberintos o cuellos de botella, esta falta de optimalidad provoca que los agentes realicen extensos recorridos ineficientes o se dirijan hacia callejones sin salida. En un entorno estático esto solo representaría una pérdida de eficiencia computacional, pero en un entorno dinámico donde el fuego avanza cada turno, el exceso de pasos dictados por DFS resulta en embotellamientos prolongados y en una caída drástica de la tasa de supervivencia poblacional.