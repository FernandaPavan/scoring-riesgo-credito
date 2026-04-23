import numpy as np

# ============================================
# SCORE (PDO - padrão bancário)
# ============================================
def get_score(prob_default, score_params):

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
# POLICY DE CRÉDITO (VERSÃO AJUSTADA)
# ============================================
def apply_business_policy(score, prob_default, valor_solicitado, cutoffs):

    reject_cutoff = cutoffs["reject_cutoff"]
    analysis_cutoff = cutoffs["analysis_cutoff"]

    # ============================================
    # SEGMENTO (define capacidade estrutural)
    # ============================================
    if score >= 700:
        segmento = "SUPER PRIME"
        base_limit = 18000
    elif score >= 650:
        segmento = "PRIME"
        base_limit = 10000
    elif score >= 600:
        segmento = "STANDARD"
        base_limit = 5000
    elif score >= 520:
        segmento = "NEAR PRIME"
        base_limit = 2500
    elif score >= 460:
        segmento = "REVIEW"
        base_limit = 1000
    else:
        segmento = "SUBPRIME"
        base_limit = 500

    # ============================================
    # LIMITE (mais estável e controlado)
    # ============================================
    risco_factor = (1 - prob_default)

    limite_sugerido = int(max(500, base_limit * (0.7 + risco_factor * 0.6)))

    # ============================================
    # DECISÃO 1: REJEIÇÃO DIRETA
    # ============================================
    if score < reject_cutoff:
        return {
            "score": score,
            "segmento": segmento,
            "limite": limite_sugerido,
            "status": "RECHAZADO",
            "icon": "❌",
            "cor": "#dc2626",
            "motivo": "Score abaixo do cutoff mínimo"
        }

    # ============================================
    # DECISÃO 2: ANÁLISE
    # ============================================
    if score < analysis_cutoff:
        return {
            "score": score,
            "segmento": segmento,
            "limite": limite_sugerido,
            "status": "EN ANÁLISIS",
            "icon": "⚠️",
            "cor": "#facc15",
            "motivo": "Perfil em zona intermediária de risco"
        }

    # ============================================
    # DECISÃO 3: APROVAÇÃO OU REPROVAÇÃO POR LIMITE
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

    return {
        "score": score,
        "segmento": segmento,
        "limite": limite_sugerido,
        "status": "RECHAZADO",
        "icon": "❌",
        "cor": "#dc2626",
        "motivo": "Excede o limite permitido"
    }