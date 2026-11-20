# src/interfaz/gui.py
"""Interfaz de escritorio (Tkinter). Ejecutar desde la raíz del proyecto:
    python -m src.interfaz.gui
"""

import tkinter as tk
from tkinter import ttk, messagebox

from src.persistencia.repositorio import RepositorioMenus
from src.servicio.optimizador import planificar_menu_optimizado, planificar_menu_greedy

NOMBRE_DP = "Programación dinámica"
NOMBRE_GREEDY = "Greedy"


def totales(menu: list) -> dict:
    return {
        "costo": sum(a["costo"] for a in menu),
        "calorias": sum(a["calorias"] for a in menu),
        "proteina": sum(a["proteina"] for a in menu),
        "sodio": sum(a["sodio"] for a in menu),
        "grasas": sum(a["grasas_saturadas"] for a in menu),
    }


class PanelResultado(ttk.LabelFrame):
    """Tabla de alimentos seleccionados + resumen de totales de un algoritmo."""

    def __init__(self, padre, titulo):
        super().__init__(padre, text=titulo, padding=6)
        self.tabla = ttk.Treeview(self, columns=("nombre", "costo"), show="headings", height=10)
        self.tabla.heading("nombre", text="Alimento")
        self.tabla.heading("costo", text="Costo ($)")
        self.tabla.column("nombre", width=220)
        self.tabla.column("costo", width=70, anchor="e")
        self.tabla.pack(fill="both", expand=True)
        self.resumen = ttk.Label(self, text="", justify="left")
        self.resumen.pack(anchor="w", pady=(6, 0))

    def mostrar(self, menu, puntaje):
        self.tabla.delete(*self.tabla.get_children())
        for a in menu:
            self.tabla.insert("", "end", values=(a["nombre"], f"{a['costo']:.2f}"))
        t = totales(menu)
        self.resumen.config(text=(
            f"Costo total: ${t['costo']:.2f}\n"
            f"Calorías: {t['calorias']:.0f} kcal   Proteína: {t['proteina']:.1f} g\n"
            f"Grasas saturadas: {t['grasas']:.1f} g   Sodio: {t['sodio']:.0f} mg\n"
            f"Puntaje nutricional: {puntaje:.2f}"))

    def limpiar(self):
        self.tabla.delete(*self.tabla.get_children())
        self.resumen.config(text="")


class App(tk.Tk):
    def __init__(self, repo: RepositorioMenus):
        super().__init__()
        self.repo = repo
        self.title("Planificador Óptimo de Menús Nutricionales")
        self.geometry("900x600")
        self.minsize(820, 540)

        cuaderno = ttk.Notebook(self)
        cuaderno.pack(fill="both", expand=True, padx=8, pady=8)
        self.tab_plan = ttk.Frame(cuaderno)
        self.tab_cat = ttk.Frame(cuaderno)
        self.tab_hist = ttk.Frame(cuaderno)
        cuaderno.add(self.tab_plan, text="Planificar")
        cuaderno.add(self.tab_cat, text="Catálogo")
        cuaderno.add(self.tab_hist, text="Historial")
        cuaderno.bind("<<NotebookTabChanged>>", lambda e: self._refrescar_historial())

        self._armar_planificar()
        self._armar_catalogo()
        self._armar_historial()
        self._refrescar_catalogo()
        self._refrescar_historial()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    def _cerrar(self):
        self.repo.cerrar()
        self.destroy()

    # ------------------------------------------------------------ Planificar
    def _armar_planificar(self):
        barra = ttk.Frame(self.tab_plan, padding=8)
        barra.pack(fill="x")
        ttk.Label(barra, text="Presupuesto ($):").pack(side="left")
        self.var_presupuesto = tk.StringVar(value="20")
        ttk.Entry(barra, textvariable=self.var_presupuesto, width=10).pack(side="left", padx=6)

        self.var_algoritmo = tk.StringVar(value="comparar")
        for texto, valor in (("Prog. dinámica", "dp"), ("Greedy", "greedy"), ("Comparar ambos", "comparar")):
            ttk.Radiobutton(barra, text=texto, value=valor, variable=self.var_algoritmo).pack(side="left", padx=6)
        ttk.Button(barra, text="Planificar", command=self._planificar).pack(side="left", padx=10)

        zona = ttk.Frame(self.tab_plan, padding=8)
        zona.pack(fill="both", expand=True)
        zona.columnconfigure((0, 1), weight=1, uniform="col")
        zona.rowconfigure(0, weight=1)
        self.panel_dp = PanelResultado(zona, NOMBRE_DP)
        self.panel_gr = PanelResultado(zona, NOMBRE_GREEDY)
        self.panel_dp.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        self.panel_gr.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        self.lbl_diferencia = ttk.Label(self.tab_plan, text="", font=("TkDefaultFont", 10, "bold"))
        self.lbl_diferencia.pack(pady=(0, 8))

    def _leer_presupuesto(self):
        try:
            valor = int(self.var_presupuesto.get())
        except ValueError:
            messagebox.showerror("Dato inválido", "Ingrese un número entero válido.")
            return None
        if valor <= 0:
            messagebox.showerror("Dato inválido", "El presupuesto debe ser mayor que cero.")
            return None
        return valor

    def _planificar(self):
        presupuesto = self._leer_presupuesto()
        if presupuesto is None:
            return
        alimentos = self.repo.listar_alimentos()  # siempre el catálogo vigente en la BD
        modo = self.var_algoritmo.get()
        self.panel_dp.limpiar()
        self.panel_gr.limpiar()
        self.lbl_diferencia.config(text="")
        p_dp = p_gr = None

        if modo in ("dp", "comparar"):
            menu, p_dp = planificar_menu_optimizado(alimentos, presupuesto)
            self.panel_dp.mostrar(menu, p_dp)
            self.repo.guardar_menu(NOMBRE_DP, presupuesto, menu, p_dp, totales(menu)["costo"])
        if modo in ("greedy", "comparar"):
            menu, p_gr, costo = planificar_menu_greedy(alimentos, presupuesto)
            self.panel_gr.mostrar(menu, p_gr)
            self.repo.guardar_menu(NOMBRE_GREEDY, presupuesto, menu, p_gr, costo)
        if modo == "comparar":
            self.lbl_diferencia.config(text=f"Diferencia de puntaje (DP - Greedy): {p_dp - p_gr:.2f}")
        self._refrescar_historial()

    # --------------------------------------------------------------- Catálogo
    CAMPOS = (("nombre", "Nombre"), ("categoria", "Categoría"), ("costo", "Costo"),
              ("calorias", "Calorías"), ("proteina", "Proteína"), ("sodio", "Sodio"),
              ("grasas_saturadas", "Grasas sat."))

    def _armar_catalogo(self):
        cols = [c for c, _ in self.CAMPOS]
        marco = ttk.Frame(self.tab_cat, padding=8)
        marco.pack(fill="both", expand=True)
        self.tabla_cat = ttk.Treeview(marco, columns=cols, show="headings", height=14)
        for c, t in self.CAMPOS:
            self.tabla_cat.heading(c, text=t)
            self.tabla_cat.column(c, width=170 if c == "nombre" else 85, anchor="w" if c in ("nombre", "categoria") else "e")
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla_cat.yview)
        self.tabla_cat.configure(yscrollcommand=barra.set)
        self.tabla_cat.pack(side="top", fill="both", expand=True)
        self.tabla_cat.bind("<<TreeviewSelect>>", self._cargar_seleccion)

        form = ttk.Frame(self.tab_cat, padding=8)
        form.pack(fill="x")
        self.vars_form = {}
        for i, (c, t) in enumerate(self.CAMPOS):
            ttk.Label(form, text=t).grid(row=0, column=i, sticky="w", padx=2)
            self.vars_form[c] = tk.StringVar()
            ttk.Entry(form, textvariable=self.vars_form[c], width=18 if c == "nombre" else 10).grid(row=1, column=i, padx=2)
        botones = ttk.Frame(self.tab_cat, padding=(8, 0, 8, 8))
        botones.pack(fill="x")
        ttk.Button(botones, text="Agregar", command=self._agregar).pack(side="left", padx=2)
        ttk.Button(botones, text="Actualizar seleccionado", command=self._actualizar).pack(side="left", padx=2)
        ttk.Button(botones, text="Eliminar seleccionado", command=self._eliminar).pack(side="left", padx=2)
        ttk.Button(botones, text="Limpiar formulario", command=self._limpiar_form).pack(side="left", padx=2)

    def _refrescar_catalogo(self):
        self.tabla_cat.delete(*self.tabla_cat.get_children())
        for a in self.repo.listar_alimentos():
            valores = [a[c] for c, _ in self.CAMPOS]
            self.tabla_cat.insert("", "end", iid=str(a["id"]), values=valores)

    def _datos_form(self):
        return {c: v.get() for c, v in self.vars_form.items()}

    def _limpiar_form(self):
        for v in self.vars_form.values():
            v.set("")
        self.tabla_cat.selection_remove(self.tabla_cat.selection())

    def _cargar_seleccion(self, _evento=None):
        sel = self.tabla_cat.selection()
        if sel:
            for (c, _), valor in zip(self.CAMPOS, self.tabla_cat.item(sel[0], "values")):
                self.vars_form[c].set(valor)

    def _id_seleccionado(self):
        sel = self.tabla_cat.selection()
        if not sel:
            messagebox.showinfo("Catálogo", "Seleccione un alimento de la tabla.")
            return None
        return int(sel[0])

    def _agregar(self):
        try:
            self.repo.agregar_alimento(self._datos_form())
        except ValueError as e:
            messagebox.showerror("Dato inválido", str(e))
            return
        self._refrescar_catalogo()
        self._limpiar_form()

    def _actualizar(self):
        id_a = self._id_seleccionado()
        if id_a is None:
            return
        try:
            self.repo.actualizar_alimento(id_a, self._datos_form())
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", str(e))
            return
        self._refrescar_catalogo()

    def _eliminar(self):
        id_a = self._id_seleccionado()
        if id_a is not None and messagebox.askyesno("Confirmar", "¿Eliminar el alimento seleccionado?"):
            self.repo.eliminar_alimento(id_a)
            self._refrescar_catalogo()
            self._limpiar_form()

    # -------------------------------------------------------------- Historial
    def _armar_historial(self):
        marco = ttk.Frame(self.tab_hist, padding=8)
        marco.pack(fill="both", expand=True)
        cols = ("id", "fecha", "algoritmo", "presupuesto", "costo", "puntaje")
        self.tabla_hist = ttk.Treeview(marco, columns=cols, show="headings", height=12)
        for c, t, w in (("id", "N°", 40), ("fecha", "Fecha", 150), ("algoritmo", "Algoritmo", 160),
                        ("presupuesto", "Presupuesto", 90), ("costo", "Costo", 80), ("puntaje", "Puntaje", 80)):
            self.tabla_hist.heading(c, text=t)
            self.tabla_hist.column(c, width=w, anchor="w" if c in ("fecha", "algoritmo") else "e")
        self.tabla_hist.pack(fill="both", expand=True)
        self.tabla_hist.bind("<<TreeviewSelect>>", self._mostrar_detalle)
        self.lbl_detalle = ttk.Label(marco, text="Seleccione un registro para ver sus alimentos.",
                                     wraplength=820, justify="left")
        self.lbl_detalle.pack(fill="x", pady=8)
        ttk.Button(marco, text="Eliminar registro", command=self._eliminar_historial).pack(anchor="w")
        self._historial = {}

    def _refrescar_historial(self):
        self.tabla_hist.delete(*self.tabla_hist.get_children())
        self._historial = {}
        for r in self.repo.listar_historial():
            self._historial[r["id"]] = r
            self.tabla_hist.insert("", "end", iid=str(r["id"]), values=(
                r["id"], r["fecha"], r["algoritmo"], f"{r['presupuesto']:.0f}",
                f"{r['costo_total']:.2f}", f"{r['puntaje']:.2f}"))

    def _mostrar_detalle(self, _evento=None):
        sel = self.tabla_hist.selection()
        if sel:
            alimentos = self._historial[int(sel[0])]["alimentos"]
            texto = ", ".join(f"{a['nombre']} (${a['costo']:.2f})" for a in alimentos)
            self.lbl_detalle.config(text=f"Alimentos: {texto or 'ninguno'}")

    def _eliminar_historial(self):
        sel = self.tabla_hist.selection()
        if sel and messagebox.askyesno("Confirmar", "¿Eliminar el registro seleccionado?"):
            self.repo.eliminar_historial(int(sel[0]))
            self._refrescar_historial()
            self.lbl_detalle.config(text="Seleccione un registro para ver sus alimentos.")


def main():
    App(RepositorioMenus()).mainloop()


if __name__ == "__main__":
    main()