import streamlit as st
import os 
import sys
import pandas as pd
import numpy as np
import scorecardpy as sc
import plotly.graph_objects as go

# ============================================
# PATH
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
# CUT-OFFS (BASEADOS NO KS)
# ============================================
cutoffs = {
    "reject_cutoff": 490,
    "approve_cutoff": 540
}

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
        # WOE
        # ============================================
        try:
            entrada_woe = sc.woebin_ply(entrada, bins_woe)
        except Exception:
            st.error("Erro na transformação WOE")
            st.stop()

        if hasattr(modelo, "feature_names_in_"):
            entrada_woe = entrada_woe.reindex(columns=modelo.feature_names_in_, fill_value=0)

        # ============================================
        # PREDIÇÃO CORRETA
        # ============================================
        probs = modelo.predict_proba(entrada_woe)[0]
        classes = list(modelo.classes_)

        idx_default = classes.index(0)
        idx_good = classes.index(1)

        prob_default = probs[idx_default]
        prob_good = probs[idx_good]

        prob = float(np.clip(prob_default, 0.0001, 0.9999))

        # ============================================
        # SCORE
        # ============================================
        score_base = get_score(prob, score_params)

        # ============================================
        # POLICY (mantendo assinatura antiga)
        # ============================================
        res = apply_business_policy(
            score_base,
            trabalho_idx,
            habitacao_val,
            ahorro_val,
            corriente_val,
            monto
        )

        # ============================================
        # DEBUG
        # ============================================
        with st.expander("🔎 DEBUG MODELO"):

            st.write("Classes:", classes)
            st.write("Probs:", probs)
            st.write("Prob DEFAULT:", prob_default)
            st.write("Prob GOOD:", prob_good)
            st.write("Prob usada:", prob)

            if prob > 0.5 and score_base > 600:
                st.error("⚠️ POSSÍVEL INVERSÃO")
            elif prob < 0.3 and score_base < 500:
                st.error("⚠️ POSSÍVEL INVERSÃO")
            else:
                st.success("✅ Coerente")

            st.write("Score Base:", score_base)
            st.write("Score Final:", res["score"])
            st.write("Reject:", cutoffs["reject_cutoff"])
            st.write("Approve:", cutoffs["approve_cutoff"])
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
                f"<p style='text-align:center;'>Probabilidad</p>"
                f"<p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;'>Límite</p>"
                f"<p style='text-align:center;font-size:22px;font-weight:700;'>${res['limite']:,.0f}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div style='text-align:center;font-size:28px;color:{res['cor']};font-weight:900;'>"
                f"{res['icon']} {res['status']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;font-size:12px;color:#64748b;'>{res['motivo']}</p>",
                unsafe_allow_html=True
            )

        # ============================================
        # GAUGE
        # ============================================
        with col_graf:

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

            st.plotly_chart(fig, use_container_width=True)