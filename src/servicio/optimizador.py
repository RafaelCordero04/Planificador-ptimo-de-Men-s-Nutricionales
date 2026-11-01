# src/servicio/optimizador.py

def calcular_puntaje_nutricional(alimento: dict) -> float:
    """Calcula un puntaje nutricional compuesto sumando aportes positivos 
    y penalizando excesos negativos (sodio y grasas saturadas)."""
    META_CALORIAS = 2250.0  # Rango base diario sugerido
    META_PROTEINA = 120.0   # Mínimo recomendado en gramos
    LIMITE_SODIO = 2300.0   # mg máximos permitidos
    LIMITE_GRASAS = 70.0    # g máximos permitidos

    pct_calorias = (alimento["calorias"] / META_CALORIAS) * 100
    pct_proteina = (alimento["proteina"] / META_PROTEINA) * 100
    pct_sodio = (alimento["sodio"] / LIMITE_SODIO) * 100
    pct_grasas = (alimento["grasas_sat"] / LIMITE_GRASAS) * 100

    # Ponderación multicriterio
    puntaje = (pct_calorias * 0.35) + (pct_proteina * 0.45) - (pct_sodio * 0.10) - (pct_grasas * 0.10)
    return max(0.1, round(puntaje, 2))


def planificar_menu_optimizado(alimentos: list, presupuesto: float):
    """Resuelve la selección óptima mediante Programación Dinámica O(N * P_max)[cite: 8, 9, 12]."""
    n = len(alimentos)
    # dp[i][p] representa el máximo valor nutricional utilizando los primeros i alimentos con presupuesto p[cite: 12]
    dp = [[0.0 for _ in range(int(presupuesto) + 1)] for _ in range(n + 1)]

    # Construcción de la tabla de memorización[cite: 12]
    for i in range(1, n + 1):
        alimento = alimentos[i - 1]
        costo = int(alimento["costo"])
        valor = calcular_puntaje_nutricional(alimento)
        for p in range(int(presupuesto) + 1):
            dp[i][p] = dp[i - 1][p]
            if costo <= p:
                valor_con_alimento = valor + dp[i - 1][p - costo]
                dp[i][p] = max(dp[i][p], valor_con_alimento)

    # Reconstrucción de la solución (Backtracking)[cite: 12, 13]
    seleccionados = []
    p = int(presupuesto)
    for i in range(n, 0, -1):
        if dp[i][p] != dp[i - 1][p]:
            alimento = alimentos[i - 1]
            seleccionados.append(alimento)
            p -= int(alimento["costo"])

    seleccionados.reverse()
    return seleccionados, dp[n][int(presupuesto)]


def planificar_menu_greedy(alimentos: list, presupuesto: float):
    """Estrategia voraz basada en la eficiencia (puntaje por unidad monetaria)."""
    for alimento in alimentos:
        puntaje = calcular_puntaje_nutricional(alimento)
        alimento["eficiencia"] = puntaje / max(0.1, alimento["costo"])

    alimentos_ordenados = sorted(alimentos, key=lambda x: x["eficiencia"], reverse=True)
    seleccionados = []
    costo_acumulado = 0.0
    puntaje_total = 0.0

    for alimento in alimentos_ordenados:
        if costo_acumulado + alimento["costo"] <= presupuesto:
            seleccionados.append(alimento)
            costo_acumulado += alimento["costo"]
            puntaje_total += calcular_puntaje_nutricional(alimento)

    return seleccionados, puntaje_total, costo_acumulado