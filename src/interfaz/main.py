# src/interfaz/main.py

from src.servicio.optimizador import planificar_menu_optimizado, planificar_menu_greedy


def cargar_alimentos():
    alimentos = [
        {"nombre": "Pollo", "costo": 5, "calorias": 300, "proteina": 40, "sodio": 70, "grasas_sat": 3},
        {"nombre": "Arroz", "costo": 2, "calorias": 250, "proteina": 5, "sodio": 5, "grasas_sat": 1},
        {"nombre": "Huevo", "costo": 1, "calorias": 70, "proteina": 6, "sodio": 60, "grasas_sat": 2},
        {"nombre": "Papa", "costo": 2, "calorias": 150, "proteina": 4, "sodio": 10, "grasas_sat": 0},
        {"nombre": "Lentejas", "costo": 3, "calorias": 230, "proteina": 18, "sodio": 15, "grasas_sat": 1}
    ]
    return alimentos


def solicitar_presupuesto():
    while True:
        try:
            presupuesto = int(input("Ingrese el presupuesto disponible: $"))

            if presupuesto > 0:
                return presupuesto
            else:
                print("El presupuesto debe ser mayor que cero.")

        except ValueError:
            print("Ingrese un número entero válido.")


def mostrar_programacion_dinamica(alimentos, presupuesto):
    menu, puntaje = planificar_menu_optimizado(alimentos, presupuesto)

    costo_total = sum(item["costo"] for item in menu)
    calorias_totales = sum(item["calorias"] for item in menu)
    proteina_total = sum(item["proteina"] for item in menu)

    print("\n===== RESULTADO: PROGRAMACIÓN DINÁMICA =====")
    print("Alimentos seleccionados:")

    for alimento in menu:
        print(f"- {alimento['nombre']} | Costo: ${alimento['costo']}")

    print("-------------------------------------------")
    print(f"Costo total: ${costo_total}")
    print(f"Calorías totales: {calorias_totales} kcal")
    print(f"Proteína total: {proteina_total} g")
    print(f"Puntaje nutricional: {puntaje}")


def mostrar_greedy(alimentos, presupuesto):
    menu, puntaje, costo = planificar_menu_greedy(alimentos, presupuesto)

    calorias = sum(item["calorias"] for item in menu)
    proteina = sum(item["proteina"] for item in menu)

    print("\n===== RESULTADO: ALGORITMO GREEDY =====")
    print("Alimentos seleccionados:")

    for alimento in menu:
        print(f"- {alimento['nombre']} | Costo: ${alimento['costo']}")

    print("--------------------------------------")
    print(f"Costo total: ${costo}")
    print(f"Calorías totales: {calorias} kcal")
    print(f"Proteína total: {proteina} g")
    print(f"Puntaje nutricional: {puntaje}")


def main():
    while True:
        print("\n==========================================")
        print(" PLANIFICADOR ÓPTIMO DE MENÚS NUTRICIONALES")
        print("==========================================")
        print("1. Planificar con programación dinámica")
        print("2. Planificar con algoritmo Greedy")
        print("3. Comparar ambos algoritmos")
        print("4. Salir")
        print("==========================================")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            alimentos = cargar_alimentos()
            presupuesto = solicitar_presupuesto()
            mostrar_programacion_dinamica(alimentos, presupuesto)

        elif opcion == "2":
            alimentos = cargar_alimentos()
            presupuesto = solicitar_presupuesto()
            mostrar_greedy(alimentos, presupuesto)

        elif opcion == "3":
            alimentos = cargar_alimentos()
            presupuesto = solicitar_presupuesto()

            mostrar_programacion_dinamica(alimentos, presupuesto)
            mostrar_greedy(alimentos, presupuesto)

        elif opcion == "4":
            print("\nGracias por utilizar el planificador.")
            break

        else:
            print("\nOpción no válida. Intente nuevamente.")


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()
