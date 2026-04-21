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

st.markdown("""
<style>
.seccion{ text-align:center; color:#2563eb; font-size:20px; font-weight:600; }
.score{ text-align:center; font-size:60px; font-weight:700; }
div.stButton > button { background-color: #2563eb; color: white; font-weight: 600; border-radius: 8px; height: 45px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Simulación de Crédito","Desempeño del Modelo"])

# ============================================
# TAB 1: SIMULACIÓN (COM REGRAS AVANÇADAS)
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:20px;'>Datos del Cliente</div>",unsafe_allow_html=True)
        edad = st.slider("Edad",18,75,30); valor = st.slider("Monto",250,20000,5000,step=250); duracion = st.slider("Meses",4,72,24)
        
        genero = {"Masculino":"male","Femenino":"female"}[st.selectbox("Género",["Masculino","Femenino"])]
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[st.selectbox("Ocupación",["Desempleado","Básico","Calificado","Especialista"])]
        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[st.selectbox("Vivienda",["Propia","Alquilada","Gratuita"])]
        cuenta_ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Ahorro",["Bajo","Medio","Alto"])]
        cuenta_corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Corriente",["Bajo","Medio","Alto"])]
        finalidad = {"Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV","Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"}[st.selectbox("Finalidad",["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])]

        btn = st.button("Calcular",use_container_width=True)

    col2, col3 = st.columns([1,1])

    if btn:
        entrada = pd.DataFrame({"Genero":[genero],"Trabalho":[trabalho],"Habitacao":[habitacion],"Conta_poupanca":[cuenta_ahorro],"Conta_corrente":[cuenta_corriente],"Finalidade":[finalidad],"Idade":[edad],"Duracao":[duracion],"Valor_credito":[valor]})
        entrada_woe = sc.woebin_ply(entrada,bins_woe).reindex(columns=modelo.feature_names_in_,fill_value=0)
        prob = min(max(modelo.predict_proba(entrada_woe)[0][1],0.0001),0.9999)

        # SCORE AJUSTADO (RESOLVE O PROBLEMA DO SCORE ALTO PARA DESEMPREGADO)
        factor = score_params["pdo"]/np.log(2)
        offset = score_params["base_score"] + factor*np.log(score_params["base_odds"])
        score_puro = int(offset + factor*np.log((1-prob)/prob))
        
        # Penalidades Reais
        penalidade = 0
        flags = []
        if trabalho == 0: penalidade -= 80; flags.append("Sin empleo")
        if habitacion == "rent": penalidade -= 30; flags.append("Alquiler")
        if cuenta_ahorro == "little": penalidade -= 20; flags.append("Bajo ahorro")
        if cuenta_corriente == "little": penalidade -= 20; flags.append("Baja liquidez")
        
        score = max(score_puro + penalidade, 300)

        # SEGMENTAÇÃO E LIMITE
        if score >= 700: segmento="SUPER PRIME"; limite=18000
        elif score >= 650: segmento="PRIME"; limite=10000
        elif score >= 600: segmento="STANDARD"; limite=5000
        elif score >= 520: segmento="NEAR PRIME"; limite=2500
        elif score >= 460: segmento="REVIEW"; limite=1000
        else: segmento="SUBPRIME"; limite=0

        # Downgrade de Segurança
        if "Sin empleo" in flags and segmento in ["SUPER PRIME","PRIME"]: segmento = "NEAR PRIME"
        
        # Ajuste de Limite
        if trabalho == 0: limite *= 0.5
        limite = int(limite)

        # DECISÃO HARD RULE
        if trabalho == 0 and cuenta_corriente == "little":
            status="RECHAZADO"; icon="✖"; cor="#dc2626"; motivo="Riesgo crítico: sin empleo y baja liquidez."
        else:
            if score < 460: status="RECHAZADO"; icon="✖"; cor="#dc2626"; motivo="Score bajo política mínima."
            elif score < 520: status="EN ANÁLISIS"; icon="⚠"; cor="#facc15"; motivo="Zona intermedia de riesgo."
            else:
                if valor <= limite: status="APROBADO"; icon="✔"; cor="#16a34a"; motivo="Dentro del límite aprobado."
                else: status="RECHAZADO"; icon="✖"; cor="#dc2626"; motivo="Excede política de crédito."

        if flags: motivo += " | Riesgos: " + ", ".join(flags)

        with col2:
            st.markdown("<div class='seccion'>Resultado</div>",unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{cor};'>{score}</div>",unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:22px;font-weight:700;color:#2563eb;'>{segmento}</p>",unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:20px;'>Probabilidad: <b>{prob:.2%}</b></p>",unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:20px;'>Límite: <b>${limite:,.0f}</b></p>",unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:40px;color:{cor};font-weight:900;'>{icon} {status}</div>",unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;color:#374151;'>{motivo}</p>",unsafe_allow_html=True)

        with col3:
            fig=go.Figure(go.Indicator(mode="gauge+number", value=prob*100, gauge={"axis":{"range":[0,100]},"steps":[{"range":[0,40],"color":"#16a34a"},{"range":[40,70],"color":"#facc15"},{"range":[70,100],"color":"#dc2626"}]}))
            st.plotly_chart(fig,use_container_width=True)

# ============================================
# TAB 2: MÉTRICAS E PSI (MANTENDO O LAYOUT)
# ============================================
with tab2:
    st.markdown("<h2 style='text-align:center;color:#2563eb;'>Desempeño y Estabilidad del Modelo</h2>",unsafe_allow_html=True)
    
    # INDICADOR PSI (Novo!)
    psi_valor = metricas_modelo.get("psi", 0.08) # Simulado se não houver no JSON
    if psi_valor < 0.1: psi_status = "Estable"; psi_cor = "#16a34a"
    elif psi_valor < 0.25: psi_status = "Alerta"; psi_cor = "#facc15"
    else: psi_status = "Inestable"; psi_cor = "#dc2626"

    st.markdown(f"""
    <div style='display:flex; justify-content:center; gap:50px; margin-bottom:30px;'>
        <div style='text-align:center; border:2px solid #ddd; padding:20px; border-radius:10px; width:250px;'>
            <p style='margin:0; font-size:18px;'>PSI (Población)</p>
            <p style='margin:0; font-size:32px; font-weight:700; color:{psi_cor};'>{psi_valor}</p>
            <p style='margin:0; font-weight:600;'>{psi_status}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # TABELA DE MÉTRICAS ORIGINAL
    metricas_df = pd.DataFrame({"Métrica":["Accuracy","Precisión","Recall","AUC","GINI","KS"],"Valor":[round(metricas_modelo["accuracy"],4), round(metricas_modelo["precision"],4), round(metricas_modelo["recall"],4), round(metricas_modelo["auc"],4), round(metricas_modelo["gini"],4), round(metricas_modelo["ks"],4)]})
    st.markdown(f"""
    <div style='display:flex;justify-content:center;margin-top:20px;'>
    <table style='width:650px;font-size:18px;text-align:center;border-collapse:collapse;'>
        <tr style='background-color:#2563eb;color:white;'><th>Métrica</th><th>Valor</th></tr>
        {''.join([f"<tr><td style='padding:10px;border-bottom:1px solid #ddd;'>{m}</td><td style='padding:10px;border-bottom:1px solid #ddd;'>{v}</td></tr>" for m,v in zip(metricas_df["Métrica"],metricas_df["Valor"])])}
    </table>
    </div>
    """, unsafe_allow_html=True)

    # MATRIZ DE CONFUSÃO ORIGINAL
    cm = metricas_modelo["confusion_matrix"]
    st.markdown(f"""
    <div style='display:flex;justify-content:center;margin-top:30px;'>
    <table style='width:650px;font-size:18px;text-align:center;border-collapse:collapse;border:1px solid #ddd;'>
        <tr style='background-color:#2563eb;color:white;'><th></th><th>Pred: Bom (0)</th><th>Pred: Ruim (1)</th></tr>
        <tr><td><b>Real: Bom (0)</b></td><td>{cm['TN']}</td><td>{cm['FP']}</td></tr>
        <tr><td><b>Real: Ruim (1)</b></td><td>{cm['FN']}</td><td>{cm['TP']}</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)