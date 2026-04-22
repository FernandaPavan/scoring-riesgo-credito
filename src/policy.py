import numpy as np

def get_score(prob, score_params):
    """
    SCORE: Transforma a probabilidade do modelo em pontuação (0-1000).
    """
    factor = score_params["pdo"] / np.log(2)
    
    # CORREÇÃO: O sinal correto é SOMA (+) para alinhar a escala do score
    offset = score_params["base_score"] + factor * np.log(score_params["base_odds"])
    
    # Evita log de zero ou valores infinitos
    prob = max(min(prob, 0.9999), 0.0001)
    
    # Cálculo do Score: Quanto menor a prob de inadimplência, maior o score final
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
        
    # Se a moradia for gratuita (free), aplicamos uma leve redução no limite por segurança
    if habitacao == "free":
        penalidade_limite *= 0.90
        
    if ahorro == "little": 
        penalidade_score -= 20
        penalidade_limite *= 0.9
        
    if corriente == "little": 
        penalidade_score -= 20
        penalidade_limite *= 0.9
    
    # Cálculo do Score Final após penalidades
    score_final = max(score + penalidade_score, 300)
    
    # 2. Definição de Segmentos e Limites Base
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

    # O limite final é o limite da faixa ajustado pelas condições do cliente
    limite_final = int(limite_base * penalidade_limite)
    
    # 3. Decisão Final (Status)
    # Regra Crítica: Desempregado + Baixa Liquidez
    if trabalho == 0 and corriente == "little":
        status, icon, cor, motivo = "RECHAZADO", "✖", "#dc2626", "Riesgo crítico: sin empleo y baja liquidez."
    
    # Regra de Score Mínimo
    elif score_final < 460: 
        status, icon, cor, motivo = "RECHAZADO", "✖", "#dc2626", f"Score insuficiente para política ({score_final} pts)."
    
    # Regra de Capacidade de Pagamento (Limite)
    elif valor_solicitado <= limite_final: 
        status, icon, cor, motivo = "APROBADO", "✔", "#16a34a", "Dentro del límite aprobado."
    
    # Caso o valor solicitado seja maior que o limite calculado
    else: 
        status, icon, cor, motivo = "RECHAZADO", "✖", "#dc2626", f"Excede límite permitido (Máx: ${limite_final:,.0f})."

    return {
        "score": score_final,
        "segmento": segmento,
        "limite": limite_final,
        "status": status,
        "icon": icon,
        "cor": cor,
        "motivo": motivo
    }