import sys
import os
import streamlit as st
import plotly.graph_objects as go

# ============================================
# PATH (garante import da pasta src e app)
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
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App", page_icon="💳")

# Injeção de CSS Customizado
apply_custom_styles()

# ============================================
# CARREGAMENTO DE ASSETS
# ============================================
@st.cache_resource
def load_all():
    return load_assets()

modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_all()

# ============================================
# HEADER PRINCIPAL
# ============================================
st.markdown(
    "<h1 style='text-align:center;color:#2563eb;font-size:26px;font-weight:700;margin-bottom:20px;'>"
    "Evaluación de Riesgo y Score de Crédito</h1>",
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "🚀 Simulación de Crédito",
    "📊 Desempeño del Modelo",
    "🛡️ Estabilidad (PSI)"
])

# ============================================
# TAB 1: SIMULACIÓN DE CRÉDITO
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:14px;font-weight:700;margin-bottom:10px;'>"
                    "DATOS DEL CLIENTE</div>", unsafe_allow_html=True)

        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero_sel = st.selectbox("Género", ["Masculino", "Femenino"])
        trabalho_sel = st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])
        vivienda_sel = st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])
        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo", "Medio", "Alto"])
        corriente_sel = st.selectbox("Cuenta Corriente", ["Bajo", "Medio", "Alto"])
        finalidad_sel = st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])

        st.markdown("---")
        btn = st.button("CALCULAR SCORE")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        # 1. TRADUÇÃO (Sincronizado com features.py)
        genero, trabalho, vivienda, ahorro, corriente, finalidad = traduzir_inputs(
            genero_sel, trabalho_sel, vivienda_sel, ahorro_sel, corriente_sel, finalidad_sel
        )

        # 2. MONTAGEM DO DATAFRAME (Variável 'corriente' corrigida)
        entrada = montar_entrada(
            genero, trabalho, vivienda, ahorro, corriente, finalidad,
            edad, duracion, monto
        )

        # 3. PREPARAÇÃO (Feature Engineering + WOE)
        entrada_woe = preparar_dados(entrada, bins_woe, modelo)

        # 4. PREDIÇÃO E SCORE
        prob = modelo.predict_proba(entrada_woe)[0][1]
        score_base = get_score(prob, score_params)

        # 5. REGRAS DE NEGÓCIO (Penalizações)
        penalidade = 0
        if trabalho == 0: penalidade -= 80 
        if vivienda == "rent": penalidade -= 30 
        score_final = max(score_base + penalidade, 300)

        # 6. DECISÃO FINAL
        decision = apply_business_policy(score_final, prob, monto, cutoffs)

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado del Análisis</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{decision['cor']};'>{decision['score']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-weight:700;font-size:18px;color:#1e40af;'>{decision['segmento']}</p>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            c1.markdown(f"<div style='text-align:center;'><small>Probabilidad</small><br><b>{prob:.2%}</b></div>", unsafe_allow_html=True)
            c2.markdown(f"<div style='text-align:center;'><small>Límite Sugerido</small><br><b>${decision['limite']:,.0f}</b></div>", unsafe_allow_html=True)

            st.markdown(f"<div style='text-align:center;font-size:26px;margin-top:15px;color:{decision['cor']};'>"
                        f"<b>{decision['icon']} {decision['status']}</b></div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:13px;color:#64748b;'>{decision['motivo']}</p>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'suffix': "%", 'font': {'size': 40}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#1e40af"},
                    "steps": [
                        {"range": [0, 30], "color": "#dcfce7"},
                        {"range": [30, 60], "color": "#fef9c3"},
                        {"range": [60, 100], "color": "#fee2e2"},
                    ],
                }
            ))
            fig.update_layout(height=320, margin=dict(l=30, r=30, t=50, b=0))
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# ============================================
# TAB 2: MÉTRICAS DO MODELO
# ============================================
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})

    # ----- MÉTRICAS -----
    st.markdown("""
    <div class='container-performance'>
        <p class='titulo-secao'>Métricas de Performance</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <table>
        <tr><th>Métrica</th><th>Valor</th></tr>
        <tr><td>Accuracy</td><td>{m.get('accuracy', 0):.4f}</td></tr>
        <tr><td>Precision</td><td>{m.get('precision', 0):.4f}</td></tr>
        <tr><td>Recall</td><td>{m.get('recall', 0):.4f}</td></tr>
        <tr><td>AUC (ROC)</td><td>{m.get('auc', 0):.4f}</td></tr>
        <tr><td>Gini</td><td>{m.get('gini', 0):.4f}</td></tr>
        <tr><td>KS Statistic</td><td>{m.get('ks', 0):.4f}</td></tr>
    </table>
    """, unsafe_allow_html=True)

    # ----- MATRIZ DE CONFUSÃO -----
    st.markdown("""
    <div class='container-performance'>
        <p class='titulo-secao' style='margin-top:25px;'>Matriz de Confusión</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <table class='cm-table'>
        <tr>
            <th>Real / Pred</th>
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
    """, unsafe_allow_html=True)

# ============================================
# TAB 3: PSI (ESTABILIDADE)
# ============================================
with tab3:
    psi_val = metricas_modelo.get("psi", 0)
    
    if psi_val < 0.1:
        status, cor, icon = "ESTABLE", "#16a34a", "✅"
    elif psi_val < 0.25:
        status, cor, icon = "ALERTA", "#facc15", "⚠️"
    else:
        status, cor, icon = "INESTABLE", "#dc2626", "🚨"

    st.markdown(f"""
    <div class='container-performance'>
        <p class='titulo-secao'>Estabilidad de la Población</p>
        <div class='psi-card'>
            <p style='font-size:13px; color:#64748b; margin-bottom:5px;'>Índice PSI</p>
            <div class='score' style='color:{cor};'>{psi_val:.4f}</div>
            <p style='color:{cor}; font-weight:700; font-size:20px; margin-top:10px;'>{icon} {status}</p>
            <div style='margin-top:20px; padding:10px; background:#f8fafc; border-radius:8px;'>
                <p style='font-size:11px; color:#475569; line-height:1.4;'>
                    <b>Guía:</b><br>
                    • < 0.10: Estable<br>
                    • 0.10 - 0.25: Alerta<br>
                    • > 0.25: Inestable
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)