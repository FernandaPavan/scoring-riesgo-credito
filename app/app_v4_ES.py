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
# ============================================
# CSS CUSTOMIZADO (CORREÇÃO DE SOBREPOSIÇÃO)
# ============================================
st.markdown("""
<style>
/* 1. Margens Gerais */
.block-container {
    padding-top: 1rem !important;
}

/* 2. SIDEBAR - Ajuste de Espaçamento para evitar sobreposição */
[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 11px !important; 
    font-weight: 500 !important;
    margin-bottom: 0px !important; /* Voltou para 0 para não sobrepor */
    padding-bottom: 0px !important;
    color: #4b5563;
}

/* Ajusta as caixas e sliders sem "puxar" para cima do texto */
[data-testid="stSidebar"] div[data-baseweb="select"], 
[data-testid="stSidebar"] div[data-testid="stSlider"] {
    transform: scale(0.92); /* Aumentado levemente para melhor leitura */
    transform-origin: left top;
    margin-top: -5px !important; /* Ajuste fino de proximidade */
    margin-bottom: 5px !important; /* Espaço para o próximo item */
}

/* Compacta o espaçamento vertical entre os blocos do Streamlit */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.5rem !important; 
}

/* 3. BOTÃO CALCULAR AZUL */
div.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    font-weight: 600;
    border-radius: 6px;
    height: 35px;
    width: 90% !important;
    margin-left: 5%;
    border: none;
    margin-top: 20px !important; /* Garante espaço antes do botão */
}

/* 4. TABELAS CENTRALIZADAS */
.container-tabela {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    margin-top: 15px;
}
table {
    margin-left: auto;
    margin-right: auto;
    font-size: 13px;
    text-align: center;
    border-collapse: collapse;
    width: 450px;
}
th { background-color: #2563eb; color: white; padding: 8px; }
td { padding: 8px; border-bottom: 1px solid #eee; }
.val-pos { color: #16a34a; font-weight: 800; }
.val-neg { color: #dc2626; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ============================================
# TAB 1: SIMULACIÓN (SIDEBAR COM ESPAÇAMENTO CORRETO)
# ============================================
with tab1:
    with st.sidebar:
        # Título centralizado
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:16px;font-weight:600;margin-bottom:15px;'>Datos del Cliente</div>", unsafe_allow_html=True)
        
        # Inputs organizados
        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto", 250, 20000, 5000, step=250)
        duracion = st.slider("Meses", 4, 72, 24)
        
        # Para Selectboxes, usamos chaves para mapear os nomes amigáveis para os valores do modelo
        genero_map = {"Masculino": "male", "Femenino": "female"}
        genero_sel = st.selectbox("Género", list(genero_map.keys()))
        genero = genero_map[genero_sel]

        trabalho_map = {"Desempleado": 0, "Básico": 1, "Calificado": 2, "Especialista": 3}
        trabalho_sel = st.selectbox("Ocupación", list(trabalho_map.keys()))
        trabalho = trabalho_map[trabalho_sel]

        habitacion_map = {"Propia": "own", "Alquilada": "rent", "Gratuita": "free"}
        habitacion_sel = st.selectbox("Vivienda", list(habitacion_map.keys()))
        habitacion = habitacion_map[habitacion_sel]

        ahorro_map = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}
        ahorro_sel = st.selectbox("Ahorro", list(ahorro_map.keys()))
        ahorro = ahorro_map[ahorro_sel]

        corriente_map = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}
        corriente_sel = st.selectbox("Corriente", list(corriente_map.keys()))
        corriente = corriente_map[corriente_sel]

        finalidad_map = {"Auto": "car", "Muebles": "furniture", "Electrónicos": "radio/TV", "Negocios": "business", "Edu": "education", "Otros": "others"}
        finalidad_sel = st.selectbox("Finalidad", list(finalidad_map.keys()))
        finalidad = finalidad_map[finalidad_sel]
        
        # Pulo de linha visual antes do botão
        st.markdown("<br>", unsafe_allow_html=True) 
        btn = st.button("Calcular")

# ============================================
# TAB 2: DESEMPENHO (CENTRALIZADO E COLORIDO)
# ============================================
with tab2:
    st.markdown("<h2 style='text-align:center;color:#2563eb;font-size:20px;'>Desempeño del Modelo</h2>", unsafe_allow_html=True)
    m = metricas_modelo
    
    # Métricas Gerais
    st.markdown("<div class='container-tabela'>", unsafe_allow_html=True)
    st.write("**Métricas Generales**")
    st.markdown(f"""
    <table>
        <tr><th>Métrica</th><th>Valor</th></tr>
        <tr><td>Accuracy</td><td>{m['accuracy']:.4f}</td></tr>
        <tr><td>AUC</td><td>{m['auc']:.4f}</td></tr>
        <tr><td>Gini</td><td>{m['gini']:.4f}</td></tr>
    </table><br>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Matriz de Confusão
    st.markdown("<div class='container-tabela'>", unsafe_allow_html=True)
    st.write("**Matriz de Confusión**")
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})
    st.markdown(f"""
    <table>
        <tr><th></th><th>Pred Negativo</th><th>Pred Positivo</th></tr>
        <tr>
            <td><b>Real Negativo</b></td>
            <td class='val-pos'>{cm['TN']} (TN)</td>
            <td class='val-neg'>{cm['FP']} (FP)</td>
        </tr>
        <tr>
            <td><b>Real Positivo</b></td>
            <td class='val-neg'>{cm['FN']} (FN)</td>
            <td class='val-pos'>{cm['TP']} (TP)</td>
        </tr>
    </table>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# TAB 3: ESTABILIDADE
# ============================================
with tab3:
    psi_valor = metricas_modelo.get("psi", 0.06)
    psi_cor = "#16a34a" if psi_valor < 0.1 else "#dc2626"
    st.markdown(f"""
    <div style='display:flex; justify-content:center; margin-top:20px;'>
        <div style='text-align:center; border:2px solid {psi_cor}; padding:15px; border-radius:15px; width:250px;'>
            <p style='margin:0;'>PSI Acumulado</p>
            <h1 style='margin:0; color:{psi_cor};'>{psi_valor}</h1>
        </div>
    </div>""", unsafe_allow_html=True)
