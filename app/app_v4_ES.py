import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import os
import json
import scorecardpy as sc

# ============================================
# PATH
# ============================================
BASE_PATH = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(BASE_PATH,"models")

# ============================================
# LOAD
# ============================================
modelo = joblib.load(os.path.join(MODEL_PATH,"modelo.pkl"))
bins_woe = joblib.load(os.path.join(MODEL_PATH,"woe_bins.pkl"))

with open(os.path.join(MODEL_PATH,"metricas.json"),"r") as f:
    metricas_modelo = json.load(f)

with open(os.path.join(MODEL_PATH,"score_params.json"),"r") as f:
    score_params = json.load(f)

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
font-size:20px;
font-weight:600;
}

.score{
text-align:center;
font-size:60px;
font-weight:700;
}

div.stButton > button {
    background-color: #2563eb;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    height: 45px;
    width: 100%;
}
div.stButton > button:hover {
    background-color: #1d4ed8;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("""
<h1 style='text-align:center;
color:#2563eb;
font-size:32px;
font-weight:700;'>
Evaluación de Riesgo y Score de Crédito
</h1><br>
""", unsafe_allow_html=True)

# ============================================
# TABS
# ============================================
tab1,tab2=st.tabs(["Simulación de Crédito","Desempeño del Modelo"])

# ============================================
# TAB 1
# ============================================
with tab1:

    with st.sidebar:

        st.markdown("<div style='text-align:center;color:#2563eb;font-size:20px;font-weight:600;'>Datos del Cliente</div>",unsafe_allow_html=True)

        edad=st.slider("Edad",18,75,30)
        valor=st.slider("Monto del Crédito",250,20000,5000,step=250)
        duracion=st.slider("Duración (meses)",4,72,24)

        genero_map={"Masculino":"male","Femenino":"female"}
        genero=genero_map[st.selectbox("Género",list(genero_map.keys()))]

        trabajo_map={"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}
        trabalho=trabajo_map[st.selectbox("Ocupación",list(trabajo_map.keys()))]

        habitacion_map={"Propia":"own","Alquilada":"rent","Gratuita":"free"}
        habitacion=habitacion_map[st.selectbox("Vivienda",list(habitacion_map.keys()))]

        conta_map={"Bajo":"little","Medio":"moderate","Alto":"rich"}
        cuenta_ahorro=conta_map[st.selectbox("Cuenta de Ahorro",list(conta_map.keys()))]
        cuenta_corriente=conta_map[st.selectbox("Cuenta Corriente",list(conta_map.keys()))]

        finalidade_map={
            "Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV",
            "Negocios":"business","Educación":"education",
            "Reparaciones":"repairs","Otros":"vacation/others"
        }

        finalidad=finalidade_map[st.selectbox("Finalidad del Crédito",list(finalidade_map.keys()))]

        btn=st.button("Calcular",use_container_width=True)

    col2,col3=st.columns([1,1])

    if btn:

        entrada=pd.DataFrame({
            "Genero":[genero],
            "Trabalho":[trabalho],
            "Habitacao":[habitacion],
            "Conta_poupanca":[cuenta_ahorro],
            "Conta_corrente":[cuenta_corriente],
            "Finalidade":[finalidad],
            "Idade":[edad],
            "Duracao":[duracion],
            "Valor_credito":[valor]
        })

        entrada_woe=sc.woebin_ply(entrada,bins_woe)
        entrada_woe=entrada_woe.reindex(columns=modelo.feature_names_in_,fill_value=0)

        prob=modelo.predict_proba(entrada_woe)[0][1]
        prob=min(max(prob,0.0001),0.9999)

        odds=(1-prob)/prob
        PDO=score_params["pdo"]
        BASE_SCORE=score_params["base_score"]
        BASE_ODDS=score_params["base_odds"]

        factor=PDO/np.log(2)
        offset=(BASE_SCORE+factor*np.log(BASE_ODDS))

        score=int(offset+factor*np.log(odds))

        # SEGMENTAÇÃO
        if score >= 700:
            segmento="SUPER PRIME"; limite=18000
        elif score >= 650:
            segmento="PRIME"; limite=10000
        elif score >= 600:
            segmento="STANDARD"; limite=5000
        elif score >= 520:
            segmento="NEAR PRIME"; limite=2500
        elif score >= 460:
            segmento="REVIEW"; limite=1000
        else:
            segmento="SUBPRIME"; limite=0

        if duracion>48:
            limite*=0.85
        elif duracion>36:
            limite*=0.92

        limite=int(limite)

        # DECISÃO
        if score < 460:
            status="RECHAZADO"; icon="✖"; cor="#dc2626"
            motivo="Score por debajo del nivel mínimo de riesgo permitido."
        elif score < 520:
            status="EN ANÁLISIS"; icon="⚠"; cor="#facc15"
            motivo="Cliente en zona de riesgo intermedio. Requiere evaluación manual."
        else:
            if valor <= limite:
                status="APROBADO"; icon="✔"; cor="#16a34a"
                motivo="Monto dentro del límite aprobado según score."
            elif valor <= limite * 1.20:
                status="EN ANÁLISIS"; icon="⚠"; cor="#facc15"
                motivo="Monto levemente superior al límite. Requiere revisión."
            else:
                status="RECHAZADO"; icon="✖"; cor="#dc2626"
                motivo="Monto solicitado excede el límite permitido."

        with col2:

            st.markdown("<div class='seccion'>Resultado del Análisis</div>",unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)

            st.markdown(f"<div class='score'>{score}</div>",unsafe_allow_html=True)

            st.markdown(f"""
            <p style='text-align:center;font-size:22px;font-weight:700;color:#2563eb;'>
            {segmento}
            </p>
            """,unsafe_allow_html=True)

            st.markdown(f"""
            <p style='text-align:center;font-size:20px;font-weight:600;'>Probabilidad de Riesgo</p>
            <p style='text-align:center;font-size:32px;font-weight:700;'>{prob:.2%}</p>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <p style='text-align:center;font-size:20px;font-weight:600;'>Límite Aprobado</p>
            <p style='text-align:center;font-size:32px;font-weight:700;'>${limite:,.0f}</p>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style='text-align:center;margin-top:30px;'>
            <div style='font-size:42px;font-weight:900;color:{cor};'>
            {icon} {status}
            </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <br>
            <p style='text-align:center;font-size:20px;font-weight:500;color:#374151;max-width:450px;margin:auto;'>
            {motivo}
            </p>
            """,unsafe_allow_html=True)

        with col3:

            st.markdown("<div class='seccion'>Indicador de Riesgo</div>",unsafe_allow_html=True)

            fig=go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob*100,
                gauge={
                    "axis":{"range":[0,100]},
                    "steps":[
                        {"range":[0,40],"color":"#16a34a"},
                        {"range":[40,70],"color":"#facc15"},
                        {"range":[70,100],"color":"#dc2626"}
                    ]
                }
            ))

            st.plotly_chart(fig,use_container_width=True)

# ============================================
# TAB 2
# ============================================
with tab2:

    st.markdown("<h2 style='text-align:center;color:#2563eb;font-size:26px;'>Métricas del Modelo</h2>",unsafe_allow_html=True)

    metricas_df = pd.DataFrame({
        "Métrica":["Accuracy","Precisión","Recall","F1-Score","AUC","GINI","KS"],
        "Valor":[
            round(metricas_modelo["accuracy"],4),
            round(metricas_modelo["precision"],4),
            round(metricas_modelo["recall"],4),
            round(metricas_modelo["f1_score"],4),
            round(metricas_modelo["auc"],4),
            round(metricas_modelo["gini"],4),
            round(metricas_modelo["ks"],4)
        ]
    })

    st.markdown(f"""
    <div style='display:flex;justify-content:center;margin-top:20px;'>

    <table style='width:600px;font-size:18px;text-align:center;border-collapse:collapse;'>
        <tr style='background-color:#2563eb;color:white;'>
            <th style='padding:12px;'>Métrica</th>
            <th style='padding:12px;'>Valor</th>
        </tr>
        {''.join([
            f"<tr><td style='padding:10px;border-bottom:1px solid #ddd;'>{m}</td><td style='padding:10px;border-bottom:1px solid #ddd;'>{v}</td></tr>"
            for m, v in zip(metricas_df["Métrica"], metricas_df["Valor"])
        ])}
    </table>

    </div>
    """, unsafe_allow_html=True)

    if "confusion_matrix" in metricas_modelo:

        cm = metricas_modelo["confusion_matrix"]

        tn = cm.get("TN",0)
        fp = cm.get("FP",0)
        fn = cm.get("FN",0)
        tp = cm.get("TP",0)

        st.markdown("<h3 style='text-align:center;color:#2563eb;font-size:22px;'>Matriz de Confusión</h3>",unsafe_allow_html=True)

        st.markdown(f"""
        <div style='display:flex;justify-content:center;margin-top:20px;'>

        <table style='width:550px;font-size:18px;text-align:center;border-collapse:collapse;'>

            <tr style='background-color:#2563eb;color:white;'>
                <th></th>
                <th>Pred: Bom (0)</th>
                <th>Pred: Ruim (1)</th>
            </tr>

            <tr>
                <td><b>Real: Bom (0)</b></td>
                <td>{tn}</td>
                <td>{fp}</td>
            </tr>

            <tr>
                <td><b>Real: Ruim (1)</b></td>
                <td>{fn}</td>
                <td>{tp}</td>
            </tr>

        </table>

        </div>
        """, unsafe_allow_html=True)