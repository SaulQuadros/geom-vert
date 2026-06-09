"""Núcleo de cálculo da concordância vertical ASSIMÉTRICA.

Curva composta por dois trechos parabólicos com comprimentos distintos
``l1`` (PCV→PIV) e ``l2`` (PIV→PTV). A formulação segue o material da disciplina
(``z_docs/08_CV_PCV-PTV_2025.pdf``, pp. 12–18).

Convenção: ``Z_I`` é a cota do **ápice** (interseção das tangentes), em ``x = l1``.
A cota da curva sob o PIV fica ``e`` abaixo (``Z_F = Z_I − e`` para curva convexa).

Módulo *puro*: não importa Streamlit/Tkinter, não usa ``input``/``print`` e não
desenha. Espelha o padrão de :mod:`geom_vert.concordancia_vertical`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ResultadoCurvaVerticalAssimetrica:
    """Resultados da curva vertical assimétrica (dois trechos parabólicos).

    Cotas em metros; inclinações em decimal com sinal (ex.: 0.03 = +3%).
    """

    # Entradas
    Z_I: float
    i1: float
    i2: float
    l1: float
    l2: float
    L: float

    # Grandezas calculadas
    s: float            # declividade no ponto da curva sob o PIV
    e: float            # flecha vertical (Z_I - Z_F)
    Z_A: float          # cota do PCV (ponto A)
    Z_B: float          # cota do PTV (ponto B)
    Z_PIV: float        # cota do PIV (ápice / interseção das tangentes) = Z_I
    Z_F: float          # cota da curva sob o PIV (em x = l1)
    curva_tipo: str     # "Convexa", "Côncava" ou "Reta"
    x_V: float          # abscissa do vértice (extremo) da curva
    Z_V: float          # cota do vértice

    # Séries para plotagem (dois trechos) e tangentes
    x1: np.ndarray
    Z1: np.ndarray
    x2: np.ndarray
    Z2: np.ndarray
    x_tanA: np.ndarray
    Z_tanA: np.ndarray
    x_tanB: np.ndarray
    Z_tanB: np.ndarray


def calcular_curva_vertical_assimetrica(
    Z_I: float,
    i1: float,
    i2: float,
    l1: float,
    l2: float,
    n_pontos: int = 200,
) -> ResultadoCurvaVerticalAssimetrica:
    """Calcula a curva vertical assimétrica (parábola composta por dois trechos).

    Args:
        Z_I: cota do PIV (ápice / interseção das tangentes).
        i1: inclinação inicial em decimal com sinal (ex.: 0.03 = +3%).
        i2: inclinação final em decimal com sinal (ex.: -0.01 = -1%).
        l1: comprimento do trecho PCV→PIV (m).
        l2: comprimento do trecho PIV→PTV (m).
        n_pontos: nº de pontos para discretizar cada trecho da parábola.

    Returns:
        Um :class:`ResultadoCurvaVerticalAssimetrica`.
    """
    L = l1 + l2
    g = i1 - i2

    # Cotas dos pontos notáveis (tangentes a partir do ápice Z_I)
    Z_A = Z_I - i1 * l1            # PCV
    Z_B = Z_I + i2 * l2            # PTV
    Z_PIV = Z_I                    # ápice / interseção das tangentes

    # Declividade comum no ponto sob o PIV e flecha
    s = (i1 * l1 + i2 * l2) / L
    e = (l1 * l2) / (2 * L) * g
    Z_F = Z_I - e                  # cota da curva sob o PIV

    if g > 0:
        curva_tipo = "Convexa"
    elif g < 0:
        curva_tipo = "Côncava"
    else:
        curva_tipo = "Reta"

    # Coeficientes quadráticos de cada trecho
    k1 = g * l2 / (2 * L * l1)
    k2 = g * l1 / (2 * L * l2)

    # Vértice (extremo): onde a declividade zera, no trecho que o contém
    x_V = Z_V = np.nan
    if g != 0:
        x_v1 = i1 * L * l1 / (g * l2)            # i1 / (2*k1)
        if 0 <= x_v1 <= l1:
            x_V = x_v1
            Z_V = Z_A + i1 * x_v1 - k1 * x_v1 ** 2
        else:
            x_v2 = L + i2 * L * l2 / (g * l1)    # L + i2 / (2*k2)
            if l1 <= x_v2 <= L:
                x_V = x_v2
                Z_V = Z_B + i2 * (x_v2 - L) - k2 * (x_v2 - L) ** 2

    # Parábola: trecho 1 (origem no PCV) e trecho 2 (escrito a partir do PTV)
    x1 = np.linspace(0, l1, n_pontos)
    Z1 = Z_A + i1 * x1 - k1 * x1 ** 2

    x2 = np.linspace(l1, L, n_pontos)
    Z2 = Z_B + i2 * (x2 - L) - k2 * (x2 - L) ** 2

    # Tangentes prolongadas (cruzam-se em (l1, Z_I))
    x_tanA = np.linspace(-L / 6, L, 100)
    Z_tanA = Z_A + i1 * x_tanA

    x_tanB = np.linspace(0, L + L / 6, 100)
    Z_tanB = Z_B + i2 * (x_tanB - L)

    return ResultadoCurvaVerticalAssimetrica(
        Z_I=Z_I,
        i1=i1,
        i2=i2,
        l1=l1,
        l2=l2,
        L=L,
        s=s,
        e=e,
        Z_A=Z_A,
        Z_B=Z_B,
        Z_PIV=Z_PIV,
        Z_F=Z_F,
        curva_tipo=curva_tipo,
        x_V=x_V,
        Z_V=Z_V,
        x1=x1,
        Z1=Z1,
        x2=x2,
        Z2=Z2,
        x_tanA=x_tanA,
        Z_tanA=Z_tanA,
        x_tanB=x_tanB,
        Z_tanB=Z_tanB,
    )
