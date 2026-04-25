import numpy as np

# ============================================
# SCORE (mantém igual ao seu)
# ============================================
def get_score(prob, params):
    factor = params["pdo"] / np.log(2)
    offset = params["base_score"] + factor * np.log(params["base_odds"])
    prob = min(max(prob, 0.0001), 0.9999)
    return int(offset + factor * np.log((1 - prob) / prob))


# ============================================
# BUSINESS POLICY EQUILIBRADA
# ============================================
def apply_business_policy(score, prob, monto_solicitado, cutoffs):

    # ============================================
    # PARÂMETROS EQUILIBRADOS
    # ============================================
    reject_score_cut = 490
    auto_approve_score = 640
    prob_reject_cut = 0.62
    prob_safe_cut = 0.40

    # ============================================
    # SEGMENTAÇÃO
    # ============================================
    if score >= 750:
        segmento, teto = "TOP PRIME", 18000
    elif score >= 700:
        segmento, teto = "SUPER PRIME", 12000
    elif score >= 640:
        segmento, teto = "PRIME", 8000
    elif score >= 600:
        segmento, teto = "STANDARD", 4500
    elif score >= 540:
        segmento, teto = "NEAR PRIME", 2500
    elif score >= 490:
        segmento, teto = "REVIEW", 1200
    else:
        segmento, teto = "SUBPRIME", 0

    # ============================================
    # 1. RECHAZO DIRECTO (RIESGO ALTO)
    # ============================================
    if prob >= prob_reject_cut or score < reject_score_cut:

        return {
            "status": "RECHAZADO",
            "icon": "✖",
            "cor": "#dc2626",
            "score": score,
            "segmento": segmento,
            "limite": 0,
            "motivo": "Riesgo elevado según política de crédito."
        }

    # ============================================
    # 2. APROBACIÓN AUTOMÁTICA (PERFIL FUERTE)
    # ============================================
    elif score >= auto_approve_score and prob <= prob_safe_cut:

        risk_factor = 1 - prob
        limite = int(teto * risk_factor)

        # proteção
        limite = max(min(limite, teto), 300)

        status = "APROBADO"
        motivo = "Perfil sólido para aprobación automática."

        # ============================================
        # CONTRAPROPOSTA AUTOMÁTICA
        # ============================================
        if monto_solicitado > limite:
            status = "EN ANÁLISIS"
            motivo = f"Monto superior al límite automático: R$ {limite}"

        return {
            "status": status,
            "icon": "✔" if status == "APROBADO" else "⚠",
            "cor": "#16a34a" if status == "APROBADO" else "#facc15",
            "score": score,
            "segmento": segmento,
            "limite": limite,
            "motivo": motivo
        }

    # ============================================
    # 3. ZONA PRINCIPAL (ANÁLISIS)
    # ============================================
    else:

        risk_factor = 1 - prob
        limite = int(teto * risk_factor * 0.5)

        return {
            "status": "EN ANÁLISIS",
            "icon": "⚠",
            "cor": "#facc15",
            "score": score,
            "segmento": segmento,
            "limite": max(limite, 250),
            "motivo": "Perfil en zona intermedia. Requiere evaluación."
        }