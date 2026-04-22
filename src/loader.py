import joblib
import json
import os
import streamlit as st

def load_assets(model_path="models"):
    """Carrega todos os artefatos do modelo centralizadamente."""
    modelo = joblib.load(os.path.join(model_path, "modelo.pkl"))
    bins_woe = joblib.load(os.path.join(model_path, "woe_bins.pkl"))
    
    with open(os.path.join(model_path, "metricas.json"), "r") as f:
        metricas = json.load(f)
        
    with open(os.path.join(model_path, "score_params.json"), "r") as f:
        params = json.load(f)
        
    return modelo, bins_woe, metricas, params