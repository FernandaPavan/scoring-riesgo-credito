import numpy as np

# ============================================
# SCORE
# ============================================
def get_score(prob, params):
    prob = float(np.clip(prob, 0.0001, 0.9999))

    factor = params["pdo"] / np.log(2)
    offset = params["base_score"] + factor * np.log(params["base_odds"])

    return int(offset + factor * np.log((1 - prob) / prob))


# ============================================
# POLICY DATA-DRIVEN (USANDO KS + PROB)
# ============================================
def apply_business_policy(
    score,
    prob,
    monto_solicitado,
    cutoffs,
    trabalho,
    habitacion
):

    # ============================================
    # PENALIZAÇÕES
    # ============================================
    penalidade_score = 0
    penalidade_limite = 1.0

    if trabalho == 0:  # desempregado
        penalidade_score -= 80
        penalidade_limite *= 0.5

    if habitacion == "rent":  # aluguel
        penalidade_score -= 30
        penalidade_limite *= 0.85

    score_final = max(score + penalidade_score, 300)

    # ============================================
    # SEGMENTAÇÃO
    # ============================================
    if score_final >= 700:
        segmento, limite_base = "SUPER PRIME", 18000
    elif score_final >= 650:
        segmento, limite_base = "PRIME", 10000
    elif score_final >= 600:
        segmento, limite_base = "STANDARD", 5000
    elif score_final >= 520:
        segmento, limite_base = "NEAR PRIME", 2500
    elif score_final >= 460:
        segmento, limite_base = "REVIEW", 1000
    else:
        segmento, limite_base = "SUBPRIME", 0

    limite_final = int(limite_base * penalidade_limite)

    # ============================================
    # CUTS DO MODELO
    # ============================================
    ks_cutoff = cutoffs.get("ks_score_cutoff", 490)
    prob_cutoff = cutoffs.get("best_prob_cutoff", 0.53)
    reject_cutoff = cutoffs.get("reject_cutoff", 460)
    approve_cutoff = cutoffs.get("approve_cutoff", 520)

    # ============================================
    # REGRAS DE DECISÃO (PRIORIDADE)
    # ============================================

    # 1. HARD RULE (negócio)
    if trabalho == 0:
        return {
            "status": "RECHAZADO",
            "icon": "✖",
            "cor": "#dc2626",
            "score": score_final,
            "segmento": segmento,
            "limite": limite_final,
            "motivo": "Riesgo alto: cliente desempleado."
        }

    # 2. REJEIÇÃO FORTE
    if score_final < reject_cutoff:
        return {
            "status": "RECHAZADO",
            "icon": "✖",
            "cor": "#dc2626",
            "score": score_final,
            "segmento": segmento,
            "limite": limite_final,
            "motivo": "Score bajo política mínima."
        }

    # 3. ALERTA MODELO (probabilidade alta de default)
    if prob >= prob_cutoff:
        return {
            "status": "RECHAZADO",
            "icon": "✖",
            "cor": "#dc2626",
            "score": score_final,
            "segmento": segmento,
            "limite": limite_final,
            "motivo": "Alta probabilidad de incumplimiento (modelo)."
        }

    # 4. ZONA KS (melhor separação estatística)
    if score_final < ks_cutoff:
        return {
            "status": "EN ANÁLISIS",
            "icon": "⚠",
            "cor": "#facc15",
            "score": score_final,
            "segmento": segmento,
            "limite": limite_final,
            "motivo": "Zona crítica según KS del modelo."
        }

    # 5. APROVAÇÃO
    if score_final >= approve_cutoff and monto_solicitado <= limite_final:
        return {
            "status": "APROBADO",
            "icon": "✔",
            "cor": "#16a34a",
            "score": score_final,
            "segmento": segmento,
            "limite": limite_final,
            "motivo": "Aprobación dentro de política y riesgo controlado."
        }

    # 6. fallback
    return {
        "status": "RECHAZADO",
        "icon": "✖",
        "cor": "#dc2626",
        "score": score_final,
        "segmento": segmento,
        "limite": limite_final,
        "motivo": "Excede limite permitido o riesgo elevado."
    }