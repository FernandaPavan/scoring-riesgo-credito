import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    /* Configuração Geral e Fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .block-container { 
        padding-top: 1.5rem !important; 
        font-family: 'Inter', sans-serif;
    }

    /* SIDEBAR ULTRA COMPACTA */
    [data-testid="stSidebar"] .stWidgetLabel p {
        font-size: 11px !important;
        font-weight: 700 !important;
        margin-bottom: -15px !important; 
        color: #4b5563;
    }

    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        min-height: 30px !important;
        font-size: 13px !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }

    /* Botão Principal */
    div.stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 700;
        border-radius: 8px;
        height: 35px;
        width: 100% !important;
        margin-top: 10px;
        border: none;
        transition: all 0.2s;
    }
    
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px);
    }

    /* CONTAINER CENTRAL */
    .container-performance {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        gap: 10px;
        padding: 10px 0;
    }

    .titulo-secao { 
        text-align: center; 
        color: #1e40af; 
        font-size: 18px; 
        font-weight: 700;
        margin-top: 5px;
    }

    .score { 
        text-align: center; 
        font-size: 42px; 
        font-weight: 800;
        color: #1e40af;
        line-height: 1;
    }

    /* 🔥 TABELAS ESTILIZADAS */
    table {
        margin: 10px auto;
        border-collapse: collapse;
        width: 100%;
        max-width: 480px !important;
        font-size: 14px;
        background-color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }

    th {
        background-color: #2563eb;
        color: white !important;
        padding: 12px 15px;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.05em;
    }

    td {
        padding: 12px 15px;
        border-bottom: 1px solid #f3f4f6;
        color: #374151;
    }

    table tr td:first-child {
        font-weight: 700;
        color: #4b5563;
        background-color: #f9fafb;
        width: 40%;
    }

    /* MATRIZ DE CONFUSÃO - CORES */
    .val-pos { 
        background-color: #dcfce7 !important;
        color: #166534 !important; 
        font-weight: 800 !important;
    }

    .val-neg { 
        background-color: #fee2e2 !important;
        color: #991b1b !important; 
        font-weight: 800 !important;
    }

    /* CARD PSI */
    .psi-card {
        text-align: center; 
        border: 1px solid #e5e7eb; 
        padding: 25px; 
        border-radius: 16px; 
        width: 100%;
        max-width: 350px;
        background-color: white;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin: 20px auto;
    }

    </style>
    """, unsafe_allow_html=True)