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
    calcular_curva_vertical_assimetrica,
    montar_inclinacoes,
    plotar_perfil,
    plotar_perfil_assimetrica,
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Concordância Vertical — Projeto Geométrico de Vias")
        self.geometry("1100x700")

        self.canvas = None

        painel = ttk.Frame(self, padding=12)
        painel.pack(side=tk.LEFT, fill=tk.Y)

        self.area_grafico = ttk.Frame(self)
        self.area_grafico.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(painel, text="Dados de entrada", font=("", 12, "bold")).pack(anchor="w", pady=(0, 8))

        # ── Tipo de concordância (modo) ──────────────────────────────────────
        ttk.Label(painel, text="Tipo de concordância").pack(anchor="w")
        self.modo = tk.StringVar(value="Simétrica")
        for val in ("Simétrica", "Assimétrica"):
            ttk.Radiobutton(painel, text=val, variable=self.modo,
                            value=val, command=self._atualizar_campos).pack(anchor="w")

        # ── Tipo de curva ────────────────────────────────────────────────────
        ttk.Label(painel, text="Tipo de curva").pack(anchor="w", pady=(8, 0))
        self.tipo = tk.StringVar(value="Convexa")
        ttk.Combobox(painel, textvariable=self.tipo, values=["Convexa", "Côncava"],
                     state="readonly").pack(fill=tk.X, pady=(0, 6))

        # ── Campos comuns (Z_I, i1, i2) ─────────────────────────────────────
        self.entradas: dict[str, tk.StringVar] = {}
        for chave, rotulo, padrao in [
            ("Z_I", "Cota do PIV — Z_I (m)", "500.0"),
            ("i1",  "Magnitude de i₁ (%)",   "3.0"),
            ("i2",  "Magnitude de i₂ (%)",   "2.0"),
        ]:
            ttk.Label(painel, text=rotulo).pack(anchor="w")
            var = tk.StringVar(value=padrao)
            ttk.Entry(painel, textvariable=var).pack(fill=tk.X, pady=(0, 6))
            self.entradas[chave] = var

        # ── Container para campos variáveis (L vs l1+l2) ────────────────────
        self.container = ttk.Frame(painel)
        self.container.pack(fill=tk.X)

        # Frame simétrica: apenas L
        self.frame_sim = ttk.Frame(self.container)
        ttk.Label(self.frame_sim, text="Comprimento L (m)").pack(anchor="w")
        self.entradas["L"] = tk.StringVar(value="100.0")
        ttk.Entry(self.frame_sim, textvariable=self.entradas["L"]).pack(fill=tk.X, pady=(0, 6))

        # Frame assimétrica: l1 e l2
        self.frame_assim = ttk.Frame(self.container)
        for chave, rotulo, padrao in [
            ("l1", "l₁ — PCV→PIV (m)", "80.0"),
            ("l2", "l₂ — PIV→PTV (m)", "120.0"),
        ]:
            ttk.Label(self.frame_assim, text=rotulo).pack(anchor="w")
            self.entradas[chave] = tk.StringVar(value=padrao)
            ttk.Entry(self.frame_assim, textvariable=self.entradas[chave]).pack(fill=tk.X, pady=(0, 6))

        # Exibe frame da simétrica inicialmente
        self.frame_sim.pack(fill=tk.X)

        # ── Botão e área de resultados ───────────────────────────────────────
        ttk.Button(painel, text="Calcular", command=self.calcular).pack(fill=tk.X, pady=10)

        self.resultado = tk.Text(painel, width=34, height=14, state="disabled")
        self.resultado.pack(fill=tk.BOTH, expand=True)

        self.calcular()

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _atualizar_campos(self):
        for w in self.container.winfo_children():
            w.pack_forget()
        if self.modo.get() == "Simétrica":
            self.frame_sim.pack(fill=tk.X)
        else:
            self.frame_assim.pack(fill=tk.X)

    def calcular(self):
        try:
            Z_I    = float(self.entradas["Z_I"].get())
            i1_pct = float(self.entradas["i1"].get())
            i2_pct = float(self.entradas["i2"].get())
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores numéricos informados.")
            return

        i1, i2 = montar_inclinacoes(self.tipo.get(), i1_pct, i2_pct)

        if self.modo.get() == "Simétrica":
            try:
                L = float(self.entradas["L"].get())
            except ValueError:
                messagebox.showerror("Erro", "Verifique os valores numéricos informados.")
                return
            r = calcular_curva_vertical(Z_I, i1, i2, L)
            fig = plotar_perfil(r)
        else:
            try:
                l1 = float(self.entradas["l1"].get())
                l2 = float(self.entradas["l2"].get())
            except ValueError:
                messagebox.showerror("Erro", "Verifique os valores numéricos informados.")
                return
            r = calcular_curva_vertical_assimetrica(Z_I, i1, i2, l1, l2)
            fig = plotar_perfil_assimetrica(r)

        self._mostrar_grafico(fig)
        self._mostrar_resultados(r)

    def _mostrar_grafico(self, fig):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.area_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _mostrar_resultados(self, r):
        assimetrica = hasattr(r, "l1")
        g = r.i1 - r.i2
        if assimetrica:
            texto = (
                f"=== {r.curva_tipo} — Assimétrica ===\n"
                f"g = i₁ − i₂ = {g:.5f}\n"
                f"Flecha e    = {r.e:.4f} m\n"
                f"Z_A (PCV)   = {r.Z_A:.3f} m\n"
                f"Z_B (PTV)   = {r.Z_B:.3f} m\n"
                f"Z_PIV (ápice)   = {r.Z_PIV:.3f} m\n"
                f"Z_F (sob PIV)   = {r.Z_F:.3f} m\n"
                f"Decl. em F: s   = {r.s * 100:.3f} %\n"
                f"x_V = {r.x_V:.3f} m\n"
                f"Z_V = {r.Z_V:.3f} m\n"
            )
        else:
            texto = (
                f"=== {r.curva_tipo} — Simétrica ===\n"
                f"g = i₁ − i₂ = {r.g:.5f}\n"
                f"Flecha e    = {r.e:.4f} m\n"
                f"Z_A (PCV)   = {r.Z_A:.3f} m\n"
                f"Z_B (PTV)   = {r.Z_B:.3f} m\n"
                f"Z_PIV (ápice)   = {r.Z_PIV:.3f} m\n"
                f"Z_M (sob PIV)   = {r.Z_I_parab:.3f} m\n"
                f"x_V = {r.x_V:.3f} m\n"
                f"Z_V = {r.Z_V:.3f} m\n"
            )
        self.resultado.configure(state="normal")
        self.resultado.delete("1.0", tk.END)
        self.resultado.insert(tk.END, texto)
        self.resultado.configure(state="disabled")


if __name__ == "__main__":
    App().mainloop()
