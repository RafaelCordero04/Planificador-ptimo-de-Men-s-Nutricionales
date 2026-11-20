# src/interfaz/main.py

import json
from pathlib import Path

from src.modelo.alimento import Alimento
from src.servicio.optimizador import planificar_menu_optimizado, planificar_menu_greedy

RUTA_CATALOGO = Path(__file__).resolve().parents[2] / "data" / "alimentos.json"


def cargar_alimentos(ruta=RUTA_CATALOGO) -> list:
    """Lee el catálogo desde el JSON y lo entrega como lista de diccionarios."""
    with open(ruta, "r", encoding="utf-8") as archivo:
        registros = json.load(archivo)
    return [Alimento.desde_diccionario(r).a_diccionario() for r in registros]


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
    alimentos = cargar_alimentos()

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
            presupuesto = solicitar_presupuesto()
            mostrar_programacion_dinamica(alimentos, presupuesto)

        elif opcion == "2":
            presupuesto = solicitar_presupuesto()
            mostrar_greedy(alimentos, presupuesto)

        elif opcion == "3":
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
