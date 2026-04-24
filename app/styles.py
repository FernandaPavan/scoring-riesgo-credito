import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>

    /* ============================= */
    /* 🎨 DESIGN SYSTEM              */
    /* ============================= */
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary: #1e40af;
        --success: #16a34a;
        --warning: #facc15;
        --danger: #dc2626;

        --text-main: #111827;
        --text-light: #6b7280;

        --bg-light: #f9fafb;
        --border: #e5e7eb;

        --radius: 12px;
        --shadow-sm: 0 2px 6px rgba(0,0,0,0.05);
        --shadow-md: 0 6px 12px rgba(0,0,0,0.08);
    }

    /* ============================= */
    /* 🌐 GLOBAL                     */
    /* ============================= */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    .block-container { 
        padding-top: 1.5rem !important; 
        font-family: 'Inter', sans-serif;
    }

    /* ============================= */
    /* 📌 SIDEBAR                   */
    /* ============================= */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
    }

    [data-testid="stSidebar"] .stWidgetLabel p {
        font-size: 11px !important;
        font-weight: 700 !important;
        margin-bottom: -10px !important; 
        color: var(--text-light);
    }

    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        min-height: 32px !important;
        font-size: 13px !important;
        border-radius: 6px;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.6rem !important;
    }

    /* ============================= */
    /* 🔘 BOTÃO                     */
    /* ============================= */
    div.stButton > button {
        background-color: var(--primary) !important;
        color: white !important;
        font-weight: 700;
        border-radius: 8px;
        height: 38px;
        width: 100% !important;
        margin-top: 12px;
        border: none;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    
    div.stButton > button:hover {
        background-color: var(--primary-dark) !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    /* ============================= */
    /* 📦 CONTAINER CENTRAL         */
    /* ============================= */
    .container-performance {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        gap: 12px;
        padding: 12px 0;
    }

    .titulo-secao { 
        text-align: center; 
        color: var(--secondary); 
        font-size: 18px; 
        font-weight: 700;
    }

    .score { 
        text-align: center; 
        font-size: 44px; 
        font-weight: 800;
        color: var(--secondary);
    }

    /* ============================= */
    /* 📊 TABELAS                   */
    /* ============================= */
    table {
        margin: 10px auto !important;
        width: 100%;
        max-width: 450px !important;
        font-size: 14px;
        background-color: white;
        border-radius: var(--radius);
        overflow: hidden;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
    }

    th {
        background-color: var(--primary);
        color: white !important;
        padding: 12px;
        font-size: 11px;
    }

    td {
        padding: 10px;
        border-bottom: 1px solid #f3f4f6;
    }

    /* ============================= */
    /* 🔲 MATRIZ                    */
    /* ============================= */
    .cm-table {
        max-width: 360px !important;
        margin: 10px auto !important;
        border-radius: 14px;
        box-shadow: var(--shadow-md);
    }

    /* ============================= */
    /* 📈 CARD PSI                  */
    /* ============================= */
    .psi-card {
        max-width: 360px;
        margin: 10px auto;
        padding: 25px;
        border-radius: 16px;
        background-color: white;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-md);
        text-align: center;
    }

    /* ============================= */
    /* 📂 EXPANDER (PERFEITO)       */
    /* ============================= */
    div[data-testid="stExpander"] {
        max-width: 600px !important;   /* 🔥 largura igual da imagem */
        margin: 25px auto !important;  /* 🔥 centralizado */
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        background-color: white !important;
        box-shadow: var(--shadow-sm) !important;
    }

    div[data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: var(--secondary) !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
    }

    /* Conteúdo interno */
    div[data-testid="stExpander"] .stMarkdown {
        padding: 15px 22px !important;
    }

    /* Texto */
    div[data-testid="stExpander"] p {
        font-size: 13.5px !important;
        color: #475569 !important;
        line-height: 1.6 !important;
        margin-bottom: 10px !important;
    }

    div[data-testid="stExpander"] li {
        font-size: 13.5px !important;
        margin-bottom: 6px !important;
        color: #334155 !important;
    }

    </style>
    """, unsafe_allow_html=True)