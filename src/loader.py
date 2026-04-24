import os
import json
import joblib

def load_assets():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_project = os.path.dirname(current_dir)
    model_path = os.path.join(base_project, "models")

    # ============================================
    # MODELO E BINS
    # ============================================
    modelo = joblib.load(os.path.join(model_path, "modelo.pkl"))
    bins_woe = joblib.load(os.path.join(model_path, "woe_bins.pkl"))

    # ============================================
    # MÉTRICAS
    # ============================================
    with open(os.path.join(model_path, "metricas.json"), "r") as f:
        metricas = json.load(f)

    # ============================================
    # PARÂMETROS DE SCORE
    # ============================================
    with open(os.path.join(model_path, "score_params.json"), "r") as f:
        score_params = json.load(f)

    # ============================================
    # CUTOFFS DO MODELO (KS + PROB)
    # ============================================
    with open(os.path.join(model_path, "ks_cutoffs.json"), "r") as f:
        ks_data = json.load(f)

    cutoffs = {
        "reject_cutoff": ks_data.get("reject_cutoff", 460),
        "approve_cutoff": ks_data.get("approve_cutoff", 520),
        "ks_score_cutoff": ks_data.get("ks_score_cutoff", 490),
        "best_prob_cutoff": ks_data.get("best_prob_cutoff", 0.53)
    }

    return modelo, bins_woe, metricas, score_params, cutoffs