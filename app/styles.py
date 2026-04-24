import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }

    [data-testid="stSidebar"] .stWidgetLabel p {
        font-size: 10px !important;
        font-weight: 600 !important;
        margin-bottom: -15px !important;
        color: #4b5563;
    }

    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        font-size: 11px !important;
    }

    [data-testid="stSidebar"] .stSlider div {
        font-size: 11px !important;
    }

    div.stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 6px;
        width: 100%;
        font-size: 12px;
    }

    .titulo-secao {
        text-align: center;
        color: #2563eb;
        font-size: 18px;
        font-weight: 700;
    }

    .score {
        text-align: center;
        font-size: 40px;
        font-weight: 700;
    }

    table {
        margin-left: auto;
        margin-right: auto;
        font-size: 13px;
        text-align: center;
        border-collapse: collapse;
        width: 450px;
    }

    th {
        background-color: #2563eb;
        color: white;
        padding: 8px;
    }

    td {
        padding: 8px;
        border-bottom: 1px solid #eee;
    }

    .val-pos {
        color: #16a34a;
        font-weight: 800;
    }

    .val-neg {
        color: #dc2626;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)