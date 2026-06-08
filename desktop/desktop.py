"""Casca desktop (Tkinter) do instrumento de Concordância Vertical.

Consome o mesmo núcleo de cálculo/plotagem usado pela app web. Serve de base
para empacotamento como executável local (.exe) via PyInstaller:

    pyinstaller --onefile --windowed desktop/desktop.py

Observações sobre o .exe (ver README): arquivo grande (~100–300 MB), específico
por sistema operacional, pode disparar alerta de antivírus/SmartScreen, e
atualizar exige redistribuir o arquivo. Por isso é a casca secundária — a web é
a recomendada para uso em sala.
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Garante que o pacote `geom_vert` seja importável (também ao rodar do .exe)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from geom_vert import (  # noqa: E402
    calcular_curva_vertical,
    montar_inclinacoes,
    plotar_perfil,
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Concordância Vertical — Projeto Geométrico de Vias")
        self.geometry("1100x650")

        self.canvas = None

        painel = ttk.Frame(self, padding=12)
        painel.pack(side=tk.LEFT, fill=tk.Y)

        self.area_grafico = ttk.Frame(self)
        self.area_grafico.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(painel, text="Dados de entrada", font=("", 12, "bold")).pack(anchor="w", pady=(0, 8))

        self.tipo = tk.StringVar(value="Convexa")
        ttk.Label(painel, text="Tipo de curva").pack(anchor="w")
        ttk.Combobox(painel, textvariable=self.tipo, values=["Convexa", "Côncava"],
                     state="readonly").pack(fill=tk.X, pady=(0, 6))

        self.entradas = {}
        for chave, rotulo, padrao in [
            ("Z_I", "Cota do PIV — Z_I (m)", "500.0"),
            ("i1", "Magnitude de i1 (%)", "3.0"),
            ("i2", "Magnitude de i2 (%)", "2.0"),
            ("L", "Comprimento L (m)", "100.0"),
        ]:
            ttk.Label(painel, text=rotulo).pack(anchor="w")
            var = tk.StringVar(value=padrao)
            ttk.Entry(painel, textvariable=var).pack(fill=tk.X, pady=(0, 6))
            self.entradas[chave] = var

        ttk.Button(painel, text="Calcular", command=self.calcular).pack(fill=tk.X, pady=10)

        self.resultado = tk.Text(painel, width=34, height=12, state="disabled")
        self.resultado.pack(fill=tk.BOTH, expand=True)

        self.calcular()

    def calcular(self):
        try:
            Z_I = float(self.entradas["Z_I"].get())
            i1_pct = float(self.entradas["i1"].get())
            i2_pct = float(self.entradas["i2"].get())
            L = float(self.entradas["L"].get())
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores numéricos informados.")
            return

        i1, i2 = montar_inclinacoes(self.tipo.get(), i1_pct, i2_pct)
        r = calcular_curva_vertical(Z_I, i1, i2, L)

        self._mostrar_grafico(plotar_perfil(r))
        self._mostrar_resultados(r)

    def _mostrar_grafico(self, fig):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.area_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _mostrar_resultados(self, r):
        texto = (
            f"=== Resultados ({r.curva_tipo}) ===\n"
            f"g = i1 - i2 = {r.g:.5f}\n"
            f"Flecha e = {r.e:.4f} m\n"
            f"Z_A (PCV) = {r.Z_A:.3f} m\n"
            f"Z_B (PTV) = {r.Z_B:.3f} m\n"
            f"Z_I parábola = {r.Z_I_parab:.3f} m\n"
            f"x_V = {r.x_V:.3f} m\n"
            f"Z_V = {r.Z_V:.3f} m\n"
        )
        self.resultado.configure(state="normal")
        self.resultado.delete("1.0", tk.END)
        self.resultado.insert(tk.END, texto)
        self.resultado.configure(state="disabled")


if __name__ == "__main__":
    App().mainloop()
