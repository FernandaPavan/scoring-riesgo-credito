import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import os
import json
import scorecardpy as sc

# ============================================
# CONFIGURAÇÃO INICIAL
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App")

# ============================================
# PATH E CARREGAMENTO
# ============================================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_PATH, "models")

@st.cache_resource
def load_data():
    modelo = joblib.load(os.path.join(MODEL_PATH, "modelo.pkl"))
    bins_woe = joblib.load(os.path.join(MODEL_PATH, "woe_bins.pkl"))
    with open(os.path.join(MODEL_PATH, "metricas.json"), "r") as f:
        metricas = json.load(f)
    with open(os.path.join(MODEL_PATH, "score_params.json"), "r") as f:
        params = json.load(f)
    return modelo, bins_woe, metricas, params

modelo, bins_woe, metricas_modelo, score_params = load_data()

# ============================================
# CSS AJUSTADO (LABELS PEQUENOS, INPUT NORMAL)
# ============================================
st.markdown("""
<style>

/* Margens gerais */
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}

/* ===== SIDEBAR ===== */

/* Labels (Edad, Monto, etc.) */
[data-testid="stSidebar"] label {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #4b5563 !important;
    margin-bottom: 2px !important;
}

/* Ajuste fino do container do label */
[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] {
    margin-bottom: 2px !important;
}

/* NÃO altera texto interno dos inputs */
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    min-height: 32px !important;
}

/* Sliders compactos */
[data-testid="stSidebar"] div[data-testid="stSlider"] {
    margin-bottom: 6px !important;
}

/* Espaçamento geral menor */
[data-testid="stSidebar"] .element-container {
    margin-bottom: 4px !important;
}

/* Botão */
div.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    font-weight: 600;
    border-radius: 6px;
    height: 32px;
    width: 70%;
    margin-left: 10%;
    border: none;
}

/* Títulos */
.titulo-secao {
    text-align: center;
    color: #2563eb;
    font-size: 18px;
    font-weight: 700;
}

/* Score */
.score {
    text-align: center;
    font-size: 40px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown(
    "<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>",
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
        st.markdown(
            "<div style='text-align:center;color:#2563eb;font-size:13px;font-weight:600;margin-bottom:10px;'>Datos del Cliente</div>",
            unsafe_allow_html=True
        )

        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto", 250, 20000, 5000, step=250)
        duracion = st.slider("Meses", 4, 72, 24)

        genero = {"Masculino": "male", "Femenino": "female"}[
            st.selectbox("Género", ["Masculino", "Femenino"])
        ]
        trabalho = {"Desempleado": 0, "Básico": 1, "Calificado": 2, "Especialista": 3}[
            st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])
        ]
        habitacion = {"Propia": "own", "Alquilada": "rent", "Gratuita": "free"}[
            st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])
        ]
        cuenta_ahorro = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}[
            st.selectbox("Ahorro", ["Bajo", "Medio", "Alto"])
        ]
        cuenta_corriente = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}[
            st.selectbox("Corriente", ["Bajo", "Medio", "Alto"])
        ]
        finalidad = {
            "Auto": "car",
            "Muebles": "furniture",
            "Electrónicos": "radio/TV",
            "Negocios": "business",
            "Edu": "education",
            "Outros": "others"
        }[
            st.selectbox("Finalidad", ["Auto", "Muebles", "Electrónicos", "Negocios", "Edu", "Outros"])
        ]

        st.markdown("<br>", unsafe_allow_html=True)
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        entrada = pd.DataFrame({
            "Genero": [genero],
            "Trabalho": [trabalho],
            "Habitacao": [habitacion],
            "Conta_poupanca": [cuenta_ahorro],
            "Conta_corrente": [cuenta_corriente],
            "Finalidade": [finalidad],
            "Idade": [edad],
            "Duracao": [duracion],
            "Valor_credito": [valor]
        })

        entrada_woe = sc.woebin_ply(entrada, bins_woe)\
            .reindex(columns=modelo.feature_names_in_, fill_value=0)

        prob = min(max(modelo.predict_proba(entrada_woe)[0][1], 0.0001), 0.9999)

        factor = score_params["pdo"] / np.log(2)
        offset = score_params["base_score"] + factor * np.log(score_params["base_odds"])
        score = max(int(offset + factor * np.log((1 - prob) / prob)), 300)

        if prob < 0.4:
            status, icon, cor, segmento = "APROBADO", "✔", "#16a34a", "PRIME"
        elif prob < 0.7:
            status, icon, cor, segmento = "EN ANÁLISIS", "⚠", "#facc15", "NEAR PRIME"
        else:
            status, icon, cor, segmento = "RECHAZADO", "✖", "#dc2626", "SUBPRIME"

        limite = 5000

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{cor};'>{score}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:16px;font-weight:700;color:#2563eb;'>{segmento}</p>", unsafe_allow_html=True)
            st.metric("Probabilidad", f"{prob:.2%}")
            st.metric("Límite", f"${limite:,.0f}")
            st.markdown(f"<div style='text-align:center;font-size:24px;color:{cor};font-weight:900;'>{icon} {status}</div>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div>", unsafe_allow_html=True)

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'font': {'size': 40}, 'suffix': "%"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "steps": [
                        {"range": [0, 40], "color": "#16a34a"},
                        {"range": [40, 70], "color": "#facc15"},
                        {"range": [70, 100], "color": "#dc2626"}
                    ]
                }
            ))

            fig.update_layout(height=250, margin=dict(l=20, r=20, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2
# ============================================
with tab2:
    st.markdown("<h3 style='text-align:center;color:#2563eb;'>Desempeño del Modelo</h3>", unsafe_allow_html=True)

    df = pd.DataFrame({
        "Métrica": ["Accuracy", "AUC", "Gini"],
        "Valor": [
            metricas_modelo["accuracy"],
            metricas_modelo["auc"],
            metricas_modelo["gini"]
        ]
    })

    st.dataframe(df, use_container_width=True, height=200)

# ============================================
# TAB 3
# ============================================
with tab3:
    psi_valor = metricas_modelo.get("psi", 0.06)
    st.metric("PSI", psi_valor)
