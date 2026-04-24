import sys
import os

# ============================================
# GARANTE QUE O PYTHON ENCONTRE /src
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

# ============================================
# IMPORTS
# ============================================
import streamlit as st
import plotly.graph_objects as go

from src.loader import load_assets
from src.policy import get_score, apply_business_policy
from src.features import montar_entrada, preparar_dados
from app.styles import apply_styles

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App")

# ============================================
# STYLE
# ============================================
apply_styles()

# ============================================
# LOAD
# ============================================
modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_assets()

# ============================================
# HEADER
# ============================================
st.markdown(
    "<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>",
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "Simulación de Crédito",
    "Desempeño del Modelo",
    "Estabilidad (PSI)"
])

# ============================================
# TAB 1: SIMULACIÓN
# ============================================
with tab1:

    with st.sidebar:
        st.markdown(
            "<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;margin-bottom:5px;'>Datos del Cliente</div>",
            unsafe_allow_html=True
        )

        idade = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero_sel = st.selectbox("Género", ["Masculino", "Femenino"])
        genero = "male" if genero_sel == "Masculino" else "female"

        trabalho_sel = st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])
        trabalho = {"Desempleado": 0, "Básico": 1, "Calificado": 2, "Especialista": 3}[trabalho_sel]

        habitacion_sel = st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])
        habitacion = {"Propia": "own", "Alquilada": "rent", "Gratuita": "free"}[habitacion_sel]

        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo", "Medio", "Alto"])
        ahorro = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}[ahorro_sel]

        corriente_sel = st.selectbox("Cuenta Corriente", ["Bajo", "Medio", "Alto"])
        corriente = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}[corriente_sel]

        finalidad_sel = st.selectbox("Finalidad", ["Auto", "Muebles", "Electrónicos", "Negocios", "Educación", "Reparaciones", "Otros"])
        finalidade = {
            "Auto": "car",
            "Muebles": "furniture/equipment",
            "Electrónicos": "radio/TV",
            "Negocios": "business",
            "Educación": "education",
            "Reparaciones": "repairs",
            "Otros": "vacation/others"
        }[finalidade_sel]

        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:

        # ============================================
        # INPUT
        # ============================================
        entrada = montar_entrada({
            "Genero": [genero],
            "Trabalho": [trabalho],
            "Habitacao": [habitacion],
            "Conta_poupanca": [ahorro],
            "Conta_corrente": [corriente],
            "Finalidade": [finalidade],
            "Idade": [idade],
            "Duracao": [duracion],
            "Valor_credito": [valor]
        })

        # ============================================
        # PIPE COMPLETO (FEATURES + WOE)
        # ============================================
        entrada_woe = preparar_dados(entrada, bins_woe, modelo)

        # ============================================
        # PREDIÇÃO
        # ============================================
        prob = modelo.predict_proba(entrada_woe)[0][1]

        # ============================================
        # SCORE
        # ============================================
        score = get_score(prob, score_params)

        # ============================================
        # POLICY
        # ============================================
        resultado = apply_business_policy(
            score,
            prob,
            valor,
            cutoffs
        )

        # ============================================
        # RESULTADO
        # ============================================
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)

            st.markdown(
                f"<div class='score' style='color:{resultado['cor']};'>{resultado['score']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{resultado['segmento']}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;margin-bottom:0;'>Probabilidad</p>"
                f"<p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;margin-bottom:0;'>Límite Sugerido</p>"
                f"<p style='text-align:center;font-size:22px;font-weight:700;'>${resultado['limite']:,.0f}</p>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div style='text-align:center;font-size:26px;color:{resultado['cor']};font-weight:900;'>"
                f"{resultado['icon']} {resultado['status']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<p style='text-align:center;font-size:12px;color:#64748b;padding:0 20px;'>"
                f"{resultado['motivo']}</p>",
                unsafe_allow_html=True
            )

        # ============================================
        # GAUGE
        # ============================================
        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div><br>", unsafe_allow_html=True)

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'font': {'size': 45}, 'suffix': "%"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "steps": [
                        {"range": [0, 40], "color": "#16a34a"},
                        {"range": [40, 70], "color": "#facc15"},
                        {"range": [70, 100], "color": "#dc2626"}
                    ]
                }
            ))

            fig.update_layout(
                height=260,
                margin=dict(l=30, r=30, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: MODELO
# ============================================
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN": 0, "FP": 0, "FN": 0, "TP": 0})

    st.markdown(f"""
    <div class='container-performance'>
        <p class='titulo-secao'>Métricas Generales</p>
        <table>
            <tr><th>Métrica</th><th>Valor</th></tr>
            <tr><td>Accuracy</td><td>{m['accuracy']:.4f}</td></tr>
            <tr><td>Precision</td><td>{m['precision']:.4f}</td></tr>
            <tr><td>Recall</td><td>{m['recall']:.4f}</td></tr>
            <tr><td>AUC</td><td>{m['auc']:.4f}</td></tr>
            <tr><td>Gini</td><td>{m['gini']:.4f}</td></tr>
            <tr><td>KS</td><td>{m['ks']:.4f}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 3: PSI
# ============================================
with tab3:
    psi_v = metricas_modelo.get("psi", 0.0)

    psi_c = "#16a34a" if psi_v < 0.1 else "#facc15" if psi_v < 0.25 else "#dc2626"
    psi_s = "ESTÁVEL" if psi_v < 0.1 else "ALERTA" if psi_v < 0.25 else "INSTÁVEL"

    st.markdown(f"""
    <div style='text-align:center; margin-top:40px;'>
        <p class='titulo-secao'>Estabilidad del Modelo (PSI)</p>
        <div style='border:1px solid #e2e8f0; padding:20px; border-radius:12px; width:280px; margin:auto;'>
            <p style='font-size:11px; color:#64748b;'>PSI ACUMULADO</p>
            <h1 style='font-size:42px; color:{psi_c};'>{psi_v:.4f}</h1>
            <p style='color:{psi_c}; font-weight:800;'>{psi_s}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)