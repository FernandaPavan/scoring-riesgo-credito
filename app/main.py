import sys
import os
import streamlit as st
import plotly.graph_objects as go

# ============================================
# PATH (garante import da pasta src)
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ============================================
# IMPORTS MODULARES
# ============================================
from src.loader import load_assets
from src.features import traduzir_inputs, montar_entrada, preparar_dados
from src.policy import get_score, apply_business_policy
from app.styles import apply_custom_styles

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App")

# ============================================
# LOAD
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
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;'>Datos del Cliente</div>", unsafe_allow_html=True)

        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero_sel = st.selectbox("Género", ["Masculino", "Femenino"])
        trabalho_sel = st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])
        vivienda_sel = st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])
        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo", "Medio", "Alto"])
        corriente_sel = st.selectbox("Cuenta Corriente", ["Bajo", "Medio", "Alto"])
        finalidad_sel = st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])

        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1,1])

    if btn:

        # ============================================
        # TRADUÇÃO
        # ============================================
        genero, trabajo, vivienda, ahorro, corriente, finalidad = traduzir_inputs(
            genero_sel, trabalho_sel, vivienda_sel, ahorro_sel, corriente_sel, finalidad_sel
        )

        # ============================================
        # DATAFRAME
        # ============================================
        entrada = montar_entrada(
            genero, trabajo, vivienda, ahorro, corriente, finalidad,
            edad, duracion, monto
        )

        # ============================================
        # PIPELINE
        # ============================================
        entrada_woe = preparar_dados(entrada, bins_woe, modelo)

        # ============================================
        # PROBABILIDADE + SCORE
        # ============================================
        prob = modelo.predict_proba(entrada_woe)[0][1]
        score_base = get_score(prob, score_params)

        # ============================================
        # 🔥 PENALIZAÇÃO (APENAS DUAS REGRAS)
        # ============================================
        penalidade = 0

        if trabajo == 0:          # Desempleado
            penalidade -= 80

        if vivienda == "rent":    # Alquilada
            penalidade -= 30

        score_final = max(score_base + penalidade, 300)

        # ============================================
        # POLICY
        # ============================================
        decision = apply_business_policy(
            score_final,
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
# TAB 2 (MÉTRICAS)
# ============================================
with tab2:

    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})

    st.markdown(f"""
    <div class='container-performance'>
        <p class='titulo-secao'>Métricas del Modelo</p>
        <table>
            <tr><th>Métrica</th><th>Valor</th></tr>
            <tr><td>Accuracy</td><td>{m['accuracy']:.4f}</td></tr>
            <tr><td>Precision</td><td>{m['precision']:.4f}</td></tr>
            <tr><td>Recall</td><td>{m['recall']:.4f}</td></tr>
            <tr><td>AUC</td><td>{m['auc']:.4f}</td></tr>
            <tr><td>Gini</td><td>{m['gini']:.4f}</td></tr>
            <tr><td>KS</td><td>{m['ks']:.4f}</td></tr>
        </table>

        <p class='titulo-secao' style='margin-top:20px;'>Matriz de Confusión</p>

        <table>
            <tr><th>Real \\ Pred</th><th>Bueno (0)</th><th>Malo (1)</th></tr>
            <tr><td>Bueno (0)</td><td class='val-pos'>{cm['TN']}</td><td class='val-neg'>{cm['FP']}</td></tr>
            <tr><td>Malo (1)</td><td class='val-neg'>{cm['FN']}</td><td class='val-pos'>{cm['TP']}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 3 (PSI)
# ============================================
with tab3:

    psi = metricas_modelo.get("psi", 0)

    status = "ESTABLE" if psi < 0.1 else "ALERTA" if psi < 0.25 else "INESTABLE"
    cor = "#16a34a" if psi < 0.1 else "#facc15" if psi < 0.25 else "#dc2626"

    st.markdown(f"""
    <div class='container-performance'>
        <p class='titulo-secao'>Estabilidad del Modelo</p>

        <div style='text-align:center;border:1px solid #e5e7eb;padding:20px;border-radius:12px;width:250px;'>
            <p style='font-size:12px;color:#64748b;'>PSI</p>
            <h1 style='color:{cor};'>{psi:.4f}</h1>
            <p style='color:{cor};font-weight:700;'>{status}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)