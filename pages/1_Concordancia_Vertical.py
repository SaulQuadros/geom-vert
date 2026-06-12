"""Página Streamlit: Concordância Vertical (simétrica ou assimétrica)."""

import io
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Garante que o pacote `geom_vert` seja importável quando executado pelo Streamlit
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from geom_vert import (  # noqa: E402
    calcular_curva_vertical,
    calcular_curva_vertical_assimetrica,
    gerar_estaqueamento,
    montar_inclinacoes,
    plotar_perfil,
    plotar_perfil_assimetrica,
)

st.set_page_config(page_title="Concordância Vertical", page_icon="📐", layout="wide")

st.title("📐 Concordância Vertical")
st.caption("Curva vertical parabólica — cálculo dos pontos notáveis e perfil longitudinal.")

# --- Entradas ---------------------------------------------------------------
with st.sidebar:
    st.header("Dados de entrada")
    modo = st.radio(
        "Tipo de concordância",
        options=["Simétrica", "Assimétrica"],
        index=0,
        help="Simétrica: PIV no meio (x = L/2). Assimétrica: dois trechos com l₁ ≠ l₂.",
    )
    assimetrica = modo == "Assimétrica"

    tipo = st.radio(
        "Tipo de curva",
        options=["Convexa", "Côncava"],
        help="Convexa: i1 > 0 e i2 < 0. Côncava: i1 < 0 e i2 > 0.",
    )
    Z_I = st.number_input(
        "Cota do PIV — Z_I (m)",
        value=500.0, step=0.1, format="%.3f",
        help="Cota do PIV (ápice / interseção das tangentes). O greide passa e abaixo.",
    )
    i1_pct = st.number_input("Magnitude de i₁ (%)", value=3.0, min_value=0.0, step=0.1)
    i2_pct = st.number_input(
        "Magnitude de i₂ (%)",
        value=1.0 if assimetrica else 2.0, min_value=0.0, step=0.1,
    )
    if assimetrica:
        l1 = st.number_input("l₁ — PCV→PIV (m)", value=80.0, min_value=1.0, step=1.0)
        l2 = st.number_input("l₂ — PIV→PTV (m)", value=120.0, min_value=1.0, step=1.0)
    else:
        L = st.number_input("Comprimento da curva — L (m)", value=100.0, min_value=1.0, step=1.0)

# --- Cálculo ----------------------------------------------------------------
i1, i2 = montar_inclinacoes(tipo, i1_pct, i2_pct)
if assimetrica:
    r = calcular_curva_vertical_assimetrica(Z_I, i1, i2, l1, l2)
    fig = plotar_perfil_assimetrica(r)
    nome_arquivo = "concordancia_vertical_assimetrica.png"
else:
    r = calcular_curva_vertical(Z_I, i1, i2, L)
    fig = plotar_perfil(r)
    nome_arquivo = "concordancia_vertical.png"

# --- Saída ------------------------------------------------------------------
col_graf, col_res = st.columns([3, 2])

with col_graf:
    st.pyplot(fig)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    st.download_button(
        "⬇️ Baixar gráfico (PNG)",
        data=buf.getvalue(),
        file_name=nome_arquivo,
        mime="image/png",
    )

with col_res:
    st.subheader(f"Resultados — {r.curva_tipo}")
    g = r.i1 - r.i2
    c1, c2 = st.columns(2)
    c1.metric("Desnível g = i₁ − i₂", f"{g:.5f}")
    c2.metric("Flecha máxima e", f"{r.e:.4f} m")

    if assimetrica:
        tabela = pd.DataFrame(
            {
                "Elemento": [
                    "l₁ (PCV→PIV)",
                    "l₂ (PIV→PTV)",
                    "Comprimento total: L",
                    "Cota de A (PCV): Z_A",
                    "Cota de B (PTV): Z_B",
                    "Cota do PIV (ápice): Z_PIV",
                    "Cota da curva sob o PIV: Z_F",
                    "Declividade no PIV: s",
                    "Abscissa do vértice: x_V",
                    "Cota do vértice: Z_V",
                ],
                "Valor": [
                    f"{r.l1:.3f} m",
                    f"{r.l2:.3f} m",
                    f"{r.L:.3f} m",
                    f"{r.Z_A:.3f} m",
                    f"{r.Z_B:.3f} m",
                    f"{r.Z_PIV:.3f} m",
                    f"{r.Z_F:.3f} m",
                    f"{r.s * 100:.3f} %",
                    f"{r.x_V:.3f} m",
                    f"{r.Z_V:.3f} m",
                ],
            }
        )
        st.table(tabela)
        st.caption("Z_I é a cota do ápice (interseção das tangentes); a curva sob o "
                   "PIV fica em Z_F = Z_I − e. PIV em x = l₁.")
    else:
        tabela = pd.DataFrame(
            {
                "Elemento": [
                    "Cota de A (PCV): Z_A",
                    "Cota de B (PTV): Z_B",
                    "Cota do PIV (ápice): Z_PIV",
                    "Cota do greide no ponto médio: Z_M",
                    "Abscissa do vértice: x_V",
                    "Cota do vértice: Z_V",
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
        st.caption("Z_I é a cota do PIV (ápice / interseção das tangentes). "
                   "O greide no ponto médio fica e abaixo: Z_M = Z_I − e.")

with st.expander("📖 Fórmulas utilizadas"):
    if assimetrica:
        st.latex(r"L = l_1 + l_2 \qquad e = \frac{l_1\,l_2}{2L}\,(i_1 - i_2)")
        st.latex(r"Z_A = Z_I - i_1\,l_1 \qquad Z_B = Z_I + i_2\,l_2")
        st.latex(r"s = \frac{i_1 l_1 + i_2 l_2}{L} \qquad Z_F = Z_I - e")
        st.latex(r"Z(x) = Z_A + i_1 x - \frac{(i_1 - i_2)\,l_2}{2L\,l_1}\,x^2"
                 r"\quad (0 \le x \le l_1)")
        st.latex(r"Z(x) = Z_B + i_2 (x - L) - \frac{(i_1 - i_2)\,l_1}{2L\,l_2}\,(x - L)^2"
                 r"\quad (l_1 \le x \le L)")
    else:
        st.markdown("**Equações gerais**")
        st.latex(r"g = i_1 - i_2 \qquad e = \frac{L}{8}\,g")
        st.latex(r"y(x) = i_1 x - \frac{i_1 - i_2}{2L}\,x^2 \qquad Z(x) = Z_A + y(x)")

        st.markdown("**1. Ancorando no ponto médio do greide $Z_M$ (x = L/2)**")
        st.latex(r"Z_M = Z_A + i_1\frac{L}{2} - e \;\Rightarrow\; Z_A = Z_M - i_1\frac{L}{2} + e")
        st.latex(r"Z_B = Z_A + \frac{i_1 + i_2}{2}\,L")

        st.markdown("**2. Relação entre $Z_M$ e o PIV (ápice) $Z_I$**")
        st.latex(r"Z_I = Z_M + e \quad\Longleftrightarrow\quad Z_M = Z_I - e")

        st.markdown("**3. Reancorando no PIV $Z_I$ — o $e$ se cancela**")
        st.latex(r"Z_A = Z_I - i_1\frac{L}{2} \qquad Z_B = Z_I + i_2\frac{L}{2}")

        st.markdown("**Vértice da parábola**")
        st.latex(r"x_V = \frac{i_1\,L}{g} \qquad Z_V = Z_A + \frac{i_1^2\,L}{2\,g}")
        st.caption("O app ancora no PIV (Z_I = ápice). No PDF 08 o mesmo Z_A aparece "
                   "com +e porque ali o valor digitado é, na verdade, o Z_M (greide no meio).")

# --- Estaqueamento ----------------------------------------------------------
with st.expander("📍 Estaqueamento (cotas das estacas)"):
    st.caption("Estaca = 20 m. Informe a estaca de um ponto de referência; as "
               "cotas do greide são geradas do PCV ao PTV.")
    c_ref, c_est, c_frac, c_passo = st.columns([2, 1, 1, 2])
    ponto_label = c_ref.selectbox(
        "Estaca conhecida do:",
        ["PIV (I)", "PCV (A)", "PTV (B)"],
        index=0,
    )
    est_inteira = c_est.number_input("Estaca inteira", value=10, min_value=0, step=1)
    fracao = c_frac.number_input("Fração (m)", value=0.0, min_value=0.0,
                                 max_value=20.0, step=0.5, format="%.2f")
    passo_label = c_passo.selectbox(
        "Intermediárias a cada",
        ["10 m", "5 m", "20 m (só inteiras)"],
        index=0,
    )
    ref_map = {"PIV (I)": "PIV", "PCV (A)": "PCV", "PTV (B)": "PTV"}
    passo_map = {"10 m": 10.0, "5 m": 5.0, "20 m (só inteiras)": 20.0}

    linhas = gerar_estaqueamento(
        r, ref_map[ponto_label], int(est_inteira), float(fracao), passo_map[passo_label]
    )
    df_est = pd.DataFrame(
        [
            {
                "Estaca": ln.estaca,
                "x (m)": round(ln.x, 2),
                "Cota tangente (m)": round(ln.cota_tangente, 3),
                "Flecha (m)": round(ln.flecha, 3),
                "Cota greide (m)": round(ln.cota_greide, 3),
                "Ponto": ln.ponto,
            }
            for ln in linhas
        ]
    )
    st.dataframe(df_est, use_container_width=True, hide_index=True)
    st.caption("No PIV: a cota na tangente é o ápice; a cota do greide é a da curva "
               "(diferem pela flecha).")
    csv = df_est.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    st.download_button(
        "⬇️ Baixar estaqueamento (CSV)",
        data=csv,
        file_name="estaqueamento.csv",
        mime="text/csv",
    )
