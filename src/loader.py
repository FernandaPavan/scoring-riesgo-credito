import os
import json
import joblib

def load_assets():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_project = os.path.dirname(current_dir)
    model_path = os.path.join(base_project, "models")

    modelo = joblib.load(os.path.join(model_path, "modelo.pkl"))
    bins_woe = joblib.load(os.path.join(model_path, "woe_bins.pkl"))

    with open(os.path.join(model_path, "metricas.json"), "r") as f:
        metricas = json.load(f)

    with open(os.path.join(model_path, "score_params.json"), "r") as f:
        score_params = json.load(f)

    cutoffs = {
        "reject_cutoff": 460,
        "analysis_cutoff": 520,
        "approve_cutoff": 520
    }

    return modelo, bins_woe, metricas, score_params, cutoffs