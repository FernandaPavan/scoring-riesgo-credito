import sys
import os
import streamlit as st
import plotly.graph_objects as go

# ============================================
# PATH (garante import da pasta src)
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ============================================
# IMPORTS MODULARES
# ============================================
from src.loader import load_assets
from src.features import traduzir_inputs, montar_entrada, preparar_dados
from src.policy import get_score, apply_business_policy
from app.styles import apply_custom_styles

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App")

# ============================================
# LOAD
# ============================================
@st.cache_resource
def load_all():
    return load_assets()

modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_all()

# ============================================
# STYLES (Injeção do CSS)
# ============================================
apply_custom_styles()

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
# TAB 1 - SIMULACIÓN
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;'>Datos del Cliente</div>", unsafe_allow_html=True)

        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero_sel = st.selectbox("Género", ["Masculino", "Femenino"])
        trabalho_sel = st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])
        vivienda_sel = st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])
        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo", "Medio", "Alto"])
        corriente_sel = st.selectbox("Cuenta Corriente", ["Bajo", "Medio", "Alto"])
        finalidad_sel = st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])

        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1,1])

    if btn:
        # TRADUÇÃO E PROCESSAMENTO
        genero, trabajo, vivienda, ahorro, corrente, finalidad = traduzir_inputs(
            genero_sel, trabalho_sel, vivienda_sel, ahorro_sel, corrente_sel, finalidad_sel
        )

        entrada = montar_entrada(genero, trabajo, vivienda, ahorro, corrente, finalidad, edad, duracion, monto)
        entrada_woe = preparar_dados(entrada, bins_woe, modelo)

        # SCORE
        prob = modelo.predict_proba(entrada_woe)[0][1]
        score_base = get_score(prob, score_params)

        # PENALIZAÇÃO
        penalidade = 0
        if trabajo == 0: penalidade -= 80
        if vivienda == "rent": penalidade -= 30
        score_final = max(score_base + penalidade, 300)

        # POLICY
        decision = apply_business_policy(score_final, prob, monto, cutoffs)

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{decision['cor']};'>{decision['score']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-weight:700;color:#2563eb;'>{decision['segmento']}</p>", unsafe_allow_html=True)
            
            # Sub-métricas rápidas
            c1, c2 = st.columns(2)
            c1.markdown(f"<p style='text-align:center;margin-bottom:0;'>Probabilidad</p><p style='text-align:center;font-size:20px;font-weight:700;'>{prob:.2%}</p>", unsafe_allow_html=True)
            c2.markdown(f"<p style='text-align:center;margin-bottom:0;'>Límite</p><p style='text-align:center;font-size:20px;font-weight:700;'>${decision['limite']:,.0f}</p>", unsafe_allow_html=True)

            st.markdown(f"<div style='text-align:center;font-size:24px;font-weight:700;color:{decision['cor']};'>{decision['icon']} {decision['status']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:12px;color:#64748b;'>{decision['motivo']}</p>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'suffix': "%", 'font': {'size': 40}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, 20], "color": "#16a34a"},
                        {"range": [20, 50], "color": "#facc15"},
                        {"range": [50, 100], "color": "#dc2626"},
                    ],
                }
            ))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2 - MÉTRICAS DO MODELO
# ============================================
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})

    st.markdown(f"""
    <div class='container-performance'>
        <p class='titulo-secao'>Métricas del Modelo</p>
        <table>
            <tr><th>Métrica</th><th>Valor</th></tr>
            <tr><td>Accuracy</td><td>{m.get('accuracy', 0):.4f}</td></tr>
            <tr><td>Precision</td><td>{m.get('precision', 0):.4f}</td></tr>
            <tr><td>Recall</td><td>{m.get('recall', 0):.4f}</td></tr>
            <tr><td>AUC</td><td>{m.get('auc', 0):.4f}</td></tr>
            <tr><td>Gini</td><td>{m.get('gini', 0):.4f}</td></tr>
            <tr><td>KS</td><td>{m.get('ks', 0):.4f}</td></tr>
        </table>

        <p class='titulo-secao' style='margin-top:30px;'>Matriz de Confusión</p>
        <table>
            <tr>
                <th>Real \ Pred</th>
                <th>Bueno (0)</th>
                <th>Malo (1)</th>
            </tr>
            <tr>
                <td><b>Bueno (0)</b></td>
                <td class='val-pos'>{cm.get('TN', 0)}</td>
                <td class='val-neg'>{cm.get('FP', 0)}</td>
            </tr>
            <tr>
                <td><b>Malo (1)</b></td>
                <td class='val-neg'>{cm.get('FN', 0)}</td>
                <td class='val-pos'>{cm.get('TP', 0)}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 3 - PSI
# ============================================
with tab3:
    psi = metricas_modelo.get("psi", 0)
    
    # Lógica de cores para o PSI
    if psi < 0.1:
        status, cor, icon = "ESTABLE", "#16a34a", "✅"
    elif psi < 0.25:
        status, cor, icon = "ALERTA", "#facc15", "⚠️"
    else:
        status, cor, icon = "INESTABLE", "#dc2626", "🚨"

    st.markdown(f"""
    <div class='container-performance'>
        <p class='titulo-secao'>Estabilidad del Modelo</p>
        <div class='psi-card'>
            <p style='font-size:14px; color:#64748b; margin-bottom:5px;'>Population Stability Index (PSI)</p>
            <div class='score' style='color:{cor};'>{psi:.4f}</div>
            <p style='color:{cor}; font-weight:700; font-size:18px;'>{icon} {status}</p>
            <hr style='border: 0; border-top: 1px solid #eee; margin: 15px 0;'>
            <p style='font-size:11px; color:#94a3b8;'>Interpretación: <br> 
            &lt; 0.1: Sin cambios | 0.1-0.25: Cambio moderado | &gt; 0.25: Cambio significativo</p>
        </div>
    </div>
    """, unsafe_allow_html=True)