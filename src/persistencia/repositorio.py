# src/persistencia/repositorio.py
"""Persistencia en SQLite (módulo nativo sqlite3, sin dependencias externas).

Tablas:
  alimentos         -> catálogo editable (se siembra desde data/alimentos.json)
  historial_menus   -> menús generados (fecha, algoritmo, presupuesto, costo, puntaje)
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RUTA_DB = RAIZ / "data" / "menus.db"
RUTA_SEMILLA = RAIZ / "data" / "alimentos.json"

CAMPOS_TEXTO = ("nombre", "categoria")
CAMPOS_NUMERICOS = ("costo", "calorias", "proteina", "sodio", "grasas_saturadas")


def validar_alimento(datos: dict) -> dict:
    """Valida y normaliza un alimento. Lanza ValueError con un mensaje claro."""
    limpio = {}
    nombre = str(datos.get("nombre", "")).strip()
    if not nombre:
        raise ValueError("El nombre no puede estar vacío.")
    limpio["nombre"] = nombre
    limpio["categoria"] = str(datos.get("categoria", "")).strip()

    for campo in CAMPOS_NUMERICOS:
        try:
            valor = float(str(datos.get(campo, "")).replace(",", "."))
        except ValueError:
            raise ValueError(f"'{campo}' debe ser un número.")
        if valor < 0:
            raise ValueError(f"'{campo}' no puede ser negativo.")
        limpio[campo] = valor
    if limpio["costo"] <= 0:
        raise ValueError("El costo debe ser mayor que cero.")
    return limpio


class RepositorioMenus:
    def __init__(self, ruta_db=RUTA_DB, ruta_semilla=RUTA_SEMILLA):
        """ruta_db=':memory:' crea una base temporal (útil para pruebas)."""
        if ruta_db != ":memory:":
            Path(ruta_db).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(ruta_db))
        self.conn.row_factory = sqlite3.Row
        self._crear_tablas()
        self._sembrar(ruta_semilla)

    # ---------- esquema ----------
    def _crear_tablas(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS alimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL DEFAULT '',
                costo REAL NOT NULL,
                calorias REAL NOT NULL,
                proteina REAL NOT NULL,
                sodio REAL NOT NULL,
                grasas_saturadas REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS historial_menus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                algoritmo TEXT NOT NULL,
                presupuesto REAL NOT NULL,
                costo_total REAL NOT NULL,
                puntaje REAL NOT NULL,
                alimentos TEXT NOT NULL      -- JSON: lista de {nombre, costo}
            );
        """)
        self.conn.commit()

    def _sembrar(self, ruta_semilla):
        """Carga el catálogo inicial desde el JSON solo si la tabla está vacía."""
        total = self.conn.execute("SELECT COUNT(*) FROM alimentos").fetchone()[0]
        if total or not ruta_semilla or not Path(ruta_semilla).exists():
            return
        with open(ruta_semilla, "r", encoding="utf-8") as f:
            for registro in json.load(f):
                self._insertar(validar_alimento(registro))
        self.conn.commit()

    # ---------- catálogo (CRUD) ----------
    def _insertar(self, a: dict) -> int:
        cur = self.conn.execute(
            "INSERT INTO alimentos (nombre, categoria, costo, calorias, proteina, sodio, grasas_saturadas) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (a["nombre"], a["categoria"], a["costo"], a["calorias"],
             a["proteina"], a["sodio"], a["grasas_saturadas"]))
        return cur.lastrowid

    def listar_alimentos(self) -> list:
        """Mismo formato (lista de dicts) que consume el optimizador."""
        filas = self.conn.execute("SELECT * FROM alimentos ORDER BY id").fetchall()
        return [dict(f) for f in filas]

    def agregar_alimento(self, datos: dict) -> int:
        nuevo_id = self._insertar(validar_alimento(datos))
        self.conn.commit()
        return nuevo_id

    def actualizar_alimento(self, id_alimento: int, datos: dict) -> None:
        a = validar_alimento(datos)
        cur = self.conn.execute(
            "UPDATE alimentos SET nombre=?, categoria=?, costo=?, calorias=?, proteina=?, "
            "sodio=?, grasas_saturadas=? WHERE id=?",
            (a["nombre"], a["categoria"], a["costo"], a["calorias"], a["proteina"],
             a["sodio"], a["grasas_saturadas"], id_alimento))
        if cur.rowcount == 0:
            raise KeyError(f"No existe el alimento con id {id_alimento}.")
        self.conn.commit()

    def eliminar_alimento(self, id_alimento: int) -> None:
        self.conn.execute("DELETE FROM alimentos WHERE id=?", (id_alimento,))
        self.conn.commit()

    # ---------- historial ----------
    def guardar_menu(self, algoritmo: str, presupuesto: float, menu: list,
                     puntaje: float, costo_total: float) -> int:
        detalle = json.dumps([{"nombre": a["nombre"], "costo": a["costo"]} for a in menu],
                             ensure_ascii=False)
        cur = self.conn.execute(
            "INSERT INTO historial_menus (fecha, algoritmo, presupuesto, costo_total, puntaje, alimentos) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), algoritmo, presupuesto,
             costo_total, puntaje, detalle))
        self.conn.commit()
        return cur.lastrowid

    def listar_historial(self) -> list:
        filas = self.conn.execute("SELECT * FROM historial_menus ORDER BY id DESC").fetchall()
        registros = []
        for f in filas:
            r = dict(f)
            r["alimentos"] = json.loads(r["alimentos"])
            registros.append(r)
        return registros

    def eliminar_historial(self, id_menu: int) -> None:
        self.conn.execute("DELETE FROM historial_menus WHERE id=?", (id_menu,))
        self.conn.commit()

    def cerrar(self):
        self.conn.close()