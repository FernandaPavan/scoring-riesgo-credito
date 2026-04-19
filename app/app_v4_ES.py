import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.figure_factory as ff
import os
import sys
import json

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide")

# ============================================
# PATH (FUNCIONA LOCAL + CLOUD)
# ============================================
try:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except:
    BASE_PATH = os.getcwd()

sys.path.append(BASE_PATH)

# ============================================
# IMPORT FEATURE
# ============================================
from src.features import criar_faixas

# ============================================
# CARREGAR MODELO
# ============================================
model_path = os.path.join(BASE_PATH, "models", "modelo.pkl")
model = joblib.load(model_path)

# ============================================
# HEADER
# ============================================
st.markdown("""
<h1 style='text-align:center;color:#2563eb'>
Evaluación de Riesgo y Score de Crédito
</h1>
""", unsafe_allow_html=True)

# ============================================
# ABAS
# ============================================
tab1, tab2 = st.tabs(["📊 Simulador de Crédito", "📈 Métricas del Modelo"])

# ============================================
# ABA 1 - SIMULADOR
# ============================================
with tab1:

    col1, col2, col3 = st.columns(3)

    # =========================
    # COLUNA 1 - INPUTS
    # =========================
    with col1:

        st.subheader("Datos del Cliente")

        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero = st.selectbox("Género", ["male","female"])
        trabajo = st.selectbox("Ocupación", [0,1,2,3])
        habitacion = st.selectbox("Vivienda", ["own","rent","free"])

        cuenta_ahorro = st.selectbox("Cuenta Ahorro", ["little","moderate","rich"])
        cuenta_corriente = st.selectbox("Cuenta Corriente", ["little","moderate","rich"])

        finalidad = st.selectbox("Finalidad", [
            "car","furniture/equipment","radio/TV",
            "business","education","vacation/others"
        ])

        btn = st.button("Calcular")

    if not btn:
        st.info("👈 Completa los datos y haz clic en Calcular")

    # =========================
    # EXECUÇÃO
    # =========================
    if btn:

        entrada = pd.DataFrame({
            "Genero":[genero],
            "Trabalho":[trabajo],
            "Habitacao":[habitacion],
            "Conta_poupanca":[cuenta_ahorro],
            "Conta_corrente":[cuenta_corriente],
            "Finalidade":[finalidad],
            "Idade":[edad],
            "Duracao":[duracion],
            "Valor_credito":[valor]
        })

        prob = model.predict_proba(entrada)[0][1]
        score = int(850 - (prob * 550))

        # =========================
        # POLÍTICA DE CRÉDITO
        # =========================
        if score >= 750:
            limite = 18000
        elif score >= 700:
            limite = 10000
        elif score >= 650:
            limite = 4000
        elif score >= 600:
            limite = 2500
        elif score >= 550:
            limite = 250
        else:
            limite = 0

        if duracion > 48:
            limite *= 0.80
        elif duracion > 36:
            limite *= 0.90

        # =========================
        # DECISÃO
        # =========================
        if score < 550:
            status = "✖ RECHAZADO"
            cor = "#dc2626"

        elif valor <= limite:
            status = "✔ APROBADO"
            cor = "#16a34a"

        elif valor <= limite * 1.20:
            status = "⚠ EN ANÁLISIS"
            cor = "#facc15"

        else:
            status = "✖ RECHAZADO"
            cor = "#dc2626"

        # =========================
        # COLUNA 2 - RESULTADO
        # =========================
        with col2:

            st.subheader("Resultado")

            # SCORE
            st.markdown(f"<h1 style='color:#2563eb;text-align:center'>{score}</h1>", unsafe_allow_html=True)

            st.write(f"**Probabilidad de Riesgo:** {prob:.2%}")
            st.write(f"**Límite Aprobado:** ${limite:,.0f}")

            # STATUS
            st.markdown(
                f"<h2 style='text-align:center;color:{cor};font-weight:800'>{status}</h2>",
                unsafe_allow_html=True
            )

            # =========================
            # EXPLICAÇÃO ESTILO BANCO
            # =========================
            if score >= 750:
                nivel = "ALTO"
                exp_score = "perfil de bajo riesgo"
            elif score >= 650:
                nivel = "MEDIO"
                exp_score = "riesgo moderado"
            else:
                nivel = "BAJO"
                exp_score = "alto riesgo de incumplimiento"

            if valor <= limite:
                exp_valor = "dentro del límite aprobado"
            elif valor <= limite * 1.2:
                exp_valor = "ligeramente por encima del límite"
            else:
                exp_valor = "por encima del límite permitido"

            if duracion <= 36:
                exp_prazo = "plazo adecuado"
            elif duracion <= 48:
                exp_prazo = "plazo moderado"
            else:
                exp_prazo = "plazo alto aumenta el riesgo"

            st.markdown("""
            ### 📌 Motivo de la Decisión
            """)

            st.markdown(f"""
            • **Score {nivel}** → {exp_score}  
            • El crédito solicitado está **{exp_valor}**  
            • El plazo es considerado **{exp_prazo}**
            """)

        # =========================
        # COLUNA 3 - GAUGE
        # =========================
        with col3:

            st.subheader("Indicador de Riesgo")

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                gauge={
                    'axis': {'range':[0,100]},
                    'steps':[
                        {'range':[0,40],'color':"#16a34a"},
                        {'range':[40,70],'color':"#facc15"},
                        {'range':[70,100],'color':"#dc2626"}
                    ]
                }
            ))

            st.plotly_chart(fig, use_container_width=True)

# ============================================
# ABA 2 - MÉTRICAS
# ============================================
with tab2:

    st.subheader("Desempeño del Modelo")

    metrics_path = os.path.join(BASE_PATH, "models", "metricas.json")

    try:
        with open(metrics_path) as f:
            m = json.load(f)
    except:
        st.warning("⚠ Métricas no encontradas. Rode el pipeline primero.")
        st.stop()

    colA, colB = st.columns(2)

    with colA:
        st.metric("AUC", f"{m.get('roc_auc',0):.3f}")
        st.metric("Gini", f"{m.get('gini',0):.3f}")

    with colB:
        st.metric("KS", f"{m.get('ks',0):.3f}")
        st.metric("Accuracy", f"{m.get('accuracy',0):.3f}")

    # MATRIZ DE CONFUSIÓN
    if "confusion_matrix" in m:

        fig = ff.create_annotated_heatmap(
            z=m["confusion_matrix"],
            x=["Previsto Bueno","Previsto Riesgo"],
            y=["Real Bueno","Real Riesgo"]
        )

        st.plotly_chart(fig, use_container_width=True)

    st.warning("Modelo entrenado con datos didácticos.")