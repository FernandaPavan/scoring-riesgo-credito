import streamlit as st
import os 
import sys
import pandas as pd
import numpy as np
import scorecardpy as sc
import plotly.graph_objects as go

# Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from styles import apply_custom_styles
from src.loader import load_assets
from src.policy import get_score, apply_business_policy

st.set_page_config(layout="wide", page_title="Credit Score App")
apply_custom_styles()

# Assets
modelo, bins_woe, metricas_modelo, score_params = load_assets()

# Cutoffs baseados no seu arquivo ou definidos manualmente
cutoffs = {"reject_cutoff": 490, "approve_cutoff": 540}

st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación", "Desempeño", "Estabilidad"])

with tab1:
    with st.sidebar:
        st.markdown("### Datos del Cliente")
        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)
        
        genero = "male" if st.selectbox("Género", ["Masculino","Femenino"]) == "Masculino" else "female"
        trabalho_map = {"Desempleado":0, "Básico":1, "Calificado":2, "Especialista":3}
        trabalho_val = trabalho_map[st.selectbox("Ocupación", list(trabalho_map.keys()))]
        
        habitacao_map = {"Propia":"own", "Alquilada":"rent", "Gratuita":"free"}
        habitacao_val = habitacao_map[st.selectbox("Vivienda", list(habitacao_map.keys()))]
        
        ahorro_map = {"Bajo":"little", "Medio":"moderate", "Alto":"rich"}
        ahorro_val = ahorro_map[st.selectbox("Conta Ahorro", list(ahorro_map.keys()))]
        
        corriente_map = {"Bajo":"little", "Medio":"moderate", "Alto":"rich"}
        corriente_val = corriente_map[st.selectbox("Conta Corriente", list(corriente_map.keys()))]

        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        entrada = pd.DataFrame({
            "Genero": [genero], "Trabalho": [trabalho_val], "Habitacao": [habitacao_val],
            "Conta_poupanca": [ahorro_val], "Conta_corrente": [corriente_val],
            "Finalidade": ["car"], "Idade": [edad], "Duracao": [duracion], "Valor_credito": [monto]
        })

        # Transformação WOE usando o nome correto do arquivo woe_bins
        entrada_woe = sc.woebin_ply(entrada, bins_woe)
        if hasattr(modelo, "feature_names_in_"):
            entrada_woe = entrada_woe.reindex(columns=modelo.feature_names_in_, fill_value=0)

        # Predição
        prob_default = float(modelo.predict_proba(entrada_woe)[0][1])

        # Score e Política
        score_base = get_score(prob_default, score_params)
        res = apply_business_policy(score_base, None, None, None, None, monto)

        # Regra de Decisão
        if score_base < cutoffs["reject_cutoff"]:
            res.update({"status": "RECHAZADO", "icon": "❌", "cor": "#dc2626"})
        elif score_base >= cutoffs["approve_cutoff"]:
            res.update({"status": "APROBADO", "icon": "✅", "cor": "#16a34a"})
        else:
            res.update({"status": "EN ANÁLISIS", "icon": "⚠️", "cor": "#facc15"})

        with col_res:
            st.markdown(f"<div class='score' style='color:{res['cor']};'>{score_base}</div>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center;color:{res['cor']};'>{res['icon']} {res['status']}</h2>", unsafe_allow_html=True)
            st.info(f"Límite Sugerido: ${res['limite']:,.0f}")
            st.write(f"Motivo: {res['motivo']}")

        with col_graf:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=prob_default * 100, number={'suffix': "%"},
                gauge={"axis":{"range":[0,100]}, "bar":{"color":res['cor']}}
            ))
            st.plotly_chart(fig, use_container_width=True)