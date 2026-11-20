# tests/test_optimizador.py
# Ejecutar desde la raíz del proyecto:  python -m unittest -v

import itertools
import random
import unittest

from src.interfaz.main import cargar_alimentos
from src.servicio.optimizador import (
    calcular_puntaje_nutricional,
    planificar_menu_optimizado,
    planificar_menu_greedy,
)


def mejor_por_fuerza_bruta(alimentos, presupuesto):
    """Referencia: prueba todos los subconjuntos (solo para catálogos pequeños)."""
    mejor = 0.0
    for r in range(len(alimentos) + 1):
        for combo in itertools.combinations(alimentos, r):
            if sum(a["costo"] for a in combo) <= presupuesto + 1e-9:
                mejor = max(mejor, sum(calcular_puntaje_nutricional(a) for a in combo))
    return mejor


class TestOptimizador(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogo = cargar_alimentos()

    def test_catalogo_tiene_50_alimentos(self):
        self.assertEqual(len(self.catalogo), 50)

    def test_dp_no_excede_presupuesto(self):
        for p in (1, 10, 25, 50, 100, 150):
            menu, _ = planificar_menu_optimizado(self.catalogo, p)
            self.assertLessEqual(sum(a["costo"] for a in menu), p + 1e-9)

    def test_greedy_no_excede_presupuesto(self):
        for p in (1, 10, 25, 50, 100, 150):
            menu, _, costo = planificar_menu_greedy(self.catalogo, p)
            self.assertLessEqual(costo, p + 1e-9)

    def test_dp_coincide_con_fuerza_bruta(self):
        random.seed(7)
        for _ in range(15):
            subconjunto = random.sample(self.catalogo, 10)
            p = random.choice([5, 8, 12, 20])
            _, puntaje = planificar_menu_optimizado(subconjunto, p)
            self.assertAlmostEqual(puntaje, mejor_por_fuerza_bruta(subconjunto, p), places=6)

    def test_dp_mayor_o_igual_que_greedy(self):
        for p in (5, 10, 15, 20, 30, 50, 100):
            _, v_dp = planificar_menu_optimizado(self.catalogo, p)
            _, v_gr, _ = planificar_menu_greedy(self.catalogo, p)
            self.assertGreaterEqual(v_dp + 1e-9, v_gr)

    def test_casos_limite_presupuesto(self):
        for p in (0, -5):
            self.assertEqual(planificar_menu_optimizado(self.catalogo, p), ([], 0.0))
            self.assertEqual(planificar_menu_greedy(self.catalogo, p), ([], 0.0, 0.0))
        # presupuesto menor que el alimento más barato
        self.assertEqual(planificar_menu_optimizado(self.catalogo, 0.5), ([], 0.0))

    def test_catalogo_vacio_y_un_solo_alimento(self):
        self.assertEqual(planificar_menu_optimizado([], 50), ([], 0.0))
        pollo = self.catalogo[0]
        menu, _ = planificar_menu_optimizado([pollo], 5)
        self.assertEqual(menu, [pollo])

    def test_penalizacion_por_sodio(self):
        base = {"nombre": "x", "costo": 1, "calorias": 100, "proteina": 10,
                "sodio": 0, "grasas_saturadas": 0}
        salado = dict(base, sodio=2300)
        self.assertLess(calcular_puntaje_nutricional(salado), calcular_puntaje_nutricional(base))

    def test_greedy_no_modifica_catalogo(self):
        antes = [dict(a) for a in self.catalogo]
        planificar_menu_greedy(self.catalogo, 50)
        self.assertEqual(antes, self.catalogo)


if __name__ == "__main__":
    unittest.main()
