import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import os
import json
import scorecardpy as sc

# ============================================
# CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando)
# ============================================
st.set_page_config(page_title="Credit Scoring App", layout="wide")

# ============================================
# PATH E CARREGAMENTO COM CACHE
# ============================================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_PATH, "models")

@st.cache_resource
def load_assets():
    """Carrega modelos e parâmetros apenas uma vez para ganhar performance."""
    modelo = joblib.load(os.path.join(MODEL_PATH, "modelo.pkl"))
    bins_woe = joblib.load(os.path.join(MODEL_PATH, "woe_bins.pkl"))
    
    with open(os.path.join(MODEL_PATH, "metricas.json"), "r") as f:
        metricas = json.load(f)
        
    with open(os.path.join(MODEL_PATH, "score_params.json"), "r") as f:
        params = json.load(f)
        
    return modelo, bins_woe, metricas, params

# Carregando os recursos
try:
    modelo, bins_woe, metricas_modelo, score_params = load_assets()
except Exception as e:
    st.error(f"Erro ao carregar arquivos do modelo: {e}")
    st.stop()

# ============================================
# CSS CUSTOMIZADO (OTIMIZADO PARA CLOUD)
# ============================================
st.markdown("""
<style>
    /* Reduz espaço em branco no topo */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* Estilo das Abas */
    button[data-baseweb="tab"] p {
        font-size: 15px !important;
        font-weight: 600 !important;
    }

    /* Títulos de Seção */
    .titulo-secao {
        text-align: center;
        color: #2563eb;
        font-size: 18px !important;
        font-weight: 700;
        margin-bottom: 5px !important;
    }

    /* Score Principal */
    .score-val { 
        text-align: center; 
        font-size: 48px !important; 
        font-weight: 800; 
        line-height: 1 !important;
        margin: 5px 0 !important;
    }

    /* Botão de Calcular */
    div.stButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        height: 40px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:28px;margin-bottom:0;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

# ============================================
# TAB 1: SIMULACIÓN
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<h3 style='text-align:center; color:#2563eb;'>Datos del Cliente</h3>", unsafe_allow_html=True)
        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero = {"Masculino":"male","Femenino":"female"}[st.selectbox("Género", ["Masculino","Femenino"])]
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])]
        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])]
        cuenta_ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta de Ahorro", ["Bajo","Medio","Alto"])]
        cuenta_corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[st.selectbox("Cuenta Corriente", ["Bajo","Medio","Alto"])]
        finalidad = {"Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV","Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"}[st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])]

        btn = st.button("Calcular Score", use_container_width=True)

    col_res, col_graf = st.columns([0.45, 0.55])

    if btn:
        # PREDICÇÃO WOE
        entrada = pd.DataFrame({
            "Genero":[genero],"Trabalho":[trabalho],"Habitacao":[habitacion],
            "Conta_poupanca":[cuenta_ahorro],"Conta_corrente":[cuenta_corriente],
            "Finalidade":[finalidad],"Idade":[edad],"Duracao":[duracion],"Valor_credito":[valor]
        })
        
        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(columns=modelo.feature_names_in_, fill_value=0)
        prob = min(max(modelo.predict_proba(entrada_woe)[0][1], 0.0001), 0.9999)

        # CÁLCULO SCORE
        factor = score_params["pdo"]/np.log(2)
        offset = score_params["base_score"] + factor*np.log(score_params["base_odds"])
        score_base = int(offset + factor*np.log((1-prob)/prob))
        
        # POLICY LAYER (REGRAS DE NEGÓCIO)
        penalidade_score = 0
        penalidade_limite = 1.0
        flags = []

        if trabalho == 0: penalidade_score -= 80; penalidade_limite *= 0.5; flags.append("Sin empleo")
        if habitacion == "rent": penalidade_score -= 30; penalidade_limite *= 0.85; flags.append("Vivienda alquilada")
        if cuenta_ahorro == "little": penalidade_score -= 20; penalidade_limite *= 0.9; flags.append("Bajo ahorro")
        
        score = max(score_base + penalidade_score, 300)

        # SEGMENTAÇÃO E LIMITES
        if score >= 700: segmento, limite_base = "SUPER PRIME", 18000
        elif score >= 600: segmento, limite_base = "PRIME", 10000
        elif score >= 520: segmento, limite_base = "STANDARD", 5000
        else: segmento, limite_base = "SUBPRIME", 0

        limite = int(limite_base * penalidade_limite)
        
        # STATUS FINAL
        if score < 460 or (trabalho == 0 and cuenta_corriente == "little"):
            status, icon, cor = "RECHAZADO", "✖", "#dc2626"
        elif score < 520 or valor > limite:
            status, icon, cor = "EN ANÁLISIS", "⚠", "#facc15"
        else:
            status, icon, cor = "APROBADO", "✔", "#16a34a"

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='score-val' style='color:{cor};'>{score}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-weight:700; color:#2563eb;'>{segmento}</p>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("Probabilidad", f"{prob:.1%}")
            c2.metric("Límite Sugerido", f"${limite:,.0f}")
            
            st.markdown(f"<div style='text-align:center; font-size:32px; color:{cor}; font-weight:900; margin-top:10px;'>{icon} {status}</div>", unsafe_allow_html=True)
            if flags: st.info(f"Fatores: {', '.join(flags)}")

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number", 
                value=prob*100,
                gauge={
                    'axis': {'range': [0, 100]},
                    'steps': [
                        {'range': [0, 40], 'color': "#16a34a"},
                        {'range': [40, 75], 'color': "#facc15"},
                        {'range': [75, 100], 'color': "#dc2626"}
                    ],
                    'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': prob*100}
                }
            ))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: DESEMPENHO
# ============================================
with tab2:
    st.markdown("<div class='titulo-secao'>Métricas Técnicas</div>", unsafe_allow_html=True)
    m = metricas_modelo
    cols = st.columns(4)
    cols[0].metric("AUC", f"{m['auc']:.3f}")
    cols[1].metric("Gini", f"{m['gini']:.3f}")
    cols[2].metric("KS", f"{m['ks']:.3f}")
    cols[3].metric("Accuracy", f"{m['accuracy']:.2%}")
    
    st.divider()
    
    st.markdown("### Matriz de Confusión")
    cm = m["confusion_matrix"]
    cm_df = pd.DataFrame(
        [[cm['TN'], cm['FP']], [cm['FN'], cm['TP']]],
        index=['Real Bom', 'Real Ruim'],
        columns=['Pred Bom', 'Pred Ruim']
    )
    st.table(cm_df)

# ============================================
# TAB 3: ESTABILIDADE
# ============================================
with tab3:
    psi_valor = metricas_modelo.get("psi", 0.06)
    psi_cor = "#16a34a" if psi_valor < 0.1 else "#facc15" if psi_valor < 0.25 else "#dc2626"
    
    st.markdown(f"""
        <div style='text-align:center; border:2px solid {psi_cor}; padding:20px; border-radius:15px; background-color:#f9fafb;'>
            <h2 style='margin:0; color:#4b5563;'>PSI Acumulado</h2>
            <h1 style='font-size:60px; color:{psi_cor};'>{psi_valor:.3f}</h1>
            <p style='font-weight:700; color:{psi_cor};'>ESTADO: {"ESTÁVEL" if psi_valor < 0.1 else "ALERTA"}</p>
        </div>
    """, unsafe_allow_html=True)