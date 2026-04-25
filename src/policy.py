def apply_business_policy(score, prob, monto_solicitado, cutoffs):

    # ============================================
    # PARÂMETROS EQUILIBRADOS
    # ============================================
    reject_score_cut = 490
    auto_approve_score = 640
    prob_reject_cut = 0.62
    prob_safe_cut = 0.40

    # ============================================
    # SEGMENTAÇÃO REALISTA
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
    # 1. REJEIÇÃO DIRETA (somente extremos reais)
    # ============================================
    if prob >= prob_reject_cut or score < reject_score_cut:
        status = "RECHAZADO"
        icon = "✖"
        cor = "#dc2626"
        motivo = "Riesgo elevado según política de crédito."
        limite = 0

    # ============================================
    # 2. APROVAÇÃO AUTOMÁTICA (elite real)
    # ============================================
    elif score >= auto_approve_score and prob <= prob_safe_cut:
        status = "APROBADO"
        icon = "✔"
        cor = "#16a34a"
        motivo = "Perfil sólido para aprobación automática."

        risk_factor = 1 - prob
        limite = int(teto * risk_factor)
        limite = max(min(limite, teto), 300)

    # ============================================
    # 3. ZONA PRINCIPAL DO MODELO (ANÁLISE)
    # ============================================
    else:
        status = "EN ANÁLISIS"
        icon = "⚠"
        cor = "#facc15"
        motivo = "Perfil requiere evaluación adicional."

        # limite conservador para análise
        risk_factor = (1 - prob)
        limite = int(teto * risk_factor * 0.5)
        limite = max(limite, 250)

    # ============================================
    # AJUSTE DE MONTANTE
    # ============================================
    if status == "APROBADO" and monto_solicitado > limite:
        status = "EN ANÁLISIS"
        motivo = f"Monto superior al límite automático: R$ {limite}"

    return {
        "status": status,
        "icon": icon,
        "cor": cor,
        "score": score,
        "segmento": segmento,
        "limite": limite,
        "motivo": motivo
    }