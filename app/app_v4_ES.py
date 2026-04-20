import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import os
import json
import scorecardpy as sc

# ============================================
# PATH
# ============================================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_PATH, "models")

modelo = joblib.load(os.path.join(MODEL_PATH, "modelo.pkl"))
bins_woe = joblib.load(os.path.join(MODEL_PATH, "woe_bins.pkl"))

# carregar métricas reais
with open(os.path.join(MODEL_PATH, "metricas.json"), "r") as f:
    metricas_modelo = json.load(f)

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide")

# ============================================
# CSS
# ============================================
st.markdown("""
<style>
.seccion {
    text-align:center;
    color:#2563eb;
    font-size:20px;
    font-weight:600;
}

.score {
    text-align:center;
    font-size:60px;
    font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("""
<h1 style='text-align:center;color:#2563eb;font-size:32px;font-weight:700;'>
Evaluación de Riesgo y Score de Crédito
</h1>
<br>
""", unsafe_allow_html=True)

# ============================================
# TABS
# ============================================
tab1, tab2 = st.tabs([
    "Simulación de Crédito",
    "Desempeño del Modelo"
])

# ============================================
# TAB 1 - SIMULACIÓN
# ============================================
with tab1:

    with st.sidebar:

        st.markdown(
            "<div style='text-align:center;color:#2563eb;font-size:20px;font-weight:600;'>Datos del Cliente</div>",
            unsafe_allow_html=True
        )

        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero_map = {
            "Masculino": "male",
            "Femenino": "female"
        }
        genero = genero_map[st.selectbox("Género", list(genero_map.keys()))]

        trabajo_map = {
            "Desempleado": 0,
            "Básico": 1,
            "Calificado": 2,
            "Especialista": 3
        }
        trabajo = trabajo_map[st.selectbox("Ocupación", list(trabajo_map.keys()))]

        habitacion_map = {
            "Propia": "own",
            "Alquilada": "rent",
            "Gratuita": "free"
        }
        habitacion = habitacion_map[st.selectbox("Vivienda", list(habitacion_map.keys()))]

        conta_map = {
            "Bajo": "little",
            "Medio": "moderate",
            "Alto": "rich"
        }

        cuenta_ahorro = conta_map[
            st.selectbox("Cuenta de Ahorro", list(conta_map.keys()))
        ]

        cuenta_corriente = conta_map[
            st.selectbox("Cuenta Corriente", list(conta_map.keys()))
        ]

        finalidade_map = {
            "Auto": "car",
            "Muebles": "furniture/equipment",
            "Electrónicos": "radio/TV",
            "Negocios": "business",
            "Educación": "education",
            "Reparaciones": "repairs",
            "Otros": "vacation/others"
        }

        finalidad = finalidade_map[
            st.selectbox(
                "Finalidad del Crédito",
                list(finalidade_map.keys())
            )
        ]

        btn = st.button("Calcular", use_container_width=True)

    col2, col3 = st.columns([1, 1])

    if btn:

        entrada = pd.DataFrame({
            "Genero": [genero],
            "Trabalho": [trabajo],
            "Habitacao": [habitacion],
            "Conta_poupanca": [cuenta_ahorro],
            "Conta_corrente": [cuenta_corriente],
            "Finalidade": [finalidad],
            "Idade": [edad],
            "Duracao": [duracion],
            "Valor_credito": [valor]
        })

        entrada_woe = sc.woebin_ply(entrada, bins_woe)
        entrada_woe = entrada_woe.reindex(
            columns=modelo.feature_names_in_,
            fill_value=0
        )

        prob = modelo.predict_proba(entrada_woe)[0][1]
        score = int(850 - (prob * 550))

        # política
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

        # decisão
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

        # resultado
        with col2:

            st.markdown(
                "<div class='seccion'>Resultado del Análisis</div>",
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(
                f"<div class='score'>{score}</div>",
                unsafe_allow_html=True
            )

            st.markdown(f"""
            <p style='text-align:center; font-size:18px;'>
                Probabilidad de Riesgo
            </p>
            <p style='text-align:center; font-size:28px; font-weight:bold;'>
                {prob:.2%}
            </p>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <p style='text-align:center; font-size:18px;'>
                Límite Aprobado
            </p>
            <p style='text-align:center; font-size:28px; font-weight:bold;'>
                ${limite:,.0f}
            </p>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="text-align:center; margin-top:20px;">
                <span style="
                    color:{cor};
                    font-size:30px;
                    font-weight:700;
                ">
                    {status}
                </span>
            </div>
            """, unsafe_allow_html=True)

        # gauge
        with col3:

            st.markdown(
                "<div class='seccion'>Indicador de Riesgo</div>",
                unsafe_allow_html=True
            )

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'font': {'size': 28}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#111"},
                    'steps': [
                        {'range': [0, 40], 'color': "#16a34a"},
                        {'range': [40, 70], 'color': "#facc15"},
                        {'range': [70, 100], 'color': "#dc2626"}
                    ],
                }
            ))

            fig.update_layout(
                height=380,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2 - MÉTRICAS REAIS
# ============================================
with tab2:

    st.markdown("""
    <h2 style='text-align:center; color:#2563eb;'>
        Métricas del Modelo
    </h2>
    """, unsafe_allow_html=True)

    # métricas reais do json
    metricas = pd.DataFrame({
        "Métrica": [
            "Accuracy",
            "Precisión",
            "Recall",
            "F1-Score",
            "AUC",
            "GINI",
            "KS"
        ],
        "Valor": [
            round(metricas_modelo["accuracy"], 6),
            round(metricas_modelo["precision"], 6),
            round(metricas_modelo["recall"], 6),
            round(metricas_modelo["f1_score"], 6),
            round(metricas_modelo["auc"], 6),
            round(metricas_modelo["gini"], 6),
            round(metricas_modelo["ks"], 6)
        ]
    })

    cm = metricas_modelo["confusion_matrix"]

    _, col_centro, _ = st.columns([1, 2, 1])

    with col_centro:

        st.table(metricas)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <h3 style='text-align:center; color:#2563eb;'>
            Matriz de Confusión
        </h3>
        """, unsafe_allow_html=True)

        cm_df = pd.DataFrame({
            "Pred 0": [cm["TN"], cm["FN"]],
            "Pred 1": [cm["FP"], cm["TP"]]
        }, index=["Real 0", "Real 1"])

        st.table(cm_df)