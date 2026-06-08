"""Instrumento didático — Projeto Geométrico de Vias (página inicial).

Execute localmente com:  ``streamlit run app.py``
"""

import streamlit as st

st.set_page_config(page_title="Projeto Geométrico de Vias", page_icon="🛣️", layout="wide")

st.title("🛣️ Projeto Geométrico de Vias")
st.subheader("Instrumento didático interativo")

st.markdown(
    """
    Ferramenta de apoio à disciplina de **Projeto Geométrico de Vias**. Cada módulo
    permite informar os dados de projeto e visualizar imediatamente o cálculo e o
    desenho correspondente.

    **Módulos disponíveis** (use o menu lateral para navegar):

    - 📐 **Concordância Vertical** — curva vertical parabólica: pontos notáveis
      (PCV, PTV, PIV, vértice), flecha, desnível e perfil longitudinal.

    ---
    *Novos tópicos (curvas horizontais, superelevação, estaqueamento, greide…)
    serão adicionados como novas páginas.*
    """
)

st.info("Selecione um módulo no menu lateral à esquerda para começar.", icon="👈")
