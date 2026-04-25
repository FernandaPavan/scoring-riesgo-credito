import sys
import os
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import scorecardpy as sc

# ============================================
# PATH CORRETO (PADRÃO PRODUÇÃO)
# ============================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ============================================
# CONFIG
# ============================================
st.set_page_config(
    layout="wide",
    page_title="Credit Score App",
    page_icon="💳"
)

# ============================================
# IMPORTS
# ============================================
from src.loader import load_assets
from src.policy import (
    get_score,
    apply_business_policy,
    aplicar_penalidades,
    calculate_final_adjustments
)
from app.styles import apply_custom_styles

apply_custom_styles()

# ============================================
# LOAD
# ============================================
@st.cache_resource
def load_all():
    return load_assets()

modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_all()

# ============================================
# HEADER
# ============================================
st.markdown("""
<h1 style='text-align:center; color:#2563eb; font-size:26px; font-weight:700;'>
Evaluación de Riesgo y Score de Crédito
</h1>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "🚀 Simulación",
    "📊 Modelo",
    "🛡️ PSI"
])

# ============================================
# TAB 1
# ============================================
with tab1:
    with st.sidebar:

        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración", 4, 72, 24)

        genero = "male" if st.selectbox("Género", ["Masculino","Femenino"]) == "Masculino" else "female"

        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[
            st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])
        ]

        habitacion = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[
            st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])
        ]

        ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[
            st.selectbox("Ahorro", ["Bajo","Medio","Alto"])
        ]

        corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[
            st.selectbox("Cuenta", ["Bajo","Medio","Alto"])
        ]

        finalidad = "car"

        btn = st.button("Calcular")

    if btn:

        entrada = pd.DataFrame({
            "Genero":[genero],
            "Trabalho":[trabalho],
            "Habitacao":[habitacion],
            "Conta_poupanca":[ahorro],
            "Conta_corrente":[corriente],
            "Finalidade":[finalidad],
            "Idade":[edad],
            "Duracao":[duracion],
            "Valor_credito":[valor]
        })

        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(
            columns=modelo.feature_names_in_,
            fill_value=0
        )

        prob = modelo.predict_proba(entrada_woe)[0][1]
        prob = min(max(prob, 0.0001), 0.9999)

        score_base = get_score(prob, score_params)

        penalidade, flags = aplicar_penalidades(
            trabalho, habitacion, ahorro, corriente
        )

        score_final = max(score_base + penalidade, 300)

        decision = apply_business_policy(score_final, prob, valor)

        limite = calculate_final_adjustments(
            decision["limite"], duracion, flags
        )

        st.metric("Score", score_final)
        st.metric("Probabilidad", f"{prob:.2%}")
        st.metric("Límite", f"${limite}")

        st.markdown(f"### {decision['icon']} {decision['status']}")
        st.caption(decision["motivo"])

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob*100,
            gauge={"axis":{"range":[0,100]}}
        ))

        st.plotly_chart(fig, use_container_width=True)


# ============================================
# TAB 2
# ============================================
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})

    st.markdown("<div class='titulo-secao'>Desempeño del Modelo</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <table>
        <tr><th>Métrica</th><th>Valor</th></tr>
        <tr><td>Accuracy</td><td>{m.get('accuracy',0):.4f}</td></tr>
        <tr><td>Precision</td><td>{m.get('precision',0):.4f}</td></tr>
        <tr><td>Recall</td><td>{m.get('recall',0):.4f}</td></tr>
        <tr><td>AUC</td><td>{m.get('auc',0):.4f}</td></tr>
        <tr><td>Gini</td><td>{m.get('gini',0):.4f}</td></tr>
        <tr><td>KS</td><td>{m.get('ks',0):.4f}</td></tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div class='titulo-secao'>Matriz de Confusión</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <table class='cm-table'>
        <tr><th>Real / Pred</th><th>Bueno</th><th>Malo</th></tr>
        <tr><td>Bueno</td><td class='val-pos'>{cm['TN']}</td><td class='val-neg'>{cm['FP']}</td></tr>
        <tr><td>Malo</td><td class='val-neg'>{cm['FN']}</td><td class='val-pos'>{cm['TP']}</td></tr>
    </table>
    """, unsafe_allow_html=True)


# ============================================
# TAB 3
# ============================================
with tab3:
    psi_val = metricas_modelo.get("psi", 0)

    status, cor = (
        ("ESTABLE", "#16a34a")
        if psi_val < 0.1
        else ("ALERTA", "#facc15")
        if psi_val < 0.25
        else ("INESTABLE", "#dc2626")
    )

    # CARD PSI
    st.markdown(
        "<div style='display:flex; justify-content:center;'>"
        "<div style='max-width:320px;'>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class='psi-card'>
            <p>Índice PSI</p>
            <div class='score' style='color:{cor};'>{psi_val:.4f}</div>
            <p style='color:{cor};font-weight:700;'>{status}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div></div><br>", unsafe_allow_html=True)

    # EXPANDER CENTRALIZADO
    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        with st.expander("Ver critérios del PSI"):
            st.markdown("""
            **Interpretación del Índice PSI (Índice de Estabilidad de la Población):**

            - **< 0.10** → Población estable  
            - **0.10 – 0.25** → Cambio posible (alerta)  
            - **> 0.25** → Cambio significativo (inestabilidad)  

            **Lectura:**

            - Un PSI bajo indica que la distribución de la población real es similar a la utilizada en el entrenamiento.
            - Un PSI elevado sugiere un cambio en el perfil de los clientes (*data drift*), lo que puede afectar el desempeño del modelo.
            """)

