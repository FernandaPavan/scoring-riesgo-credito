import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
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

    /* RESULTADOS E TABELAS CENTRALIZADAS */
    .container-performance {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
    }

    .titulo-secao { text-align: center; color: #2563eb; font-size: 18px; font-weight: 700; }
    .score { text-align: center; font-size: 40px; font-weight: 700; }

    table { margin-left: auto; margin-right: auto; font-size: 13px; text-align: center; border-collapse: collapse; width: 450px; }
    th { background-color: #2563eb; color: white; padding: 8px; }
    td { padding: 8px; border-bottom: 1px solid #eee; }
    
    .val-pos { 
        color: #16a34a !important; 
        font-weight: 800; 
        background-color: #dcfce7 !important;
    }
    .val-neg { 
        color: #dc2626 !important; 
        font-weight: 800; 
        background-color: #fee2e2 !important;
    }

    /* CARD DE PSI */
    .psi-card {
        text-align: center; 
        border: 1px solid #e2e8f0; 
        padding: 20px; 
        border-radius: 12px; 
        width: 280px;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)