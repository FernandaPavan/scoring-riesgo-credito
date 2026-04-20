# ==================================================
# 1. IMPORTS
# ==================================================
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.graph_objects as go
import scorecardpy as sc

# ==================================================
# PATH
# ==================================================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_PATH, "models")

model = joblib.load(os.path.join(MODEL_PATH, "modelo.pkl"))
bins = joblib.load(os.path.join(MODEL_PATH, "woe_bins.pkl"))

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(layout="wide")

st.markdown("""
<h1 style='text-align:center;color:#2563eb'>
Scoring de Crédito
</h1>
<br><br>
""", unsafe_allow_html=True)

# ==================================================
# SIDEBAR - DATOS DEL CLIENTE
# ==================================================
with st.sidebar:

    st.markdown(
        "<div style='text-align:center;font-size:20px;font-weight:600;color:#2563eb'>Datos del Cliente</div>",
        unsafe_allow_html=True
    )

    edad = st.slider("Edad", 18, 75, 30)
    valor = st.slider("Monto del crédito", 250, 20000, 5000, step=250)
    duracao = st.slider("Duración (meses)", 4, 72, 24)

    genero_map = {"Masculino": "male", "Femenino": "female"}
    genero = genero_map[st.selectbox("Género", list(genero_map.keys()))]

    # =========================
    # TRABAJO (CORRIGIDO)
    # =========================
    trabajo_map = {
        "Desempleado": 0,
        "Básico": 1,
        "Calificado": 2,
        "Especialista": 3
    }

    trabajo = trabajo_map[st.selectbox("Ocupación", list(trabajo_map.keys()))]

    habitacao_map = {
        "Propia": "own",
        "Alquilada": "rent",
        "Gratuita": "free"
    }
    habitacao = habitacao_map[st.selectbox("Vivienda", list(habitacao_map.keys()))]

    conta_map = {
        "Bajo": "little",
        "Medio": "moderate",
        "Alto": "rich"
    }

    conta_poup = conta_map[st.selectbox("Cuenta de ahorro", list(conta_map.keys()))]
    conta_corr = conta_map[st.selectbox("Cuenta corriente", list(conta_map.keys()))]

    finalidad_map = {
        "Auto": "car",
        "Muebles": "furniture/equipment",
        "TV": "radio/TV",
        "Negocios": "business",
        "Educación": "education",
        "Reparaciones": "repairs",
        "Otros": "vacation/others"
    }

    finalidad = finalidad_map[st.selectbox("Finalidad", list(finalidade_map.keys()))]

    btn = st.button("Calcular", use_container_width=True)

# ==================================================
# LAYOUT
# ==================================================
col2, col3 = st.columns([1, 1])

# ==================================================
# EXECUÇÃO
# ==================================================
if btn:

    # ==========================================
    # INPUT RAW (NÃO MEXER NAS COLUNAS DO MODELO)
    # ==========================================
    entrada = pd.DataFrame([{
        "Genero": genero,
        "Trabalho": trabalho,
        "Habitacao": habitacao,
        "Conta_poupanca": conta_poup,
        "Conta_corrente": conta_corr,
        "Finalidade": finalidade,
        "Idade": edad,
        "Duracao": duracao,
        "Valor_credito": valor
    }])

    # ==========================================
    # WOE TRANSFORM
    # ==========================================
    entrada_woe = sc.woebin_ply(entrada, bins)

    entrada_woe = entrada_woe.reindex(
        columns=model.feature_names_in_,
        fill_value=0
    )

    # ==========================================
    # PREDIÇÃO
    # ==========================================
    prob = model.predict_proba(entrada_woe)[0][1]
    score = int(850 - prob * 550)

    # ==========================================
    # POLÍTICA DE CRÉDITO
    # ==========================================
    if score >= 750:
        limite = 18000
    elif score >= 700:
        limite = 10000
    elif score >= 650:
        limite = 4000
    elif score >= 600:
        limite = 2500
    elif score >= 550:
        limite = 250
    else:
        limite = 0

    if duracao > 48:
        limite *= 0.80
    elif duracao > 36:
        limite *= 0.90

    if score < 550:
        status = "✖ RECHAZADO"
        cor = "#dc2626"

    elif valor <= limite:
        status = "✔ APROBADO"
        cor = "#16a34a"

    elif valor <= limite * 1.2:
        status = "⚠ EN ANÁLISIS"
        cor = "#facc15"

    else:
        status = "✖ RECHAZADO"
        cor = "#dc2626"

    # ==================================================
    # COLUNA 2 - RESULTADO
    # ==================================================
    with col2:

        st.markdown(
            "<div style='text-align:center;font-size:20px;font-weight:600;color:#2563eb'>Resultado</div>",
            unsafe_allow_html=True
        )

        st.markdown(f"## Score: {score}")
        st.markdown(f"Probabilidad: {prob:.2%}")
        st.markdown(f"Límite aprobado: R$ {limite:,.0f}")

        st.markdown(
            f"<h2 style='color:{cor};text-align:center'>{status}</h2>",
            unsafe_allow_html=True
        )

    # ==================================================
    # COLUNA 3 - RISCO
    # ==================================================
    with col3:

        st.markdown(
            "<div style='text-align:center;font-size:20px;font-weight:600;color:#2563eb'>Indicador de Riesgo</div>",
            unsafe_allow_html=True
        )

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            gauge={
                "axis": {"range": [0, 100]},
                "steps": [
                    {"range": [0, 40], "color": "#16a34a"},
                    {"range": [40, 70], "color": "#facc15"},
                    {"range": [70, 100], "color": "#dc2626"}
                ]
            }
        ))

        fig.update_layout(
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig, use_container_width=True)