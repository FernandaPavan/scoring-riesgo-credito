import numpy as np


# ============================================
# SCORE (PDO - padrão bancário)
# ============================================
def get_score(prob, score_params):
    """
    Calcula o score de crédito baseado na probabilidade de default.
    Padrão bancário usando PDO.
    """

    print("DEBUG SCORE FUNCIONANDO")  # 👈 coloca aqui

    prob = np.clip(prob, 1e-6, 1 - 1e-6)

    # Odds
    odds = (1 - prob) / prob

    # Parâmetros do JSON
    pdo = score_params['pdo']
    base_score = score_params['base_score']
    base_odds = score_params['base_odds']

    # Conversão
    factor = pdo / np.log(2)
    offset = base_score - factor * np.log(base_odds)

    # Score final
    score = offset + factor * np.log(odds)

    return int(score)


# ============================================
# AJUSTES FINAIS (centralizado)
# ============================================
def calculate_final_adjustments(limite, duracion, flags=None):
    """
    Ajustes finais no limite (prazo, flags, etc.)
    """

    # Penalidade por prazo longo
    if duracion > 48:
        limite = int(limite * 0.85)

    return limite


# ============================================
# POLÍTICA DE CRÉDITO
# ============================================
def apply_business_policy(score, prob, monto_solicitado, cutoffs=None):
    """
    Aplica regras de decisão de crédito.
    """

    # ============================================
    # CUTS
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
    # DECISÃO
    # ============================================

    # 1. REJEIÇÃO
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

    # 2. APROVAÇÃO AUTOMÁTICA
    elif score >= auto_approve_score and prob <= prob_safe_cut:
        risk_factor = 1 - prob
        limite = int(teto * risk_factor)
        limite = max(min(limite, teto), 300)

        return {
            "status": "APROBADO",
            "icon": "✔",
            "cor": "#16a34a",
            "score": score,
            "segmento": segmento,
            "limite": limite,
            "motivo": "Aprobación automática por perfil sólido."
        }

    # 3. ANÁLISE
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
