import numpy as np

# ============================================
# SCORE (PDO)
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
# POLICY (KS + LIMITE)
# ============================================
def apply_business_policy(score, prob_default, valor_solicitado, cutoffs):

    reject_cutoff = cutoffs["reject_cutoff"]
    approve_cutoff = cutoffs["approve_cutoff"]

    # ============================================
    # LIMITE (BASEADO NA PROBABILIDADE)
    # ============================================
    limite_sugerido = int(max(500, (1 - prob_default) * 20000))

    # ============================================
    # SEGMENTO
    # ============================================
    if score >= 700:
        segmento = "SUPER PRIME"
    elif score >= 650:
        segmento = "PRIME"
    elif score >= 600:
        segmento = "STANDARD"
    elif score >= approve_cutoff:
        segmento = "NEAR PRIME"
    elif score >= reject_cutoff:
        segmento = "REVIEW"
    else:
        segmento = "SUBPRIME"

    # ============================================
    # DECISÃO FINAL (SEM PENALIDADE)
    # ============================================
    if score < reject_cutoff:
        status = "RECHAZADO"
        icon = "❌"
        cor = "#dc2626"
        motivo = "Score abaixo do cutoff mínimo"

    elif score >= approve_cutoff:
        if valor_solicitado <= limite_sugerido:
            status = "APROBADO"
            icon = "✅"
            cor = "#16a34a"
            motivo = "Dentro del límite aprobado"

        elif valor_solicitado <= limite_sugerido * 1.2:
            status = "EN ANÁLISIS"
            icon = "⚠️"
            cor = "#facc15"
            motivo = "Monto levemente superior al límite"

        else:
            status = "RECHAZADO"
            icon = "❌"
            cor = "#dc2626"
            motivo = "Excede límite permitido"

    else:
        status = "EN ANÁLISIS"
        icon = "⚠️"
        cor = "#facc15"
        motivo = "Zona intermedia (cutoff KS)"

    return {
        "score": score,
        "segmento": segmento,
        "limite": limite_sugerido,
        "status": status,
        "icon": icon,
        "cor": cor,
        "motivo": motivo
    }