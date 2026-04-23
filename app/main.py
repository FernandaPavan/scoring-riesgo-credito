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
st.set_page_config(layout="wide", page_title="Credit Score App")

# ============================================
# LOAD
# ============================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PROJECT = os.path.dirname(CURRENT_DIR)
MODEL_PATH = os.path.join(BASE_PROJECT, "models")

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
# CUT-OFFS (DO MODELO)
# ============================================
prob_cutoff = 0.5304270540931582
reject_cutoff = 460
approve_cutoff = 520

# ============================================
# UI
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

# ============================================
# TAB 1
# ============================================
with tab1:
    with st.sidebar:
        edad = st.slider("Edad", 18, 75, 30)
        valor_solicitado = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero = "male" if st.selectbox("Género", ["Masculino","Femenino"]) == "Masculino" else "female"

        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])]

        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])]

        ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta de Ahorro", ["Bajo","Medio","Alto"])]

        corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta Corriente", ["Bajo","Medio","Alto"])]

        finalidad = {"Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV","Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"}[st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])]

        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:

        # ============================================
        # INPUT
        # ============================================
        entrada = pd.DataFrame({
            "Genero":[genero],
            "Trabalho":[trabalho],
            "Habitacao":[habitacion],
            "Conta_poupanca":[ahorro],
            "Conta_corrente":[corriente],
            "Finalidade":[finalidad],
            "Idade":[edad],
            "Duracao":[duracion],
            "Valor_credito":[valor_solicitado]
        })

        entrada_woe = sc.woebin_ply(entrada, bins_woe)\
            .reindex(columns=modelo.feature_names_in_, fill_value=0)

        # ============================================
        # PROBABILIDADE
        # ============================================
        prob = float(np.clip(modelo.predict_proba(entrada_woe)[0][1], 0.0001, 0.9999))

        # ============================================
        # SCORE (PDO)
        # ============================================
        factor = score_params["pdo"] / np.log(2)
        offset = score_params["base_score"] - factor * np.log(score_params["base_odds"])

        odds = (1 - prob) / prob
        score = int(round(offset + factor * np.log(odds)))

        # ============================================
        # LIMITE (BASEADO NO SCORE)
        # ============================================
        limite = int(np.interp(score, [460, 700], [500, 20000]))

        # ============================================
        # DECISÃO (PROB + KS)
        # ============================================
        if prob >= prob_cutoff:
            status = "RECHAZADO"
            icon = "❌"
            cor = "#dc2626"
            motivo = "Alta probabilidad de default"

        elif score < reject_cutoff:
            status = "RECHAZADO"
            icon = "❌"
            cor = "#dc2626"
            motivo = "Score muy bajo"

        elif score >= approve_cutoff:
            status = "APROBADO"
            icon = "✅"
            cor = "#16a34a"
            motivo = "Riesgo bajo"

        else:
            status = "EN ANÁLISIS"
            icon = "⚠️"
            cor = "#facc15"
            motivo = "Zona intermedia"

        # ============================================
        # SEGMENTO
        # ============================================
        if score >= 700: segmento="SUPER PRIME"
        elif score >= 650: segmento="PRIME"
        elif score >= 600: segmento="STANDARD"
        elif score >= 520: segmento="NEAR PRIME"
        elif score >= 460: segmento="REVIEW"
        else: segmento="SUBPRIME"

        # ============================================
        # RESULTADO
        # ============================================
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)

            st.markdown(f"<div class='score' style='color:{cor};'>{score}</div>", unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{segmento}</p>", unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center;'>Probabilidad</p><p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>", unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center;'>Límite Sugerido</p><p style='text-align:center;font-size:22px;font-weight:700;'>${limite:,.0f}</p>", unsafe_allow_html=True)

            st.markdown(f"<div style='text-align:center;font-size:28px;color:{cor};font-weight:900;'>{icon} {status}</div>", unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center;font-size:12px;color:#64748b;'>{motivo}</p>", unsafe_allow_html=True)

        # ============================================
        # GAUGE
        # ============================================
        with col_graf:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'suffix': "%"},
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