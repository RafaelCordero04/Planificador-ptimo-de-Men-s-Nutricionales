# Planificador Óptimo de Menús Nutricionales

Selecciona alimentos de un catálogo de 50 ítems (`data/alimentos.json`) maximizando un
puntaje nutricional compuesto bajo un presupuesto, con dos métodos:
programación dinámica (mochila 0/1, óptimo) y algoritmo voraz (Greedy, aproximado).

Proyecto de Análisis y Diseño de Algoritmos, Universidad Católica de Colombia.

## Estructura
```
data/alimentos.json          catálogo (50 alimentos)
src/modelo/alimento.py       clase Alimento
src/servicio/optimizador.py  puntaje, programación dinámica y Greedy
src/interfaz/main.py         menú de consola
tests/test_optimizador.py    pruebas unitarias
```

## Ejecutar (Python 3.8+, sin dependencias externas)
Desde la raíz del proyecto:
```
python -m src.interfaz.main
python -m unittest -v
```
