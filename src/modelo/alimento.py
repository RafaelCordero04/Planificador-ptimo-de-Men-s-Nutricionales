# src/modelo/alimento.py

class Alimento:
    """Entidad que representa un alimento del catálogo (costo y aportes por porción)."""

    def __init__(self, nombre: str, costo: float, calorias: float, proteina: float,
                 sodio: float, grasas_saturadas: float, categoria: str = ""):
        self.nombre = nombre
        self.costo = costo
        self.calorias = calorias
        self.proteina = proteina
        self.sodio = sodio
        self.grasas_saturadas = grasas_saturadas
        self.categoria = categoria

    @classmethod
    def desde_diccionario(cls, datos: dict) -> "Alimento":
        """Crea un Alimento a partir de un registro del JSON.
        Lanza KeyError si falta alguna clave obligatoria."""
        return cls(
            nombre=datos["nombre"],
            costo=datos["costo"],
            calorias=datos["calorias"],
            proteina=datos["proteina"],
            sodio=datos["sodio"],
            grasas_saturadas=datos["grasas_saturadas"],
            categoria=datos.get("categoria", ""),
        )

    def a_diccionario(self) -> dict:
        """Convierte el objeto en el diccionario que consume el optimizador."""
        return {
            "nombre": self.nombre,
            "costo": self.costo,
            "calorias": self.calorias,
            "proteina": self.proteina,
            "sodio": self.sodio,
            "grasas_saturadas": self.grasas_saturadas,
            "categoria": self.categoria,
        }
