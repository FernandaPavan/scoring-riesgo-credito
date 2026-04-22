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
# CSS CUSTOMIZADO (MANTENDO SEU LAYOUT)
# ============================================
st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }

/* SIDEBAR ULTRA COMPACTA */
[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 10px !important;
    font-weight: 600 !important;
    margin-bottom: -15px !important; 
    padding-bottom: 0px !important;
    color: #4b5563;
}

[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
[data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMin"],
[data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMax"],
[data-testid="stSidebar"] .stSlider div[role="slider"] {
    font-size: 12px !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    margin-bottom: -12px !important;
}

[data-testid="stSidebar"] [data-testid="stSlider"] {
    padding-top: 0px !important;
    margin-top: -10px !important;
}

div.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    font-weight: 600;
    border-radius: 6px;
    height: 30px;
    width: 90% !important;
    margin-left: 5%;
    margin-top: 15px;
    font-size: 11px;
}

/* RESULTADOS */
.container-performance {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    margin-top: -45px !important; 
}

.titulo-secao { text-align: center; color: #2563eb; font-size: 18px; font-weight: 700; }
.score { text-align: center; font-size: 40px; font-weight: 700; }

/* TABELAS */
table { margin-left: auto; margin-right: auto; font-size: 13px; text-align: center; border-collapse: collapse; width: 450px; }
th { background-color: #2563eb; color: white; padding: 8px; }
td { padding: 8px; border-bottom: 1px solid #eee; }
.val-pos { color: #16a34a; font-weight: 800; }
.val-neg { color: #dc2626; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

# ============================================
# TAB 1: SIMULACIÓN (COM REGRA DE NEGÓCIO)
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;margin-bottom:5px;'>Datos del Cliente</div>", unsafe_allow_html=True)
        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)
        
        # Mapeamento para o modelo
        genero_sel = st.selectbox("Género", ["Masculino","Femenino"])
        genero = "male" if genero_sel == "Masculino" else "female"
        
        trabalho_sel = st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[trabalho_sel]
        
        habitacion_sel = st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])
        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[habitacion_sel]
        
        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo","Medio","Alto"])
        cuenta_ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[ahorro_sel]
        
        corriente_sel = st.selectbox("Cuenta Corriente", ["Bajo","Medio","Alto"])
        cuenta_corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[corriente_sel]
        
        finalidad_sel = st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])
        finalidad = {"Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV","Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"}[finalidad_sel]
        
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])
    
    if btn:
        # 1. PREDICÇÃO WOE
        entrada = pd.DataFrame({"Genero":[genero],"Trabalho":[trabalho],"Habitacao":[habitacion],"Conta_poupanca":[cuenta_ahorro],"Conta_corrente":[cuenta_corriente],"Finalidade":[finalidad],"Idade":[edad],"Duracao":[duracion],"Valor_credito":[valor]})
        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(columns=modelo.feature_names_in_, fill_value=0)
        prob = min(max(modelo.predict_proba(entrada_woe)[0][1], 0.0001), 0.9999)

        # 2. CÁLCULO SCORE E POLICY LAYER
        factor = score_params["pdo"]/np.log(2)
        offset = score_params["base_score"] + factor*np.log(score_params["base_odds"])
        score_base = int(offset + factor*np.log((1-prob)/prob))
        
        penalidade_score = 0
        penalidade_limite = 1.0
        flags = []

        if trabalho == 0: penalidade_score -= 80; penalidade_limite *= 0.5; flags.append("Sin empleo")
        if habitacion == "rent": penalidade_score -= 30; penalidade_limite *= 0.85; flags.append("Vivienda alquilada")
        if cuenta_ahorro == "little": penalidade_score -= 20; penalidade_limite *= 0.9; flags.append("Bajo ahorro")
        if cuenta_corriente == "little": penalidade_score -= 20; penalidade_limite *= 0.9; flags.append("Baja liquidez")
        
        score = max(score_base + penalidade_score, 300)

        # 3. SEGMENTAÇÃO
        if score >= 700: segmento="SUPER PRIME"; limite_base=18000
        elif score >= 650: segmento="PRIME"; limite_base=10000
        elif score >= 600: segmento="STANDARD"; limite_base=5000
        elif score >= 520: segmento="NEAR PRIME"; limite_base=2500
        elif score >= 460: segmento="REVIEW"; limite_base=1000
        else: segmento="SUBPRIME"; limite_base=0

        if "Sin emprego" in flags and segmento in ["SUPER PRIME","PRIME"]: segmento = "NEAR PRIME"
        limite = int(limite_base * penalidade_limite)
        if duracion > 48: limite = int(limite * 0.85)
        
        # 4. DECISÃO FINAL
        if trabalho == 0 and cuenta_corriente == "little":
            status="RECHAZADO"; icon="✖"; cor="#dc2626"; motivo="Riesgo crítico: sin empleo y baja liquidez."
        else:
            if score < 460: status="RECHAZADO"; icon="✖"; cor="#dc2626"; motivo="Score bajo política mínima."
            elif score < 520: status="EN ANÁLISIS"; icon="⚠"; cor="#facc15"; motivo="Zona intermedia de riesgo."
            else:
                if valor <= limite: status="APROBADO"; icon="✔"; cor="#16a34a"; motivo="Dentro del límite aprobado."
                elif valor <= limite * 1.2: status="EN ANÁLISIS"; icon="⚠"; cor="#facc15"; motivo="Monto superior al limite sugerido."
                else: status="RECHAZADO"; icon="✖"; cor="#dc2626"; motivo="Excede límite permitido."

        if flags: motivo += " | Riesgos: " + ", ".join(flags)
        
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{cor};'>{score}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{segmento}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Probabilidad</p><p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Límite Sugerido</p><p style='text-align:center;font-size:22px;font-weight:700;'>${limite:,.0f}</p>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:28px;color:{cor};font-weight:900;'>{icon} {status}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:12px;color:#64748b;padding:0 20px;'>{motivo}</p>", unsafe_allow_html=True)

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
# TAB 2 e 3 (Mantidos conforme layout novo)
# ============================================
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})
    st.markdown("<div class='container-performance'><p class='titulo-secao'>Métricas Generales</p>", unsafe_allow_html=True)
    st.markdown(f"<table><tr><th>Métrica</th><th>Valor</th></tr><tr><td>Accuracy</td><td>{m['accuracy']:.4f}</td></tr><tr><td>Precision</td><td>{m['precision']:.4f}</td></tr><tr><td>Recall</td><td>{m['recall']:.4f}</td></tr><tr><td>AUC</td><td>{m['auc']:.4f}</td></tr><tr><td>Gini</td><td>{m['gini']:.4f}</td></tr><tr><td>KS</td><td>{m['ks']:.4f}</td></tr></table>", unsafe_allow_html=True)
    st.markdown("<p class='titulo-secao' style='margin-top:20px;'>Matriz de Confusión</p>", unsafe_allow_html=True)
    st.markdown(f"<table><tr><th>Real\Pred</th><th>Bom (0)</th><th>Ruim (1)</th></tr><tr><td>Bom (0)</td><td class='val-pos'>{cm['TN']}</td><td class='val-neg'>{cm['FP']}</td></tr><tr><td>Ruim (1)</td><td class='val-neg'>{cm['FN']}</td><td class='val-pos'>{cm['TP']}</td></tr></table></div>", unsafe_allow_html=True)

with tab3:
    psi_valor = metricas_modelo.get("psi", 0.00)
    psi_cor = "#16a34a" if psi_valor < 0.1 else "#facc15" if psi_valor < 0.25 else "#dc2626"
    psi_status = "ESTÁVEL" if psi_valor < 0.1 else "ALERTA" if psi_valor < 0.25 else "INSTÁVEL"
    st.markdown(f"<div class='container-performance'><br><br><p class='titulo-secao'>Estabilidad del Modelo (PSI)</p><br><div style='text-align:center; border:1px solid #e2e8f0; padding:20px; border-radius:12px; width:280px;'><p style='font-size:11px; color:#64748b;'>PSI ACUMULADO</p><h1 style='font-size:42px; color:{psi_cor};'>{psi_valor:.4f}</h1><p style='color:{psi_cor}; font-weight:800;'>{psi_status}</p></div></div>", unsafe_allow_html=True)