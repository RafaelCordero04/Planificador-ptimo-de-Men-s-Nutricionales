# src/interfaz/main.py

from src.servicio.optimizador import planificar_menu_optimizado, planificar_menu_greedy

def main():
    # Catálogo de alimentos de prueba estructurado[cite: 8, 11]
    alimentos = [
        {"nombre": "Pollo", "costo": 5, "calorias": 300, "proteina": 40, "sodio": 70, "grasas_sat": 3},
        {"nombre": "Arroz", "costo": 2, "calorias": 250, "proteina": 5, "sodio": 5, "grasas_sat": 1},
        {"nombre": "Huevo", "costo": 1, "calorias": 70, "proteina": 6, "sodio": 60, "grasas_sat": 2},
        {"nombre": "Papa", "costo": 2, "calorias": 150, "proteina": 4, "sodio": 10, "grasas_sat": 0},
        {"nombre": "Lentejas", "costo": 3, "calorias": 230, "proteina": 18, "sodio": 15, "grasas_sat": 1}
    ]

    presupuesto = 10  # Presupuesto de prueba[cite: 11]

    print("=" * 50)
    print(" PLANIFICADOR ÓPTIMO DE MENÚS (PROGRAMACIÓN DINÁMICA)")
    print("=" * 50)
    print(f"Presupuesto disponible: ${presupuesto}\n")

    menu_dp, valor_total_dp = planificar_menu_optimizado(alimentos, presupuesto)
    
    costo_total = sum(item["costo"] for item in menu_dp)
    calorias_totales = sum(item["calorias"] for item in menu_dp)
    proteina_total = sum(item["proteina"] for item in menu_dp)

    print("Alimentos seleccionados:")
    for alimento in menu_dp:
        print(f" - {alimento['nombre']} (Costo: ${alimento['costo']}, Proteína: {alimento['proteina']}g)")

    print("-" * 50)
    print(f"Costo total acumulado: ${costo_total}")
    print(f"Calorías totales: {calorias_totales} kcal")
    print(f"Proteína total: {proteina_total} g")
    print(f"Puntaje Nutricional Óptimo (DP): {valor_total_dp}")
    print("=" * 50)

    # Ejecución comparativa con Greedy
    print("\n" + "=" * 50)
    print(" COMPARATIVA CON ENFOQUE GREEDY (VORAZ)")
    print("=" * 50)
    menu_greedy, valor_g, costo_g = planificar_menu_greedy(alimentos, presupuesto)
    print(f"Costo total Greedy: ${costo_g}")
    print(f"Puntaje Nutricional Greedy: {valor_g}")
    print("=" * 50)


if __name__ == "__main__":
    main()