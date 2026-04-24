import numpy as np

def get_score(prob_default, score_params):
    prob_default = float(np.clip(prob_default, 0.0001, 0.9999))

    pdo = score_params.get("pdo", 20)
    base_score = score_params.get("base_score", 600)
    base_odds = score_params.get("base_odds", 50)

    factor = pdo / np.log(2)
    offset = base_score - factor * np.log(base_odds)

    odds = (1 - prob_default) / prob_default

    score = int(round(offset + factor * np.log(odds)))

    return max(score, 300)


def apply_business_policy(score, prob_default, valor_solicitado, cutoffs):

    reject_cutoff = cutoffs["reject_cutoff"]
    analysis_cutoff = cutoffs["analysis_cutoff"]

    if score >= 700:
        segmento = "SUPER PRIME"; base_limit = 18000
    elif score >= 650:
        segmento = "PRIME"; base_limit = 10000
    elif score >= 600:
        segmento = "STANDARD"; base_limit = 5000
    elif score >= 520:
        segmento = "NEAR PRIME"; base_limit = 2500
    elif score >= 460:
        segmento = "REVIEW"; base_limit = 1000
    else:
        segmento = "SUBPRIME"; base_limit = 500

    risco_factor = (1 - prob_default)
    limite_sugerido = int(max(500, base_limit * (0.7 + risco_factor * 0.6)))

    if score < reject_cutoff:
        return build_response(score, segmento, limite_sugerido, "RECHAZADO", "❌", "#dc2626", "Score abaixo do cutoff mínimo")

    if score < analysis_cutoff:
        return build_response(score, segmento, limite_sugerido, "EN ANÁLISIS", "⚠️", "#facc15", "Perfil intermediário")

    if valor_solicitado <= limite_sugerido:
        return build_response(score, segmento, limite_sugerido, "APROBADO", "✅", "#16a34a", "Dentro do limite")

    return build_response(score, segmento, limite_sugerido, "RECHAZADO", "❌", "#dc2626", "Excede limite")


def build_response(score, segmento, limite, status, icon, cor, motivo):
    return {
        "score": score,
        "segmento": segmento,
        "limite": limite,
        "status": status,
        "icon": icon,
        "cor": cor,
        "motivo": motivo
    }