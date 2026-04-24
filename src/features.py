import pandas as pd
import scorecardpy as sc

# Dicionários: Chave em Espanhol (UI) -> Valor que o Modelo conhece
MAP_GENERO = {"Masculino": "male", "Femenino": "female"}
MAP_TRABAJO = {"Desempleado": 0, "Básico": 1, "Calificado": 2, "Especialista":3}
MAP_VIVIENDA = {"Propia": "own", "Alquilada": "rent", "Gratuita": "free"}
MAP_AHORRO = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}
MAP_CORRIENTE = {"Bajo": "little", "Medio": "moderate", "Alto": "rich"}
MAP_FINALIDAD = {
    "Auto": "car", "Muebles": "furniture/equipment", "Electrónicos": "radio/TV",
    "Negocios": "business", "Educación": "education", "Reparaciones": "repairs", "Otros": "vacation/others"
}

def traduzir_inputs(genero_sel, trabajo_sel, vivienda_sel, ahorro_sel, corriente_sel, finalidad_sel):
    try:
        return (
            MAP_GENERO[genero_sel], MAP_TRABAJO[trabajo_sel], MAP_VIVIENDA[vivienda_sel],
            MAP_AHORRO[ahorro_sel], MAP_CORRIENTE[corriente_sel], MAP_FINALIDAD[finalidad_sel]
        )
    except KeyError as e:
        raise ValueError(f"Valor inválido: {e}")

def montar_entrada(genero, trabajo, vivienda, ahorro, corriente, finalidad, edad, duracion, monto):
    # Nomes das colunas em Português conforme seu modelo pkl
    return pd.DataFrame({
        "Genero": [genero],
        "Trabalho": [trabajo],
        "Habitacao": [vivienda],
        "Conta_poupanca": [ahorro],
        "Conta_corrente": [corriente],
        "Finalidade": [finalidad],
        "Idade": [edad],
        "Duracao": [duracion],
        "Valor_credito": [monto]
    })



# ============================================
# FEATURE ENGINEERING (IGUAL AO TREINO)
# ============================================

def criar_faixas(X):
    X = X.copy()

    # Faixa etária
    X['Faixa_Etaria'] = pd.cut(
        X['Idade'],
        bins=[19, 29, 39, 49, 59, 69, 79],
        include_lowest=True
    ).astype(str)

    # Faixa duração
    X['Faixa_Duracao'] = pd.cut(
        X['Duracao'],
        bins=[4, 16, 28, 40, 52, 64, 76],
        include_lowest=True
    ).astype(str)

    # Faixa crédito
    X['Faixa_Credito'] = pd.cut(
        X['Valor_credito'],
        bins=[250, 1250, 2250, 3250, 4250, 5250, 6250],
        include_lowest=True
    ).astype(str)

    # Remove originais
    X = X.drop(columns=['Idade', 'Duracao', 'Valor_credito'], errors='ignore')

    return X


# ============================================
# PIPE COMPLETO (PRODUÇÃO)
# ============================================

def preparar_dados(df, bins_woe, modelo):

    df = criar_faixas(df)

    df_woe = sc.woebin_ply(df, bins_woe)

    df_woe = df_woe.reindex(
        columns=modelo.feature_names_in_,
        fill_value=0
    )

    # 🔥 ESSENCIAL
    df_woe = df_woe.fillna(0)

    return df_woe