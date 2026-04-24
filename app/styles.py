import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>

    /* ============================= */
    /* 🎨 DESIGN SYSTEM (VARIÁVEIS)  */
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
    /* 🔘 BOTÃO PRINCIPAL           */
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
    /* 📦 CONTAINERS                */
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
        margin-top: 5px;
    }

    .score { 
        text-align: center; 
        font-size: 44px; 
        font-weight: 800;
        color: var(--secondary);
        line-height: 1;
    }

    /* ============================= */
    /* 📊 TABELAS GERAIS            */
    /* ============================= */
    table {
        margin: 10px auto !important;
        border-collapse: collapse;
        width: 100%;
        max-width: 450px !important;
        font-size: 14px;
        background-color: white;
        box-shadow: var(--shadow-sm);
        border-radius: var(--radius);
        overflow: hidden;
        border: 1px solid var(--border);
    }

    th {
        background-color: var(--primary);
        color: white !important;
        padding: 12px 15px;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.05em;
    }

    td {
        padding: 10px 15px;
        border-bottom: 1px solid #f3f4f6;
        color: #374151;
    }

    table tr td:first-child {
        font-weight: 700;
        color: var(--text-light);
        background-color: var(--bg-light);
        width: 50%;
    }

    /* ============================= */
    /* 🔲 MATRIZ DE CONFUSÃO        */
    /* ============================= */
    .cm-table {
        width: 100% !important;
        max-width: 360px !important;
        margin: 10px auto !important;
        border-collapse: collapse !important;
        text-align: center;
        background-color: white;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border);
    }

    .cm-table th {
        text-align: center;
        background-color: var(--secondary);
        color: white !important;
        padding: 8px;
        font-size: 11px;
    }

    .cm-table td {
        text-align: center;
        padding: 14px;
        font-size: 15px;
        border: 1px solid #f1f5f9;
    }

    .cm-table tr td:first-child {
        background-color: white !important;
        font-weight: 700;
        color: #374151;
        width: auto !important;
    }

    .cm-table .val-pos { 
        background-color: #dcfce7 !important;
        color: #166534 !important; 
        font-weight: 800 !important;
    }

    .cm-table .val-neg { 
        background-color: #fee2e2 !important;
        color: #991b1b !important; 
        font-weight: 800 !important;
    }

    /* ============================= */
    /* 📈 CARD PSI                  */
    /* ============================= */
    .psi-card {
        text-align: center; 
        border: 1px solid var(--border); 
        padding: 25px; 
        border-radius: 16px; 
        width: 100%;
        max-width: 360px;
        background-color: white;
        box-shadow: var(--shadow-md);
        margin: 10px auto;
        transition: all 0.2s ease;
    }

    .psi-card:hover {
        transform: translateY(-2px);
    }

    /* ================================= */
    /* 📂 EXPANDER (LARGURA CONTROLADA)  */
    /* ================================= */
    div[data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        background-color: white !important;
        
        /* Largura não ocupa 100% da tela */
        width: 100% !important;
        max-width: 600px !important; 
        
        margin: 20px auto !important; /* Centraliza horizontalmente */
        box-shadow: var(--shadow-sm) !important;
    }

    div[data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: var(--secondary) !important;
        padding: 10px 15px !important;
    }

    div[data-testid="stExpander"] .stMarkdown {
        padding: 10px 20px !important;
    }

    div[data-testid="stExpander"] p, 
    div[data-testid="stExpander"] li {
        font-size: 13.5px !important;
        line-height: 1.6 !important;
        color: #475569 !important;
        text-align: left !important;
    }

    </style>
    """, unsafe_allow_html=True)