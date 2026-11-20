# src/servicio/optimizador.py

# Los costos del catálogo tienen un decimal (0.8, 7.5, ...). La tabla dp necesita
# índices enteros, así que el costo y el presupuesto se trabajan en décimas de
# unidad (0.8 -> 8, 7.5 -> 75). Así no se pierde precisión ni se excede el presupuesto.
ESCALA = 10


def _a_entero(valor: float) -> int:
    """Convierte un monto a décimas de unidad (entero)."""
    return round(valor * ESCALA)


def calcular_puntaje_nutricional(alimento: dict) -> float:
    """Puntaje compuesto: suma aportes positivos (calorías, proteína) y resta
    penalizaciones (sodio, grasas saturadas), cada uno como % de su meta diaria
    y con un ponderador fijo."""
    META_CALORIAS = 2250.0  # punto medio del rango diario 2000-2500 kcal
    META_PROTEINA = 120.0   # mínimo diario en gramos
    LIMITE_SODIO = 2300.0   # máximo diario en mg
    LIMITE_GRASAS = 70.0    # máximo diario en g

    pct_calorias = (alimento["calorias"] / META_CALORIAS) * 100
    pct_proteina = (alimento["proteina"] / META_PROTEINA) * 100
    pct_sodio = (alimento["sodio"] / LIMITE_SODIO) * 100
    pct_grasas = (alimento["grasas_sat"] / LIMITE_GRASAS) * 100

    puntaje = (pct_calorias * 0.35) + (pct_proteina * 0.45) - (pct_sodio * 0.10) - (pct_grasas * 0.10)
    return round(puntaje, 2)


def planificar_menu_optimizado(alimentos: list, presupuesto: float):
    """Mochila 0/1 por programación dinámica, O(N * Pmax).
    dp[i][p] = máximo puntaje usando los primeros i alimentos con presupuesto p.
    Devuelve (seleccionados, puntaje_total)."""
    if presupuesto <= 0 or not alimentos:
        return [], 0.0

    n = len(alimentos)
    capacidad = _a_entero(presupuesto)
    dp = [[0.0 for _ in range(capacidad + 1)] for _ in range(n + 1)]

    # Construcción de la tabla de memorización
    for i in range(1, n + 1):
        alimento = alimentos[i - 1]
        costo = _a_entero(alimento["costo"])
        valor = calcular_puntaje_nutricional(alimento)
        for p in range(capacidad + 1):
            dp[i][p] = dp[i - 1][p]                       # opción 1: no tomarlo
            if costo <= p:                                # opción 2: tomarlo si cabe
                dp[i][p] = max(dp[i][p], valor + dp[i - 1][p - costo])

    # Reconstrucción (backtracking): si el valor cambió respecto a la fila anterior,
    # el alimento i participó en la solución.
    seleccionados = []
    p = capacidad
    for i in range(n, 0, -1):
        if dp[i][p] != dp[i - 1][p]:
            alimento = alimentos[i - 1]
            seleccionados.append(alimento)
            p -= _a_entero(alimento["costo"])

    seleccionados.reverse()
    return seleccionados, dp[n][capacidad]


def planificar_menu_greedy(alimentos: list, presupuesto: float):
    """Estrategia voraz: ordena por eficiencia (puntaje / costo) y agrega mientras
    quepa en el presupuesto, O(N log N). No modifica el catálogo recibido.
    Devuelve (seleccionados, puntaje_total, costo_acumulado)."""
    if presupuesto <= 0 or not alimentos:
        return [], 0.0, 0.0

    capacidad = _a_entero(presupuesto)
    candidatos = []
    for alimento in alimentos:
        puntaje = calcular_puntaje_nutricional(alimento)
        if puntaje > 0:  # un alimento con puntaje no positivo nunca conviene
            eficiencia = puntaje / max(0.1, alimento["costo"])
            candidatos.append((eficiencia, puntaje, alimento))

    candidatos.sort(key=lambda c: c[0], reverse=True)

    seleccionados = []
    gastado = 0  # en décimas de unidad
    puntaje_total = 0.0
    for _, puntaje, alimento in candidatos:
        costo = _a_entero(alimento["costo"])
        if gastado + costo <= capacidad:
            seleccionados.append(alimento)
            gastado += costo
            puntaje_total += puntaje

    return seleccionados, puntaje_total, gastado / ESCALA
