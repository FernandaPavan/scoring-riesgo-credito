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
# CSS CUSTOMIZADO (SIDEBAR E GRÁFICO OTIMIZADOS)
# ============================================
st.markdown("""
<style>
/* 1. Redução de Margens Gerais */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0rem !important;
}

/* 2. SIDEBAR ULTRA-COMPACTO */
[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 12px !important;
    font-weight: 500 !important;
    margin-bottom: -15px !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.1rem !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"], 
[data-testid="stSidebar"] div[data-testid="stSlider"] {
    transform: scale(0.95);
    transform-origin: left top;
}

/* 3. TÍTULOS E TEXTOS */
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
button[data-baseweb="tab"] p {
    font-size: 14px !important;
}

/* 4. BOTÃO CALCULAR */
div.stButton > button {
    background-color: #2563eb;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    height: 35px;
    width: 100%;
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
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:16px;font-weight:600;'>Datos del Cliente</div>", unsafe_allow_html=True)
        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero = {"Masculino":"male","Femenino":"female"}[st.selectbox("Género", ["Masculino","Femenino"])]
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])]
        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])]
        cuenta_ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta de Ahorro", ["Bajo","Medio","Alto"])]
        cuenta_corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta Corriente", ["Bajo","Medio","Alto"])]
        finalidad = {"Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV","Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"}[st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])]

        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        # PREDICÇÃO
        entrada = pd.DataFrame({"Genero":[genero],"Trabalho":[trabalho],"Habitacao":[habitacion],"Conta_poupanca":[cuenta_ahorro],"Conta_corrente":[cuenta_corriente],"Finalidade":[finalidad],"Idade":[edad],"Duracao":[duracion],"Valor_credito":[valor]})
        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(columns=modelo.feature_names_in_, fill_value=0)
        prob = min(max(modelo.predict_proba(entrada_woe)[0][1], 0.0001), 0.9999)

        # CÁLCULO SCORE E POLICY
        factor = score_params["pdo"]/np.log(2)
        offset = score_params["base_score"] + factor*np.log(score_params["base_odds"])
        score_base = int(offset + factor*np.log((1-prob)/prob))
        
        penalidade_score, penalidade_limite, flags = 0, 1.0, []
        if trabalho == 0: penalidade_score -= 80; penalidade_limite *= 0.5; flags.append("Sin empleo")
        if habitacion == "rent": penalidade_score -= 30; penalidade_limite *= 0.85; flags.append("Vivienda alquilada")
        if cuenta_ahorro == "little": penalidade_score -= 20; penalidade_limite *= 0.9; flags.append("Bajo ahorro")
        if cuenta_corriente == "little": penalidade_score -= 20; penalidade_limite *= 0.9; flags.append("Baja liquidez")
        
        score = max(score_base + penalidade_score, 300)

        # SEGMENTAÇÃO
        if score >= 700: segmento, limite_base = "SUPER PRIME", 18000
        elif score >= 650: segmento, limite_base = "PRIME", 10000
        elif score >= 600: segmento, limite_base = "STANDARD", 5000
        elif score >= 520: segmento, limite_base = "NEAR PRIME", 2500
        elif score >= 460: segmento, limite_base = "REVIEW", 1000
        else: segmento, limite_base = "SUBPRIME", 0

        limite = int(limite_base * penalidade_limite)
        if duracion > 48: limite = int(limite * 0.85)
        
        # DECISÃO FINAL
        if trabalho == 0 and cuenta_corriente == "little":
            status, icon, cor, motivo = "RECHAZADO", "✖", "#dc2626", "Riesgo crítico: sin empleo y baja liquidez."
        else:
            if score < 460: status, icon, cor, motivo = "RECHAZADO", "✖", "#dc2626", "Score bajo política mínima."
            elif score < 520: status, icon, cor, motivo = "EN ANÁLISIS", "⚠", "#facc15", "Zona intermedia de riesgo."
            else:
                if valor <= limite: status, icon, cor, motivo = "APROBADO", "✔", "#16a34a", "Dentro del límite aprobado."
                elif valor <= limite * 1.2: status, icon, cor, motivo = "EN ANÁLISIS", "⚠", "#facc15", "Monto superior al límite sugerido."
                else: status, icon, cor, motivo = "RECHAZADO", "✖", "#dc2626", "Excede límite permitido."
        
        if flags: motivo += " | Riesgos: " + ", ".join(flags)

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{cor};'>{score}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;margin-bottom:0;'>{segmento}</p>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("Probabilidad", f"{prob:.1%}")
            c2.metric("Límite", f"${limite:,.0f}")
            
            st.markdown(f"<div style='text-align:center;font-size:28px;color:{cor};font-weight:900;'>{icon} {status}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:12px;color:#374151;'>{motivo}</p>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div><br>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, 
                gauge={"axis":{"range":[0,100]},"steps":[
                    {"range":[0,40],"color":"#16a34a"},
                    {"range":[40,70],"color":"#facc15"},
                    {"range":[70,100],"color":"#dc2626"}]}))
            
            fig.update_layout(
                height=220, 
                margin=dict(l=30, r=30, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(size=10)
            )
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: DESEMPENHO
# ============================================
with tab2:
    st.markdown("<h2 style='text-align:center;color:#2563eb;font-size:20px;'>Métricas del Modelo</h2>", unsafe_allow_html=True)
    m = metricas_modelo
    metricas_df = pd.DataFrame({"Métrica":["Accuracy","Precisión","Recall","AUC","GINI","KS"],"Valor":[round(m["accuracy"],4), round(m["precision"],4), round(m["recall"],4), round(m["auc"],4), round(m["gini"],4), round(m["ks"],4)]})
    
    st.markdown(f"""
    <div style='display:flex;justify-content:center;margin-top:5px;'>
    <table style='width:450px;font-size:13px;text-align:center;border-collapse:collapse;'>
        <tr style='background-color:#2563eb;color:white;'><th>Métrica</th><th>Valor</th></tr>
        {''.join([f"<tr><td style='padding:5px;border-bottom:1px solid #ddd;'>{m}</td><td style='padding:5px;border-bottom:1px solid #ddd;'>{v}</td></tr>" for m,v in zip(metricas_df["Métrica"],metricas_df["Valor"])])}
    </table>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 3: ESTABILIDADE
# ============================================
with tab3:
    st.markdown("<h2 style='text-align:center;color:#2563eb;font-size:20px;'>Estabilidad (PSI)</h2>", unsafe_allow_html=True)
    psi_valor = metricas_modelo.get("psi", 0.06)
    psi_cor = "#16a34a" if psi_valor < 0.1 else "#facc15" if psi_valor < 0.25 else "#dc2626"
    psi_status = "Estable" if psi_valor < 0.1 else "Alerta" if psi_valor < 0.25 else "Inestable"

    st.markdown(f"""
    <div style='display:flex; justify-content:center; margin-top:10px;'>
        <div style='text-align:center; border:2px solid {psi_cor}; padding:15px; border-radius:15px; width:280px; background-color:#f9fafb;'>
            <p style='margin:0; font-size:16px; color:#4b5563;'>PSI Acumulado</p>
            <p style='margin:5px 0; font-size:42px; font-weight:800; color:{psi_cor};'>{psi_valor}</p>
            <div style='background-color:{psi_cor}; color:white; padding:4px 12px; border-radius:20px; display:inline-block; font-weight:700; font-size:14px;'>{psi_status}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    