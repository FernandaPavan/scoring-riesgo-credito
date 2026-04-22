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
    trabalho,
    habitacao,
    ahorro,
    corriente,
    valor_solicitado
):
    """
    Policy 100% baseada em cutoff (SEM penalização)
    """

    # CUT-OFF FIXO (ou pode vir do score_params depois)
    REJECT_CUTOFF = 460
    APPROVE_CUTOFF = 520

    # =============================
    # 1. SEGMENTAÇÃO (só informativa)
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

    limite_final = limite_base

    # =============================
    # 2. DECISÃO (CORRETA)
    # =============================

    # HARD RULE
    if trabalho == 0 and corriente == "little":
        return {
            "score": score,
            "segmento": segmento,
            "limite": 0,
            "status": "RECHAZADO",
            "icon": "✖",
            "cor": "#dc2626",
            "motivo": "Riesgo crítico: sin empleo y baja liquidez."
        }

    # ❌ REJECT
    if score < REJECT_CUTOFF:
        return {
            "score": score,
            "segmento": segmento,
            "limite": 0,
            "status": "RECHAZADO",
            "icon": "✖",
            "cor": "#dc2626",
            "motivo": f"Score bajo cutoff ({score} < {REJECT_CUTOFF})"
        }

    # ⚠ REVIEW (AQUI ESTAVA O ERRO)
    if REJECT_CUTOFF <= score < APPROVE_CUTOFF:
        return {
            "score": score,
            "segmento": segmento,
            "limite": limite_final,
            "status": "EN ANÁLISIS",
            "icon": "⚠",
            "cor": "#facc15",
            "motivo": "Zona intermedia entre cutoffs"
        }

    # ✅ APPROVE
    if score >= APPROVE_CUTOFF:
        if valor_solicitado <= limite_final:
            return {
                "score": score,
                "segmento": segmento,
                "limite": limite_final,
                "status": "APROBADO",
                "icon": "✔",
                "cor": "#16a34a",
                "motivo": "Dentro del límite"
            }
        else:
            return {
                "score": score,
                "segmento": segmento,
                "limite": limite_final,
                "status": "EN ANÁLISIS",
                "icon": "⚠",
                "cor": "#facc15",
                "motivo": "Excede límite, requiere análisis"
            }