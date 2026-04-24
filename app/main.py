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

apply_custom_styles()

# ============================================
# CARREGAMENTO
# ============================================
@st.cache_resource
def load_all():
    return load_assets()

modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_all()

# ============================================
# HEADER
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
# TAB 1
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:14px;font-weight:700;margin-bottom:10px;'>DATOS DEL CLIENTE</div>", unsafe_allow_html=True)

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

    col_res, col_graf = st.columns(2)

    if btn:
        genero, trabalho, vivienda, ahorro, corriente, finalidad = traduzir_inputs(
            genero_sel, trabalho_sel, vivienda_sel, ahorro_sel, corriente_sel, finalidad_sel
        )

        entrada = montar_entrada(
            genero, trabalho, vivienda, ahorro, corriente, finalidad,
            edad, duracion, monto
        )

        entrada_woe = preparar_dados(entrada, bins_woe, modelo)

        prob = modelo.predict_proba(entrada_woe)[0][1]
        score_base = get_score(prob, score_params)

        penalidade = 0
        if trabalho == 0: penalidade -= 80
        if vivienda == "rent": penalidade -= 30

        score_final = max(score_base + penalidade, 300)

        decision = apply_business_policy(score_final, prob, monto, cutoffs)

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado del Análisis</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{decision['cor']};'>{decision['score']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-weight:700;font-size:18px;color:#1e40af;'>{decision['segmento']}</p>", unsafe_allow_html=True)

        with col_graf:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100
            ))
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# ============================================
# TAB 2: DESEMPENHO DO MODELO
# ============================================
with tab2:
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})

    # ----- TÍTULO GERAL -----
    st.markdown(
        "<div class='container-performance'>"
        "<p class='titulo-secao'>Desempeño del Modelo</p>"
        "</div>",
        unsafe_allow_html=True
    )

    # ----- TABELA DE MÉTRICAS -----
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

    # ----- ESPAÇO -----
    st.markdown("<br>", unsafe_allow_html=True)

    # ----- TÍTULO MATRIZ -----
    st.markdown(
        "<div class='container-performance'>"
        "<p class='titulo-secao'>Matriz de Confusión</p>"
        "</div>",
        unsafe_allow_html=True
    )

    # ----- MATRIZ DE CONFUSÃO (APENAS UMA VEZ) -----
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

    # ----- CARD PRINCIPAL -----
    st.markdown(f"""
    <div class='container-performance'>
        <p class='titulo-secao'>Estabilidad de la Población</p>
        <div class='psi-card'>
            <p style='font-size:13px; color:#64748b; margin-bottom:5px;'>Índice PSI</p>
            <div class='score' style='color:{cor};'>{psi_val:.4f}</div>
            <p style='color:{cor}; font-weight:700; font-size:20px; margin-top:10px;'>
                {icon} {status}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ----- ESPAÇO ENTRE CARD E EXPANDER -----
    st.markdown("<br>", unsafe_allow_html=True)

    # ----- CONTAINER CENTRALIZADO -----
    st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)
    st.markdown("<div style='width:100%; max-width:360px;'>", unsafe_allow_html=True)

    # ----- EXPANDER (AGORA CORRETO) -----
    with st.expander("Ver criterios del PSI"):
        st.markdown("""
        **Interpretación del Índice PSI (Population Stability Index):**
        
        - **< 0.10** → Población estable  
        - **0.10 – 0.25** → Posible cambio (alerta)  
        - **> 0.25** → Cambio significativo (inestabilidad)  
        
        **Lectura práctica:**
        - Un PSI bajo indica que la distribución de la población actual es similar a la utilizada en el entrenamiento  
        - Un PSI elevado sugiere un cambio en el perfil de los clientes (data drift), lo que puede afectar el desempeño del modelo  
        """)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)