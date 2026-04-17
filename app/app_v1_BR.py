import streamlit as st 
import pandas as pd
import joblib
import plotly.graph_objects as go
import os
import sys
import time

# ============================================
# CORREÇÃO DO PATH
# ============================================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

from src.features import criar_faixas

# ============================================
# CONFIG
# ============================================
st.set_page_config(layout="wide")

# ============================================
# CSS
# ============================================
st.markdown("""
<style>

.stApp {
    background-color: #eef2f7;
}

.block-container {
    padding-top: 1rem;
}

.secao {
    text-align:center;
    color:#2563eb;
    font-size:22px;
    font-weight:600;
    margin-bottom:10px;
}

.score {
    text-align:center;
    font-size:72px;
    font-weight:700;
}

div.stButton > button {
    background-color:#2563eb;
    color:white;
    border-radius:10px;
    height:45px;
    width:100%;
    font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# ============================================
# MODELO
# ============================================
model_path = os.path.join(BASE_PATH, "models", "modelo.pkl")
model = joblib.load(model_path)

# ============================================
# HEADER (TÍTULO FINAL)
# ============================================
st.markdown("""
<br>

<h1 style='text-align:center; color:#2563eb; font-size:42px; font-weight:700;'>
Avaliação de Risco e Score de Crédito
</h1>

<br><br>
""", unsafe_allow_html=True)

# ============================================
# LAYOUT
# ============================================
col1, col2, col3 = st.columns(3)

# ============================================
# COLUNA 1 — INPUTS
# ============================================
with col1:

    st.markdown("<div class='secao'>Dados do Cliente</div>", unsafe_allow_html=True)

    idade = st.slider("Idade", 18, 75, 30)
    valor = st.number_input("Valor do Crédito", 250, 20000, 5000)
    duracao = st.slider("Duração (meses)", 4, 72, 24)

    genero_map = {"Masculino": "male", "Feminino": "female"}
    genero = genero_map[st.selectbox("Gênero", list(genero_map.keys()))]

    trabalho_map = {
        "Desempregado": 0,
        "Básico": 1,
        "Qualificado": 2,
        "Especialista": 3
    }
    trabalho = trabalho_map[st.selectbox("Trabalho", list(trabalho_map.keys()))]

    habitacao_map = {
        "Própria": "own",
        "Alugada": "rent",
        "Gratuita": "free"
    }
    habitacao = habitacao_map[st.selectbox("Habitação", list(habitacao_map.keys()))]

    conta_opcoes = {
        "Baixo": "little",
        "Médio": "moderate",
        "Alto": "rich"
    }

    conta_poupanca = conta_opcoes[
        st.selectbox("Saldo em Conta Poupança", list(conta_opcoes.keys()))
    ]

    conta_corrente = conta_opcoes[
        st.selectbox("Saldo em Conta Corrente", list(conta_opcoes.keys()))
    ]

    finalidade_map = {
        "Carro": "car",
        "Móveis/Equipamentos": "furniture/equipment",
        "Eletrônicos": "radio/TV",
        "Negócios": "business",
        "Educação": "education",
        "Reparos": "repairs",
        "Outros": "vacation/others"
    }
    finalidade = finalidade_map[
        st.selectbox("Finalidade do Crédito", list(finalidade_map.keys()))
    ]

# ============================================
# BOTÃO
# ============================================
if st.button("Calcular"):

    entrada = pd.DataFrame({
        "Genero":[genero],
        "Trabalho":[trabalho],
        "Habitacao":[habitacao],
        "Conta_poupanca":[conta_poupanca],
        "Conta_corrente":[conta_corrente],
        "Finalidade":[finalidade],
        "Idade":[idade],
        "Duracao":[duracao],
        "Valor_credito":[valor]
    })

    prob = model.predict_proba(entrada)[0][1]
    score = int(850 - (prob * 550))

    # ============================================
    # COLUNA 2 — RESULTADO
    # ============================================
    with col2:

        st.markdown("<div class='secao'>Resultado da Análise</div><br>", unsafe_allow_html=True)

        score_placeholder = st.empty()

        for i in range(300, score, 15):
            score_placeholder.markdown(
                f"<div class='score'>{i}</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.01)

        score_placeholder.markdown(
            f"<div class='score'>{score}</div>",
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <p style='text-align:center; font-size:20px;'>Probabilidade de Risco</p>
        <p style='text-align:center; font-size:36px; font-weight:bold;'>{prob:.2%}</p>
        <br><br>
        """, unsafe_allow_html=True)

        # ============================================
        # STATUS COM ÍCONES
        # ============================================
        if score >= 700:
            status = "✔ APROVADO"
            cor = "#16a34a"

        elif score >= 600:
            status = "⚠ EM ANÁLISE"
            cor = "#facc15"

        else:
            status = "✖ REPROVADO"
            cor = "#dc2626"

        st.markdown(f"""
        <div style='text-align:center; margin-top:20px;'>
            <span style='
                color:{cor};
                font-size:36px;
                font-weight:700;
                letter-spacing:1px;
            '>
                {status}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ============================================
    # COLUNA 3 — INDICADOR
    # ============================================
    with col3:

        st.markdown("<div class='secao'>Indicador de Risco</div>", unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            number={'font': {'size': 30}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#111"},
                'steps': [
                    {'range': [0, 40], 'color': "#16a34a"},
                    {'range': [40, 70], 'color': "#facc15"},
                    {'range': [70, 100], 'color': "#dc2626"}
                ],
            }
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True)