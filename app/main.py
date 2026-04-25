import sys
import os
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import scorecardpy as sc

# ============================================
# PATH
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ============================================
# IMPORTS
# ============================================
from src.loader import load_assets
from src.policy import get_score
from app.styles import apply_custom_styles

# ============================================
# CONFIG
# ============================================
st.set_page_config(
    layout="wide",
    page_title="Credit Score App",
    page_icon="💳"
)

apply_custom_styles()

# ============================================
# LOAD
# ============================================
@st.cache_resource
def load_all():
    return load_assets()

modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_all()

# ============================================
# POLICY EQUILIBRADA (ÚNICA ALTERAÇÃO REAL)
# ============================================
def apply_business_policy(score, prob, monto_solicitado, cutoffs):

    # ============================================
    # CALIBRAÇÃO EQUILIBRADA
    # ============================================
    reject_score_cut = 490
    auto_approve_score = 640
    prob_reject_cut = 0.62
    prob_safe_cut = 0.40

    # ============================================
    # SEGMENTAÇÃO
    # ============================================
    if score >= 750:
        segmento, teto = "TOP PRIME", 18000
    elif score >= 700:
        segmento, teto = "SUPER PRIME", 12000
    elif score >= 640:
        segmento, teto = "PRIME", 8000
    elif score >= 600:
        segmento, teto = "STANDARD", 4500
    elif score >= 540:
        segmento, teto = "NEAR PRIME", 2500
    elif score >= 490:
        segmento, teto = "REVIEW", 1200
    else:
        segmento, teto = "SUBPRIME", 0

    # ============================================
    # REPROVAÇÃO DIRETA (RISCO ALTO)
    # ============================================
    if prob >= prob_reject_cut or score < reject_score_cut:
        return {
            "status": "RECHAZADO",
            "icon": "✖",
            "cor": "#dc2626",
            "score": score,
            "segmento": segmento,
            "limite": 0,
            "motivo": "Riesgo elevado según política de crédito."
        }

    # ============================================
    # APROVAÇÃO AUTOMÁTICA (PERFIL MUITO BOM)
    # ============================================
    elif score >= auto_approve_score and prob <= prob_safe_cut:
        risk_factor = 1 - prob
        limite = int(teto * risk_factor)
        limite = max(min(limite, teto), 300)

        return {
            "status": "APROBADO",
            "icon": "✔",
            "cor": "#16a34a",
            "score": score,
            "segmento": segmento,
            "limite": limite,
            "motivo": "Aprobación automática por perfil sólido."
        }

    # ============================================
    # ZONA PRINCIPAL (ANÁLISE - MAIOR PARTE DOS CASOS)
    # ============================================
    else:
        risk_factor = 1 - prob
        limite = int(teto * risk_factor * 0.5)

        return {
            "status": "EN ANÁLISIS",
            "icon": "⚠",
            "cor": "#facc15",
            "score": score,
            "segmento": segmento,
            "limite": max(limite, 250),
            "motivo": "Perfil en zona intermedia. Requiere evaluación."
        }

# ============================================
# HEADER
# ============================================
st.markdown(
    """
    <h1 style='text-align:center;
               color:#2563eb;
               font-size:26px;
               font-weight:700;
               margin-bottom:20px;'>
        Evaluación de Riesgo y Score de Crédito
    </h1>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "🚀 Simulación de Crédito",
    "📊 Desempeño del Modelo",
    "🛡️ Estabilidad (PSI)"
])

# ============================================
# TAB 1
# ============================================
with tab1:
    with st.sidebar:

        st.markdown("<div class='titulo-secao'>Datos del Cliente</div>", unsafe_allow_html=True)

        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero = "male" if st.selectbox("Género", ["Masculino", "Femenino"]) == "Masculino" else "female"

        trabalho = {
            "Desempleado": 0,
            "Básico": 1,
            "Calificado": 2,
            "Especialista": 3
        }[st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])]

        habitacion = {
            "Propia": "own",
            "Alquilada": "rent",
            "Gratuita": "free"
        }[st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])]

        cuenta_ahorro = {
            "Bajo": "little",
            "Medio": "moderate",
            "Alto": "rich"
        }[st.selectbox("Cuenta de Ahorro", ["Bajo", "Medio", "Alto"])]

        cuenta_corriente = {
            "Bajo": "little",
            "Medio": "moderate",
            "Alto": "rich"
        }[st.selectbox("Cuenta Corriente", ["Bajo", "Medio", "Alto"])]

        finalidad = {
            "Auto": "car",
            "Muebles": "furniture/equipment",
            "Electrónicos": "radio/TV",
            "Negocios": "business",
            "Educación": "education",
            "Reparaciones": "repairs",
            "Otros": "vacation/others"
        }[st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])]

        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:

        entrada = pd.DataFrame({
            "Genero": [genero],
            "Trabalho": [trabalho],
            "Habitacao": [habitacion],
            "Conta_poupanca": [cuenta_ahorro],
            "Conta_corrente": [cuenta_corriente],
            "Finalidade": [finalidad],
            "Idade": [edad],
            "Duracao": [duracion],
            "Valor_credito": [valor]
        })

        entrada_woe = sc.woebin_ply(
            entrada,
            bins_woe
        ).reindex(
            columns=modelo.feature_names_in_,
            fill_value=0
        )

        prob = modelo.predict_proba(entrada_woe)[0][1]
        prob = min(max(prob, 0.0001), 0.9999)

        score_base = get_score(prob, score_params)

        penalidade = 0
        flags = []

        if trabalho == 0:
            penalidade -= 80
            flags.append("Sin empleo")

        if habitacion == "rent":
            penalidade -= 30
            flags.append("Vivienda alquilada")

        if cuenta_ahorro == "little":
            penalidade -= 20
            flags.append("Bajo ahorro")

        if cuenta_corriente == "little":
            penalidade -= 20
            flags.append("Baja liquidez")

        score_final = max(score_base + penalidade, 300)

        decision = apply_business_policy(
            score_final,
            prob,
            valor,
            cutoffs
        )

        limite = decision["limite"]

        if duracion > 48:
            limite = int(limite * 0.85)

        motivo = decision["motivo"]

        if flags:
            motivo += " | Riesgos: " + ", ".join(flags)

        # RESULTADO
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)

            st.markdown(
                f"<div class='score' style='color:{decision['cor']};'>{decision['score']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{decision['segmento']}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;'>Probabilidad</p>"
                f"<p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;'>Límite Sugerido</p>"
                f"<p style='text-align:center;font-size:22px;font-weight:700;'>${limite:,.0f}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div style='text-align:center;font-size:28px;color:{decision['cor']};font-weight:900;'>"
                f"{decision['icon']} {decision['status']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;font-size:12px;color:#64748b;'>{motivo}</p>",
                unsafe_allow_html=True
            )

        # GAUGE (INTOCADO)
        with col_graf:

            st.markdown("<div class='titulo-secao' style='text-align:center;'>Indicador de Riesgo</div>", unsafe_allow_html=True)

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={"font": {"size": 26}, "suffix": "%"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"thickness": 0.25},
                    "steps": [
                        {"range": [0, 40], "color": "#16a34a"},
                        {"range": [40, 70], "color": "#facc15"},
                        {"range": [70, 100], "color": "#dc2626"},
                    ]
                }
            ))

            fig.update_layout(
                width=380,
                height=280,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)"
            )

            col_esq, col_centro, col_dir = st.columns([1, 3, 1])

            with col_centro:
                st.plotly_chart(fig, use_container_width=False, config={"displayModeBar": False})

# ============================================
# TAB 2 (SEM ALTERAÇÃO)
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

# ============================================
# TAB 3 (SEM ALTERAÇÃO)
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