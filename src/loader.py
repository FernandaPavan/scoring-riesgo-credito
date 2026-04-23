import os
import joblib
import json
import streamlit as st

def load_assets():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_project = os.path.dirname(current_dir)
    model_path = os.path.join(base_project, "models")

    try:
        # Carregando binários (PKL)
        modelo = joblib.load(os.path.join(model_path, "modelo.pkl"))
        bins_woe = joblib.load(os.path.join(model_path, "woe_bins.pkl")) # Nome corrigido

        # Carregando textos (JSON)
        with open(os.path.join(model_path, "score_params.json"), 'r') as f:
            score_params = json.load(f)
            
        with open(os.path.join(model_path, "metricas.json"), 'r') as f:
            metricas = json.load(f)

        # Opcional: Carregar cutoffs se quiser usar os do arquivo JSON
        # with open(os.path.join(model_path, "ks_cutoffs.json"), 'r') as f:
        #     cutoffs = json.load(f)

        return modelo, bins_woe, metricas, score_params

    except Exception as e:
        st.error(f"❌ Erro ao carregar ativos: {e}")
        st.stop()