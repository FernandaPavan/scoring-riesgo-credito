import numpy as np

def get_score(prob, score_params):
    """
    SCORE: Transforma a probabilidade do modelo em pontuação (0-1000).
    """
    factor = score_params["pdo"] / np.log(2)
    offset = score_params["base_score"] - factor * np.log(score_params["base_odds"])
    
    # Evita log de zero
    prob = max(min(prob, 0.9999), 0.0001)
    
    # Cálculo do Score (Inverso da probabilidade: quanto menor a prob de inadimplência, maior o score)
    score_base = int(offset + factor * np.log((1 - prob) / prob))
    return max(min(score_base, 1000), 300)

def apply_business_policy(score, trabalho, habitacao, ahorro, corriente, valor_solicitado):
    """
    POLICY: Aplica as regras de decisão, penalidades e limites.
    """
    penalidade_score = 0
    penalidade_limite = 1.0

    # 1. Regras de Penalização
    if trabalho == 0: 
        penalidade_score -= 80
        penalidade_limite *= 0.5
    if habitacao == "rent": 
        penalidade_score -= 30
        penalidade_limite *= 0.85
    if ahorro == "little": 
        penalidade_score -= 20
        penalidade_limite *= 0.9
    if corriente == "little": 
        penalidade_score -= 20
        penalidade_limite *= 0.9
    
    score_final = max(score + penalidade_score, 300)
    
    # 2. Definição de Segmentos e Limites Base
    if score_final >= 700: segmento, limite_base = "SUPER PRIME", 18000
    elif score_final >= 650: segmento, limite_base = "PRIME", 10000
    elif score_final >= 600: segmento, limite_base = "STANDARD", 5000
    elif score_final >= 520: segmento, limite_base = "NEAR PRIME", 2500
    elif score_final >= 460: segmento, limite_base = "REVIEW", 1000
    else: segmento, limite_base = "SUBPRIME", 0

    limite_final = int(limite_base * penalidade_limite)
    
    # 3. Decisão Final (Status)
    if trabalho == 0 and corriente == "little":
        status, icon, cor, motivo = "RECHAZADO", "✖", "#dc2626", "Riesgo crítico: sin empleo y baja liquidez."
    elif score_final < 460: 
        status, icon, cor, motivo = "RECHAZADO", "✖", "#dc2626", "Score bajo política mínima."
    elif valor_solicitado <= limite_final: 
        status, icon, cor, motivo = "APROBADO", "✔", "#16a34a", "Dentro del límite aprobado."
    else: 
        status, icon, cor, motivo = "RECHAZADO", "✖", "#dc2626", "Excede límite permitido."

    return {
        "score": score_final,
        "segmento": segmento,
        "limite": limite_final,
        "status": status,
        "icon": icon,
        "cor": cor,
        "motivo": motivo
    }