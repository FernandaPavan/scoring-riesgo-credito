import numpy as np

def get_score(prob, params):
    factor = params["pdo"] / np.log(2)
    offset = params["base_score"] + factor * np.log(params["base_odds"])
    prob = min(max(prob, 0.0001), 0.9999)
    return int(offset + factor * np.log((1 - prob) / prob))

def apply_business_policy(score, prob, monto_solicitado, cutoffs):
    # Definir Segmento
    if score >= 700: segmento, limite_base = "SUPER PRIME", 18000
    elif score >= 650: segmento, limite_base = "PRIME", 10000
    elif score >= 600: segmento, limite_base = "STANDARD", 5000
    elif score >= 520: segmento, limite_base = "NEAR PRIME", 2500
    elif score >= 460: segmento, limite_base = "REVIEW", 1000
    else: segmento, limite_base = "SUBPRIME", 0

    # Lógica de Decisão
    if score < 460:
        return {"status": "RECHAZADO", "icon": "✖", "cor": "#dc2626", "score": score, "segmento": segmento, "limite": 0, "motivo": "Score bajo política mínima."}
    elif score < 520:
        return {"status": "EN ANÁLISIS", "icon": "⚠", "cor": "#facc15", "score": score, "segmento": segmento, "limite": limite_base, "motivo": "Zona intermedia de riesgo."}
    elif monto_solicitado <= limite_base:
        return {"status": "APROBADO", "icon": "✔", "cor": "#16a34a", "score": score, "segmento": segmento, "limite": limite_base, "motivo": "Dentro del límite aprobado."}
    else:
        return {"status": "RECHAZADO", "icon": "✖", "cor": "#dc2626", "score": score, "segmento": segmento, "limite": limite_base, "motivo": "Excede limite permitido."}