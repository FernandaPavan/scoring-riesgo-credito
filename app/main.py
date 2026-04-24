import sys
import os
import streamlit as st
import plotly.graph_objects as go

# Ajuste de Path para importar do src
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.loader import load_assets
from src.policy import get_score, apply_business_policy
from src.features import traduzir_inputs, montar_entrada, preparar_dados
from app.styles import apply_custom_styles

# Configuração Inicial
st.set_page_config(layout="wide", page_title="Credit Score App")

# Load Data
@st.cache_resource
def load_all():
    return load_assets()

modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_all()

# Aplica Styles
apply_custom_styles()

# Header
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

# --- TAB 1: SIMULACIÓN ---
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;margin-bottom:5px;'>Datos del Cliente</div>", unsafe_allow_html=True)
        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero_sel = st.selectbox("Género", ["Masculino", "Femenino"])
        trabajo_sel = st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])
        vivienda_sel = st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])
        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo", "Medio", "Alto"])
        corriente_sel = st.selectbox("Cuenta Corriente", ["Bajo", "Medio", "Alto"])
        finalidad_sel = st.selectbox("Finalidad", ["Auto", "Muebles", "Electrónicos", "Negocios", "Educación", "Reparaciones", "Otros"])

        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        genero, trabalho, vivienda, ahorro, corriente, finalidad = traduzir_inputs(
            genero_sel, trabalho_sel, vivienda_sel, ahorro_sel, corriente_sel, finalidad_sel
        )

        entrada = montar_entrada(genero, trabalho, vivienda, ahorro, corriente, finalidad, edad, duracion, monto)
        entrada_woe = preparar_dados(entrada, bins_woe, modelo)

        prob = modelo.predict_proba(entrada_woe)[0][1]
        score = get_score(prob, score_params)
        decision = apply_business_policy(score, prob, monto, cutoffs)

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{decision['cor']};'>{decision['score']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{decision['segmento']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Probabilidad</p><p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Límite Sugerido</p><p style='text-align:center;font-size:22px;font-weight:700;'>${decision['limite']:,.0f}</p>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:28px;color:{decision['cor']};font-weight:900;'>{decision['icon']} {decision['status']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:12px;color:#64748b;padding:0 20px;'>{decision['motivo']}</p>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div><br>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, number={'font': {'size': 45}, 'suffix': "%"},
                gauge={"axis":{"range":[0,100]},"steps":[{"range":[0,40],"color":"#16a34a"},{"range":[40,70],"color":"#facc15"},{"range":[70,100],"color":"#dc2626"}]}))
            fig.update_layout(height=260, margin=dict(l=30, r=30, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: DESEMPEÑO ---
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})
    st.markdown(f"""
    <div class='container-performance'>
        <br><p class='titulo-secao'>Métricas Generales</p>
        <table>
            <tr><th>Métrica</th><th>Valor</th></tr>
            <tr><td>Accuracy</td><td>{m['accuracy']:.4f}</td></tr>
            <tr><td>Precision</td><td>{m['precision']:.4f}</td></tr>
            <tr><td>Recall</td><td>{m['recall']:.4f}</td></tr>
            <tr><td>AUC</td><td>{m['auc']:.4f}</td></tr>
            <tr><td>Gini</td><td>{m['gini']:.4f}</td></tr>
            <tr><td>KS</td><td>{m['ks']:.4f}</td></tr>
        </table>
        <p class='titulo-secao' style='margin-top:25px;'>Matriz de Confusión</p>
        <table>
            <tr><th>Real \\ Pred</th><th>Bueno (0)</th><th>Malo (1)</th></tr>
            <tr><td>Bueno (0)</td><td class='val-pos'>{cm['TN']}</td><td class='val-neg'>{cm['FP']}</td></tr>
            <tr><td>Malo (1)</td><td class='val-neg'>{cm['FN']}</td><td class='val-pos'>{cm['TP']}</td></tr>
        </table>
    </div>""", unsafe_allow_html=True)

# --- TAB 3: ESTABILIDADE ---
with tab3:
    psi_v = metricas_modelo.get("psi", 0.00)
    psi_c = "#16a34a" if psi_v < 0.1 else "#facc15" if psi_v < 0.25 else "#dc2626"
    psi_s = "ESTABLE" if psi_v < 0.1 else "ALERTA" if psi_v < 0.25 else "INESTABLE"
    st.markdown(f"""
    <div class='container-performance'>
        <br><br><p class='titulo-secao'>Estabilidad del Modelo (PSI)</p><br>
        <div class='psi-card'>
            <p style='font-size:11px; color:#64748b;'>PSI ACUMULADO</p>
            <h1 style='font-size:42px; color:{psi_c};'>{psi_v:.4f}</h1>
            <p style='color:{psi_c}; font-weight:800;'>{psi_s}</p>
        </div>
    </div>""", unsafe_allow_html=True)