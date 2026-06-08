"""Geração do gráfico do perfil longitudinal da concordância vertical.

Módulo *puro* de visualização: recebe um :class:`ResultadoCurvaVertical` e
devolve uma ``matplotlib.figure.Figure`` — **sem** ``plt.show()``. Quem decide
como exibir (``st.pyplot``, ``FigureCanvasTkAgg``, ``savefig``...) é a interface.
"""

from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure

from .concordancia_vertical import ResultadoCurvaVertical


def plotar_perfil(r: ResultadoCurvaVertical) -> Figure:
    """Desenha o perfil longitudinal da curva vertical e retorna a figura.

    Reproduz o gráfico didático: parábola de concordância, tangentes em A e B,
    pontos notáveis (PCV, PTV, PIV, vértice) e anotações das inclinações, com
    posicionamento de rótulos adaptado a curva convexa/côncava.
    """
    convexa = r.curva_tipo == "Convexa"

    x_A, x_B, x_I = 0.0, r.L, r.L / 2

    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    # Parábola e tangentes
    ax.plot(r.x_vals, r.Z_parab, "k", lw=2, label="Parábola de Concordância")
    ax.plot(r.x_tanA, r.Z_tanA, "--", color="gray", label="Tangente em A (PCV)")
    ax.plot(r.x_tanB, r.Z_tanB, "--", color="orange", label="Tangente em B (PTV)")

    # Pontos notáveis
    ax.scatter([x_A, x_B, x_I], [r.Z_A, r.Z_B, r.Z_I_parab], color="red", zorder=5)
    if not np.isnan(r.Z_V):
        ax.scatter([r.x_V], [r.Z_V], color="blue", zorder=6, marker="*", s=180)

    # Rótulos de A e B
    ax.text(x_A, r.Z_A + (0.4 if convexa else -0.4), "A (PCV)",
            ha="center", fontsize=11, fontweight="bold")
    ax.text(x_B, r.Z_B + (0.4 if convexa else -0.4), "B (PTV)",
            ha="center", fontsize=11, fontweight="bold")

    # Rótulos de V (vértice) e I (PIV) com posicionamento inteligente
    if not np.isnan(r.Z_V):
        dx = r.L * 0.03
        dy = abs(r.Z_V - r.Z_I_parab) + 0.6

        if abs(r.x_V - x_I) < 0.15 * r.L:
            # Muito próximos: separam na vertical
            if convexa:
                ax.text(r.x_V, r.Z_V + dy, "V (Vértice)",
                        ha="center", fontsize=11, color="blue", fontweight="bold")
                ax.text(x_I, r.Z_I_parab - dy, "I (PIV)",
                        ha="center", fontsize=11, fontweight="bold")
            else:
                ax.text(r.x_V, r.Z_V - dy, "V (Vértice)",
                        ha="center", fontsize=11, color="blue", fontweight="bold")
                ax.text(x_I, r.Z_I_parab + dy, "I (PIV)",
                        ha="center", fontsize=11, fontweight="bold")
        else:
            # Afastados: um à esquerda e um à direita
            offset = 0.7 if convexa else -0.7
            ax.text(r.x_V - dx, r.Z_V + offset, "V (Vértice)",
                    ha="center", fontsize=11, color="blue", fontweight="bold")
            ax.text(x_I + dx, r.Z_I_parab + offset, "I (PIV)",
                    ha="center", fontsize=11, fontweight="bold")

    # Anotações das inclinações
    offset_i = 0.7 if convexa else -0.7
    ax.text(x_I / 2, r.Z_A + r.i1 * (x_I / 2) + offset_i,
            rf"$i_1$ = {r.i1 * 100:+.2f}%", ha="center", fontsize=10, color="gray")
    ax.text((x_I + r.L) / 2, r.Z_B + r.i2 * (((x_I + r.L) / 2) - r.L) + offset_i,
            rf"$i_2$ = {r.i2 * 100:+.2f}%", ha="center", fontsize=10, color="orange")

    ax.set_xlabel("x (m)")
    ax.set_ylabel("Cota Z (m)")
    ax.set_title(f"Perfil Longitudinal: Concordância Vertical ({r.curva_tipo})")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

    return fig
