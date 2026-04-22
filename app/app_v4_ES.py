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
# PATH E CARREGAMENTO (DINÂMICO PARA LOCAL E CLOUD)
# ============================================
# Pega o caminho de onde o arquivo app_v4_ES.py está
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Sobe um nível para encontrar a pasta 'models' (ajuste se a pasta estiver no mesmo nível)
BASE_PROJECT = os.path.dirname(CURRENT_DIR)
MODEL_PATH = os.path.join(BASE_PROJECT, "models")

# Caminhos específicos para os arquivos
FILE_MODELO = os.path.join(MODEL_PATH, "modelo.pkl")
FILE_BINS = os.path.join(MODEL_PATH, "woe_bins.pkl")
FILE_PARAMS = os.path.join(MODEL_PATH, "score_params.json")
FILE_METRICAS = os.path.join(MODEL_PATH, "metricas.json")

@st.cache_resource
def load_data():
    with open(FILE_METRICAS, "r") as f:
        metricas = json.load(f)
    with open(FILE_PARAMS, "r") as f:
        params = json.load(f)
        
    modelo = joblib.load(FILE_MODELO)
    bins_woe = joblib.load(FILE_BINS)
        
    return modelo, bins_woe, metricas, params

modelo, bins_woe, metricas_modelo, score_params = load_data()

# ============================================
# CSS CUSTOMIZADO
# ============================================
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #f8fafc; }
[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 10px !important;
    font-weight: 600 !important;
    color: #4b5563 !important;
    margin-bottom: -15px !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] div {
    font-size: 11px !important;
    min-height: 28px !important;
}
[data-testid="stSidebar"] [data-testid="stTickBarMinMax"], 
[data-testid="stSidebar"] [data-testid="stThumbValue"] {
    font-size: 10px !important;
}
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
.performance-table th { background-color: #2563eb; color: white; padding: 10px; }
.performance-table td { padding: 8px; border-bottom: 1px solid #eee; }
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
        # Mapeamento para predição
        gen_val = "male" if genero == "Masculino" else "female"
        entrada = pd.DataFrame({"Genero":[gen_val],"Trabalho":[0],"Habitacao":["own"],"Conta_poupanca":["little"],"Conta_corrente":["little"],"Finalidade":["car"],"Idade":[edad],"Duracao":[duracion],"Valor_credito":[valor]})
        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(columns=modelo.feature_names_in_, fill_value=0)
        prob = min(max(modelo.predict_proba(entrada_woe)[0][1], 0.0001), 0.9999)
        
        # Cálculo Score
        factor = score_params["pdo"]/np.log(2)
        offset = score_params["base_score"] + factor*np.log(score_params["base_odds"])
        score = max(int(offset + factor*np.log((1-prob)/prob)), 300)
        
        cor = "#16a34a" if prob < 0.4 else "#facc15" if prob < 0.7 else "#dc2626"
        status = "APROBADO" if prob < 0.4 else "EN ANÁLISIS" if prob < 0.7 else "RECHAZADO"

        with col_res:
            st.markdown(f"<div class='centered-container'><p style='color:#2563eb;font-weight:700;'>Resultado</p><h1 style='color:{cor};font-size:40px;'>{score}</h1></div>", unsafe_allow_html=True)
        with col_graf:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, number={'suffix': "%"}))
            fig.update_layout(height=240, margin=dict(l=20, r=20, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: DESEMPENHO (CENTRALIZADO)
# ============================================
with tab2:
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
        </table>

        <p style='font-weight:700; color:#2563eb; font-size:16px;'>Matriz de Confusión</p>
        <table class='performance-table'>
            <tr><th></th><th>Pred Negativo</th><th>Pred Positivo</th></tr>
            <tr><td><b>Real Negativo</b></td><td class='val-pos'>{cm['TN']}</td><td class='val-neg'>{cm['FP']}</td></tr>
            <tr><td><b>Real Positivo</b></td><td class='val-neg'>{cm['FN']}</td><td class='val-pos'>{cm['TP']}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 3: ESTABILIDADE
# ============================================
with tab3:
    psi_valor = metricas_modelo.get("psi", 0.00)
    st.markdown(f"<div class='centered-container'><p style='font-weight:700; color:#2563eb; margin-top:20px;'>PSI</p><h1>{psi_valor}</h1></div>", unsafe_allow_html=True)
