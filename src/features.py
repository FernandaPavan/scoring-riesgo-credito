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
        return (
            MAP_GENERO.get(genero_sel, "male"),
            MAP_TRABAJO.get(trabalho_sel, 0),
            MAP_VIVIENDA.get(vivienda_sel, "rent"),
            MAP_AHORRO.get(ahorro_sel, "little"),
            MAP_CORRIENTE.get(corriente_sel, "little"),
            MAP_FINALIDAD.get(finalidad_sel, "other")
        )
    except Exception as e:
        raise ValueError(f"Erro na tradução de inputs: {e}")

# ============================================
# DATAFRAME INICIAL
# ============================================
def montar_entrada(genero, trabajo, vivienda, ahorro, corriente, finalidad, edad, duracion, monto):

    df = pd.DataFrame({
        "Genero": [genero],
        "Trabalho": [trabajo],
        "Habitacao": [vivienda],
        "Conta_poupanca": [ahorro],
        "Conta_corrente": [corriente],
        "Finalidade": [finalidad],
        "Idade": [int(edad)],
        "Duracao": [int(duracion)],
        "Valor_credito": [float(monto)]
    })

    return df

# ============================================
# FEATURE ENGINEERING
# ============================================
def criar_faixas(X):
    X = X.copy()

    # Proteção contra valores fora do range
    X["Idade"] = X["Idade"].clip(18, 80)
    X["Duracao"] = X["Duracao"].clip(4, 80)
    X["Valor_credito"] = X["Valor_credito"].clip(250, 100000)

    # Faixa Etária
    X['Faixa_Etaria'] = pd.cut(
        X['Idade'],
        bins=[18, 29, 39, 49, 59, 69, 80],
        include_lowest=True
    ).astype(str)

    # Faixa Duração
    X['Faixa_Duracao'] = pd.cut(
        X['Duracao'],
        bins=[4, 16, 28, 40, 52, 64, 80],
        include_lowest=True
    ).astype(str)

    # Faixa Crédito
    X['Faixa_Credito'] = pd.cut(
        X['Valor_credito'],
        bins=[250, 1250, 2250, 3250, 4250, 5250, 100000],
        include_lowest=True
    ).astype(str)

    # Remove originais
    X = X.drop(columns=['Idade', 'Duracao', 'Valor_credito'], errors='ignore')

    return X

# ============================================
# PIPELINE COMPLETO
# ============================================
def preparar_dados(df, bins_woe, modelo):

    # 1. Feature engineering
    df = criar_faixas(df)

    # 2. Tratamento pré-woe (segurança)
    df = df.fillna("missing")

    # 3. WOE
    try:
        df_woe = sc.woebin_ply(df, bins_woe)
    except Exception as e:
        raise ValueError(f"Erro no WOE: {e}")

    # 4. Garantir colunas do modelo
    df_woe = df_woe.reindex(
        columns=modelo.feature_names_in_,
        fill_value=0
    )

    # 5. 🔥 CRÍTICO: remover NaN final
    df_woe = df_woe.replace([np.inf, -np.inf], 0)
    df_woe = df_woe.fillna(0)

    return df_woe