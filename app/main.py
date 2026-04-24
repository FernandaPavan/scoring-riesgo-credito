import sys
import os
import streamlit as st
import plotly.graph_objects as go

# 1. AJUSTE DE PATH (Garante que o Python localize a pasta 'src')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# 2. IMPORTAÇÃO DOS MÓDULOS MODULARIZADOS
from src.loader import load_assets
from src.policy import get_score, apply_business_policy
from src.features import traduzir_inputs, montar_entrada, preparar_dados
from app.styles import apply_custom_styles

# ============================================
# CONFIGURACIÓN E CARREGAMENTO
# ============================================
st.set_page_config(layout="wide", page_title="Credit Score App")

# Carrega modelo, bins, métricas e parâmetros
modelo, bins_woe, metricas_modelo, score_params, cutoffs = load_assets()

# Aplica os estilos visuais (Sidebar, tabelas e cores)
apply_custom_styles()

# Título Principal da Aplicação
st.markdown("<h1 style='text-align:center;color:#2563eb;font-size:24px;font-weight:700;'>Evaluación de Riesgo y Score de Crédito</h1>", unsafe_allow_html=True)

# Definição das Abas
tab1, tab2, tab3 = st.tabs(["Simulación de Crédito", "Desempeño del Modelo", "Estabilidad (PSI)"])

# ============================================
# TAB 1: SIMULACIÓN DE CRÉDITO
# ============================================
with tab1:
    with st.sidebar:
        st.markdown("<div style='text-align:center;color:#2563eb;font-size:12px;font-weight:600;margin-bottom:5px;'>Datos del Cliente</div>", unsafe_allow_html=True)
        
        # Sliders de entrada numérica
        edad = st.slider("Edad", 18, 75, 30)
        monto = st.slider("Monto del Crédito", 250, 20000, 5000, step=250)
        duracion = st.slider("Duración (meses)", 4, 72, 24)

        # Selectboxes (Interface em Espanhol)
        # Os nomes das variáveis terminam em '_sel' para indicar que é a seleção bruta da UI
        genero_sel = st.selectbox("Género", ["Masculino", "Femenino"])
        trabalho_sel = st.selectbox("Ocupación", ["Desempleado", "Básico", "Calificado", "Especialista"])
        vivienda_sel = st.selectbox("Vivienda", ["Propia", "Alquilada", "Gratuita"])
        ahorro_sel = st.selectbox("Cuenta de Ahorro", ["Bajo", "Medio", "Alto"])
        corriente_sel = st.selectbox("Cuenta Corriente", ["Bajo", "Medio", "Alto"])
        finalidad_sel = st.selectbox("Finalidad", ["Auto", "Muebles", "Electrónicos", "Negocios", "Educación", "Reparaciones", "Otros"])

        btn = st.button("Calcular")

    # Colunas para exibir o resultado e o gráfico lado a lado
    col_res, col_graf = st.columns([1, 1])

    if btn:
        # 1. Tradução: Converte "Masculino" -> "male", "Básico" -> 1, etc.
        genero, trabajo, vivienda, ahorro, corriente, finalidad = traduzir_inputs(
            genero_sel, trabalho_sel, vivienda_sel, ahorro_sel, corrente_sel, finalidad_sel
        )
        
        # 2. DataFrame: Monta os dados no formato que o modelo espera
        entrada = montar_entrada(
            genero, trabajo, vivienda, ahorro, corriente, finalidad, 
            edad, duracion, monto
        )
        
        # 3. Pré-processamento: Aplica Faixas e transformação WOE
        entrada_woe = preparar_dados(entrada, bins_woe, modelo)

        # 4. Predição: Calcula probabilidade e Score final
        prob = modelo.predict_proba(entrada_woe)[0][1]
        score = get_score(prob, score_params)
        
        # 5. Política: Aplica regras de aprovação e limite
        res = apply_business_policy(score, prob, monto, cutoffs)

        # --- EXIBIÇÃO DOS RESULTADOS ---
        with col_res:
            st.markdown("<div class='titulo-secao'>Resultado</div><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='score' style='color:{res['cor']};'>{res['score']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:18px;font-weight:700;color:#2563eb;'>{res['segmento']}</p>", unsafe_allow_html=True)
            
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Probabilidad</p><p style='text-align:center;font-size:22px;font-weight:700;'>{prob:.2%}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;margin-bottom:0;font-size:14px;'>Límite Sugerido</p><p style='text-align:center;font-size:22px;font-weight:700;'>${res['limite']:,.0f}</p>", unsafe_allow_html=True)
            
            st.markdown(f"<div style='text-align:center;font-size:28px;color:{res['cor']};font-weight:900;'>{res['icon']} {res['status']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;font-size:12px;color:#64748b;padding:0 20px;'>{res['motivo']}</p>", unsafe_allow_html=True)

        with col_graf:
            st.markdown("<div class='titulo-secao'>Indicador de Riesgo</div><br>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number", 
                value=prob*100, 
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
            fig.update_layout(height=260, margin=dict(l=30, r=30, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: DESEMPEÑO DEL MODELO
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
            <tr><th>Real \\ Pred</th><th>Bueno (0)</th><th>Malo (1)</th></tr>
            <tr><td>Bueno (0)</td><td class='val-pos'>{cm['TN']}</td><td class='val-neg'>{cm['FP']}</td></tr>
            <tr><td>Malo (1)</td><td class='val-neg'>{cm['FN']}</td><td class='val-pos'>{cm['TP']}</td></tr>
        </table>
    </div>""", unsafe_allow_html=True)

# ============================================
# TAB 3: ESTABILIDAD (PSI)
# ============================================
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