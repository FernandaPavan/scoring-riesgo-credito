import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import os
import sys

# ============================================
# PATH (STREAMLIT CLOUD)
# ============================================
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_PATH)

# (remova se não estiver usando)
# from src.features import criar_faixas

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide")

# ============================================
# CSS
# ============================================
st.markdown("""
<style>

.seccion{
    text-align:center;
    color:#2563eb;
    font-size:22px;
    font-weight:700;
}

.score{
    text-align:center;
    font-size:90px;
    font-weight:900;
    color:#2563eb;
}

div.stButton > button{
    height:42px;
    background:#2563eb;
    color:white;
    border-radius:8px;
    border:none;
    font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# ============================================
# MODELO
# ============================================
model_path = os.path.join(BASE_PATH, "models", "modelo.pkl")

@st.cache_resource
def load_model(path):
    return joblib.load(path)

model = load_model(model_path)

# ============================================
# HEADER
# ============================================
st.markdown("""
<h1 style='text-align:center;color:#2563eb;font-size:32px;font-weight:700'>
Evaluación de Riesgo y Score de Crédito
</h1>
<br><br>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:

    st.markdown("### Datos del Cliente")

    edad = st.slider("Edad",18,75,30)
    valor = st.slider("Monto del Crédito",250,20000,5000,step=250)
    duracion = st.slider("Duración (meses)",4,72,24)

    genero = st.selectbox("Género",["male","female"])
    trabajo = st.selectbox("Ocupación",[0,1,2,3])
    habitacion = st.selectbox("Vivienda",["own","rent","free"])
    cuenta_ahorro = st.selectbox("Cuenta Ahorro",["little","moderate","rich"])
    cuenta_corriente = st.selectbox("Cuenta Corriente",["little","moderate","rich"])
    finalidad = st.selectbox("Finalidad",[
        "car","furniture/equipment","radio/TV",
        "business","education","repairs","vacation/others"
    ])

    btn = st.button("Calcular", use_container_width=True)

# ============================================
# LAYOUT
# ============================================
col2, col3 = st.columns([1,1])

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

    # ============================================
    # POLÍTICA
    # ============================================
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

    # ============================================
    # DECISÃO
    # ============================================
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

    # ============================================
    # COLUNA 2 (RESULTADO)
    # ============================================
    with col2:

        st.markdown("<div class='seccion'>Resultado del Análisis</div>", unsafe_allow_html=True)

        # SCORE
        st.markdown(f"""
        <div class='score'>
        {score}
        </div>
        """, unsafe_allow_html=True)

        # PROBABILIDADE
        st.markdown(f"""
        <p style='text-align:center;font-size:24px;font-weight:600'>
        Probabilidad de Riesgo
        </p>

        <p style='text-align:center;font-size:36px;font-weight:900;'>
        {prob:.2%}
        </p>
        """, unsafe_allow_html=True)

        # LIMITE
        st.markdown(f"""
        <p style='text-align:center;font-size:24px;font-weight:600'>
        Límite Aprobado
        </p>

        <p style='text-align:center;font-size:36px;font-weight:900;'>
        ${limite:,.0f}
        </p>
        """, unsafe_allow_html=True)

        # STATUS (AGORA FUNCIONA 100%)
        st.markdown(f"""
        <div style="text-align:center;margin-top:30px;">

        <span style="
        color:{cor} !important;
        font-size:42px !important;
        font-weight:900 !important;
        ">

        {status.upper()}

        </span>

        </div>
        """, unsafe_allow_html=True)

    # ============================================
    # COLUNA 3 (GAUGE)
    # ============================================
    with col3:

        st.markdown("<div class='seccion'>Indicador de Riesgo</div>", unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 40], 'color': "#16a34a"},
                    {'range': [40, 70], 'color': "#facc15"},
                    {'range': [70, 100], 'color': "#dc2626"}
                ]
            }
        ))

        st.plotly_chart(fig, use_container_width=True)