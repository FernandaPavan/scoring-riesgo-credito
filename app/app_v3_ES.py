import streamlit as st 
import pandas as pd
import joblib
import plotly.graph_objects as go
import os
import sys
import time

# ============================================
# PATH
# ============================================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

from src.features import criar_faixas

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide")

# ============================================
# CSS (VERSÃO CORRETA COM 14px)
# ============================================
st.markdown("""
<style>

/* 🔥 fonte menor só nos inputs da sidebar */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSlider,
section[data-testid="stSidebar"] .stSelectbox,
section[data-testid="stSidebar"] .stNumberInput {
    font-size: 14px !important;
}

/* 🔥 título sidebar maior */
.sidebar-title {
    text-align:center;
    color:#2563eb;
    font-size:20px;
    font-weight:600;
    margin-top:-5px;
    margin-bottom:10px;
}

/* 🔥 espaçamento compacto só na sidebar */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
    gap: 0.15rem !important;
}

/* 🔥 ajuste fino dos inputs */
section[data-testid="stSidebar"] .stSlider {
    margin-top: -6px;
    margin-bottom: -12px;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] {
    margin-top: -6px;
    margin-bottom: -10px;
}

/* 🔥 botão */
div.stButton > button {
    height:38px;
    margin-top: 5px;
    background-color:#2563eb;
    color:white;
    font-weight:600;
    border-radius:8px;
    border:none;
}

/* 🔥 títulos principais */
.seccion {
    text-align:center;
    color:#2563eb;
    font-size:20px;
    font-weight:600;
}

/* 🔥 score */
.score {
    text-align:center;
    font-size:60px;
    font-weight:700;
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
<h1 style='
    text-align:center; 
    color:#2563eb; 
    font-size:32px; 
    font-weight:700;
    margin-top:-10px;
'>
Evaluación de Riesgo y Score de Crédito
</h1>

<br><br>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:

    st.markdown("<div class='sidebar-title'>Datos del Cliente</div>", unsafe_allow_html=True)

    edad = st.slider("Edad", 18, 75, 30)
    valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
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

    finalidade_map = {
        "Auto": "car",
        "Muebles/Equipamiento": "furniture/equipment",
        "Electrónicos": "radio/TV",
        "Negocios": "business",
        "Educación": "education",
        "Reparaciones": "repairs",
        "Otros": "vacation/others"
    }

    finalidad = finalidade_map[
        st.selectbox("Finalidad del Crédito", list(finalidade_map.keys()))
    ]

    st.markdown("<br>", unsafe_allow_html=True)

    btn = st.button("Calcular", use_container_width=True)

# ============================================
# LAYOUT
# ============================================
col2, col3 = st.columns([1, 1])

# ============================================
# EXECUÇÃO
# ============================================
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

    with col2:

        st.markdown("<div class='seccion'>Resultado del Análisis</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='score'>{score}</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <p style='text-align:center; font-size:18px;'>Probabilidad de Riesgo</p>
        <p style='text-align:center; font-size:28px; font-weight:bold;'>{prob:.2%}</p>
        """, unsafe_allow_html=True)

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
        <div style="text-align:center; margin-top:20px;">
            <span style="color:{cor}; font-size:28px; font-weight:700;">
                {status}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown("<div class='seccion'>Indicador de Riesgo</div>", unsafe_allow_html=True)

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