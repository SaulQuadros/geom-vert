"""Instrumento didático de Projeto Geométrico de Vias — núcleo de cálculo.

Expõe as funções de cálculo e plotagem usadas pelas interfaces (Streamlit,
Tkinter, notebooks). O núcleo é puro: não depende de nenhuma biblioteca de UI.
"""

from .concordancia_vertical import (
    ResultadoCurvaVertical,
    calcular_curva_vertical,
    montar_inclinacoes,
)
from .plotagem import plotar_perfil

__all__ = [
    "ResultadoCurvaVertical",
    "calcular_curva_vertical",
    "montar_inclinacoes",
    "plotar_perfil",
]
