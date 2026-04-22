import numpy as np

# ============================================
# SCORE
# ============================================
def get_score(prob, score_params):
    """
    Transforma probabilidade em score (300 - 1000)
    """
    prob = max(min(prob, 0.9999), 0.0001)

    factor = score_params["pdo"] / np.log(2)
    offset = score_params["base_score"] + factor * np.log(score_params["base_odds"])

    score = int(offset + factor * np.log((1 - prob) / prob))

    return max(min(score, 1000), 300)


# ============================================
# POLICY (SEM PENALIDADE DE SCORE)
# ============================================
def apply_business_policy(
    score,
    prob,
    trabalho,
    habitacao,
    valor_solicitado
):
    """
    - Decisão via probabilidade (cutoff)
    - Score apenas para segmentação
    - Penalidade apenas no limite
    """

    # =============================
    # 1. SEGMENTAÇÃO
    # =============================
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

    # =============================
    # 2. AJUSTE DE LIMITE (APENAS)
    # =============================
    penalidade_limite = 1.0
    flags = []

    # desemprego
    if trabalho == 0:
        penalidade_limite *= 0.7
        flags.append("Sin empleo")

    # aluguel
    if habitacao == "rent":
        penalidade_limite *= 0.9
        flags.append("Vivienda alquilada")

    # moradia gratuita (leve ajuste)
    if habitacao == "free":
        penalidade_limite *= 0.95
        flags.append("Vivienda gratuita")

    limite_final = int(limite_base * penalidade_limite)

    # =============================
    # 3. DECISÃO PELO MODELO (CUT-OFF)
    # =============================
    REJECT_CUTOFF = 0.5304
    REVIEW_CUTOFF = 0.45

    # HARD RULE (opcional)
    if trabalho == 0 and limite_final < 800:
        status = "RECHAZADO"
        icon = "✖"
        cor = "#dc2626"
        motivo = "Sin capacidad mínima de pago."

    # REJEIÇÃO
    elif prob >= REJECT_CUTOFF:
        status = "RECHAZADO"
        icon = "✖"
        cor = "#dc2626"
        motivo = "Alta probabilidad de incumplimiento."

    # ZONA CINZA
    elif REVIEW_CUTOFF <= prob < REJECT_CUTOFF:
        status = "EN ANÁLISIS"
        icon = "⚠"
        cor = "#facc15"
        motivo = "Zona intermedia de riesgo."

    # APROVAÇÃO
    else:
        if valor_solicitado <= limite_final:
            status = "APROBADO"
            icon = "✔"
            cor = "#16a34a"
            motivo = "Dentro del límite aprobado."
        else:
            status = "EN ANÁLISIS"
            icon = "⚠"
            cor = "#facc15"
            motivo = f"Excede límite (${limite_final:,.0f})."

    # adiciona explicação
    if flags:
        motivo += " | " + ", ".join(flags)

    return {
        "score": score,
        "segmento": segmento,
        "limite": limite_final,
        "status": status,
        "icon": icon,
        "cor": cor,
        "motivo": motivo
    }