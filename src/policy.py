import numpy as np

def apply_business_policy(score, valor_solicitado):

    reject_cutoff = 490
    approve_cutoff = 540

    # =============================
    # SEGMENTAÇÃO
    # =============================
    if score >= 700:
        segmento, limite = "SUPER PRIME", 18000
    elif score >= 650:
        segmento, limite = "PRIME", 10000
    elif score >= 600:
        segmento, limite = "STANDARD", 5000
    elif score >= 550:
        segmento, limite = "NEAR PRIME", 3000
    elif score >= 490:
        segmento, limite = "REVIEW", 1500
    else:
        segmento, limite = "SUBPRIME", 0

    # =============================
    # DECISÃO
    # =============================
    if score < reject_cutoff:
        status = "RECHAZADO"
        cor = "#dc2626"
        icon = "✖"
        motivo = f"Score abaixo do cutoff ({score} < {reject_cutoff})"

    elif score < approve_cutoff:
        status = "EN ANÁLISIS"
        cor = "#facc15"
        icon = "⚠"
        motivo = "Zona cinza (KS ótimo) — revisão manual"

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
        "score": score,
        "segmento": segmento,
        "limite": limite,
        "status": status,
        "icon": icon,
        "cor": cor,
        "motivo": motivo
    }