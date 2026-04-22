import numpy as np

# ============================================
# SCORE
# ============================================
def get_score(prob, score_params):
    """
    Transforma probabilidade de inadimplência em score (300 - 1000)
    """
    # Proteção numérica
    prob = max(min(prob, 0.9999), 0.0001)

    factor = score_params["pdo"] / np.log(2)
    offset = score_params["base_score"] + factor * np.log(score_params["base_odds"])

    score = int(offset + factor * np.log((1 - prob) / prob))

    return max(min(score, 1000), 300)


# ============================================
# POLICY
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
    Aplica regras de negócio:
    - Penalizações calibradas
    - Segmentação
    - Limite
    - Decisão com cutoffs
    """

    # =============================
    # 1. PENALIZAÇÕES (AJUSTADAS)
    # =============================
    penalidade_score = 0
    penalidade_limite = 1.0
    flags = []

    if trabalho == 0:
        penalidade_score -= 60   # antes -80 (muito agressivo)
        penalidade_limite *= 0.6
        flags.append("Sin empleo")

    if habitacao == "rent":
        penalidade_score -= 20
        penalidade_limite *= 0.90
        flags.append("Vivienda alquilada")

    if habitacao == "free":
        penalidade_limite *= 0.95
        flags.append("Vivienda gratuita")

    if ahorro == "little":
        penalidade_score -= 15
        penalidade_limite *= 0.95
        flags.append("Bajo ahorro")

    if corriente == "little":
        penalidade_score -= 15
        penalidade_limite *= 0.95
        flags.append("Baja liquidez")

    # =============================
    # 2. SCORE FINAL
    # =============================
    score_final = max(score + penalidade_score, 300)

    # =============================
    # 3. SEGMENTAÇÃO
    # =============================
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

    # =============================
    # 4. LIMITE FINAL
    # =============================
    limite_final = int(limite_base * penalidade_limite)

    # =============================
    # 5. DECISÃO COM CUT-OFF
    # =============================

    # HARD RULE (sempre prioriza)
    if trabalho == 0 and corriente == "little":
        status = "RECHAZADO"
        icon = "✖"
        cor = "#dc2626"
        motivo = "Riesgo crítico: sin empleo y baja liquidez."

    # ❌ REJEIÇÃO
    elif score_final < 460:
        status = "RECHAZADO"
        icon = "✖"
        cor = "#dc2626"
        motivo = f"Score por debajo del cutoff ({score_final} < 460)."

    # ⚠ ZONA CINZA (ESSENCIAL)
    elif 460 <= score_final < 520:
        status = "EN ANÁLISIS"
        icon = "⚠"
        cor = "#facc15"
        motivo = "Zona intermedia de riesgo. Requiere análisis."

    # ✅ APROVAÇÃO CONTROLADA
    else:
        if valor_solicitado <= limite_final:
            status = "APROBADO"
            icon = "✔"
            cor = "#16a34a"
            motivo = "Dentro del límite aprobado."

        elif valor_solicitado <= limite_final * 1.2:
            status = "EN ANÁLISIS"
            icon = "⚠"
            cor = "#facc15"
            motivo = "Monto levemente superior al límite."

        else:
            status = "RECHAZADO"
            icon = "✖"
            cor = "#dc2626"
            motivo = f"Excede límite permitido (${limite_final:,.0f})."

    # =============================
    # 6. FLAGS (EXPLICAÇÃO)
    # =============================
    if flags:
        motivo += " | Riesgos: " + ", ".join(flags)

    return {
        "score": score_final,
        "segmento": segmento,
        "limite": limite_final,
        "status": status,
        "icon": icon,
        "cor": cor,
        "motivo": motivo
    }