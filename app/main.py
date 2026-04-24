import streamlit as st
import plotly.graph_objects as go

from loader import load_assets
from features import build_input, apply_woe
from policy import calcular_score, aplicar_penalidades, classificar, decisao_final
from styles import load_css

# CONFIG
st.set_page_config(layout="wide", page_title="Credit Score App")

# LOAD
modelo, bins_woe, metricas, params = load_assets()

# STYLE
st.markdown(load_css(), unsafe_allow_html=True)

# HEADER
st.title("Evaluación de Riesgo y Score de Crédito")

tab1, tab2, tab3 = st.tabs(["Simulación", "Modelo", "PSI"])

# ============================================
# TAB 1
# ============================================
with tab1:
    with st.sidebar:
        idade = st.slider("Edad", 18, 75, 30)
        valor = st.slider("Monto", 250, 20000, 5000)
        duracion = st.slider("Duración", 4, 72, 24)

        genero = st.selectbox("Género", ["male", "female"])
        trabalho = st.selectbox("Trabajo", [0,1,2,3])
        habitacion = st.selectbox("Vivienda", ["own","rent","free"])
        poupanca = st.selectbox("Ahorro", ["little","moderate","rich"])
        corrente = st.selectbox("Corriente", ["little","moderate","rich"])
        finalidade = st.selectbox("Finalidad", ["car","business","education"])

        btn = st.button("Calcular")

    if btn:
        entrada = build_input({
            "Genero":[genero],
            "Trabalho":[trabalho],
            "Habitacao":[habitacion],
            "Conta_poupanca":[poupanca],
            "Conta_corrente":[corrente],
            "Finalidade":[finalidade],
            "Idade":[idade],
            "Duracao":[duracion],
            "Valor_credito":[valor]
        })

        entrada_woe = apply_woe(entrada, bins_woe, modelo)

        prob = modelo.predict_proba(entrada_woe)[0][1]

        score = calcular_score(prob, params)

        score, mult = aplicar_penalidades(
            score, trabalho, habitacion, poupanca, corrente
        )

        segmento, limite_base = classificar(score)
        limite = int(limite_base * mult)

        status, icon, cor, motivo = decisao_final(
            score, limite, valor, trabalho, corrente
        )

        st.metric("Score", score)
        st.metric("Probabilidade", f"{prob:.2%}")
        st.metric("Limite", limite)
        st.write(status, motivo)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob*100
        ))
        st.plotly_chart(fig)

# ============================================
# TAB 2
# ============================================
with tab2:
    st.write(metricas)

# ============================================
# TAB 3
# ============================================
with tab3:
    st.write("PSI:", metricas.get("psi", 0))