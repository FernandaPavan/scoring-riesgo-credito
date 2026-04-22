import streamlit as st
import os 
import sys
import pandas as pd
import numpy as np
import scorecardpy as sc
import plotly.graph_objects as go

# Ajuste de caminho para localizar a pasta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from styles import apply_custom_styles
from src.loader import load_assets
from src.policy import get_score, apply_business_policy

# 1. Configuração e Estilos
st.set_page_config(layout="wide", page_title="Credit Score App")
apply_custom_styles()

# 2. Carregar Modelos (Ajustado para o seu loader modular)
modelo, bins_woe, metricas_modelo, score_params = load_assets()

# 3. Header
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;margin-bottom:5px;'>Datos del Cliente</div>", unsafe_allow_html=True)
        
        # --- VARIÁVEIS EM ESPANHOL (O que o usuário vê) ---
        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)
        
        gen_sel = st.selectbox("Género", ["Masculino","Femenino"])
        genero = "male" if gen_sel == "Masculino" else "female"
        
        trab_sel = st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[trab_sel]
        
        hab_sel = st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])
        habitacao = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[hab_sel]
        
        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo","Medio","Alto"])
        ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[ahorro_sel]
        
        corr_sel = st.selectbox("Cuenta Corriente", ["Bajo","Medio","Alto"])
        corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[corr_sel]
        
        fin_sel = st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])
        finalidade = {"Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV","Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"}[fin_sel]
        
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        # =========================================================================
        # A PONTE: Traduzindo nomes do App para nomes do Pipeline (Português)
        # Esquerda (aspas) = Como está no seu Pipeline
        # Direita (variável) = Como você definiu nos sliders acima
        # =========================================================================
        entrada = pd.DataFrame({
            "Genero": [genero],
            "Trabalho": [trabalho],
            "Habitacao": [habitacao],
            "Conta_poupanca": [ahorro],
            "Conta_corrente": [corriente],
            "Finalidade": [finalidade],
            "Idade": [edad],
            "Duracao": [duracion],
            "Valor_credito": [monto]
        })

        # Processamento WoE e Predição
        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(columns=modelo.feature_names_in_, fill_value=0)
        prob = modelo.predict_proba(entrada_woe)[0][1]

        # Chamar a política de negócio (Passando as variáveis em espanhol/sem acento)
        res = apply_business_policy(get_score(prob, score_params), trabalho, habitacao, ahorro, corriente, monto)

        # Exibição dos resultados (Mantendo seu layout original)
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{res['cor']};'>{res['score']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{res['segmento']}</p>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:28px;color:{res['cor']};font-weight:900;'>{res['icon']} {res['status']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:12px;color:#64748b;'>{res['motivo']}</p>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, number={'suffix': "%"},
                gauge={"axis":{"range":[0,100]},"steps":[{"range":[0,40],"color":"#16a34a"},{"range":[40,70],"color":"#facc15"},{"range":[70,100],"color":"#dc2626"}]}))
            st.plotly_chart(fig, use_container_width=True)

# ... (restante das abas Tab 2 e Tab 3 que já estão corretas)