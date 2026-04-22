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
# CSS CUSTOMIZADO
# ============================================
st.markdown("""
<style>
/* 1. Margens Gerais */
.block-container { padding-top: 1rem !important; }

/* 2. SIDEBAR - Ajuste de Labels e Caixas */
[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 11px !important;
    font-weight: 600 !important;
    margin-bottom: 5px !important;
    color: #4b5563;
}

[data-testid="stSidebar"] div[data-baseweb="select"], 
[data-testid="stSidebar"] div[data-testid="stSlider"] {
    margin-bottom: 15px !important;
}

/* 3. BOTÃO CALCULAR */
div.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    font-weight: 600;
    border-radius: 6px;
    height: 35px;
    width: 90% !important;
    margin-left: 5%;
    border: none;
    margin-top: 20px;
}

/* 4. ABA DESEMPENHO E PSI - CENTRALIZAÇÃO E ALTURA */
.container-performance {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    margin-top: -45px !important; 
}

.titulo-tabela-azul {
    text-align: center;
    color: #2563eb;
    font-size: 16px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 5px;
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

/* 5. CARD PSI ESTILIZADO */
.card-psi {
    text-align: center;
    border: 1px solid #e2e8f0;
    padding: 20px;
    border-radius: 12px;
    background-color: #ffffff;
    width: 280px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-top: 15px;
}

.psi-valor {
    margin: 0;
    font-size: 42px;
    font-weight: 800;
    line-height: 1;
}

/* 6. TEXTOS RESULTADO TAB 1 */
.titulo-secao { text-align: center; color: #2563eb; font-size: 18px; font-weight: 700; }
.score { text-align: center; font-size: 40px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño do Modelo", "Estabilidad (PSI)"])

# ============================================
# TAB 1: SIMULACIÓN
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:14px;font-weight:600;margin-bottom:10px;'>Datos del Cliente</div>", unsafe_allow_html=True)
        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto", 250, 20000, 5000, step=250)
        duracion = st.slider("Meses", 4, 72, 24)
        genero = st.selectbox("Género", ["Masculino","Femenino"])
        trabalho = st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])
        habitacion = st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])
        ahorro = st.selectbox("Ahorro", ["Bajo","Medio","Alto"])
        corriente = st.selectbox("Corriente", ["Bajo","Medio","Alto"])
        finalidad = st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Edu","Outros"])
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])
    if btn:
        prob, score, cor_score = 0.5547, 586, "#facc15" 
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{cor_score};'>{score}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-weight:700;color:#2563eb;'>NEAR PRIME</p>", unsafe_allow_html=True)
        with col_graf:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, number={'suffix': "%"}))
            fig.update_layout(height=240, margin=dict(l=30, r=30, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: DESEMPENHO
# ============================================
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})
    
    st.markdown("<div class='container-performance'>", unsafe_allow_html=True)
    st.markdown("<p class='titulo-tabela-azul'>Métricas Generales</p>", unsafe_allow_html=True)
    st.markdown(f"""
    <table style='margin-bottom: 15px;'>
        <tr><th>Métrica</th><th>Valor</th></tr>
        <tr><td>Best Model</td><td>{m.get('best_model', 'N/A')}</td></tr>
        <tr><td>Accuracy</td><td>{m.get('accuracy', 0):.4f}</td></tr>
        <tr><td>Precision</td><td>{m.get('precision', 0):.4f}</td></tr>
        <tr><td>Recall</td><td>{m.get('recall', 0):.4f}</td></tr>
        <tr><td>F1-Score</td><td>{m.get('f1_score', 0):.4f}</td></tr>
        <tr><td>AUC</td><td>{m.get('auc', 0):.4f}</td></tr>
        <tr><td>Gini</td><td>{m.get('gini', 0):.4f}</td></tr>
        <tr><td>KS</td><td>{m.get('ks', 0):.4f}</td></tr>
    </table>""", unsafe_allow_html=True)

    st.markdown("<p class='titulo-tabela-azul'>Matriz de Confusión</p>", unsafe_allow_html=True)
    st.markdown(f"""
    <table>
        <tr><th></th><th>Pred Negativo</th><th>Pred Positivo</th></tr>
        <tr>
            <td><b>Real Negativo</b></td>
            <td class='val-pos'>{cm.get('TN', 0)} (TN)</td>
            <td class='val-neg'>{cm.get('FP', 0)} (FP)</td>
        </tr>
        <tr>
            <td><b>Real Positivo</b></td>
            <td class='val-neg'>{cm.get('FN', 0)} (FN)</td>
            <td class='val-pos'>{cm.get('TP', 0)} (TP)</td>
        </tr>
    </table>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# TAB 3: ESTABILIDADE (PSI AJUSTADO)
# ============================================
with tab3:
    psi_valor = metricas_modelo.get("psi", 0.00)
    # Lógica de cor: Verde para estável (< 0.1), Amarelo (< 0.25), Vermelho (> 0.25)
    psi_cor = "#16a34a" if psi_valor < 0.1 else "#facc15" if psi_valor < 0.25 else "#dc2626"
    psi_status = "ESTÁVEL" if psi_valor < 0.1 else "ALERTA" if psi_valor < 0.25 else "INSTÁVEL"

    st.markdown(f"""
    <div class='container-performance'>
        <p class='titulo-tabela-azul'>Estabilidad del Modelo (PSI)</p>
        <div class='card-psi'>
            <p style='margin:0; font-size:11px; color:#64748b; font-weight:700; letter-spacing:1px;'>PSI ACUMULADO</p>
            <h1 class='psi-valor' style='color:{psi_cor};'>{psi_valor:.4f}</h1>
            <p style='margin-top:10px; margin-bottom:0; font-size:12px; color:{psi_cor}; font-weight:800;'>
                STATUS: {psi_status}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)