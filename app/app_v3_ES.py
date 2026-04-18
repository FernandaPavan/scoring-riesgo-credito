import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import os
import sys

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
# CSS
# ============================================
st.markdown("""
<style>

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSlider,
section[data-testid="stSidebar"] .stSelectbox {
    font-size:14px !important;
}

.sidebar-title{
    text-align:center;
    color:#2563eb;
    font-size:20px;
    font-weight:600;
}

.seccion{
    text-align:center;
    color:#2563eb;
    font-size:20px;
    font-weight:600;
}

.score{
    text-align:center;
    font-size:60px;
    font-weight:700;
}

div.stButton > button{
    height:38px;
    background:#2563eb;
    color:white;
    border-radius:8px;
    border:none;
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
<h1 style='text-align:center;color:#2563eb;font-size:32px;font-weight:700'>
Evaluación de Riesgo y Score de Crédito
</h1>
<br><br>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:

    st.markdown("<div class='sidebar-title'>Datos del Cliente</div>", unsafe_allow_html=True)

    edad = st.slider("Edad",18,75,30)
    valor = st.slider("Monto del Crédito",250,20000,5000,step=250)
    duracion = st.slider("Duración (meses)",4,72,24)

    genero_map={
        "Masculino":"male",
        "Femenino":"female"
    }

    genero=genero_map[
        st.selectbox("Género",list(genero_map.keys()))
    ]

    trabajo_map={
        "Desempleado":0,
        "Básico":1,
        "Calificado":2,
        "Especialista":3
    }

    trabajo=trabajo_map[
        st.selectbox("Ocupación",list(trabajo_map.keys()))
    ]

    habitacion_map={
        "Propia":"own",
        "Alquilada":"rent",
        "Gratuita":"free"
    }

    habitacion=habitacion_map[
        st.selectbox("Vivienda",list(habitacion_map.keys()))
    ]

    cuenta_opciones={
        "Bajo":"little",
        "Medio":"moderate",
        "Alto":"rich"
    }

    cuenta_ahorro=cuenta_opciones[
        st.selectbox(
            "Saldo en Cuenta de Ahorro",
            list(cuenta_opciones.keys())
        )
    ]

    cuenta_corriente=cuenta_opciones[
        st.selectbox(
            "Saldo en Cuenta Corriente",
            list(cuenta_opciones.keys())
        )
    ]

    finalidade_map={
        "Auto":"car",
        "Muebles/Equipamiento":"furniture/equipment",
        "Electrónicos":"radio/TV",
        "Negocios":"business",
        "Educación":"education",
        "Reparaciones":"repairs",
        "Otros":"vacation/others"
    }

    finalidad=finalidade_map[
        st.selectbox(
            "Finalidad del Crédito",
            list(finalidade_map.keys())
        )
    ]

    btn=st.button("Calcular",use_container_width=True)

# ============================================
# LAYOUT
# ============================================
col2,col3=st.columns([1,1])

# ============================================
# EXECUÇÃO
# ============================================
if btn:

    entrada=pd.DataFrame({

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

    # Probabilidade e Score
    prob=model.predict_proba(entrada)[0][1]

    score=int(
        850-(prob*550)
    )

    # ============================================
    # POLÍTICA DE CRÉDITO
    # ============================================

    if score >= 750:
        limite=18000

    elif score >=700:
        limite=10000

    elif score >=650:
        limite=4000

    elif score >=600:
        limite=2500

    elif score >=550:
        limite=250

    else:
        limite=0

    # Ajuste por prazo

    if duracion > 48:
        limite*=0.80

    elif duracion >36:
        limite*=0.90

    # ============================================
    # DECISÃO
    # ============================================

    if score <550:
        status="✖ RECHAZADO"
        cor="#dc2626"

    elif valor <= limite:
        status="✔ APROBADO"
        cor="#16a34a"

    elif valor <= limite*1.20:
        status="⚠ EN ANÁLISIS"
        cor="#facc15"

    else:
        status="✖ RECHAZADO"
        cor="#dc2626"

    # ============================================
    # COLUNA RESULTADO
    # ============================================

    with col2:

        st.markdown(
            "<div class='seccion'>Resultado del Análisis</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<div class='score'>{score}</div>",
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <p style='text-align:center;font-size:18px'>
        Probabilidad de Riesgo
        </p>

        <p style='text-align:center;font-size:28px;font-weight:bold;'>
        {prob:.2%}
        </p>
        """,unsafe_allow_html=True)

        st.markdown(f"""
        <p style='text-align:center;font-size:18px'>
        Límite Aprobado
        </p>

        <p style='text-align:center;font-size:28px;font-weight:bold;'>
        ${limite:,.0f}
        </p>
        """,unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center;margin-top:20px;">

        <span style="
        color:{cor};
        font-size:28px;
        font-weight:700;
        ">

        {status}

        </span>

        </div>
        """,unsafe_allow_html=True)

    # ============================================
    # COLUNA GAUGE
    # ============================================

    with col3:

        st.markdown(
            "<div class='seccion'>Indicador de Riesgo</div>",
            unsafe_allow_html=True
        )

        fig=go.Figure(go.Indicator(

            mode="gauge+number",

            value=prob*100,

            number={'font':{'size':28}},

            gauge={

                'axis':{'range':[0,100]},

                'bar':{'color':"#111"},

                'steps':[

                    {'range':[0,40],'color':"#16a34a"},
                    {'range':[40,70],'color':"#facc15"},
                    {'range':[70,100],'color':"#dc2626"}

                ]

            }

        ))

        fig.update_layout(
            height=380,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )