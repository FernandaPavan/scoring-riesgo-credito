import numpy as np
import numpy as np

# ============================================
# SCORE
# ============================================
def get_score(prob, score_params):
    prob = max(min(prob, 0.9999), 0.0001)

    factor = score_params["pdo"] / np.log(2)
    offset = score_params["base_score"] + factor * np.log(score_params["base_odds"])

    score = int(offset + factor * np.log((1 - prob) / prob))

    return max(min(score, 1000), 300)


# ============================================
# POLICY (NOVA - COMPATÍVEL)
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
    Nova regra:
    - SEM penalização
    - Baseada no KS (490)
    - Zona cinza estratégica
    """

    # CUT-OFFS (KS)
    reject_cutoff = 490
    approve_cutoff = 540

    # =============================
    # SCORE FINAL (SEM ALTERAÇÃO)
    # =============================
    score_final = score

    # =============================
    # SEGMENTAÇÃO
    # =============================
    if score_final >= 700:
        segmento, limite = "SUPER PRIME", 18000
    elif score_final >= 650:
        segmento, limite = "PRIME", 10000
    elif score_final >= 600:
        segmento, limite = "STANDARD", 5000
    elif score_final >= 550:
        segmento, limite = "NEAR PRIME", 3000
    elif score_final >= 490:
        segmento, limite = "REVIEW", 1500
    else:
        segmento, limite = "SUBPRIME", 0

    # =============================
    # DECISÃO
    # =============================
    if score_final < reject_cutoff:
        status = "RECHAZADO"
        cor = "#dc2626"
        icon = "✖"
        motivo = f"Score abaixo do cutoff ({score_final} < {reject_cutoff})"

    elif score_final < approve_cutoff:
        status = "EN ANÁLISIS"
        cor = "#facc15"
        icon = "⚠"
        motivo = "Zona cinza (KS) — revisão manual"

    else:
        if valor_solicitado <= limite:
            status = "APROBADO"
            cor = "#16a34a"
            icon = "✔"
            motivo = "Aprovado dentro do limite"
        else:
            status = "EN ANÁLISIS"
            cor = "#facc15"
            icon = "⚠"
            motivo = "Acima do limite — revisão"

    return {
        "score": score_final,
        "segmento": segmento,
        "limite": limite,
        "status": status,
        "icon": icon,
        "cor": cor,
        "motivo": motivo
    }