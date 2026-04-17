import pandas as pd

def criar_faixas(X):
    """
    Função de feature engineering usada no pipeline.
    Cria variáveis categóricas (faixas) a partir de variáveis numéricas.
    """

    X = X.copy()

    # ============================================
    # FAIXA ETÁRIA
    # ============================================
    X['Faixa_Etaria'] = pd.cut(
        X['Idade'],
        bins=[19, 29, 39, 49, 59, 69, 79],
        include_lowest=True
    ).astype(str)

    # ============================================
    # FAIXA DE DURAÇÃO
    # ============================================
    X['Faixa_Duracao'] = pd.cut(
        X['Duracao'],
        bins=[4, 16, 28, 40, 52, 64, 76],
        include_lowest=True
    ).astype(str)

    # ============================================
    # FAIXA DE CRÉDITO
    # ============================================
    X['Faixa_Credito'] = pd.cut(
        X['Valor_credito'],
        bins=[250, 1250, 2250, 3250, 4250, 5250, 6250],
        include_lowest=True
    ).astype(str)

    # ============================================
    # REMOVER VARIÁVEIS ORIGINAIS
    # ============================================
    X = X.drop(columns=['Idade', 'Duracao', 'Valor_credito'], errors='ignore')

    return X