import streamlit as st 
import pandas as pd
import joblib
import plotly.graph_objects as go
import os
import sys
import time

# ============================================
# CORRECCIÓN DEL PATH
# ============================================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

from src.features import criar_faixas

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide")

# ============================================
# CSS
# ============================================
st.markdown("""
<style>

.stApp {
    background-color: #eef2f7;
}

.block-container {
    padding-top: 1rem;
}

.seccion {
    text-align:center;
    color:#2563eb;
    font-size:22px;
    font-weight:600;
    margin-bottom:10px;
}

.score {
    text-align:center;
    font-size:72px;
    font-weight:700;
}

div.stButton > button {
    background-color:#2563eb;
    color:white;
    border-radius:10px;
    height:45px;
    width:100%;
    font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# ============================================
# MODELO
# ============================================
model_path = os.path.join(BASE_PATH, "models", "modelo.pkl")
model = joblib.load(model_path)

# ============================================
# HEADER
# ============================================
st.markdown("""
<br>

<h1 style='text-align:center; color:#2563eb; font-size:42px; font-weight:700;'>
Evaluación de Riesgo y Score de Crédito
</h1>

<br><br>
""", unsafe_allow_html=True)

# ============================================
# LAYOUT
# ============================================
col1, col2, col3 = st.columns(3)

# ============================================
# COLUMNA 1 — INPUTS
# ============================================
with col1:

    st.markdown("<div class='seccion'>Datos del Cliente</div>", unsafe_allow_html=True)

    edad = st.slider("Edad", 18, 75, 30)
    valor = st.number_input("Monto del Crédito", 250, 20000, 5000)
    duracion = st.slider("Duración (meses)", 4, 72, 24)

    genero_map = {"Masculino": "male", "Femenino": "female"}
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

    cuenta_opciones = {
        "Bajo": "little",
        "Medio": "moderate",
        "Alto": "rich"
    }

    cuenta_ahorro = cuenta_opciones[
        st.selectbox("Saldo en Cuenta de Ahorro", list(cuenta_opciones.keys()))
    ]

    cuenta_corriente = cuenta_opciones[
        st.selectbox("Saldo en Cuenta Corriente", list(cuenta_opciones.keys()))
    ]

    finalidad_map = {
        "Auto": "car",
        "Muebles/Equipamiento": "furniture/equipment",
        "Electrónicos": "radio/TV",
        "Negocios": "business",
        "Educación": "education",
        "Reparaciones": "repairs",
        "Otros": "vacation/others"
    }

    finalidad = finalidade_map = None  # evita erro caso não clique ainda
    finalidad = finalidad_map[
        st.selectbox("Finalidad del Crédito", list(finalidad_map.keys()))
    ]

# ============================================
# BOTÓN
# ============================================
if st.button("Calcular"):

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

    # ============================================
    # COLUMNA 2 — RESULTADO
    # ============================================
    with col2:

        st.markdown("<div class='seccion'>Resultado del Análisis</div><br>", unsafe_allow_html=True)

        score_placeholder = st.empty()

        for i in range(300, score, 15):
            score_placeholder.markdown(
                f"<div class='score'>{i}</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.01)

        score_placeholder.markdown(
            f"<div class='score'>{score}</div>",
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <p style='text-align:center; font-size:20px;'>Probabilidad de Riesgo</p>
        <p style='text-align:center; font-size:36px; font-weight:bold;'>{prob:.2%}</p>
        <br><br>
        """, unsafe_allow_html=True)

        # STATUS
        if score >= 700:
            status = "✔ APROBADO"
            cor = "#16a34a"
        elif score >= 600:
            status = "⚠ EN ANÁLISIS"
            cor = "#facc15"
        else:
            status = "✖ RECHAZADO"
            cor = "#dc2626"

        st.markdown(f"""
        <div style='text-align:center; margin-top:20px;'>
            <span style='
                color:{cor};
                font-size:36px;
                font-weight:700;
                letter-spacing:1px;
            '>
                {status}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ============================================
    # COLUMNA 3 — INDICADOR
    # ============================================
    with col3:

        st.markdown("<div class='seccion'>Indicador de Riesgo</div>", unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            number={'font': {'size': 30}},
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
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True)