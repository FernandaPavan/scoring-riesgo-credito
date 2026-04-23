import math

# ============================================
# SCORE (PDO)
# ============================================
def get_score(prob, params):
    """
    Converte probabilidade de default em score
    """

    pdo = params.get("pdo", 20)
    base_score = params.get("base_score", 600)
    base_odds = params.get("base_odds", 50)

    # fator
    factor = pdo / math.log(2)

    # offset
    offset = base_score - factor * math.log(base_odds)

    # evita erro numérico
    prob = min(max(prob, 1e-6), 1 - 1e-6)

    odds = (1 - prob) / prob

    score = offset + factor * math.log(odds)

    return int(round(score))


# ============================================
# LIMITE DE CRÉDITO
# ============================================
def calcular_limite(score, monto):
    """
    Define limite baseado no score
    """

    if score >= 700:
        return monto * 2.0
    elif score >= 650:
        return monto * 1.5
    elif score >= 600:
        return monto * 1.2
    elif score >= 550:
        return monto * 1.0
    elif score >= 500:
        return monto * 0.5
    else:
        return 0


# ============================================
# POLICY PRINCIPAL
# ============================================
def apply_business_policy(
    score,
    trabalho,
    habitacao,
    ahorro,
    corriente,
    monto
):
    """
    Policy NÃO decide aprovação.
    Apenas enriquece com limite e informações visuais.
    """

    limite = calcular_limite(score, monto)

    # status neutro (será sobrescrito pelo app via cutoff KS)
    status = "EN ANÁLISIS"
    icon = "⚠️"
    cor = "#facc15"
    segmento = "Riesgo Medio"

    # motivo básico
    if score < 500:
        motivo = "Score bajo"
    elif score < 600:
        motivo = "Score medio"
    else:
        motivo = "Buen perfil de crédito"

    return {
        "score": score,
        "status": status,
        "icon": icon,
        "cor": cor,
        "segmento": segmento,
        "limite": int(limite),
        "motivo": motivo
    }