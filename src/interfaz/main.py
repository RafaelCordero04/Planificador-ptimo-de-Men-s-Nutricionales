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


def solicitar_presupuesto() -> int:
    while True:
        try:
            presupuesto = int(input("Ingrese el presupuesto disponible: $"))

            if presupuesto > 0:
                return presupuesto
            else:
                print("El presupuesto debe ser mayor que cero.")

        except ValueError:
            print("Ingrese un número entero válido.")


def imprimir_resultado(titulo, menu, puntaje, costo):
    print(f"\n===== RESULTADO: {titulo} =====")
    print("Alimentos seleccionados:")
    for alimento in menu:
        print(f"- {alimento['nombre']} | Costo: ${alimento['costo']:.2f}")

    print("-" * 45)
    print(f"Costo total: ${costo:.2f}")
    print(f"Calorías totales: {sum(a['calorias'] for a in menu):.0f} kcal")
    print(f"Proteína total: {sum(a['proteina'] for a in menu):.1f} g")
    print(f"Grasas saturadas totales: {sum(a['grasas_saturadas'] for a in menu):.1f} g")
    print(f"Sodio total: {sum(a['sodio'] for a in menu):.0f} mg")
    print(f"Puntaje nutricional: {puntaje:.2f}")


def mostrar_programacion_dinamica(alimentos, presupuesto):
    menu, puntaje = planificar_menu_optimizado(alimentos, presupuesto)
    costo = sum(a["costo"] for a in menu)
    imprimir_resultado("PROGRAMACIÓN DINÁMICA", menu, puntaje, costo)
    return puntaje


def mostrar_greedy(alimentos, presupuesto):
    menu, puntaje, costo = planificar_menu_greedy(alimentos, presupuesto)
    imprimir_resultado("ALGORITMO GREEDY", menu, puntaje, costo)
    return puntaje


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
            p_dp = mostrar_programacion_dinamica(alimentos, presupuesto)
            p_gr = mostrar_greedy(alimentos, presupuesto)
            print(f"\nDiferencia de puntaje (DP - Greedy): {p_dp - p_gr:.2f}")

        elif opcion == "4":
            print("\nGracias por utilizar el planificador.")
            break

        else:
            print("\nOpción no válida. Intente nuevamente.")


if __name__ == "__main__":
    main()
