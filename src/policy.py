import pandas as pd

def get_score(prob, score_params):
    """
    Calcula o score de crédito baseado na probabilidade de default.
    Equação: Score = Offset + Factor * ln(odds)
    """
    odds = (1 - prob) / prob
    score = score_params['offset'] + score_params['factor'] * pd.np.log(odds)
    return int(score)

def apply_business_policy(score, prob, monto_solicitado, cutoffs=None):
    """
    Aplica as regras de decisão de negócio baseadas no score e probabilidade.
    Retorna um dicionário com o status, cor, ícone e limite sugerido.
    """
    
    # ============================================
    # CALIBRAÇÃO DE PARÂMETROS
    # ============================================
    reject_score_cut = 490
    auto_approve_score = 640
    prob_reject_cut = 0.62
    prob_safe_cut = 0.40

    # ============================================
    # SEGMENTAÇÃO POR FAIXA DE SCORE
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
    # LÓGICA DE DECISÃO (STATUS)
    # ============================================
    
    # 1. REPROVAÇÃO DIRETA (RISCO ALTO)
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

    # 2. APROVAÇÃO AUTOMÁTICA (PERFIL EXCELENTE)
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

    # 3. ZONA DE ANÁLISE (CASOS INTERMEDIÁRIOS)
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

def calculate_final_adjustments(limite, duracion, flags):
    """
    Aplica ajustes finais ao limite baseados em variáveis externas (prazo e flags).
    """
    # Penalidade por prazo longo
    if duracion > 48:
        limite = int(limite * 0.85)
        
    return limite