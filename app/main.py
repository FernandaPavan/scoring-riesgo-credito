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
@st.cache_resource
def load_data():
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_PROJECT = os.path.dirname(CURRENT_DIR)
    MODEL_PATH = os.path.join(BASE_PROJECT, "models")
    
    modelo = joblib.load(os.path.join(MODEL_PATH, "modelo.pkl"))
    bins_woe = joblib.load(os.path.join(MODEL_PATH, "woe_bins.pkl"))
    
    with open(os.path.join(MODEL_PATH, "metricas.json")) as f:
        metricas = json.load(f)
        
    with open(os.path.join(MODEL_PATH, "score_params.json")) as f:
        params = json.load(f)
        
    return modelo, bins_woe, metricas, params

modelo, bins_woe, metricas_modelo, score_params = load_data()

# ============================================
# HEADER
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación", "Modelo", "PSI"])

# ============================================
# TAB 1
# ============================================
with tab1:
    with st.sidebar:
        st.header("Cliente")

        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto", 250, 20000, 5000, step=250)
        duracion = st.slider("Meses", 1, 72, 24)

        genero = "male" if st.selectbox("Género", ["Masculino","Femenino"]) == "Masculino" else "female"

        trabalho = {
            "Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3
        }[st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])]

        habitacion = {
            "Propia":"own","Alquilada":"rent","Gratuita":"free"
        }[st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])]

        ahorro = {
            "Bajo":"little","Medio":"moderate","Alto":"rich"
        }[st.selectbox("Ahorro", ["Bajo","Medio","Alto"])]

        corriente = {
            "Bajo":"little","Medio":"moderate","Alto":"rich"
        }[st.selectbox("Corriente", ["Bajo","Medio","Alto"])]

        finalidad = {
            "Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV",
            "Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"
        }[st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])]

        btn = st.button("Calcular")

    col1, col2 = st.columns(2)

    if btn:
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

        # segurança (evita mismatch silencioso)
        assert set(modelo.feature_names_in_) == set(df_woe.columns)

        prob = np.clip(modelo.predict_proba(df_woe)[0][1], 0.0001, 0.9999)

        # SCORE BASE
        factor = score_params["pdo"] / np.log(2)
        offset = score_params["base_score"] + factor*np.log(score_params["base_odds"])
        score_base = int(offset + factor*np.log((1-prob)/prob))

        # ============================================
        # PENALIDADES (SUAVES)
        # ============================================
        penal_score = 0
        penal_limite = 1.0

        if trabalho == 0:
            penal_score -= 40
            penal_limite *= 0.7

        if habitacion == "rent":
            penal_score -= 15
            penal_limite *= 0.9

        if duracion > 24:
            penal_score -= 15
            penal_limite *= 0.9

        score = max(score_base + penal_score, 300)

        # SEGMENTO
        if score >= 700: seg, lim_base = "SUPER PRIME", 18000
        elif score >= 650: seg, lim_base = "PRIME", 10000
        elif score >= 600: seg, lim_base = "STANDARD", 5000
        elif score >= 520: seg, lim_base = "NEAR PRIME", 2500
        elif score >= 460: seg, lim_base = "REVIEW", 1000
        else: seg, lim_base = "SUBPRIME", 0

        limite = int(lim_base * penal_limite)

        # ============================================
        # DECISÃO FINAL (CORRIGIDA)
        # ============================================
        if trabalho == 0 and duracion > 24:
            status, cor = "RECHAZADO", "#dc2626"
            motivo = "Riesgo crítico: desempleado con plazo largo."

        elif score < 460:
            status, cor = "RECHAZADO", "#dc2626"
            motivo = "Score bajo política mínima."

        elif score < 520:
            status, cor = "EN ANÁLISIS", "#facc15"
            motivo = f"Perfil en evaluación. Monto será validado contra límite estimado de ${limite:,.0f}."

        elif score >= 520 and valor <= limite:
            status, cor = "APROBADO", "#16a34a"
            motivo = "Dentro del límite aprobado."

        else:
            status, cor = "RECHAZADO", "#dc2626"
            motivo = f"Excede el límite de ${limite:,.0f}."

        icon = "✔" if status=="APROBADO" else "⚠" if status=="EN ANÁLISIS" else "✖"

        # RESULTADO
        with col1:
            st.metric("Score", score)
            st.metric("Segmento", seg)
            st.metric("Riesgo", f"{prob:.2%}")
            st.metric("Límite", f"${limite:,.0f}")

            st.markdown(f"<h2 style='color:{cor}'>{icon} {status}</h2>", unsafe_allow_html=True)
            st.caption(motivo)

        # GAUGE
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob*100,
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

# ============================================
# TAB 2
# ============================================
with tab2:
    st.json(metricas_modelo)

# ============================================
# TAB 3
# ============================================
with tab3:
    psi = metricas_modelo.get("psi", 0)
    st.metric("PSI", f"{psi:.4f}")