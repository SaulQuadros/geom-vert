"""Geração do gráfico do perfil longitudinal da concordância vertical.

Módulo *puro* de visualização: recebe um :class:`ResultadoCurvaVertical` e
devolve uma ``matplotlib.figure.Figure`` — **sem** ``plt.show()``. Quem decide
como exibir (``st.pyplot``, ``FigureCanvasTkAgg``, ``savefig``...) é a interface.
"""

from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure

from .concordancia_vertical import ResultadoCurvaVertical
from .concordancia_vertical_assimetrica import ResultadoCurvaVerticalAssimetrica


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

    # Pontos notáveis:
    #  - A (PCV), B (PTV) e PIV (interseção das tangentes) em vermelho
    #  - ponto médio sobre a parábola em azul (separado do PIV pela flecha e)
    #  - vértice da parábola como estrela azul
    ax.scatter([x_A, x_B, x_I], [r.Z_A, r.Z_B, r.Z_PIV], color="red", zorder=5)
    ax.scatter([x_I], [r.Z_I_parab], color="blue", zorder=6)
    if not np.isnan(r.Z_V):
        ax.scatter([r.x_V], [r.Z_V], color="blue", zorder=6, marker="*", s=180)

    # Rótulos de A e B
    ax.text(x_A, r.Z_A + (0.4 if convexa else -0.4), "A (PCV)",
            ha="center", fontsize=11, fontweight="bold")
    ax.text(x_B, r.Z_B + (0.4 if convexa else -0.4), "B (PTV)",
            ha="center", fontsize=11, fontweight="bold")

    # Rótulo do PIV (I), junto à interseção das tangentes
    off_i = 0.4 if convexa else -0.4
    ax.text(x_I, r.Z_PIV + off_i, "I (PIV)", ha="center", fontsize=11, fontweight="bold")

    # Rótulo do ponto médio do greide M (sob o PIV, separado de I pela flecha e)
    off_m = -0.7 if convexa else 0.7
    ax.text(x_I, r.Z_I_parab + off_m, "M (sob PIV)",
            ha="center", fontsize=11, color="blue", fontweight="bold")

    # Seta dupla da flecha e (entre M e PIV), deslocada levemente à direita
    if abs(r.e) > 1e-9:
        x_fl = x_I + r.L * 0.04
        ax.annotate("", xy=(x_fl, r.Z_PIV), xytext=(x_fl, r.Z_I_parab),
                    arrowprops=dict(arrowstyle="<->", color="blue", lw=1.1))
        ax.text(x_fl + r.L * 0.01, (r.Z_PIV + r.Z_I_parab) / 2,
                "$e$", color="blue", va="center", ha="left", fontsize=10)

    # Rótulo do vértice (V), junto à curva e no lado oposto ao PIV para não colidir
    if not np.isnan(r.Z_V):
        off_v = -0.7 if convexa else 0.7
        ax.text(r.x_V, r.Z_V + off_v, "V (Vértice)",
                ha="center", fontsize=11, color="blue", fontweight="bold")

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


def plotar_perfil_assimetrica(r: ResultadoCurvaVerticalAssimetrica) -> Figure:
    """Desenha o perfil longitudinal da curva vertical assimétrica.

    Mesmas convenções da :func:`plotar_perfil`: A (PCV), B (PTV) e o PIV
    (interseção das tangentes, em x = l1) em vermelho; o ponto da curva sob o PIV
    em azul (o vão até o PIV é a flecha ``e``); vértice como estrela azul.
    """
    convexa = r.curva_tipo == "Convexa"
    x_I = r.l1  # abscissa do PIV

    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    # Parábola (dois trechos concatenados em uma curva, com legenda única)
    x_parab = np.concatenate([r.x1, r.x2])
    Z_parab = np.concatenate([r.Z1, r.Z2])
    ax.plot(x_parab, Z_parab, "k", lw=2, label="Parábola de Concordância")
    ax.plot(r.x_tanA, r.Z_tanA, "--", color="gray", label="Tangente em A (PCV)")
    ax.plot(r.x_tanB, r.Z_tanB, "--", color="orange", label="Tangente em B (PTV)")

    # Pontos notáveis: A, B e PIV (ápice) em vermelho; curva sob o PIV em azul
    ax.scatter([0, r.L, x_I], [r.Z_A, r.Z_B, r.Z_PIV], color="red", zorder=5)
    ax.scatter([x_I], [r.Z_F], color="blue", zorder=6)
    if not np.isnan(r.Z_V):
        ax.scatter([r.x_V], [r.Z_V], color="blue", zorder=6, marker="*", s=180)

    # Rótulos de A e B
    ax.text(0, r.Z_A + (0.4 if convexa else -0.4), "A (PCV)",
            ha="center", fontsize=11, fontweight="bold")
    ax.text(r.L, r.Z_B + (0.4 if convexa else -0.4), "B (PTV)",
            ha="center", fontsize=11, fontweight="bold")

    # Rótulo do PIV (I), junto ao ápice
    off_i = 0.4 if convexa else -0.4
    ax.text(x_I, r.Z_PIV + off_i, "I (PIV)", ha="center", fontsize=11, fontweight="bold")

    # Rótulo do ponto F (sob o PIV, separado de I pela flecha e)
    off_f = -0.7 if convexa else 0.7
    ax.text(x_I, r.Z_F + off_f, "F (sob PIV)",
            ha="center", fontsize=11, color="blue", fontweight="bold")

    # Seta dupla da flecha e (entre F e PIV), deslocada levemente à direita
    if abs(r.e) > 1e-9:
        x_fl = x_I + r.L * 0.04
        ax.annotate("", xy=(x_fl, r.Z_PIV), xytext=(x_fl, r.Z_F),
                    arrowprops=dict(arrowstyle="<->", color="blue", lw=1.1))
        ax.text(x_fl + r.L * 0.01, (r.Z_PIV + r.Z_F) / 2,
                "$e$", color="blue", va="center", ha="left", fontsize=10)

    # Rótulo do vértice (V), no lado oposto ao PIV para não colidir
    if not np.isnan(r.Z_V):
        off_v = -0.7 if convexa else 0.7
        ax.text(r.x_V, r.Z_V + off_v, "V (Vértice)",
                ha="center", fontsize=11, color="blue", fontweight="bold")

    # Anotações das inclinações (ao longo das tangentes)
    off_a = 0.7 if convexa else -0.7
    ax.text(x_I / 2, r.Z_A + r.i1 * (x_I / 2) + off_a,
            rf"$i_1$ = {r.i1 * 100:+.2f}%", ha="center", fontsize=10, color="gray")
    ax.text((x_I + r.L) / 2, r.Z_B + r.i2 * (((x_I + r.L) / 2) - r.L) + off_a,
            rf"$i_2$ = {r.i2 * 100:+.2f}%", ha="center", fontsize=10, color="orange")

    ax.set_xlabel("x (m)")
    ax.set_ylabel("Cota Z (m)")
    ax.set_title(f"Perfil Longitudinal: Concordância Vertical Assimétrica ({r.curva_tipo})")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

    return fig
