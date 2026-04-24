import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    /* Configuração Geral */
    .block-container { padding-top: 1rem !important; }

    /* SIDEBAR ULTRA COMPACTA */
    [data-testid="stSidebar"] .stWidgetLabel p {
        font-size: 10px !important;
        font-weight: 600 !important;
        margin-bottom: -15px !important; 
        padding-bottom: 0px !important;
        color: #4b5563;
    }

    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMin"],
    [data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMax"],
    [data-testid="stSidebar"] .stSlider div[role="slider"] {
        font-size: 12px !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        margin-bottom: -12px !important;
    }

    [data-testid="stSidebar"] [data-testid="stSlider"] {
        padding-top: 0px !important;
        margin-top: -10px !important;
    }

    div.stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 600;
        border-radius: 6px;
        height: 30px;
        width: 90% !important;
        margin-left: 5%;
        margin-top: 15px;
        font-size: 11px;
    }

    /* CONTAINER CENTRAL */
    .container-performance {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        gap: 15px;
    }

    .titulo-secao { 
        text-align: center; 
        color: #2563eb; 
        font-size: 18px; 
        font-weight: 700;
        margin-bottom: 10px;
    }

    .score { 
        text-align: center; 
        font-size: 40px; 
        font-weight: 700;
        color: #1e40af;
    }

    /* 🔥 TABELA PADRÃO - Melhorado para Streamlit */
    table {
        margin-left: auto;
        margin-right: auto;
        border-collapse: collapse;
        width: 450px !important;
        font-size: 14px;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-radius: 8px;
        overflow: hidden;
    }

    th {
        background-color: #2563eb;
        color: white !important;
        padding: 12px;
        font-weight: 700;
        text-align: center;
    }

    td {
        padding: 10px;
        border-bottom: 1px solid #eee;
        font-weight: 600;
        text-align: center;
        color: #374151;
    }

    /* Alinhamento da primeira coluna de métricas */
    table tr td:first-child {
        text-align: left;
        padding-left: 20px;
        color: #4b5563;
    }

    /* 🔥 MATRIZ DE CONFUSÃO (DESTAQUE REAL) */
    .val-pos { 
        background-color: #dcfce7 !important;
        color: #166534 !important; 
        font-weight: 900 !important;
    }

    .val-neg { 
        background-color: #fee2e2 !important;
        color: #991b1b !important; 
        font-weight: 900 !important;
    }

    /* CARD PSI */
    .psi-card {
        text-align: center; 
        border: 1px solid #e2e8f0; 
        padding: 20px; 
        border-radius: 12px; 
        width: 320px;
        background-color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 10px auto;
    }

    </style>
    """, unsafe_allow_html=True)