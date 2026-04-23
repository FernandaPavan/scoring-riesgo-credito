import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import scorecardpy as sc
import sys
import os

# ============================================
# IMPORTS LOCAIS (RESOLVE MODULE ERROR)
# ============================================
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loader import load_assets
from policy import get_score, apply_business_policy

# ============================================
# CONFIGURAÇÃO
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App")

# ============================================
# LOAD MODELO + REGRAS
# ============================================
modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_assets()

# ============================================
# CSS ORIGINAL (MANTIDO)
# ============================================
st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }

[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 10px !important;
    font-weight: 600 !important;
    margin-bottom: -15px !important;
    color: #4b5563;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
    margin-bottom: -12px !important;
}

div.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    font-weight: 600;
    border-radius: 6px;
    width: 90% !important;
    margin-left: 5%;
    font-size: 11px;
}

.container-performance {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

.titulo-secao {
    text-align: center;
    color: #2563eb;
    font-size: 18px;
    font-weight: 700;
}

.score {
    text-align: center;
    font-size: 40px;
    font-weight: 700;
}

table {
    margin: auto;
    font-size: 13px;
    text-align: center;
    border-collapse: collapse;
    width: 450px;
}

th {
    background-color: #2563eb;
    color: white;
    padding: 8px;
}

td {
    padding: 8px;
    border-bottom: 1px solid #eee;
}

.val-pos { color: #16a34a; font-weight: 800; }
.val-neg { color: #dc2626; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown(
    "<h1 style='text-align:center;color:#2563eb;'>"
    "Evaluación de Riesgo y Score de Crédito</h1>",
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "Simulación de Crédito",
    "Desempeño del Modelo",
    "Estabilidad (PSI)"
])

# ============================================
# TAB 1
# ============================================
with tab1:

    with st.sidebar:
        st.markdown("### Datos del Cliente")

        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero = "male" if st.selectbox("Género", ["Masculino", "Femenino"]) == "Masculino" else "female"

        trabajo = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[
            st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])
        ]

        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[
            st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])
        ]

        ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[
            st.selectbox("Ahorro", ["Bajo","Medio","Alto"])
        ]

        corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[
            st.selectbox("Corriente", ["Bajo","Medio","Alto"])
        ]

        finalidad = {
            "Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV",
            "Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"
        }[
            st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])
        ]

        btn = st.button("Calcular")

    col1, col2 = st.columns(2)

    if btn:

        # =========================
        # INPUT
        # =========================
        df = pd.DataFrame({
            "Genero":[genero],
            "Trabalho":[trabalho],
            "Habitacao":[habitacion],
            "Conta_poupanca":[ahorro],
            "Conta_corrente":[corriente],
            "Finalidade":[finalidad],
            "Idade":[edad],
            "Duracao":[duracion],
            "Valor_credito":[valor]
        })

        df_woe = sc.woebin_ply(df, bins_woe)\
            .reindex(columns=modelo.feature_names_in_, fill_value=0)

        prob = modelo.predict_proba(df_woe)[0][1]

        # =========================
        # SCORE
        # =========================
        score = get_score(prob, score_params)

        # =========================
        # POLICY ENGINE
        # =========================
        result = apply_business_policy(score, prob, valor, cutoffs)

        # =========================
        # RESULTADO
        # =========================
        with col1:
            st.markdown("<div class='titulo-secao'>Resultado</div>", unsafe_allow_html=True)

            st.markdown(
                f"<div class='score' style='color:{result['cor']};'>{score}</div>",
                unsafe_allow_html=True
            )

            st.markdown(f"<h3 style='text-align:center;color:#2563eb;'>{result['segmento']}</h3>", unsafe_allow_html=True)

            st.metric("Probabilidad", f"{prob:.2%}")
            st.metric("Límite", f"${result['limite']:,.0f}")

            st.markdown(
                f"<h2 style='text-align:center;color:{result['cor']};'>{result['icon']} {result['status']}</h2>",
                unsafe_allow_html=True
            )

            st.caption(result["motivo"])

        # =========================
        # GAUGE
        # =========================
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                gauge={
                    "axis":{"range":[0,100]},
                    "steps":[
                        {"range":[0,40],"color":"#16a34a"},
                        {"range":[40,70],"color":"#facc15"},
                        {"range":[70,100],"color":"#dc2626"}
                    ]
                }
            ))

            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2
# ============================================
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {})

    st.markdown("### Métricas del Modelo")
    st.json(m)

    st.markdown("### Matriz de Confusión")

    st.table(pd.DataFrame({
        "": ["Bom(0)", "Ruim(1)"],
        "Pred 0": [cm.get("TN",0), cm.get("FN",0)],
        "Pred 1": [cm.get("FP",0), cm.get("TP",0)]
    }))

# ============================================
# TAB 3
# ============================================
with tab3:
    psi = metricas_modelo.get("psi", 0)

    st.markdown("### PSI (Estabilidad del Modelo)")

    st.metric("PSI", f"{psi:.4f}")

    if psi < 0.1:
        st.success("Modelo Estável")
    elif psi < 0.25:
        st.warning("Alerta de drift")
    else:
        st.error("Modelo instável")