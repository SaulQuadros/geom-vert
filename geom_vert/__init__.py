"""Instrumento didático de Projeto Geométrico de Vias — núcleo de cálculo.

Expõe as funções de cálculo e plotagem usadas pelas interfaces (Streamlit,
Tkinter, notebooks). O núcleo é puro: não depende de nenhuma biblioteca de UI.
"""

from .concordancia_vertical import (
    ResultadoCurvaVertical,
    calcular_curva_vertical,
    montar_inclinacoes,
)
from .concordancia_vertical_assimetrica import (
    ResultadoCurvaVerticalAssimetrica,
    calcular_curva_vertical_assimetrica,
)
from .estaqueamento import LinhaEstaca, gerar_estaqueamento
from .plotagem import plotar_perfil, plotar_perfil_assimetrica

__all__ = [
    "ResultadoCurvaVertical",
    "calcular_curva_vertical",
    "montar_inclinacoes",
    "plotar_perfil",
    "ResultadoCurvaVerticalAssimetrica",
    "calcular_curva_vertical_assimetrica",
    "plotar_perfil_assimetrica",
    "LinhaEstaca",
    "gerar_estaqueamento",
]
