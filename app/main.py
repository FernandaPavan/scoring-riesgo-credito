import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import os
import json
import scorecardpy as sc

# IMPORTS NOVOS (SEPARAÇÃO CORRETA)
from loader import load_assets
from policy import get_score, apply_business_policy

# ============================================
# CONFIGURAÇÃO INICIAL
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App")

# ============================================
# LOAD CENTRALIZADO
# ============================================
modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_assets()

# ============================================
# CSS ORIGINAL (MANTIDO)
# ============================================
st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }

[data-testid="stSidebar"] .stWidgetLabel p {
    font-size: 10px !important;
    font-weight: 600 !important;
    margin-bottom: -15px !important; 
    padding-bottom: 0px !important;
    color: #4b5563;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    margin-bottom: -12px !important;
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

.container-performance {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

.titulo-secao { text-align: center; color: #2563eb; font-size: 18px; font-weight: 700; }
.score { text-align: center; font-size: 40px; font-weight: 700; }

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
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown(
    "<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>"
    "Evaluación de Riesgo y Score de Crédito</h1>",
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "Simulación de Crédito",
    "Desempeño del Modelo",
    "Estabilidad (PSI)"
])

# ============================================
# TAB 1
# ============================================
with tab1:

    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;'>Datos del Cliente</div>", unsafe_allow_html=True)

        edad = st.slider("Edad", 18, 75, 30)
        valor_solicitado = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero = "male" if st.selectbox("Género", ["Masculino","Femenino"]) == "Masculino" else "female"

        trabajo = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[
            st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])
        ]

        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[
            st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])
        ]

        ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[
            st.selectbox("Cuenta de Ahorro", ["Bajo","Medio","Alto"])
        ]

        corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[
            st.selectbox("Cuenta Corriente", ["Bajo","Medio","Alto"])
        ]

        finalidad = {
            "Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV",
            "Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"
        }[
            st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])
        ]

        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:

        # =========================
        # INPUT
        # =========================
        entrada = pd.DataFrame({
            "Genero":[genero],
            "Trabalho":[trabajo],
            "Habitacao":[habitacion],
            "Conta_poupanca":[ahorro],
            "Conta_corrente":[corriente],
            "Finalidade":[finalidad],
            "Idade":[edad],
            "Duracao":[duracion],
            "Valor_credito":[valor_solicitado]
        })

        entrada_woe = sc.woebin_ply(entrada, bins_woe)\
            .reindex(columns=modelo.feature_names_in_, fill_value=0)

        prob = modelo.predict_proba(entrada_woe)[0][1]

        # =========================
        # SCORE VIA POLICY MODULE
        # =========================
        score = get_score(prob, score_params)

        policy = apply_business_policy(
            score=score,
            prob_default=prob,
            valor_solicitado=valor_solicitado,
            cutoffs=cutoffs
        )

        # =========================
        # RESULTADO (UI ORIGINAL)
        # =========================
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br><br>", unsafe_allow_html=True)

            st.markdown(f"<div class='score' style='color:{policy['cor']};'>{score}</div>", unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>"
                        f"{policy['segmento']}</p>", unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center;'>Probabilidad</p>"
                        f"<p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>",
                        unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center;'>Límite Sugerido</p>"
                        f"<p style='text-align:center;font-size:22px;font-weight:700;'>${policy['limite']:,.0f}</p>",
                        unsafe_allow_html=True)

            st.markdown(f"<div style='text-align:center;font-size:28px;color:{policy['cor']};font-weight:900;'>"
                        f"{policy['icon']} {policy['status']}</div>", unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center;font-size:12px;color:#64748b;'>"
                        f"{policy['motivo']}</p>", unsafe_allow_html=True)

        # =========================
        # GAUGE (INALTERADO)
        # =========================
        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div><br><br>", unsafe_allow_html=True)

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'suffix': "%"},
                gauge={
                    "axis":{"range":[0,100]},
                    "steps":[
                        {"range":[0,40],"color":"#16a34a"},
                        {"range":[40,70],"color":"#facc15"},
                        {"range":[70,100],"color":"#dc2626"}
                    ]
                }
            ))

            fig.update_layout(height=260)
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2 (MANTIDO)
# ============================================
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})

    st.markdown(f"""
    <div class='container-performance'>
        <br>
        <p class='titulo-secao'>Métricas Generales</p>
        <table>
            <tr><th>Métrica</th><th>Valor</th></tr>
            <tr><td>Accuracy</td><td>{m['accuracy']:.4f}</td></tr>
            <tr><td>Precision</td><td>{m['precision']:.4f}</td></tr>
            <tr><td>Recall</td><td>{m['recall']:.4f}</td></tr>
            <tr><td>AUC</td><td>{m['auc']:.4f}</td></tr>
            <tr><td>Gini</td><td>{m['gini']:.4f}</td></tr>
            <tr><td>KS</td><td>{m['ks']:.4f}</td></tr>
        </table>

        <p class='titulo-secao' style='margin-top:25px;'>Matriz de Confusión</p>
        <table>
            <tr><th>Real \ Pred</th><th>Bom (0)</th><th>Ruim (1)</th></tr>
            <tr><td>Bom (0)</td><td class='val-pos'>{cm['TN']}</td><td class='val-neg'>{cm['FP']}</td></tr>
            <tr><td>Ruim (1)</td><td class='val-neg'>{cm['FN']}</td><td class='val-pos'>{cm['TP']}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 3 (MANTIDO)
# ============================================
with tab3:
    psi_v = metricas_modelo.get("psi", 0.00)
    psi_c = "#16a34a" if psi_v < 0.1 else "#facc15" if psi_v < 0.25 else "#dc2626"
    psi_s = "ESTÁVEL" if psi_v < 0.1 else "ALERTA" if psi_v < 0.25 else "INSTÁVEL"

    st.markdown(f"""
    <div class='container-performance'>
        <br><br>
        <p class='titulo-secao'>Estabilidad del Modelo (PSI)</p><br>

        <div style='text-align:center; border:1px solid #e2e8f0; padding:20px; border-radius:12px; width:280px;'>
            <p style='font-size:11px; color:#64748b;'>PSI ACUMULADO</p>
            <h1 style='font-size:42px; color:{psi_c};'>{psi_v:.4f}</h1>
            <p style='color:{psi_c}; font-weight:800;'>{psi_s}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)