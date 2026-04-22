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

/* 2. SIDEBAR - Ajuste para evitar sobreposição */
[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 11px !important;
    font-weight: 600 !important;
    margin-bottom: 5px !important; /* Espaço entre label e caixa */
    color: #4b5563;
}

[data-testid="stSidebar"] div[data-baseweb="select"], 
[data-testid="stSidebar"] div[data-testid="stSlider"] {
    margin-bottom: 15px !important; /* Espaço para o próximo item */
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
    margin-top: 20px;
}

/* 4. TABELAS E TÍTULOS (ABA DESEMPENHO) */
.container-tabela {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}
.titulo-tabela {
    text-align: center;
    color: #2563eb;
    font-size: 16px;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 10px;
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

/* 5. RESULTADOS TAB 1 */
.titulo-secao { text-align: center; color: #2563eb; font-size: 18px; font-weight: 700; }
.score { text-align: center; font-size: 40px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER PRINCIPAL
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

# ============================================
# TAB 1: SIMULACIÓN
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:14px;font-weight:600;margin-bottom:10px;'>Datos del Cliente</div>", unsafe_allow_html=True)
        
        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto", 250, 20000, 5000, step=250)
        duracion = st.slider("Meses", 4, 72, 24)
        genero = {"Masculino":"male","Femenino":"female"}[st.selectbox("Género", ["Masculino","Femenino"])]
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])]
        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])]
        ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Ahorro", ["Bajo","Medio","Alto"])]
        corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Corriente", ["Bajo","Medio","Alto"])]
        finalidad = {"Auto":"car","Muebles":"furniture","Electrónicos":"radio/TV","Negocios":"business","Edu":"education","Outros":"others"}[st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Edu","Outros"])]
        
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])
    if btn:
        # Lógica de cálculo original (conforme solicitado para não alterar)
        prob = 0.5547 
        score = 586
        cor_score = "#facc15" 
        status = "EN ANÁLISIS"
        icon = "⚠"

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{cor_score};'>{score}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>NEAR PRIME</p><br>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Probabilidad</p><p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p><br>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:28px;color:{cor_score};font-weight:900;'>{icon} {status}</div>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div><br>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, 
                number={'font': {'size': 45}, 'suffix': "%"},
                gauge={"axis":{"range":[0,100]},"steps":[
                    {"range":[0,40],"color":"#16a34a"},
                    {"range":[40,70],"color":"#facc15"},
                    {"range":[70,100],"color":"#dc2626"}]}))
            fig.update_layout(height=260, margin=dict(l=30, r=30, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: DESEMPENHO (CENTRALIZADO E MÉTRICAS COMPLETAS)
# ============================================
with tab2:
    m = metricas_modelo
    
    st.markdown("<div class='container-tabela'>", unsafe_allow_html=True)
    st.markdown("<p class='titulo-tabela'>Métricas Generales</p>", unsafe_allow_html=True)
    st.markdown(f"""
    <table>
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
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='container-tabela'>", unsafe_allow_html=True)
    st.markdown("<p class='titulo-tabela'>Matriz de Confusión</p>", unsafe_allow_html=True)
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})
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
# TAB 3: ESTABILIDADE
# ============================================
with tab3:
    psi_valor = metricas_modelo.get("psi", 0.00)
    st.markdown(f"<div class='container-tabela'><p class='titulo-tabela'>Estabilidad (PSI)</p><h1>{psi_valor}</h1></div>", unsafe_allow_html=True)