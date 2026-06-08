"""Página Streamlit: Concordância Vertical (curva vertical parabólica)."""

import io
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Garante que o pacote `geom_vert` seja importável quando executado pelo Streamlit
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from geom_vert import (  # noqa: E402
    calcular_curva_vertical,
    montar_inclinacoes,
    plotar_perfil,
)

st.set_page_config(page_title="Concordância Vertical", page_icon="📐", layout="wide")

st.title("📐 Concordância Vertical")
st.caption("Curva vertical parabólica — cálculo dos pontos notáveis e perfil longitudinal.")

# --- Entradas ---------------------------------------------------------------
with st.sidebar:
    st.header("Dados de entrada")
    tipo = st.radio(
        "Tipo de curva",
        options=["Convexa", "Côncava"],
        help="Convexa: i1 > 0 e i2 < 0. Côncava: i1 < 0 e i2 > 0.",
    )
    Z_I = st.number_input("Cota do PIV — Z_I (m)", value=500.0, step=0.1, format="%.3f")
    i1_pct = st.number_input("Magnitude de i₁ (%)", value=3.0, min_value=0.0, step=0.1)
    i2_pct = st.number_input("Magnitude de i₂ (%)", value=2.0, min_value=0.0, step=0.1)
    L = st.number_input("Comprimento da curva — L (m)", value=100.0, min_value=1.0, step=1.0)

# --- Cálculo ----------------------------------------------------------------
i1, i2 = montar_inclinacoes(tipo, i1_pct, i2_pct)
r = calcular_curva_vertical(Z_I, i1, i2, L)

# --- Saída ------------------------------------------------------------------
col_graf, col_res = st.columns([3, 2])

with col_graf:
    fig = plotar_perfil(r)
    st.pyplot(fig)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    st.download_button(
        "⬇️ Baixar gráfico (PNG)",
        data=buf.getvalue(),
        file_name="concordancia_vertical.png",
        mime="image/png",
    )

with col_res:
    st.subheader(f"Resultados — {r.curva_tipo}")
    c1, c2 = st.columns(2)
    c1.metric("Desnível g = i₁ − i₂", f"{r.g:.5f}")
    c2.metric("Flecha vertical e", f"{r.e:.4f} m")

    tabela = pd.DataFrame(
        {
            "Elemento": [
                "Cota de A (PCV) — Z_A",
                "Cota de B (PTV) — Z_B",
                "Cota do PIV (tangentes) — Z_PIV",
                "Cota do ponto médio na parábola",
                "Abscissa do vértice — x_V",
                "Cota do vértice — Z_V",
            ],
            "Valor": [
                f"{r.Z_A:.3f} m",
                f"{r.Z_B:.3f} m",
                f"{r.Z_PIV:.3f} m",
                f"{r.Z_I_parab:.3f} m",
                f"{r.x_V:.3f} m",
                f"{r.Z_V:.3f} m",
            ],
        }
    )
    st.table(tabela)
    st.caption("O PIV é a interseção das tangentes; afasta-se da curva pela flecha e. "
               "O ponto médio sobre a parábola coincide com o Z_I de entrada.")

with st.expander("📖 Fórmulas utilizadas"):
    st.latex(r"g = i_1 - i_2 \qquad e = \frac{L}{8}\,g")
    st.latex(r"Z_A = Z_I - i_1\frac{L}{2} + e \qquad Z_B = Z_A + \frac{i_1 + i_2}{2}\,L")
    st.latex(r"x_V = \frac{i_1\,L}{g} \qquad Z_V = Z_A + \frac{i_1^2\,L}{2\,g}")
    st.latex(r"Z(x) = Z_A + i_1 x - \frac{g}{2L}\,x^2")
