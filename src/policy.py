import numpy as np

# ============================================
# SCORE (PDO)
# ============================================
def get_score(prob, params):
    factor = params["pdo"] / np.log(2)
    offset = params["base_score"] + factor * np.log(params["base_odds"])

    prob = min(max(prob, 0.0001), 0.9999)

    return int(offset + factor * np.log((1 - prob) / prob))


# ============================================
# BUSINESS POLICY (AJUSTADA AO MODELO REAL)
# ============================================
def apply_business_policy(score, prob, monto_solicitado, cutoffs):

    reject_cutoff = cutoffs["reject_cutoff"]          # 460
    approve_cutoff = cutoffs["approve_cutoff"]        # 520
    prob_cutoff = cutoffs["best_prob_cutoff"]         # 0.53

    # ================================
    # SEGMENTAÇÃO (mantida, mas mais conservadora)
    # ================================
    if score >= 700:
        segmento = "SUPER PRIME"
        teto = 12000
    elif score >= 650:
        segmento = "PRIME"
        teto = 8000
    elif score >= 600:
        segmento = "STANDARD"
        teto = 4000
    elif score >= 520:
        segmento = "NEAR PRIME"
        teto = 2000
    elif score >= 460:
        segmento = "REVIEW"
        teto = 800
    else:
        segmento = "SUBPRIME"
        teto = 0

    # ================================
    # REGRA PRINCIPAL (probabilidade manda)
    # ================================
    if prob >= 0.70:
        status = "RECHAZADO"
        icon = "✖"
        cor = "#dc2626"
        motivo = "Alta probabilidad de default."
        limite = 0

    elif prob >= prob_cutoff:
        status = "EN ANÁLISIS"
        icon = "⚠"
        cor = "#facc15"
        motivo = "Zona de riesgo intermedia."
        limite = int(teto * 0.4)

    elif score < reject_cutoff:
        status = "RECHAZADO"
        icon = "✖"
        cor = "#dc2626"
        motivo = "Score bajo política mínima."
        limite = 0

    else:
        status = "APROBADO"
        icon = "✔"
        cor = "#16a34a"
        motivo = "Aprobación dentro de política."

        # ================================
        # LIMITE AJUSTADO POR RISCO
        # ================================
        risk_factor = 1 - prob  # núcleo do equilíbrio

        limite = int(teto * risk_factor)

        # trava de segurança
        limite = max(min(limite, teto), 300)

    # ================================
    # EXCEÇÃO DE EXCESSO DE VALOR
    # ================================
    if monto_solicitado > limite and status == "APROBADO":
        status = "RECHAZADO"
        icon = "✖"
        cor = "#dc2626"
        motivo = "Monto excede límite de riesgo."
        limite = 0

    return {
        "status": status,
        "icon": icon,
        "cor": cor,
        "score": score,
        "segmento": segmento,
        "limite": limite,
        "motivo": motivo
    }