import pandas as pd
import numpy as np
import scorecardpy as sc

# ============================================
# MAPEAMENTOS: UI (Espanhol) -> Técnico (Modelo)
# ============================================
MAP_GENERO = {"Masculino": "male", "Femenino": "female"}
MAP_TRABAJO = {"Desempleado": 0, "Básico": 1, "Calificado": 2, "Especialista": 3}
MAP_VIVIENDA = {"Propia": "own", "Alquilada": "rent", "Gratuita": "free"}
MAP_AHORRO = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}
MAP_CORRIENTE = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}
MAP_FINALIDAD = {
    "Auto": "car",
    "Muebles": "furniture/equipment",
    "Electrónicos": "radio/TV",
    "Negocios": "business",
    "Educación": "education",
    "Reparaciones": "repairs",
    "Otros": "vacation/others"
}

# ============================================
# TRADUÇÃO (ROBUSTA)
# ============================================
def traduzir_inputs(genero_sel, trabalho_sel, vivienda_sel, ahorro_sel, corriente_sel, finalidad_sel):
    try:
        # Retornamos 'corriente' para manter o padrão hispânico da sua UI
        return (
            MAP_GENERO.get(genero_sel, "male"),
            MAP_TRABAJO.get(trabalho_sel, 0),
            MAP_VIVIENDA.get(vivienda_sel, "rent"),
            MAP_AHORRO.get(ahorro_sel, "little"),
            MAP_CORRIENTE.get(corriente_sel, "little"),
            MAP_FINALIDAD.get(finalidad_sel, "vacation/others")
        )
    except Exception as e:
        raise ValueError(f"Erro na tradução de inputs: {e}")

# ============================================
# DATAFRAME INICIAL
# ============================================
def montar_entrada(genero, trabalho, vivienda, ahorro, corriente, finalidad, edad, duracion, monto):
    # IMPORTANTE: O nome do argumento aqui deve ser 'corriente' 
    # para bater com o que o main.py envia.
    df = pd.DataFrame({
        "Genero": [genero],
        "Trabalho": [trabalho],
        "Habitacao": [vivienda],
        "Conta_poupanca": [ahorro],
        "Conta_corrente": [corriente], # Variável interna ajustada
        "Finalidade": [finalidad],
        "Idade": [int(edad)],
        "Duracao": [int(duracion)],
        "Valor_credito": [float(monto)]
    })
    return df

# ============================================
# FEATURE ENGINEERING (CRIAR FAIXAS)
# ============================================
def criar_faixas(X):
    X = X.copy()

    # Proteção contra valores fora do range
    X["Idade"] = X["Idade"].clip(18, 80)
    X["Duracao"] = X["Duracao"].clip(4, 80)
    X["Valor_credito"] = X["Valor_credito"].clip(250, 100000)

    # Binning manual
    X['Faixa_Etaria'] = pd.cut(
        X['Idade'],
        bins=[0, 25, 35, 45, 60, 120],
        labels=["[0,25]", "(25,35]", "(35,45]", "(45,60]", "(60,120]"],
        include_lowest=True
    ).astype(str)

    X['Faixa_Duracao'] = pd.cut(
        X['Duracao'],
        bins=[0, 12, 24, 36, 48, 120],
        labels=["[0,12]", "(12,24]", "(24,36]", "(36,48]", "(48,120]"],
        include_lowest=True
    ).astype(str)

    X['Faixa_Credito'] = pd.cut(
        X['Valor_credito'],
        bins=[0, 2000, 5000, 10000, 20000, 1000000],
        labels=["[0,2000]", "(2000,5000]", "(5000,10000]", "(10000,20000]", "(20000,inf]"],
        include_lowest=True
    ).astype(str)

    X = X.drop(columns=['Idade', 'Duracao', 'Valor_credito'], errors='ignore')
    return X

# ============================================
# PIPELINE COMPLETO
# ============================================
def preparar_dados(df, bins_woe, modelo):
    df_feat = criar_faixas(df)
    df_feat = df_feat.fillna("missing")

    try:
        df_woe = sc.woebin_ply(df_feat, bins_woe)
    except Exception as e:
        raise ValueError(f"Erro ao aplicar WOE: {e}")

    df_final = df_woe.reindex(
        columns=modelo.feature_names_in_,
        fill_value=0
    )

    df_final = df_final.replace([np.inf, -np.inf], 0).fillna(0)
    return df_final