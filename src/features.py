import pandas as pd
import scorecardpy as sc


# ============================================
# FEATURE ENGINEERING (igual ao treino)
# ============================================
def criar_faixas(X):
    X = X.copy()

    X['Faixa_Etaria'] = pd.cut(
        X['Idade'],
        bins=[19, 29, 39, 49, 59, 69, 79],
        include_lowest=True
    ).astype(str)

    X['Faixa_Duracao'] = pd.cut(
        X['Duracao'],
        bins=[4, 16, 28, 40, 52, 64, 76],
        include_lowest=True
    ).astype(str)

    X['Faixa_Credito'] = pd.cut(
        X['Valor_credito'],
        bins=[250, 1250, 2250, 3250, 4250, 5250, 6250],
        include_lowest=True
    ).astype(str)

    X = X.drop(columns=['Idade', 'Duracao', 'Valor_credito'], errors='ignore')

    return X


# ============================================
# PIPE COMPLETO DE TRANSFORMAÇÃO
# ============================================
def preparar_dados(df, bins_woe, modelo):
    """
    Pipeline completo:
    1. Feature engineering
    2. WOE
    3. Alinhamento com modelo
    """

    # 1. Feature engineering
    df = criar_faixas(df)

    # 2. WOE
    df_woe = sc.woebin_ply(df, bins_woe)

    # 3. Garantir mesmas colunas do treino
    df_woe = df_woe.reindex(
        columns=modelo.feature_names_in_,
        fill_value=0
    )

    return df_woe


# ============================================
# CONSTRUTOR DE INPUT
# ============================================
def montar_entrada(data_dict):
    return pd.DataFrame(data_dict)