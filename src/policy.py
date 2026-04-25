import numpy as np

# ============================================
# SCORE
# ============================================
def get_score(prob, params):
    factor = params["pdo"] / np.log(2)
    offset = params["base_score"] + factor * np.log(params["base_odds"])
    prob = min(max(prob, 0.0001), 0.9999)
    return int(offset + factor * np.log((1 - prob) / prob))


# ============================================
# BUSINESS POLICY (SEM VARIÁVEIS OPERACIONAIS)
# ============================================
def apply_business_policy(score, prob, monto_solicitado, cutoffs):

    # SEGMENTAÇÃO
    if score >= 700: 
        segmento, limite_base = "SUPER PRIME", 18000
    elif score >= 650: 
        segmento, limite_base = "PRIME", 10000
    elif score >= 600: 
        segmento, limite_base = "STANDARD", 5000
    elif score >= 520: 
        segmento, limite_base = "NEAR PRIME", 2500
    elif score >= 460: 
        segmento, limite_base = "REVIEW", 1000
    else: 
        segmento, limite_base = "SUBPRIME", 0

    # CUTS (usando seus thresholds)
    reject_cutoff = cutoffs["reject_cutoff"]
    approve_cutoff = cutoffs["approve_cutoff"]

    # DECISÃO
    if score < reject_cutoff:
        status = "RECHAZADO"
        icon = "✖"
        cor = "#dc2626"
        motivo = "Score bajo política mínima."
        limite = 0

    elif score < approve_cutoff:
        status = "EN ANÁLISIS"
        icon = "⚠"
        cor = "#facc15"
        motivo = "Zona intermedia de riesgo."
        limite = limite_base

    elif monto_solicitado <= limite_base:
        status = "APROBADO"
        icon = "✔"
        cor = "#16a34a"
        motivo = "Dentro del límite aprobado."
        limite = limite_base

    else:
        status = "RECHAZADO"
        icon = "✖"
        cor = "#dc2626"
        motivo = "Excede limite permitido."
        limite = limite_base

    return {
        "status": status,
        "icon": icon,
        "cor": cor,
        "score": score,
        "segmento": segmento,
        "limite": limite,
        "motivo": motivo
    }
