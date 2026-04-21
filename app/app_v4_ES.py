import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import os
import json
import scorecardpy as sc

# ============================================
# PATH
# ============================================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_PATH,"models")

# ============================================
# LOAD
# ============================================
modelo = joblib.load(os.path.join(MODEL_PATH,"modelo.pkl"))
bins_woe = joblib.load(os.path.join(MODEL_PATH,"woe_bins.pkl"))

with open(os.path.join(MODEL_PATH,"metricas.json"),"r") as f:
    metricas_modelo = json.load(f)

with open(os.path.join(MODEL_PATH,"score_params.json"),"r") as f:
    score_params = json.load(f)

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide")

# ============================================
# CSS ATUALIZADO (ABAS 20px | TITULOS 26px)
# ============================================
st.markdown("""
<style>
/* Estilo das Abas - Ajustado para 20px */
button[data-baseweb="tab"] p {
    font-size: 20px !important;
    font-weight: 600 !important;
}

/* Títulos de Seção - Ajustados para 26px */
.titulo-azul {
    text-align: center;
    color: #2563eb;
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 20px;
}

.score { text-align: center; font-size: 60px; font-weight: 700; }

div.stButton > button {
    background-color: #2563eb;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    height: 45px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:32px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1><br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

# ============================================
# TAB 1: SIMULACIÓN
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:20px;font-weight:600;'>Datos del Cliente</div>",unsafe_allow_html=True)
        edad = st.slider("Edad",18,75,30)
        valor = st.slider("Monto del Crédito",250,20000,5000,step=250)
        duracion = st.slider("Duración (meses)",4,72,24)

        genero = {"Masculino":"male","Femenino":"female"}[st.selectbox("Género",["Masculino","Femenino"])]
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[st.selectbox("Ocupación",["Desempleado","Básico","Calificado","Especialista"])]
        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[st.selectbox("Vivienda",["Propia","Alquilada","Gratuita"])]
        cuenta_ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta de Ahorro",["Bajo","Medio","Alto"])]
        cuenta_corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta Corriente",["Bajo","Medio","Alto"])]
        finalidad = {"Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV","Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"}[st.selectbox("Finalidad",["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])]

        btn = st.button("Calcular", use_container_width=True)

    col2, col3 = st.columns([1,1])

    if btn:
        entrada = pd.DataFrame({"Genero":[genero],"Trabalho":[trabalho],"Habitacao":[habitacion],"Conta_poupanca":[cuenta_ahorro],"Conta_corrente":[cuenta_corriente],"Finalidade":[finalidad],"Idade":[edad],"Duracao":[duracion],"Valor_credito":[valor]})
        entrada_woe = sc.woebin_ply(entrada,bins_woe).reindex(columns=modelo.feature_names_in_,fill_value=0)
        prob = min(max(modelo.predict_proba(entrada_woe)[0][1],0.0001),0.9999)

        # Regras de Negócio e Cálculo de Score
        factor = score_params["pdo"]/np.log(2)
        offset = score_params["base_score"] + factor*np.log(score_params["base_odds"])
        score_base = int(offset + factor*np.log((1-prob)/prob))
        
        penalidade = 0
        flags = []
        if trabalho == 0: penalidade -= 80; flags.append("Sin empleo")
        if habitacion == "rent": penalidade -= 30; flags.append("Vivienda alquilada")
        if conta_ahorro == "little": penalidade -= 20; flags.append("Bajo ahorro")
        if conta_corriente == "little": penalidade -= 20; flags.append("Baja liquidez")
        
        score = max(score_base + penalidade, 300)

        # Segmentação e Status (A mesma lógica anterior)
        # ... [omitido para brevidade, manter igual ao anterior]

        with col2:
            st.markdown("<div class='titulo-azul'>Resultado del Análisis</div>", unsafe_allow_html=True)
            # ... [código de exibição dos resultados]

        with col3:
            st.markdown("<div class='titulo-azul'>Indicador de Riesgo</div>", unsafe_allow_html=True)
            # ... [código do gauge]

# Manter Tab 2 e Tab 3 com o layout de tabelas/cards centralizados.

# ============================================
# TAB 2: MÉTRICAS (WITH GREEN VALUES)
# ============================================
with tab2:
    st.markdown("<h2 style='text-align:center;color:#2563eb;font-size:26px;'>Métricas del Modelo</h2>",unsafe_allow_html=True)
    metricas_df = pd.DataFrame({"Métrica":["Accuracy","Precisión","Recall","AUC","GINI","KS"],"Valor":[round(metricas_modelo["accuracy"],4), round(metricas_modelo["precision"],4), round(metricas_modelo["recall"],4), round(metricas_modelo["auc"],4), round(metricas_modelo["gini"],4), round(metricas_modelo["ks"],4)]})
    
    st.markdown(f"""
    <div style='display:flex;justify-content:center;margin-top:20px;'>
    <table style='width:650px;font-size:18px;text-align:center;border-collapse:collapse;'>
        <tr style='background-color:#2563eb;color:white;'><th>Métrica</th><th>Valor</th></tr>
        {''.join([f"<tr><td style='padding:10px;border-bottom:1px solid #ddd;'>{m}</td><td style='padding:10px;border-bottom:1px solid #ddd;'>{v}</td></tr>" for m,v in zip(metricas_df["Métrica"],metricas_df["Valor"])])}
    </table>
    </div>
    """, unsafe_allow_html=True)

    cm = metricas_modelo["confusion_matrix"]
    st.markdown(f"""
    <div style='display:flex;justify-content:center;margin-top:30px;'>
    <table style='width:650px;font-size:18px;text-align:center;border-collapse:collapse;border:1px solid #ddd;'>
        <tr style='background-color:#2563eb;color:white;'><th>Real \ Pred</th><th>Bom (0)</th><th>Ruim (1)</th></tr>
        <tr><td><b>Real: Bom (0)</b></td><td style='color:#16a34a; font-weight:700;'>{cm['TN']}</td><td style='color:#dc2626; font-weight:700;'>{cm['FP']}</td></tr>
        <tr><td><b>Real: Ruim (1)</b></td><td style='color:#dc2626; font-weight:700;'>{cm['FN']}</td><td style='color:#16a34a; font-weight:700;'>{cm['TP']}</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 3: ESTABILIDADE
# ============================================
with tab3:
    st.markdown("<h2 style='text-align:center;color:#2563eb;'>Estabilidad de la Población (PSI)</h2><br>", unsafe_allow_html=True)
    psi_valor = metricas_modelo.get("psi", 0.06)
    psi_cor = "#16a34a" if psi_valor < 0.1 else "#facc15" if psi_valor < 0.25 else "#dc2626"
    psi_status = "Estable" if psi_valor < 0.1 else "Alerta" if psi_valor < 0.25 else "Inestable"

    st.markdown(f"""
    <div style='display:flex; justify-content:center;'>
        <div style='text-align:center; border:2px solid {psi_cor}; padding:40px; border-radius:15px; width:400px; background-color:#f9fafb;'>
            <p style='margin:0; font-size:24px; color:#4b5563;'>PSI Acumulado</p>
            <p style='margin:10px 0; font-size:64px; font-weight:800; color:{psi_cor};'>{psi_valor}</p>
            <div style='background-color:{psi_cor}; color:white; padding:8px 20px; border-radius:20px; display:inline-block; font-weight:700; font-size:20px;'>{psi_status}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)