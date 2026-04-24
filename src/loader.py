import os
import joblib
import json
import streamlit as st

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PROJECT = os.path.dirname(CURRENT_DIR)
MODEL_PATH = os.path.join(BASE_PROJECT, "models")

@st.cache_resource
def load_assets():
    try:
        modelo = joblib.load(os.path.join(MODEL_PATH, "modelo.pkl"))
        bins_woe = joblib.load(os.path.join(MODEL_PATH, "woe_bins.pkl"))

        with open(os.path.join(MODEL_PATH, "metricas.json"), "r") as f:
            metricas = json.load(f)

        with open(os.path.join(MODEL_PATH, "score_params.json"), "r") as f:
            params = json.load(f)

        return modelo, bins_woe, metricas, params

    except Exception as e:
        st.error(f"Erro ao carregar modelos: {e}")
        st.stop()