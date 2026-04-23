import streamlit as st
import os 
import sys
import pandas as pd
import numpy as np
import scorecardpy as sc
import plotly.graph_objects as go

# Ajuste de PATH para encontrar a pasta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from styles import apply_custom_styles
from src.loader import load_assets
from src.policy import get_score, apply_business_policy

# Configurações iniciais
st.set_page_config(layout="wide", page_title="Credit Score App")
apply_custom_styles()

# Carregar Assets (Tratado no loader.py)
try:
    modelo, bins_woe, metricas_modelo, score_params = load_assets()
except Exception as e:
    st.error(f"Erro ao carregar arquivos .pkl: {e}")
    st.stop()

cutoffs = {"reject_cutoff": 490, "approve_cutoff": 540}

st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;margin-bottom:5px;'>Datos del Cliente</div>", unsafe_allow_html=True)
        
        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)
        
        # Mapeamentos para o modelo
        genero = "male" if st.selectbox("Género", ["Masculino","Femenino"]) == "Masculino" else "female"
        trabalho_idx = {"Desempleado":0, "Básico":1, "Calificado":2, "Especialista":3}[st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])]
        habitacao_val = {"Propia":"own", "Alquilada":"rent", "Gratuita":"free"}[st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])]
        ahorro_val = {"Bajo":"little", "Medio":"moderate", "Alto":"rich"}[st.selectbox("Cuenta de Ahorro", ["Bajo","Medio","Alto"])]
        corriente_val = {"Bajo":"little", "Medio":"moderate", "Alto":"rich"}[st.selectbox("Cuenta Corriente", ["Bajo","Medio","Alto"])]
        
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        # DataFrame de Entrada
        entrada = pd.DataFrame({
            "Genero": [genero], "Trabalho": [trabalho_idx], "Habitacao": [habitacao_val],
            "Conta_poupanca": [ahorro_val], "Conta_corrente": [corriente_val],
            "Finalidade": ["car"], "Idade": [edad], "Duracao": [duracion], "Valor_credito": [monto]
        })

        # Processamento WOE e Modelo
        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(columns=modelo.feature_names_in_, fill_value=0)
        
        # Probabilidade de Risco (Classe 0)
        probs = modelo.predict_proba(entrada_woe)[0]
        prob_default = float(probs[0]) 

        # Score e Política
        score_base = get_score(prob_default, score_params)
        res = apply_business_policy(score_base, None, None, None, None, monto)

        # Regra de Decisão Final
        if score_base < cutoffs["reject_cutoff"]:
            res.update({"status": "RECHAZADO", "icon": "❌", "cor": "#dc2626"})
        elif score_base >= cutoffs["approve_cutoff"]:
            res.update({"status": "APROBADO", "icon": "✅", "cor": "#16a34a"})
        else:
            res.update({"status": "EN ANÁLISIS", "icon": "⚠️", "cor": "#facc15"})

        # Renderização do Resultado (Layout Original)
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{res['cor']};'>{score_base}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{res['segmento']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'>Límite Sugerido: <b>${res['limite']:,.0f}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:28px;color:{res['cor']};font-weight:900;'>{res['icon']} {res['status']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:12px;color:#64748b;'>{res['motivo']}</p>", unsafe_allow_html=True)

        with col_graf:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=prob_default * 100, number={'suffix': "%"},
                gauge={"axis":{"range":[0,100]}, "steps":[{"range":[0,40],"color":"#16a34a"}, {"range":[40,70],"color":"#facc15"}, {"range":[70,100],"color":"#dc2626"}]}
            ))
            st.plotly_chart(fig, use_container_width=True)