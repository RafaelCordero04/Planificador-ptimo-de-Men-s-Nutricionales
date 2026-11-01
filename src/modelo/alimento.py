# src/modelo/alimento.py

class Alimento:
    def __init__(self, nombre: str, costo: float, calorias: float, proteina: float, sodio: float, grasas_sat: float):
        self.nombre = nombre
        self.costo = costo
        self.calorias = calorias
        self.proteina = proteina
        self.sodio = sodio
        self.grasas_sat = grasas_sat

    def a_diccionario(self) -> dict:
        return {
            "nombre": self.nombre,
            "costo": self.costo,
            "calorias": self.calorias,
            "proteina": self.proteina,
            "sodio": self.sodio,
            "grasas_sat": self.grasas_sat
        }