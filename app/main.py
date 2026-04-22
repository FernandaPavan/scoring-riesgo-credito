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
        # WOE TRANSFORM
        # ============================================
        try:
            entrada_woe = sc.woebin_ply(entrada, bins_woe)
        except Exception:
            st.error("Erro na transformação WOE. Verifique os bins.")
            st.stop()

        if hasattr(modelo, "feature_names_in_"):
            entrada_woe = entrada_woe.reindex(columns=modelo.feature_names_in_, fill_value=0)

        # ============================================
        # PREDIÇÃO
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
        # DEBUG (ESSENCIAL)
        # ============================================
        with st.expander("🔎 DEBUG MODELO"):
            st.write("Probabilidade:", prob)
            st.write("Score Base:", score_base)
            st.write("Score Final:", res["score"])
            st.write("Status:", res["status"])
            st.write("Limite:", res["limite"])

        # ============================================
        # RESULTADO
        # ============================================
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)

            st.markdown(f"<div class='score' style='color:{res['cor']};'>{res['score']}</div>", unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{res['segmento']}</p>", unsafe_allow_html=True)

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

            fig.update_layout(height=260, margin=dict(l=30, r=30, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)