import streamlit as st
import os 
import sys
import pandas as pd
import numpy as np
import scorecardpy as sc
import plotly.graph_objects as go

# ============================================
# PATH (IMPORTANTE PARA STREAMLIT CLOUD)
# ============================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from styles import apply_custom_styles
from src.loader import load_assets
from src.policy import get_score, apply_business_policy

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App")
apply_custom_styles()

# ============================================
# LOAD
# ============================================
@st.cache_resource
def get_all_assets():
    return load_assets()

modelo, bins_woe, metricas_modelo, score_params = get_all_assets()

# ============================================
# HEADER
# ============================================
st.markdown(
    "<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>",
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
        st.markdown(
            "<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;margin-bottom:5px;'>Datos del Cliente</div>",
            unsafe_allow_html=True
        )
        
        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)
        
        genero = "male" if st.selectbox("Género", ["Masculino","Femenino"]) == "Masculino" else "female"
        
        trabalho_idx = {
            "Desempleado":0,
            "Básico":1,
            "Calificado":2,
            "Especialista":3
        }[st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])]
        
        habitacao_val = {
            "Propia":"own",
            "Alquilada":"rent",
            "Gratuita":"free"
        }[st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])]
        
        ahorro_val = {
            "Bajo":"little",
            "Medio":"moderate",
            "Alto":"rich"
        }[st.selectbox("Cuenta de Ahorro", ["Bajo","Medio","Alto"])]
        
        corriente_val = {
            "Bajo":"little",
            "Medio":"moderate",
            "Alto":"rich"
        }[st.selectbox("Cuenta Corriente", ["Bajo","Medio","Alto"])]
        
        finalidade_val = {
            "Auto":"car",
            "Muebles":"furniture/equipment",
            "Electrónicos":"radio/TV",
            "Negocios":"business",
            "Educación":"education",
            "Reparaciones":"repairs",
            "Otros":"vacation/others"
        }[st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])]
        
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        # ============================================
        # INPUT
        # ============================================
        entrada = pd.DataFrame({
            "Genero": [genero],
            "Trabalho": [trabalho_idx],
            "Habitacao": [habitacao_val],
            "Conta_poupanca": [ahorro_val],
            "Conta_corrente": [corriente_val],
            "Finalidade": [finalidade_val],
            "Idade": [edad],
            "Duracao": [duracion],
            "Valor_credito": [monto]
        })

        # ============================================
        # WOE TRANSFORM (com proteção)
        # ============================================
        try:
            entrada_woe = sc.woebin_ply(entrada, bins_woe)
        except Exception:
            st.error("Erro na transformação WOE. Verifique os bins.")
            st.stop()

        if hasattr(modelo, "feature_names_in_"):
            entrada_woe = entrada_woe.reindex(columns=modelo.feature_names_in_, fill_value=0)

        # ============================================
        # PREDIÇÃO (estável)
        # ============================================
        prob = modelo.predict_proba(entrada_woe)[0][1]
        prob = float(np.clip(prob, 0.0001, 0.9999))

        # ============================================
        # SCORE + POLICY
        # ============================================
        score_base = get_score(prob, score_params)

        res = apply_business_policy(
            score_base,
            trabalho_idx,
            habitacao_val,
            ahorro_val,
            corriente_val,
            monto
        )

        # ============================================
        # RESULTADO
        # ============================================
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)

            st.markdown(
                f"<div class='score' style='color:{res['cor']};'>{res['score']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{res['segmento']}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Probabilidad de Incumplimiento</p>"
                f"<p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Límite Sugerido</p>"
                f"<p style='text-align:center;font-size:22px;font-weight:700;'>${res['limite']:,.0f}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div style='text-align:center;font-size:28px;color:{res['cor']};font-weight:900;'>"
                f"{res['icon']} {res['status']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;font-size:12px;color:#64748b;padding:0 20px;'>{res['motivo']}</p>",
                unsafe_allow_html=True
            )

        # ============================================
        # GAUGE
        # ============================================
        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div><br>", unsafe_allow_html=True)

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'font': {'size': 45}, 'suffix': "%"},
                gauge={
                    "axis":{"range":[0,100]},
                    "steps":[
                        {"range":[0,40],"color":"#16a34a"},
                        {"range":[40,70],"color":"#facc15"},
                        {"range":[70,100],"color":"#dc2626"}
                    ]
                }
            ))

            fig.update_layout(
                height=260,
                margin=dict(l=30, r=30, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2
# ============================================
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})

    st.markdown(f"""
    <div class='container-performance'>
        <br><p class='titulo-secao'>Métricas Generales</p>
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
            <tr><th>Real \\ Pred</th><th>Bom (1)</th><th>Mau (0)</th></tr>
            <tr><td>Bom (1)</td><td class='val-pos'>{cm['TP']}</td><td class='val-neg'>{cm['FN']}</td></tr>
            <tr><td>Mau (0)</td><td class='val-neg'>{cm['FP']}</td><td class='val-pos'>{cm['TN']}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 3
# ============================================
with tab3:
    psi_v = metricas_modelo.get("psi", 0.00)
    psi_c = "#16a34a" if psi_v < 0.1 else "#facc15" if psi_v < 0.25 else "#dc2626"
    psi_s = "ESTÁVEL" if psi_v < 0.1 else "ALERTA" if psi_v < 0.25 else "INSTÁVEL"

    _, col_central, _ = st.columns([1,1,1])

    with col_central:
        st.markdown(f"""
        <div style='text-align: center;'>
            <br><br>
            <p class='titulo-secao'>Estabilidad del Modelo (PSI)</p>
            <br>
            <div style='
                border: 1px solid #e2e8f0; 
                padding: 20px; 
                border-radius: 12px; 
                width: 280px;
                margin: auto;
                background-color: white;'>

                <p style='font-size:11px; color:#64748b;'>PSI ACUMULADO</p>
                <h1 style='font-size:42px; color:{psi_c};'>{psi_v:.4f}</h1>
                <p style='color:{psi_c}; font-weight:800;'>{psi_s}</p>

            </div>
        </div>
        """, unsafe_allow_html=True)