import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import streamlit as st
import plotly.graph_objects as go

from src.loader import load_assets
from src.policy import get_score, apply_business_policy
from src.features import traduzir_inputs, montar_entrada, preparar_dados
from app.styles import apply_custom_styles

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App")

# ============================================
# LOAD (cache)
# ============================================
@st.cache_resource
def load_all():
    return load_assets()

modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_all()

# ============================================
# STYLES
# ============================================
apply_custom_styles()

# ============================================
# HEADER
# ============================================
st.markdown(
    "<h1 style='text-align:center;color:#2563eb;'>Evaluación de Riesgo y Score de Crédito</h1>",
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "Simulación de Crédito",
    "Desempeño del Modelo",
    "Estabilidad (PSI)"
])

# ============================================
# TAB 1 - SIMULACIÓN
# ============================================
with tab1:

    with st.sidebar:
        st.markdown("### Datos del Cliente")

        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero_sel = st.selectbox("Género", ["Masculino", "Femenino"])
        trabajo_sel = st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])
        vivienda_sel = st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])
        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo", "Medio", "Alto"])
        corriente_sel = st.selectbox("Cuenta Corriente", ["Bajo", "Medio", "Alto"])
        finalidad_sel = st.selectbox(
            "Finalidad",
            ["Auto", "Muebles", "Electrónicos", "Negocios", "Educación", "Reparaciones", "Otros"]
        )

        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:

        # ============================================
        # TRADUÇÃO INPUTS
        # ============================================
        genero, trabajo, vivienda, ahorro, corriente, finalidad = traduzir_inputs(
            genero_sel,
            trabajo_sel,
            vivienda_sel,
            ahorro_sel,
            corriente_sel,
            finalidad_sel
        )

        # ============================================
        # MONTA DATAFRAME
        # ============================================
        entrada = montar_entrada(
            genero,
            trabajo,
            vivienda,
            ahorro,
            corriente,
            finalidad,
            edad,
            duracion,
            monto
        )

        # ============================================
        # PIPE (features + WOE)
        # ============================================
        entrada_woe = preparar_dados(entrada, bins_woe, modelo)

        # ============================================
        # PROBABILIDADE
        # ============================================
        prob = modelo.predict_proba(entrada_woe)[0][1]

        # ============================================
        # SCORE
        # ============================================
        score = get_score(prob, score_params)

        # ============================================
        # POLICY
        # ============================================
        decision = apply_business_policy(
            score,
            prob,
            monto,
            cutoffs
        )

        # ============================================
        # RESULTADOS
        # ============================================
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div>", unsafe_allow_html=True)

            st.markdown(
                f"<div class='score' style='color:{decision['cor']};'>{decision['score']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;font-weight:700;color:#2563eb;'>{decision['segmento']}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;'>Probabilidad</p>"
                f"<p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;'>Límite Sugerido</p>"
                f"<p style='text-align:center;font-size:22px;font-weight:700;'>${decision['limite']:,.0f}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div style='text-align:center;font-size:26px;color:{decision['cor']};'>"
                f"{decision['icon']} {decision['status']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;font-size:12px;color:#64748b;'>"
                f"{decision['motivo']}</p>",
                unsafe_allow_html=True
            )

        # ============================================
        # GAUGE
        # ============================================
        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div>", unsafe_allow_html=True)

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'suffix': "%"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "steps": [
                        {"range": [0, 40], "color": "#16a34a"},
                        {"range": [40, 70], "color": "#facc15"},
                        {"range": [70, 100], "color": "#dc2626"},
                    ],
                }
            ))

            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2 - MÉTRICAS
# ============================================
with tab2:

    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})

    st.markdown("### Métricas del Modelo")

    st.write({
        "Accuracy": m["accuracy"],
        "Precision": m["precision"],
        "Recall": m["recall"],
        "AUC": m["auc"],
        "Gini": m["gini"],
        "KS": m["ks"]
    })

    st.markdown("### Matriz de Confusión")

    st.write(cm)

# ============================================
# TAB 3 - PSI
# ============================================
with tab3:

    psi = metricas_modelo.get("psi", 0)

    status = "ESTABLE" if psi < 0.1 else "ALERTA" if psi < 0.25 else "INestable"

    st.markdown("### Estabilidad del Modelo")

    st.metric("PSI", f"{psi:.4f}", status)