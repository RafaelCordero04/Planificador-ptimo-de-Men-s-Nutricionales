# tests/test_repositorio.py
# Ejecutar desde la raíz del proyecto:  python -m unittest -v

import unittest

from src.persistencia.repositorio import RepositorioMenus, validar_alimento
from src.servicio.optimizador import planificar_menu_optimizado

NUEVO = {"nombre": "Mango", "categoria": "fruta", "costo": 2.0, "calorias": 100,
         "proteina": 1.0, "sodio": 2, "grasas_saturadas": 0.1}


class TestRepositorio(unittest.TestCase):
    def setUp(self):
        self.repo = RepositorioMenus(":memory:")

    def tearDown(self):
        self.repo.cerrar()

    def test_siembra_desde_json(self):
        self.assertEqual(len(self.repo.listar_alimentos()), 50)

    def test_siembra_no_duplica(self):
        self.repo._sembrar(self.repo_semilla()) 
        self.assertEqual(len(self.repo.listar_alimentos()), 50)

    def repo_semilla(self):
        from src.persistencia.repositorio import RUTA_SEMILLA
        return RUTA_SEMILLA

    def test_crud_alimento(self):
        nuevo_id = self.repo.agregar_alimento(NUEVO)
        self.assertEqual(len(self.repo.listar_alimentos()), 51)
        self.repo.actualizar_alimento(nuevo_id, dict(NUEVO, costo=3.5))
        mango = [a for a in self.repo.listar_alimentos() if a["id"] == nuevo_id][0]
        self.assertEqual(mango["costo"], 3.5)
        self.repo.eliminar_alimento(nuevo_id)
        self.assertEqual(len(self.repo.listar_alimentos()), 50)

    def test_actualizar_inexistente(self):
        with self.assertRaises(KeyError):
            self.repo.actualizar_alimento(9999, NUEVO)

    def test_validaciones(self):
        with self.assertRaises(ValueError):
            validar_alimento(dict(NUEVO, nombre="  "))
        with self.assertRaises(ValueError):
            validar_alimento(dict(NUEVO, costo=0))
        with self.assertRaises(ValueError):
            validar_alimento(dict(NUEVO, sodio=-1))
        with self.assertRaises(ValueError):
            validar_alimento(dict(NUEVO, proteina="abc"))
        self.assertEqual(validar_alimento(dict(NUEVO, costo="2,5"))["costo"], 2.5)

    def test_catalogo_compatible_con_optimizador(self):
        menu, puntaje = planificar_menu_optimizado(self.repo.listar_alimentos(), 20)
        self.assertGreater(puntaje, 0)
        self.assertLessEqual(sum(a["costo"] for a in menu), 20 + 1e-9)

    def test_historial(self):
        menu, puntaje = planificar_menu_optimizado(self.repo.listar_alimentos(), 10)
        costo = sum(a["costo"] for a in menu)
        id_menu = self.repo.guardar_menu("Programación dinámica", 10, menu, puntaje, costo)
        historial = self.repo.listar_historial()
        self.assertEqual(len(historial), 1)
        self.assertEqual(historial[0]["id"], id_menu)
        self.assertEqual(len(historial[0]["alimentos"]), len(menu))
        self.repo.eliminar_historial(id_menu)
        self.assertEqual(self.repo.listar_historial(), [])


if __name__ == "__main__":
    unittest.main()