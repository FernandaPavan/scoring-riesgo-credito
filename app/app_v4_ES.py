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

MODEL_PATH = os.path.join(
    BASE_PATH,
    "models"
)

# ============================================
# LOAD ARQUIVOS
# ============================================
modelo = joblib.load(
    os.path.join(MODEL_PATH,"modelo.pkl")
)

bins_woe = joblib.load(
    os.path.join(MODEL_PATH,"woe_bins.pkl")
)

with open(
    os.path.join(MODEL_PATH,"metricas.json"),
    "r"
) as f:
    metricas_modelo = json.load(f)

with open(
    os.path.join(MODEL_PATH,"score_params.json"),
    "r"
) as f:
    score_params = json.load(f)

with open(
    os.path.join(MODEL_PATH,"ks_cutoffs.json"),
    "r"
) as f:
    ks_cutoffs = json.load(f)

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
</h1>
<br>
""", unsafe_allow_html=True)

# ============================================
# TABS
# ============================================
tab1,tab2=st.tabs([
"Simulación de Crédito",
"Desempeño del Modelo"
])

# ============================================
# TAB 1
# ============================================
with tab1:

    with st.sidebar:

        st.markdown(
            "<div style='text-align:center;color:#2563eb;font-size:20px;font-weight:600;'>Datos del Cliente</div>",
            unsafe_allow_html=True
        )

        edad=st.slider("Edad",18,75,30)

        valor=st.slider(
            "Monto del Crédito",
            250,
            20000,
            5000,
            step=250
        )

        duracion=st.slider(
            "Duración (meses)",
            4,
            72,
            24
        )

        genero_map={
            "Masculino":"male",
            "Femenino":"female"
        }

        genero=genero_map[
            st.selectbox(
                "Género",
                list(genero_map.keys())
            )
        ]

        trabajo_map={
            "Desempleado":0,
            "Básico":1,
            "Calificado":2,
            "Especialista":3
        }

        trabajo=trabajo_map[
            st.selectbox(
                "Ocupación",
                list(trabajo_map.keys())
            )
        ]

        habitacion_map={
            "Propia":"own",
            "Alquilada":"rent",
            "Gratuita":"free"
        }

        habitacion=habitacion_map[
            st.selectbox(
                "Vivienda",
                list(habitacion_map.keys())
            )
        ]

        conta_map={
            "Bajo":"little",
            "Medio":"moderate",
            "Alto":"rich"
        }

        cuenta_ahorro=conta_map[
            st.selectbox(
                "Cuenta de Ahorro",
                list(conta_map.keys())
            )
        ]

        cuenta_corriente=conta_map[
            st.selectbox(
                "Cuenta Corriente",
                list(conta_map.keys())
            )
        ]

        finalidade_map={
            "Auto":"car",
            "Muebles":"furniture/equipment",
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

        btn=st.button(
            "Calcular",
            use_container_width=True
        )

    col2,col3=st.columns([1,1])

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

        entrada_woe=sc.woebin_ply(
            entrada,
            bins_woe
        )

        entrada_woe=entrada_woe.reindex(
            columns=modelo.feature_names_in_,
            fill_value=0
        )

        # ============================================
        # PROBABILIDADE
        # ============================================
        prob=modelo.predict_proba(
            entrada_woe
        )[0][1]

        prob=min(
            max(prob,0.0001),
            0.9999
        )

        # ============================================
        # SCORE PDO
        # ============================================
        odds=(1-prob)/prob

        PDO=score_params["pdo"]
        BASE_SCORE=score_params["base_score"]
        BASE_ODDS=score_params["base_odds"]

        factor=PDO/np.log(2)

        offset=(
            BASE_SCORE
            +factor*np.log(BASE_ODDS)
        )

        score=int(
            offset
            +factor*np.log(odds)
        )

        # ============================================
        # KS CUTOFFS
        # ============================================
        reject_cutoff=ks_cutoffs["reject_cutoff"]
        review_cutoff=ks_cutoffs["review_cutoff"]
        approve_cutoff=ks_cutoffs["approve_cutoff"]

        # ============================================
        # SEGMENTAÇÃO
        # ============================================
        if score < 460:
            segmento="SUBPRIME"

        elif score < 520:
            segmento="STANDARD"

        elif score < 650:
            segmento="PRIME"

        else:
            segmento="SUPER PRIME"

        # ============================================
        # LIMITE
        # ============================================
        if score>=750:
            limite=18000

        elif score>=700:
            limite=10000

        elif score>=650:
            limite=4000

        elif score>=600:
            limite=2500

        elif score>=550:
            limite=250

        else:
            limite=0

        if duracion>48:
            limite*=0.80

        elif duracion>36:
            limite*=0.90

        # ============================================
        # DECISÃO KS
        # ============================================
        if score < reject_cutoff:

            status="✖ RECHAZADO"
            cor="#dc2626"

            motivo="Score por debajo del cutoff mínimo definido por política de riesgo."

        elif score < approve_cutoff:

            status="⚠ EN ANÁLISIS"
            cor="#facc15"

            motivo="Cliente ubicado en zona intermedia (review band) y requiere análisis manual."

        else:

            if valor <= limite:

                status="✔ APROBADO"
                cor="#16a34a"

                motivo="Monto solicitado dentro del límite aprobado por score y política."

            else:

                status="⚠ EN ANÁLISIS"
                cor="#facc15"

                motivo="Score aprobado, pero monto solicitado supera el límite automático."

        # ============================================
        # RESULTADO
        # ============================================
        with col2:

            st.markdown(
                "<div class='seccion'>Resultado del Análisis</div>",
                unsafe_allow_html=True
            )

            st.markdown("<br>",unsafe_allow_html=True)

            st.markdown(
                f"<div class='score'>{score}</div>",
                unsafe_allow_html=True
            )

            st.markdown(f"""
            <p style='text-align:center;font-size:26px;font-weight:bold;'>
            Segmento: {segmento}
            </p>
            """,
            unsafe_allow_html=True)

            st.markdown(f"""
            <p style='text-align:center;font-size:18px;'>
            Probabilidad de Riesgo
            </p>

            <p style='text-align:center;font-size:28px;font-weight:bold;'>
            {prob:.2%}
            </p>
            """,
            unsafe_allow_html=True)

            st.markdown(f"""
            <p style='text-align:center;font-size:18px;'>
            Límite Aprobado
            </p>

            <p style='text-align:center;font-size:28px;font-weight:bold;'>
            ${limite:,.0f}
            </p>
            """,
            unsafe_allow_html=True)

            st.markdown(f"""
            <div style='text-align:center;margin-top:20px;'>

            <span style='
            color:{cor};
            font-size:30px;
            font-weight:700;'>

            {status}

            </span>

            </div>
            """,
            unsafe_allow_html=True)

            st.markdown(f"""
            <br>
            <p style='text-align:center;font-size:17px;color:#374151;'>
            {motivo}
            </p>
            """,
            unsafe_allow_html=True)

        # ============================================
        # GAUGE
        # ============================================
        with col3:

            st.markdown(
                "<div class='seccion'>Indicador de Riesgo</div>",
                unsafe_allow_html=True
            )

            fig=go.Figure(
                go.Indicator(

                    mode="gauge+number",

                    value=prob*100,

                    number={"font":{"size":28}},

                    gauge={

                        "axis":{
                            "range":[0,100]
                        },

                        "bar":{
                            "color":"#111"
                        },

                        "steps":[

                            {
                            "range":[0,40],
                            "color":"#16a34a"
                            },

                            {
                            "range":[40,70],
                            "color":"#facc15"
                            },

                            {
                            "range":[70,100],
                            "color":"#dc2626"
                            }

                        ]
                    }
                )
            )

            fig.update_layout(
                height=380,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

# ============================================
# TAB 2
# ============================================
with tab2:

    st.markdown("""
    <h2 style='text-align:center;
    color:#2563eb;
    font-size:22px;'>
    Métricas del Modelo
    </h2>
    """,
    unsafe_allow_html=True)

    metricas=pd.DataFrame({

        "Métrica":[
            "Accuracy",
            "Precisión",
            "Recall",
            "F1-Score",
            "AUC",
            "GINI",
            "KS"
        ],

        "Valor":[

            round(metricas_modelo["accuracy"],6),
            round(metricas_modelo["precision"],6),
            round(metricas_modelo["recall"],6),
            round(metricas_modelo["f1_score"],6),
            round(metricas_modelo["auc"],6),
            round(metricas_modelo["gini"],6),
            round(metricas_modelo["ks"],6)

        ]
    })

    st.dataframe(
        metricas,
        use_container_width=True
    )