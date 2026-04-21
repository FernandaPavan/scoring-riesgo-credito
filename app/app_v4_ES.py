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
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_PATH, "models")

# ============================================
# LOAD
# ============================================
# Carregamento com tratamento de erro básico
try:
    modelo = joblib.load(os.path.join(MODEL_PATH, "modelo.pkl"))
    bins_woe = joblib.load(os.path.join(MODEL_PATH, "woe_bins.pkl"))

    with open(os.path.join(MODEL_PATH, "metricas.json"), "r") as f:
        metricas_modelo = json.load(f)

    with open(os.path.join(MODEL_PATH, "score_params.json"), "r") as f:
        score_params = json.load(f)
except Exception as e:
    st.error(f"Error al cargar archivos del modelo: {e}")
    st.stop()

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide", page_title="Credit Scoring App")

# ============================================
# CSS
# ============================================
st.markdown("""
<style>
.seccion{ text-align:center; color:#2563eb; font-size:20px; font-weight:600; }
.score{ text-align:center; font-size:60px; font-weight:700; line-height:1; margin:10px 0; }
div.stButton > button {
    background-color: #2563eb; color: white; font-weight: 600; border-radius: 8px; height: 45px; width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:32px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1><br>", unsafe_allow_html=True)

# ============================================
# TABS
# ============================================
tab1, tab2 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo"])

# ============================================
# TAB 1: SIMULACIÓN
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div class='seccion'>Datos del Cliente</div>", unsafe_allow_html=True)
        
        edad = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        genero_map = {"Masculino": "male", "Femenino": "female"}
        genero = genero_map[st.selectbox("Género", list(genero_map.keys()))]

        trabajo_map = {"Desempleado": 0, "Básico": 1, "Calificado": 2, "Especialista": 3}
        trabalho = trabajo_map[st.selectbox("Ocupación", list(trabajo_map.keys()))]

        habitacion_map = {"Propia": "own", "Alquilada": "rent", "Gratuita": "free"}
        habitacion = habitacion_map[st.selectbox("Vivienda", list(habitacion_map.keys()))]

        conta_map = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}
        cuenta_ahorro = conta_map[st.selectbox("Cuenta de Ahorro", list(conta_map.keys()))]
        cuenta_corriente = conta_map[st.selectbox("Cuenta Corriente", list(conta_map.keys()))]

        finalidade_map = {
            "Auto": "car", "Muebles": "furniture/equipment", "Electrónicos": "radio/TV",
            "Negocios": "business", "Educación": "education", "Reparaciones": "repairs", "Otros": "vacation/others"
        }
        finalidad = finalidade_map[st.selectbox("Finalidad del Crédito", list(finalidade_map.keys()))]

        btn = st.button("Calcular")

    col2, col3 = st.columns([1, 1])

    if btn:
        # Preparación de datos
        entrada = pd.DataFrame({
            "Genero": [genero], "Trabalho": [trabalho], "Habitacao": [habitacion],
            "Conta_poupanca": [cuenta_ahorro], "Conta_corrente": [cuenta_corriente],
            "Finalidade": [finalidad], "Idade": [edad], "Duracao": [duracion], "Valor_credito": [valor]
        })

        # Predicción
        entrada_woe = sc.woebin_ply(entrada, bins_woe)
        entrada_woe = entrada_woe.reindex(columns=modelo.feature_names_in_, fill_value=0)
        
        prob = modelo.predict_proba(entrada_woe)[0][1]
        prob = min(max(prob, 0.0001), 0.9999)

        # Cálculo de Score Base
        odds = (1 - prob) / prob
        factor = score_params["pdo"] / np.log(2)
        offset = (score_params["base_score"] + factor * np.log(score_params["base_odds"]))
        score_inicial = int(offset + factor * np.log(odds))

        # ============================================
        # POLICY LAYER (REGRAS DE NEGÓCIO)
        # ============================================
        penalidade_score = 0
        penalidade_limite = 1.0
        flags_risco = []

        if trabalho == 0:
            penalidade_score -= 80
            penalidade_limite *= 0.5
            flags_risco.append("Sin empleo")
        if habitacion == "rent":
            penalidade_score -= 30
            penalidade_limite *= 0.85
            flags_risco.append("Alquiler")
        if cuenta_ahorro == "little":
            penalidade_score -= 25
            penalidade_limite *= 0.9
            flags_risco.append("Bajo ahorro")

        score_ajustado = max(score_inicial + penalidade_score, 300)
        
        # Límite inicial basado en Score Ajustado
        if score_ajustado >= 700: segmento, limite = "SUPER PRIME", 18000
        elif score_ajustado >= 650: segmento, limite = "PRIME", 10000
        elif score_ajustado >= 600: segmento, limite = "STANDARD", 5000
        elif score_ajustado >= 520: segmento, limite = "NEAR PRIME", 2500
        elif score_ajustado >= 460: segmento, limite = "REVIEW", 1000
        else: segmento, limite = "SUBPRIME", 0

        # Aplicar penalidad de límite y plazo
        if duracion > 48: limite *= 0.85
        elif duracion > 36: limite *= 0.92
        limite = int(limite * penalidade_limite)

        # Decisión Final
        if score_ajustado < 460:
            status, icon, cor = "RECHAZADO", "✖", "#dc2626"
            motivo = "Score insuficiente para política de riesgo."
        elif score_ajustado < 520:
            status, icon, cor = "EN ANÁLISIS", "⚠", "#facc15"
            motivo = "Zona de riesgo moderado. Requiere comprobación manual."
        else:
            if valor <= limite:
                status, icon, cor = "APROBADO", "✔", "#16a34a"
                motivo = "Monto aprobado bajo política automática."
            elif valor <= limite * 1.2:
                status, icon, cor = "EN ANÁLISIS", "⚠", "#facc15"
                motivo = "Monto excede ligeramente el límite sugerido."
            else:
                status, icon, cor = "RECHAZADO", "✖", "#dc2626"
                motivo = "Monto solicitado muy superior al límite de riesgo."

        if flags_risco:
            motivo += f" (Factores: {', '.join(flags_risco)})"

        with col2:
            st.markdown("<div class='seccion'>Resultado del Análisis</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{cor};'>{score_ajustado}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:22px;font-weight:700;'>{segmento}</p>", unsafe_allow_html=True)
            st.write("---")
            st.markdown(f"<p style='text-align:center;'>Probabilidad de Riesgo: <b>{prob:.2%}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'>Límite Sugerido: <b>${limite:,.0f}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;margin-top:20px;font-size:38px;font-weight:900;color:{cor};'>{icon} {status}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;color:#4b5563;'>{motivo}</p>", unsafe_allow_html=True)

        with col3:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=prob*100,
                title={'text': "Índice de Riesgo (%)"},
                gauge={'axis': {'range': [0, 100]},
                       'steps': [{'range': [0, 30], 'color': "#16a34a"},
                                 {'range': [30, 70], 'color': "#facc15"},
                                 {'range': [70, 100], 'color': "#dc2626"}],
                       'bar': {'color': "black"}}))
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: MÉTRICAS (CORRIGIDO)
# ============================================
with tab2:
    st.markdown("<h2 style='text-align:center;color:#2563eb;'>Desempeño del Modelo</h2>", unsafe_allow_html=True)
    
    # Tabela de Métricas
    m = metricas_modelo
    df_m = pd.DataFrame({
        "Métrica": ["Accuracy", "Precisión", "Recall", "AUC", "Gini", "KS"],
        "Valor": [m.get("accuracy",0), m.get("precision",0), m.get("recall",0), m.get("auc",0), m.get("gini",0), m.get("ks",0)]
    })
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.table(df_m.style.format({"Valor": "{:.4f}"}))

    # Matriz de Confusão Corrigida
    with col_b:
        cm = m.get("confusion_matrix", {"TN": 0, "FP": 0, "FN": 0, "TP": 0})
        st.markdown(f"""
        <table style='width:100%; text-align:center; border-collapse:collapse; border:1px solid #ddd;'>
            <tr style='background-color:#2563eb; color:white;'>
                <th>Real \ Pred</th><th>Bom (0)</th><th>Ruim (1)</th>
            </tr>
            <tr>
                <td style='font-weight:bold; background-color:#f3f4f6;'>Bom (0)</td>
                <td style='color:#16a34a; font-weight:700;'>{cm['TN']}<br><small>TN</small></td>
                <td style='color:#dc2626; font-weight:700;'>{cm['FP']}<br><small>FP</small></td>
            </tr>
            <tr>
                <td style='font-weight:bold; background-color:#f3f4f6;'>Ruim (1)</td>
                <td style='color:#dc2626; font-weight:700;'>{cm['FN']}<br><small>FN</small></td>
                <td style='color:#16a34a; font-weight:700;'>{cm['TP']}<br><small>TP</small></td>
            </tr>
        </table>
        """, unsafe_allow_html=True)