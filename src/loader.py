import os
import joblib
import streamlit as st

def load_assets():
    # Pega o caminho absoluto da pasta onde este arquivo (loader.py) está
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Sobe um nível para a raiz e aponta para a pasta models
    # Usamos o caminho que você enviou como base de verificação
    base_project = os.path.dirname(current_dir)
    model_path = os.path.join(base_project, "models")

    def try_load(filename):
        full_path = os.path.join(model_path, filename)
        if not os.path.exists(full_path):
            st.error(f"❌ Arquivo não encontrado: {filename}")
            st.warning(f"O sistema procurou em: {full_path}")
            st.info("Verifique se o nome do arquivo na pasta 'models' está exatamente igual (letras minúsculas).")
            st.stop()
        return joblib.load(full_path)

    modelo = try_load("modelo.pkl")
    bins_woe = try_load("bins_woe.pkl")
    metricas = try_load("metricas.pkl")
    score_params = try_load("score_params.pkl")

    return modelo, bins_woe, metricas, score_params