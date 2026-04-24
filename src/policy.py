import numpy as np

def calcular_score(prob, params):
    prob = min(max(prob, 0.0001), 0.9999)

    factor = params["pdo"] / np.log(2)
    offset = params["base_score"] + factor * np.log(params["base_odds"])

    score = int(offset + factor * np.log((1 - prob) / prob))
    return score


def aplicar_penalidades(score, trabalho, habitacao, poupanca, corrente):
    penalidade_score = 0
    penalidade_limite = 1.0

    if trabalho == 0:
        penalidade_score -= 80
        penalidade_limite *= 0.5

    if habitacao == "rent":
        penalidade_score -= 30
        penalidade_limite *= 0.85

    if poupanca == "little":
        penalidade_score -= 20
        penalidade_limite *= 0.9

    if corrente == "little":
        penalidade_score -= 20
        penalidade_limite *= 0.9

    return score + penalidade_score, penalidade_limite


def classificar(score):
    if score >= 700:
        return "SUPER PRIME", 18000
    elif score >= 650:
        return "PRIME", 10000
    elif score >= 600:
        return "STANDARD", 5000
    elif score >= 520:
        return "NEAR PRIME", 2500
    elif score >= 460:
        return "REVIEW", 1000
    else:
        return "SUBPRIME", 0


def decisao_final(score, limite, valor, trabalho, corrente):
    if trabalho == 0 and corrente == "little":
        return "RECHAZADO", "✖", "#dc2626", "Riesgo crítico"

    if score < 460:
        return "RECHAZADO", "✖", "#dc2626", "Score bajo"

    if score < 520:
        return "EN ANÁLISIS", "⚠", "#facc15", "Zona intermedia"

    if valor <= limite:
        return "APROBADO", "✔", "#16a34a", "Dentro del límite"

    return "RECHAZADO", "✖", "#dc2626", "Excede límite"