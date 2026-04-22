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
# Caminho absoluto solicitado para as métricas
METRICAS_PATH = r"C:/Users/Fernanda Pavan/OneDrive/Desktop/Projeto_Risco_Credito/models/metricas.json"
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_PATH, "models")

@st.cache_resource
def load_data():
    # Carregamento do modelo e bins (mantendo lógica anterior)
    modelo = joblib.load(os.path.join(MODEL_PATH, "modelo.pkl"))
    bins_woe = joblib.load(os.path.join(MODEL_PATH, "woe_bins.pkl"))
    with open(os.path.join(MODEL_PATH, "score_params.json"), "r") as f:
        params = json.load(f)
    
    # Carregamento das métricas do caminho específico
    with open(METRICAS_PATH, "r") as f:
        metricas = json.load(f)
        
    return modelo, bins_woe, metricas, params

modelo, bins_woe, metricas_modelo, score_params = load_data()

# ============================================
# CSS CUSTOMIZADO
# ============================================
st.markdown("""
<style>
/* 1. Ajuste Geral do Sidebar */
[data-testid="stSidebar"] {
    background-color: #f8fafc;
}

/* 2. LABELS DO SIDEBAR (Fontes Pequenas) */
[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 10px !important;
    font-weight: 600 !important;
    color: #4b5563 !important;
    margin-bottom: -15px !important;
}

/* 3. TEXTO INTERNO DAS CAIXAS */
[data-testid="stSidebar"] div[data-baseweb="select"] div {
    font-size: 11px !important;
    min-height: 28px !important;
}

/* 4. VALORES DO SLIDER */
[data-testid="stSidebar"] [data-testid="stTickBarMinMax"], 
[data-testid="stSidebar"] [data-testid="stThumbValue"] {
    font-size: 10px !important;
}

/* 5. BOTÃO CALCULAR AZUL */
div.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    font-weight: 600;
    border-radius: 6px;
    height: 32px;
    width: 90% !important;
    margin-left: 5%;
    border: none;
    margin-top: 15px !important;
}

/* 6. CENTRALIZAÇÃO TOTAL (ABA DESEMPENHO) */
.centered-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 100%;
}

.performance-table {
    margin-left: auto;
    margin-right: auto;
    font-size: 12px;
    text-align: center;
    border-collapse: collapse;
    width: 450px;
    margin-top: 10px;
    margin-bottom: 25px;
}

.performance-table th {
    background-color: #2563eb;
    color: white;
    padding: 10px;
}

.performance-table td {
    padding: 8px;
    border-bottom: 1px solid #eee;
}

.val-pos { color: #16a34a; font-weight: 800; }
.val-neg { color: #dc2626; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:22px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

# ============================================
# TAB 1: SIMULACIÓN
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<p style='text-align:center;color:#2563eb;font-size:13px;font-weight:700;'>Datos del Cliente</p>", unsafe_allow_html=True)
        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto", 250, 20000, 5000, step=250)
        duracion = st.slider("Meses", 4, 72, 24)
        genero = st.selectbox("Género", ["Masculino", "Femenino"])
        ocupacion = st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])
        vivienda = st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])
        ahorro = st.selectbox("Ahorro", ["Bajo", "Medio", "Alto"])
        corriente = st.selectbox("Corriente", ["Bajo", "Medio", "Alto"])
        finalidad = st.selectbox("Finalidad", ["Auto", "Muebles", "Electrónicos", "Negocios", "Edu", "Otros"])
        
        st.write("")
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])
    if btn:
        # Lógica de simulação simplificada para visualização
        prob = 0.5547 
        score = 586
        cor = "#facc15" 
        
        with col_res:
            st.markdown(f"<div class='centered-container'><p style='color:#2563eb;font-weight:700;'>Resultado</p><h1 style='color:{cor};font-size:40px;'>{score}</h1><p><b>NEAR PRIME</b></p></div>", unsafe_allow_html=True)
        with col_graf:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, number={'suffix': "%"}))
            fig.update_layout(height=240, margin=dict(l=20, r=20, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: DESEMPENHO (CENTRALIZADO SEM TÍTULO)
# ============================================
with tab2:
    # Uso das métricas carregadas do arquivo metricas.json
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})
    
    st.markdown(f"""
    <div class='centered-container'>
        <p style='font-weight:700; color:#2563eb; font-size:16px; margin-top:20px;'>Métricas Generales</p>
        <table class='performance-table'>
            <tr><th>Métrica</th><th>Valor</th></tr>
            <tr><td>Accuracy</td><td>{m.get('accuracy', 0):.4f}</td></tr>
            <tr><td>AUC</td><td>{m.get('auc', 0):.4f}</td></tr>
            <tr><td>Gini</td><td>{m.get('gini', 0):.4f}</td></tr>
            <tr><td>F1-Score</td><td>{m.get('f1', 0):.4f}</td></tr>
        </table>

        <p style='font-weight:700; color:#2563eb; font-size:16px;'>Matriz de Confusión</p>
        <table class='performance-table'>
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
        </table>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 3: ESTABILIDADE
# ============================================
with tab3:
    psi_valor = metricas_modelo.get("psi", 0.00)
    st.markdown(f"""
    <div class='centered-container'>
        <p style='font-weight:700; color:#2563eb; font-size:16px; margin-top:20px;'>Estabilidad del Modelo (PSI)</p>
        <h1 style='color:#16a34a;'>{psi_valor}</h1>
    </div>
    """, unsafe_allow_html=True)
