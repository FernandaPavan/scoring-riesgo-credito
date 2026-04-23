import streamlit as st
import os 
import sys
import pandas as pd
import numpy as np
import scorecardpy as sc
import plotly.graph_objects as go

# Ajuste de Caminho
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from styles import apply_custom_styles
from src.loader import load_assets
from src.policy import get_score, apply_business_policy

# Configuração da Página
st.set_page_config(layout="wide", page_title="Credit Score App")
apply_custom_styles()

# Carregar Ativos
modelo, bins_woe, metricas_modelo, score_params = load_assets()

cutoffs = {"reject_cutoff": 490, "approve_cutoff": 540}

st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación", "Desempeño", "Estabilidad"])

with tab1:
    with st.sidebar:
        st.header("Datos del Cliente")
        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto", 250, 20000, 5000, step=250)
        duracion = st.slider("Meses", 4, 72, 24)
        genero = "male" if st.selectbox("Género", ["Masculino","Femenino"]) == "Masculino" else "female"
        trabalho_idx = st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"], index=2)
        trabalho_map = {"Desempleado":0, "Básico":1, "Calificado":2, "Especialista":3}
        
        habitacao = st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])
        habitacao_map = {"Propia":"own", "Alquilada":"rent", "Gratuita":"free"}
        
        ahorro = st.selectbox("Ahorro", ["Bajo","Medio","Alto"])
        ahorro_map = {"Bajo":"little", "Medio":"moderate", "Alto":"rich"}
        
        corriente = st.selectbox("Corriente", ["Bajo","Medio","Alto"])
        corriente_map = {"Bajo":"little", "Medio":"moderate", "Alto":"rich"}
        
        btn = st.button("Calcular Score")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        # 1. Preparar Dados
        entrada = pd.DataFrame({
            "Genero": [genero], "Trabalho": [trabalho_map[trabalho_idx]], 
            "Habitacao": [habitacao_map[habitacao]], "Conta_poupanca": [ahorro_map[ahorro]], 
            "Conta_corrente": [corriente_map[corriente]], "Finalidade": ["car"], 
            "Idade": [edad], "Duracao": [duracion], "Valor_credito": [monto]
        })

        # 2. Processar Score
        entrada_woe = sc.woebin_ply(entrada, bins_woe)
        if hasattr(modelo, "feature_names_in_"):
            entrada_woe = entrada_woe.reindex(columns=modelo.feature_names_in_, fill_value=0)
        
        prob_risco = modelo.predict_proba(entrada_woe)[0][0] # Captura prob. de classe 0
        score_base = get_score(prob_risco, score_params)
        res = apply_business_policy(score_base, None, None, None, None, monto)

        # 3. Decisão Final (Cut-offs)
        if score_base < cutoffs["reject_cutoff"]:
            res.update({"status": "RECHAZADO", "icon": "❌", "cor": "#dc2626"})
        elif score_base >= cutoffs["approve_cutoff"]:
            res.update({"status": "APROBADO", "icon": "✅", "cor": "#16a34a"})
        else:
            res.update({"status": "EN ANÁLISIS", "icon": "⚠️", "cor": "#facc15"})

        # 4. Renderizar Resultados
        with col_res:
            st.markdown(f"""
                <div style='text-align:center; padding:20px; border-radius:10px; border:1px solid #eee;'>
                    <h2 style='color:{res['cor']}; font-size:60px; margin:0;'>{score_base}</h2>
                    <p style='font-weight:bold; color:#2563eb;'>{res['segmento']}</p>
                    <hr>
                    <p>Límite Sugerido: <b>${res['limite']:,.0f}</b></p>
                    <h1 style='color:{res['cor']};'>{res['icon']} {res['status']}</h1>
                    <p style='font-size:14px; color:gray;'>{res['motivo']}</p>
                </div>
            """, unsafe_allow_html=True)

        with col_graf:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=prob_risco*100, number={'suffix': "%"},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': res['cor']}}
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)