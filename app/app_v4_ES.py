import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import os
import json
import scorecardpy as sc

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide")

# ============================================
# PATH
# ============================================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_PATH,"models")

# ============================================
# LOAD
# ============================================
modelo = joblib.load(os.path.join(MODEL_PATH,"modelo.pkl"))
bins_woe = joblib.load(os.path.join(MODEL_PATH,"woe_bins.pkl"))

with open(os.path.join(MODEL_PATH,"metricas.json"),"r") as f:
    metricas_modelo = json.load(f)

with open(os.path.join(MODEL_PATH,"score_params.json"),"r") as f:
    score_params = json.load(f)

# ============================================
# CSS ULTRA COMPACTO
# ============================================
st.markdown("""
<style>

/* Sidebar menor */
section[data-testid="stSidebar"] {
    width: 260px !important;
}

/* Inputs mais compactos */
div[data-baseweb="select"] > div {
    min-height: 35px !important;
    font-size: 14px !important;
}

div[data-testid="stSlider"] {
    margin-bottom: 10px !important;
}

/* Botão */
div.stButton > button {
    height: 38px;
    font-size: 14px;
    border-radius: 6px;
}

/* Tabs menores */
button[data-baseweb="tab"] p {
    font-size: 16px !important;
}

/* Títulos */
.titulo-secao {
    text-align: center;
    color: #2563eb;
    font-size: 18px;
    font-weight: 700;
}

/* Score menor */
.score {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
}

/* Reduz padding geral */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* Remove espaços extras */
.element-container {
    margin-bottom: 0.5rem !important;
}

</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("<h2 style='text-align:center;color:#2563eb;'>Evaluación de Riesgo y Score de Crédito</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación", "Modelo", "PSI"])

# ============================================
# TAB 1
# ============================================
with tab1:

    with st.sidebar:
        st.markdown("<b>Datos del Cliente</b>", unsafe_allow_html=True)

        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Meses", 4, 72, 24)

        genero = {"Masculino":"male","Femenino":"female"}[st.selectbox("Género", ["Masculino","Femenino"])]
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])]
        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])]
        cuenta_ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Ahorro", ["Bajo","Medio","Alto"])]
        cuenta_corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta", ["Bajo","Medio","Alto"])]

        btn = st.button("Calcular", use_container_width=True)

    col2, col3 = st.columns([1.2, 0.8])

    if btn:

        entrada = pd.DataFrame({
            "Genero":[genero],
            "Trabalho":[trabalho],
            "Habitacao":[habitacion],
            "Conta_poupanca":[cuenta_ahorro],
            "Conta_corrente":[cuenta_corriente],
            "Idade":[edad],
            "Duracao":[duracion],
            "Valor_credito":[valor]
        })

        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(columns=modelo.feature_names_in_, fill_value=0)

        prob = min(max(modelo.predict_proba(entrada_woe)[0][1], 0.0001), 0.9999)

        factor = score_params["pdo"]/np.log(2)
        offset = score_params["base_score"] + factor*np.log(score_params["base_odds"])
        score = int(offset + factor*np.log((1-prob)/prob))

        with col2:
            st.markdown("<div class='titulo-secao'>Resultado</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='score'>{score}</div>", unsafe_allow_html=True)
            st.metric("Probabilidad", f"{prob:.2%}")

        with col3:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob*100,
                gauge={"axis":{"range":[0,100]}}
            ))
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2
# ============================================
with tab2:

    st.markdown("<div class='titulo-secao'>Métricas</div>", unsafe_allow_html=True)

    df = pd.DataFrame({
        "Métrica":["AUC","GINI","KS"],
        "Valor":[metricas_modelo["auc"], metricas_modelo["gini"], metricas_modelo["ks"]]
    })

    st.dataframe(df, use_container_width=True, height=200)

# ============================================
# TAB 3
# ============================================
with tab3:

    psi = metricas_modelo.get("psi", 0.06)

    st.metric("PSI", psi)
    
