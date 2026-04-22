import streamlit as st
import os 
import sys
import pandas as pd
import numpy as np
import scorecardpy as sc
import plotly.graph_objects as go

# ============================================
# AJUSTE DE PATH PARA MODULARIZAÇÃO
# ============================================
# Permite que o app encontre a pasta 'src' na raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from styles import apply_custom_styles
from src.loader import load_assets
from src.policy import get_score, apply_business_policy

# ============================================
# CONFIGURAÇÃO INICIAL E ESTILOS
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App")

# Aplica o CSS (Verifique se o seu styles.py contém o CSS que te enviei)
apply_custom_styles()

# ============================================
# CARREGAMENTO DE ATIVOS (MODELOS E MÉTRICAS)
# ============================================
@st.cache_resource
def get_all_assets():
    # O loader.py resolve os caminhos automaticamente
    return load_assets()

modelo, bins_woe, metricas_modelo, score_params = get_all_assets()

# ============================================
# HEADER
# ============================================
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

# ============================================
# TAB 1: SIMULACIÓN (A INTERFACE FALA ESPANHOL)
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;margin-bottom:5px;'>Datos del Cliente</div>", unsafe_allow_html=True)
        
        # Variáveis em espanhol (Inputs do usuário)
        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)
        
        gen_sel = st.selectbox("Género", ["Masculino","Femenino"])
        genero = "male" if gen_sel == "Masculino" else "female"
        
        trab_sel = st.selectbox("Ocupación", ["Desempleado","Básico","Calificado","Especialista"])
        trabalho = {"Desempleado":0,"Básico":1,"Calificado":2,"Especialista":3}[trab_sel]
        
        hab_sel = st.selectbox("Vivienda", ["Propia","Alquilada","Gratuita"])
        habitacao = {"Propia":"own","Alquilada":"rent","Gratuita":"free"}[hab_sel]
        
        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo","Medio","Alto"])
        ahorro = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[ahorro_sel]
        
        corr_sel = st.selectbox("Cuenta Corriente", ["Bajo","Medio","Alto"])
        corriente = {"Bajo":"little","Medio":"moderate","Alto":"rich"}[corr_sel]
        
        fin_sel = st.selectbox("Finalidad", ["Auto","Muebles","Electrónicos","Negocios","Educación","Reparaciones","Otros"])
        finalidade = {"Auto":"car","Muebles":"furniture/equipment","Electrónicos":"radio/TV","Negocios":"business","Educación":"education","Reparaciones":"repairs","Otros":"vacation/others"}[fin_sel]
        
        btn = st.button("Calcular")

    col_res, col_graf = st.columns([1, 1])
    
    if btn:
        # =========================================================================
        # PONTE DE TRADUÇÃO: O Modelo recebe nomes em Português
        # =========================================================================
        entrada = pd.DataFrame({
            "Genero": [genero],
            "Trabalho": [trabalho],
            "Habitacao": [habitacao],
            "Conta_poupanca": [ahorro],
            "Conta_corrente": [corriente],
            "Finalidade": [finalidade],
            "Idade": [edad],
            "Duracao": [duracion],
            "Valor_credito": [monto]
        })

        # Processamento WoE (Scorecardpy usa os nomes do DataFrame 'entrada')
        entrada_woe = sc.woebin_ply(entrada, bins_woe).reindex(columns=modelo.feature_names_in_, fill_value=0)
        
        # Probabilidade
        prob = modelo.predict_proba(entrada_woe)[0][1]
        
        # Cálculos de Score e Política (Chamando src/policy.py)
        score_base = get_score(prob, score_params)
        res = apply_business_policy(score_base, trabalho, habitacao, ahorro, corriente, monto)

        # Exibição (Layout Centralizado)
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{res['cor']};'>{res['score']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{res['segmento']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Probabilidad de Cumplimiento</p><p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Límite Sugerido</p><p style='text-align:center;font-size:22px;font-weight:700;'>${res['limite']:,.0f}</p>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:28px;color:{res['cor']};font-weight:900;'>{res['icon']} {res['status']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:12px;color:#64748b;padding:0 20px;'>{res['motivo']}</p>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div><br>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(mode="gauge+number", value=prob*100, number={'font': {'size': 45}, 'suffix': "%"},
                gauge={"axis":{"range":[0,100]},"steps":[{"range":[0,40],"color":"#16a34a"},{"range":[40,70],"color":"#facc15"},{"range":[70,100],"color":"#dc2626"}]}))
            fig.update_layout(height=260, margin=dict(l=30, r=30, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: DESEMPEÑO (ESTÁTICO DO JSON)
# ============================================
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
            <tr><th>Real \ Pred</th><th>Bom (1)</th><th>Mau (0)</th></tr>
            <tr><td>Bom (1)</td><td class='val-pos'>{cm['TP']}</td><td class='val-neg'>{cm['FN']}</td></tr>
            <tr><td>Mau (0)</td><td class='val-neg'>{cm['FP']}</td><td class='val-pos'>{cm['TN']}</td></tr>
        </table>
    </div>""", unsafe_allow_html=True)

# ============================================
# TAB 3: ESTABILIDADE (PSI)
# ============================================
with tab3:
    psi_v = metricas_modelo.get("psi", 0.00)
    psi_c = "#16a34a" if psi_v < 0.1 else "#facc15" if psi_v < 0.25 else "#dc2626"
    psi_s = "ESTÁVEL" if psi_v < 0.1 else "ALERTA" if psi_v < 0.25 else "INSTÁVEL"
    st.markdown(f"""
    <div class='container-performance'>
        <br><br><p class='titulo-secao'>Estabilidad del Modelo (PSI)</p><br>
        <div style='text-align:center; border:1px solid #e2e8f0; padding:20px; border-radius:12px; width:280px;'>
            <p style='font-size:11px; color:#64748b;'>PSI ACUMULADO</p>
            <h1 style='font-size:42px; color:{psi_c};'>{psi_v:.4f}</h1>
            <p style='color:{psi_c}; font-weight:800;'>{psi_s}</p>
        </div>
    </div>""", unsafe_allow_html=True)