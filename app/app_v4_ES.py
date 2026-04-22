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
# PATH E CARREGAMENTO (DINÂMICO)
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
# CSS CUSTOMIZADO (SIDEBAR COMPACTO E TABELAS)
# ============================================
st.markdown("""
<style>
/* 1. Margens Gerais */
.block-container { padding-top: 1rem !important; }

/* 2. SIDEBAR - Fontes Minúsculas e Caixas Compactas */
[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 10px !important;
    font-weight: 500 !important;
    margin-bottom: -25px !important;
    color: #4b5563;
}

[data-testid="stSidebar"] div[data-baseweb="select"], 
[data-testid="stSidebar"] div[data-testid="stSlider"] {
    transform: scale(0.88);
    transform-origin: left top;
    margin-bottom: -15px !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0rem !important;
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
}

/* 4. TABELAS CENTRALIZADAS (ABA DESEMPENHO) */
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

/* 5. TÍTULOS E SCORE (VOLTANDO AO ORIGINAL) */
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
        st.markdown("<br>", unsafe_allow_html=True) 
        
        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto", 250, 20000, 5000, step=250)
        duracion = st.slider("Meses", 4, 72, 24)
        genero = {"Masculino":"male","Femenino":"female"}[st.selectbox("Género", ["Masculino","Femenino"])]
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])]
        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])]
        ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Ahorro", ["Bajo","Medio","Alto"])]
        corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Corriente", ["Bajo","Medio","Alto"])]
        finalidad = {"Auto":"car","Muebles":"furniture","Electrónicos":"radio/TV","Negocios":"business","Edu":"education","Outros":"others"}[st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Edu","Outros"])]
        
        st.markdown("<br><br>", unsafe_allow_html=True) 
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        entrada = pd.DataFrame({"Genero":[genero],"Trabalho":[trabalho],"Habitacao":[habitacion],"Conta_poupanca":[ahorro],"Conta_corrente":[corriente],"Finalidade":[finalidad],"Idade":[edad],"Duracao":[duracion],"Valor_credito":[valor]})
        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(columns=modelo.feature_names_in_, fill_value=0)
        prob = min(max(modelo.predict_proba(entrada_woe)[0][1], 0.0001), 0.9999)

        factor = score_params["pdo"]/np.log(2)
        offset = score_params["base_score"] + factor*np.log(score_params["base_odds"])
        score = max(int(offset + factor*np.log((1-prob)/prob)), 300)
        
        cor_score = "#16a34a" if prob < 0.4 else "#facc15" if prob < 0.7 else "#dc2626"
        status = "APROBADO" if prob < 0.4 else "EN ANÁLISIS" if prob < 0.7 else "RECHAZADO"
        icon = "✔" if prob < 0.4 else "⚠" if prob < 0.7 else "✖"
        segmento = "PRIME" if prob < 0.4 else "NEAR PRIME" if prob < 0.7 else "SUBPRIME"

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{cor_score};'>{score}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{segmento}</p><br>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Probabilidad</p><p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p><br>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Límite</p><p style='text-align:center;font-size:22px;font-weight:700;'>$1,012</p><br>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:28px;color:{cor_score};font-weight:900;'>{icon} {status}</div>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div><br>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, 
                number={'font': {'size': 45}, 'suffix': "%", 'valueformat': ".1f"},
                gauge={"axis":{"range":[0,100]},"steps":[
                    {"range":[0,40],"color":"#16a34a"},
                    {"range":[40,70],"color":"#facc15"},
                    {"range":[70,100],"color":"#dc2626"}]}))
            fig.update_layout(height=260, margin=dict(l=30, r=30, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: DESEMPENHO (MÉTRICAS COMPLETAS E CENTRALIZADAS)
# ============================================
with tab2:
    m = metricas_modelo
    
    st.markdown("<div class='container-tabela'>", unsafe_allow_html=True)
    st.write("**Métricas Generales**")
    st.markdown(f"""
    <table>
        <tr><th>Métrica</th><th>Valor</th></tr>
        <tr><td>Accuracy</td><td>{m.get('accuracy', 0):.4f}</td></tr>
        <tr><td>AUC</td><td>{m.get('auc', 0):.4f}</td></tr>
        <tr><td>Gini</td><td>{m.get('gini', 0):.4f}</td></tr>
        <tr><td>F1-Score</td><td>{m.get('f1', 0):.4f}</td></tr>
    </table><br>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

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
    psi_valor = metricas_modelo.get("psi", 0.00)
    psi_cor = "#16a34a" if psi_valor < 0.1 else "#dc2626"
    st.markdown(f"""
    <div style='display:flex; justify-content:center; margin-top:20px;'>
        <div style='text-align:center; border:2px solid {psi_cor}; padding:15px; border-radius:15px; width:250px;'>
            <p style='margin:0; font-weight:700; color:#2563eb;'>PSI Acumulado</p>
            <h1 style='margin:0; color:{psi_cor};'>{psi_valor}</h1>
        </div>
    </div>""", unsafe_allow_html=True)
