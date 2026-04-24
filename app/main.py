import sys
import os

# Garante que o Python encontre a pasta 'src'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import streamlit as st
import plotly.graph_objects as go

from src.loader import load_assets
from src.policy import get_score, apply_business_policy
from src.features import traduzir_inputs, montar_entrada, preparar_dados
from app.styles import apply_custom_styles

# Configuração da Página
st.set_page_config(layout="wide", page_title="Credit Score App")

# Carregamento de Ativos (Modelos, Bins, Métricas)
@st.cache_resource
def load_all():
    return load_assets()

modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_all()

# Aplica o CSS do styles.py
apply_custom_styles()

st.markdown("<h1 style='text-align:center;color:#2563eb;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

with tab1:
    with st.sidebar:
        st.markdown("### Datos del Cliente")
        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero_sel = st.selectbox("Género", ["Masculino", "Femenino"])
        trabajo_sel = st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])
        vivienda_sel = st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])
        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo", "Medio", "Alto"])
        corriente_sel = st.selectbox("Cuenta Corriente", ["Bajo", "Medio", "Alto"])
        finalidad_sel = st.selectbox("Finalidad", ["Auto", "Muebles", "Electrónicos", "Negocios", "Educación", "Reparaciones", "Otros"])

        btn = st.button("Calcular Score")

    col_res, col_graf = st.columns([1, 1])

    if btn:
        # Tradução: UI (Espanhol) -> Modelo (Valores Internos)
        genero, trabajo, vivienda, ahorro, corriente, finalidad = traduzir_inputs(
            genero_sel, trabajo_sel, vivienda_sel, ahorro_sel, corriente_sel, finalidad_sel
        )

        # Montagem do DataFrame com nomes de colunas que o modelo espera
        entrada = montar_entrada(
            genero, trabajo, vivienda, ahorro, corriente, 
            finalidad, edad, duracion, monto
        )

        # Transformação WOE e Alinhamento de colunas
        entrada_woe = preparar_dados(entrada, bins_woe, modelo)

        # Predição
        prob = modelo.predict_proba(entrada_woe)[0][1]
        score = get_score(prob, score_params)
        decision = apply_business_policy(score, prob, monto, cutoffs)

        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{decision['cor']};'>{decision['score']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-weight:700;color:#2563eb;'>{decision['segmento']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'>Probabilidad de Impago: <b>{prob:.2%}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'>Límite Sugerido: <b>${decision['limite']:,.0f}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:26px;color:{decision['cor']};'>{decision['icon']} {decision['status']}</div>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'suffix': "%"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "steps": [
                        {"range": [0, 30], "color": "#16a34a"},
                        {"range": [30, 60], "color": "#facc15"},
                        {"range": [60, 100], "color": "#dc2626"}
                    ],
                }
            ))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)

# Abas de métricas seguem conforme o código anterior...

# ============================================
# ============================================
# TAB 2 - MÉTRICAS (DESEMPEÑO)
# ============================================
with tab2:
    st.markdown("<p class='titulo-azul-centrado'>Desempeño del Modelo</p>", unsafe_allow_html=True)
    
    m = metricas_modelo
    cm = m.get("confusion_matrix", {"TN":0,"FP":0,"FN":0,"TP":0})

    # Centralizando as tabelas
    st.markdown(f"""
    <div class='centrar-conteudo'>
        <table>
            <tr><th>Métrica</th><th>Valor</th></tr>
            <tr><td>Accuracy</td><td>{m['accuracy']:.4f}</td></tr>
            <tr><td>Precision</td><td>{m['precision']:.4f}</td></tr>
            <tr><td>Recall</td><td>{m['recall']:.4f}</td></tr>
            <tr><td>AUC</td><td>{m['auc']:.4f}</td></tr>
            <tr><td>Gini</td><td>{m['gini']:.4f}</td></tr>
            <tr><td>KS</td><td>{m['ks']:.4f}</td></tr>
        </table>

        <p class='titulo-secao' style='margin-top:30px;'>Matriz de Confusión</p>

        <table>
            <tr>
                <th>Real \\ Pred</th>
                <th>Bueno (0)</th>
                <th>Malo (1)</th>
            </tr>
            <tr>
                <td>Bueno (0)</td>
                <td class='val-pos'>{cm['TN']}</td>
                <td class='val-neg'>{cm['FP']}</td>
            </tr>
            <tr>
                <td>Malo (1)</td>
                <td class='val-neg'>{cm['FN']}</td>
                <td class='val-pos'>{cm['TP']}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TAB 3 - PSI (ESTABILIDAD)
# ============================================
with tab3:
    st.markdown("<p class='titulo-azul-centrado'>Estabilidad del Modelo</p>", unsafe_allow_html=True)
    
    psi = metricas_modelo.get("psi", 0)

    # Lógica de Cores e Labels
    if psi < 0.1:
        classe_card = "estavel"
        status_texto = "ESTABLE"
    elif psi < 0.25:
        classe_card = "alerta"
        status_texto = "ALERTA"
    else:
        classe_card = "instavel"
        status_texto = "INESTABLE"

    # Renderização do Card Centralizado
    st.markdown(f"""
    <div class='centrar-conteudo'>
        <div class='card-psi {classe_card}'>
            <p style='margin:0; font-size:14px; font-weight:bold;'>PSI</p>
            <p style='margin:10px 0; font-size:48px; font-weight:800;'>{psi:.4f}</p>
            <p style='margin:0; font-size:18px; font-weight:700;'>↑ {status_texto}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)