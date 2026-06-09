"""Núcleo de cálculo da concordância vertical (curva vertical parabólica).

Módulo *puro*: não importa Streamlit nem Tkinter, não usa ``input``/``print`` e
não desenha nada. Recebe números e devolve uma estrutura de dados com todos os
elementos da curva — pronta para ser consumida por qualquer interface (web,
desktop, notebook ou testes).

Convenção de sinais (Projeto Geométrico de Vias):
    * Curva **convexa**: i1 > 0 e i2 < 0  (g = i1 - i2 > 0)
    * Curva **côncava**: i1 < 0 e i2 > 0  (g = i1 - i2 < 0)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ResultadoCurvaVertical:
    """Resultados do cálculo de uma curva vertical parabólica.

    Cotas em metros; inclinações em decimal com sinal (ex.: 0.03 = +3%).
    """

    # Dados de entrada (ecoados para conveniência das interfaces)
    Z_I: float
    i1: float
    i2: float
    L: float

    # Grandezas calculadas
    g: float            # desnível das rampas (i1 - i2)
    e: float            # flecha vertical
    Z_A: float          # cota do PCV (ponto A)
    Z_B: float          # cota do PTV (ponto B)
    Z_I_parab: float    # cota do ponto médio sobre a parábola (confere com Z_I de entrada)
    Z_PIV: float        # cota do PIV (interseção das tangentes; afastada da curva pela flecha e)
    x_V: float          # abscissa do vértice da parábola
    y_V: float          # ordenada do vértice em relação a A
    Z_V: float          # cota do vértice
    curva_tipo: str     # "Convexa", "Côncava" ou "Reta"

    # Séries para plotagem
    x_vals: np.ndarray
    Z_parab: np.ndarray
    x_tanA: np.ndarray
    Z_tanA: np.ndarray
    x_tanB: np.ndarray
    Z_tanB: np.ndarray

    @property
    def x_piv(self) -> float:
        """Abscissa do PIV a partir do PCV (no simétrico, L/2)."""
        return self.L / 2

    def greide_em(self, x: float) -> float:
        """Cota do greide (curva) a `x` metros do PCV (0 ≤ x ≤ L)."""
        return self.Z_A + self.i1 * x - (self.g / (2 * self.L)) * x ** 2

    def tangente_em(self, x: float) -> float:
        """Cota da rampa tangente de referência (i1 antes do PIV, i2 depois)."""
        if x <= self.L / 2:
            return self.Z_A + self.i1 * x
        return self.Z_B + self.i2 * (x - self.L)


def montar_inclinacoes(tipo: str, i1_pct: float, i2_pct: float) -> tuple[float, float]:
    """Converte magnitudes em % + tipo de curva em inclinações com sinal (decimal).

    Reproduz a convenção do curso a partir de valores positivos digitados pelo
    aluno.

    Args:
        tipo: ``"C"``/``"Convexa"`` ou ``"N"``/``"Côncava"`` (sem distinção de caixa).
        i1_pct: magnitude de i1 em porcentagem (valor positivo, ex.: 3.0).
        i2_pct: magnitude de i2 em porcentagem (valor positivo, ex.: 2.0).

    Returns:
        ``(i1, i2)`` em decimal e já com o sinal correto.
    """
    t = tipo.strip().upper()
    convexa = t in ("C", "CONVEXA")
    if convexa:
        return i1_pct / 100, -i2_pct / 100
    return -i1_pct / 100, i2_pct / 100


def calcular_curva_vertical(
    Z_I: float,
    i1: float,
    i2: float,
    L: float,
    n_pontos: int = 200,
) -> ResultadoCurvaVertical:
    """Calcula todos os elementos da curva vertical parabólica.

    Args:
        Z_I: cota do PIV (ponto I).
        i1: inclinação inicial em decimal **com sinal** (ex.: 0.03 = +3%).
        i2: inclinação final em decimal **com sinal** (ex.: -0.02 = -2%).
        L: comprimento da curva (m).
        n_pontos: nº de pontos para discretizar a parábola.

    Returns:
        Um :class:`ResultadoCurvaVertical`.
    """
    g = i1 - i2
    e = (L / 8) * g

    # Cotas dos pontos notáveis
    Z_A = Z_I - i1 * (L / 2) + e          # PCV (ponto A)
    Z_B = Z_A + ((i1 + i2) / 2) * L       # PTV (ponto B)
    Z_I_parab = Z_A + i1 * (L / 2) - e    # ponto médio sobre a parábola
    Z_PIV = Z_A + i1 * (L / 2)            # PIV: interseção das tangentes (em x = L/2)

    # Vértice da parábola (ponto de inclinação nula)
    if g != 0:
        x_V = (i1 * L) / g
        y_V = (i1 ** 2 * L) / (2 * g)
        Z_V = Z_A + y_V
    else:
        x_V = y_V = Z_V = np.nan

    if g > 0:
        curva_tipo = "Convexa"
    elif g < 0:
        curva_tipo = "Côncava"
    else:
        curva_tipo = "Reta"

    # Parábola de concordância
    x_vals = np.linspace(0, L, n_pontos)
    y_vals = i1 * x_vals - (g / (2 * L)) * x_vals ** 2
    Z_parab = Z_A + y_vals

    # Tangentes (prolongadas para fora do trecho para fins didáticos)
    x_tanA = np.linspace(-L / 3, L, 100)
    Z_tanA = Z_A + i1 * x_tanA

    x_tanB = np.linspace(0, L + L / 3, 100)
    Z_tanB = Z_B + i2 * (x_tanB - L)

    return ResultadoCurvaVertical(
        Z_I=Z_I,
        i1=i1,
        i2=i2,
        L=L,
        g=g,
        e=e,
        Z_A=Z_A,
        Z_B=Z_B,
        Z_I_parab=Z_I_parab,
        Z_PIV=Z_PIV,
        x_V=x_V,
        y_V=y_V,
        Z_V=Z_V,
        curva_tipo=curva_tipo,
        x_vals=x_vals,
        Z_parab=Z_parab,
        x_tanA=x_tanA,
        Z_tanA=Z_tanA,
        x_tanB=x_tanB,
        Z_tanB=Z_tanB,
    )
