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
# CSS CUSTOMIZADO
# ============================================
st.markdown("""
<style>
/* 1. Margens Gerais */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0rem !important;
}

/* 2. SIDEBAR ULTRA-COMPACTO */
[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 11px !important;
    font-weight: 500 !important;
    margin-bottom: -20px !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.05rem !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"], 
[data-testid="stSidebar"] div[data-testid="stSlider"] {
    transform: scale(0.90);
    transform-origin: left top;
}

/* 3. BOTÃO CALCULAR AZUL */
div.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    font-weight: 600;
    border-radius: 8px;
    height: 35px;
    width: 100%;
    border: none;
}

/* 4. TÍTULOS E SCORE */
.titulo-secao {
    text-align: center;
    color: #2563eb;
    font-size: 18px;
    font-weight: 700;
}
.score { 
    text-align: center; 
    font-size: 40px; 
    font-weight: 700; 
    line-height: 1;
}

/* 5. TABELAS CENTRALIZADAS */
.container-tabela {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    margin-bottom: 10px;
}
table {
    margin-left: auto;
    margin-right: auto;
    font-size: 13px;
    text-align: center;
    border-collapse: collapse;
    width: 500px; /* Largura fixa para padronizar */
}
th {
    background-color: #2563eb;
    color: white;
    padding: 8px;
}
td {
    padding: 6px;
    border-bottom: 1px solid #eee;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER PRINCIPAL
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;margin-bottom:0;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

# ============================================
# TAB 1: SIMULACIÓN
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:14px;font-weight:600;'>Datos del Cliente</div>", unsafe_allow_html=True)
        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero = {"Masculino":"male","Femenino":"female"}[st.selectbox("Género", ["Masculino","Femenino"])]
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])]
        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])]
        cuenta_ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta de Ahorro", ["Bajo","Medio","Alto"])]
        cuenta_corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta Corriente", ["Bajo","Medio","Alto"])]
        finalidad = {"Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV","Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"}[st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])]
        
        st.write("") 
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        entrada = pd.DataFrame({"Genero":[genero],"Trabalho":[trabalho],"Habitacao":[habitacion],"Conta_poupanca":[cuenta_ahorro],"Conta_corrente":[cuenta_corriente],"Finalidade":[finalidad],"Idade":[edad],"Duracao":[duracion],"Valor_credito":[valor]})
        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(columns=modelo.feature_names_in_, fill_value=0)
        prob = min(max(modelo.predict_proba(entrada_woe)[0][1], 0.0001), 0.9999)

        # SCORE E STATUS
        factor = score_params["pdo"]/np.log(2)
        offset = score_params["base_score"] + factor*np.log(score_params["base_odds"])
        score = max(int(offset + factor*np.log((1-prob)/prob)), 300)
        
        if prob < 0.4: status, icon, cor, segmento = "APROBADO", "✔", "#16a34a", "PRIME"
        elif prob < 0.7: status, icon, cor, segmento = "EN ANÁLISIS", "⚠", "#facc15", "NEAR PRIME"
        else: status, icon, cor, segmento = "RECHAZADO", "✖", "#dc2626", "SUBPRIME"
        
        limite = 5000
        motivo = "Perfil analizado mediante el modelo de scoring crediticio."

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{cor};'>{score}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{segmento}</p><br>", unsafe_allow_html=True)
            
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Probabilidad</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p><br>", unsafe_allow_html=True)
            
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Límite</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:22px;font-weight:700;'>${limite:,.0f}</p><br>", unsafe_allow_html=True)
            
            st.markdown(f"<div style='text-align:center;font-size:28px;color:{cor};font-weight:900;'>{icon} {status}</div><br>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:12px;'>{motivo}</p>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div><br>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, 
                number={'font': {'size': 40}, 'suffix': "%", 'valueformat': ".1f"},
                gauge={"axis":{"range":[0,100]},"steps":[
                    {"range":[0,40],"color":"#16a34a"},
                    {"range":[40,70],"color":"#facc15"},
                    {"range":[70,100],"color":"#dc2626"}]}))
            fig.update_layout(height=250, margin=dict(l=30, r=30, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: DESEMPENHO (Centralizado e Organizado)
# ============================================
with tab2:
    st.markdown("<h2 style='text-align:center;color:#2563eb;font-size:20px;'>Desempeño del Modelo</h2>", unsafe_allow_html=True)
    
    # 1. Tabela de Métricas Centralizada
    st.markdown("<div class='container-tabela'>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:700; text-align:center;'>Métricas Generales</p>", unsafe_allow_html=True)
    m = metricas_modelo
    metrics_html = f"""
    <table>
        <tr><th>Métrica</th><th>Valor</th></tr>
        <tr><td>Accuracy</td><td>{m['accuracy']:.4f}</td></tr>
        <tr><td>AUC</td><td>{m['auc']:.4f}</td></tr>
        <tr><td>Gini</td><td>{m['gini']:.4f}</td></tr>
        <tr><td>KS</td><td>{m['ks']:.4f}</td></tr>
    </table><br>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Pulo de linha e Matriz de Confusão Centralizada
    st.markdown("<div class='container-tabela'>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:700; text-align:center;'>Matriz de Confusión</p>", unsafe_allow_html=True)
    cm = m.get("confusion_matrix", {"TN": 0, "FP": 0, "FN": 0, "TP": 0})
    matrix_html = f"""
    <table>
        <tr><th></th><th>Pred. Negativo</th><th>Pred. Positivo</th></tr>
        <tr><td style='font-weight:700; background-color:#f9f9f9;'>Real Negativo</td><td style='color:#16a34a; font-weight:900;'>{cm['TN']} (TN)</td><td>{cm['FP']} (FP)</td></tr>
        <tr><td style='font-weight:700; background-color:#f9f9f9;'>Real Positivo</td><td>{cm['FN']} (FN)</td><td style='color:#16a34a; font-weight:900;'>{cm['TP']} (TP)</td></tr>
    </table>
    """
    st.markdown(matrix_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# TAB 3: ESTABILIDADE
# ============================================
with tab3:
    st.markdown("<h2 style='text-align:center;color:#2563eb;font-size:20px;'>Estabilidad (PSI)</h2>", unsafe_allow_html=True)
    psi_valor = metricas_modelo.get("psi", 0.06)
    psi_cor = "#16a34a" if psi_valor < 0.1 else "#facc15" if psi_valor < 0.25 else "#dc2626"
    
    st.markdown(f"""
    <div style='display:flex; justify-content:center; margin-top:10px;'>
        <div style='text-align:center; border:2px solid {psi_cor}; padding:15px; border-radius:15px; width:280px; background-color:#f9fafb;'>
            <p style='margin:0; font-size:16px;'>PSI Acumulado</p>
            <p style='margin:5px 0; font-size:42px; font-weight:800; color:{psi_cor};'>{psi_valor}</p>
        </div>
    </div>""", unsafe_allow_html=True)
