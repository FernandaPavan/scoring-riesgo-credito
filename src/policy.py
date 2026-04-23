import numpy as np

# ============================================
# SCORE (PDO - padrão bancário)
# ============================================
def get_score(prob_default, score_params):
    """
    Converte probabilidade de default em score (PDO)
    """

    prob_default = float(np.clip(prob_default, 0.0001, 0.9999))

    pdo = score_params.get("pdo", 20)
    base_score = score_params.get("base_score", 600)
    base_odds = score_params.get("base_odds", 50)

    factor = pdo / np.log(2)
    offset = base_score - factor * np.log(base_odds)

    odds = (1 - prob_default) / prob_default

    score = int(round(offset + factor * np.log(odds)))

    return max(score, 300)


# ============================================
# POLICY DE CRÉDITO (DECISÃO FINAL)
# ============================================
def apply_business_policy(score, prob_default, valor_solicitado, cutoffs):
    """
    Regras de crédito baseadas em:
    - score (risco)
    - limite (capacidade de pagamento)
    """

    reject_cutoff = cutoffs["reject_score"]
    analysis_cutoff = cutoffs["analysis_score"]

    # ============================================
    # LIMITE SUGERIDO (BASE ESTÁVEL)
    # ============================================
    limite_sugerido = int(max(500, (1 - prob_default) * 20000))

    # ============================================
    # SEGMENTAÇÃO DE RISCO
    # ============================================
    if score >= 700:
        segmento = "SUPER PRIME"
    elif score >= 650:
        segmento = "PRIME"
    elif score >= 600:
        segmento = "STANDARD"
    elif score >= 520:
        segmento = "NEAR PRIME"
    elif score >= 460:
        segmento = "REVIEW"
    else:
        segmento = "SUBPRIME"

    # ============================================
    # REJEIÇÃO AUTOMÁTICA
    # ============================================
    if score < reject_cutoff:
        return {
            "score": score,
            "segmento": segmento,
            "limite": limite_sugerido,
            "status": "RECHAZADO",
            "icon": "❌",
            "cor": "#dc2626",
            "motivo": "Score abaixo do mínimo de política de crédito"
        }

    # ============================================
    # ZONA DE ANÁLISE
    # ============================================
    if score < analysis_cutoff:
        return {
            "score": score,
            "segmento": segmento,
            "limite": limite_sugerido,
            "status": "EN ANÁLISIS",
            "icon": "⚠️",
            "cor": "#facc15",
            "motivo": f"Perfil em análise. Limite estimado: ${limite_sugerido:,.0f}"
        }

    # ============================================
    # DECISÃO FINAL (APROVAÇÃO POR LIMITE)
    # ============================================
    if valor_solicitado <= limite_sugerido:
        return {
            "score": score,
            "segmento": segmento,
            "limite": limite_sugerido,
            "status": "APROBADO",
            "icon": "✅",
            "cor": "#16a34a",
            "motivo": "Dentro do limite aprovado"
        }

    # ============================================
    # REJEIÇÃO POR EXCESSO DE LIMITE
    # ============================================
    return {
        "score": score,
        "segmento": segmento,
        "limite": limite_sugerido,
        "status": "RECHAZADO",
        "icon": "❌",
        "cor": "#dc2626",
        "motivo": f"Valor solicitado excede o limite de ${limite_sugerido:,.0f}"
    }