import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    /* Estilos anteriores mantidos... */
    .block-container { padding-top: 1rem !important; }

    .titulo-azul-centrado {
        text-align: center;
        color: #2563eb;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 20px;
    }

    /* Centralização de Tabelas e Conteúdo */
    .centrar-conteudo {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        width: 100%;
    }

    /* Cards de Estabilidade (PSI) */
    .card-psi {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        width: 300px;
        margin: 0 auto;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .estavel { background-color: #dcfce7; border: 1px solid #166534; color: #166534; }
    .alerta { background-color: #fef9c3; border: 1px solid #854d0e; color: #854d0e; }
    .instavel { background-color: #fee2e2; border: 1px solid #991b1b; color: #991b1b; }

    /* Ajuste de Tabelas */
    .table-container {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    
    table {
        margin-left: auto;
        margin-right: auto;
        border-collapse: collapse;
        width: 500px;
    }
    </style>
    """, unsafe_allow_html=True)