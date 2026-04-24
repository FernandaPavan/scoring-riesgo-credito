import pandas as pd
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
# FUNÇÕES DE TRADUÇÃO E MONTAGEM
# ============================================

def traduzir_inputs(genero_sel, trabalho_sel, vivienda_sel, ahorro_sel, corriente_sel, finalidad_sel):
    """Traduz as seleções da interface para os valores esperados pelo modelo."""
    return (
        MAP_GENERO[genero_sel], 
        MAP_TRABAJO[trabalho_sel], 
        MAP_VIVIENDA[vivienda_sel],
        MAP_AHORRO[ahorro_sel], 
        MAP_CORRIENTE[corriente_sel], 
        MAP_FINALIDAD[finalidad_sel]
    )

def montar_entrada(genero, trabajo, vivienda, ahorro, corriente, finalidad, edad, duracion, monto):
    """Cria o DataFrame inicial com as colunas que o modelo pkl conhece."""
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
# PROCESSAMENTO TÉCNICO (FEATURE ENGINEERING)
# ============================================

def criar_faixas(X):
    """Aplica o binning (mesmo processo do treinamento)."""
    X = X.copy()
    
    # Faixa Etária
    X['Faixa_Etaria'] = pd.cut(
        X['Idade'], bins=[19, 29, 39, 49, 59, 69, 79], include_lowest=True
    ).astype(str)
    
    # Faixa Duração
    X['Faixa_Duracao'] = pd.cut(
        X['Duracao'], bins=[4, 16, 28, 40, 52, 64, 76], include_lowest=True
    ).astype(str)
    
    # Faixa Crédito
    X['Faixa_Credito'] = pd.cut(
        X['Valor_credito'], bins=[250, 1250, 2250, 3250, 4250, 5250, 6250], include_lowest=True
    ).astype(str)
    
    # Remove colunas numéricas originais que foram transformadas
    return X.drop(columns=['Idade', 'Duracao', 'Valor_credito'], errors='ignore')

def preparar_dados(df, bins_woe, modelo):
    """Executa o pipeline completo: Faixas -> WOE -> Alinhamento de Colunas."""
    # 1. Cria faixas categóricas
    df = criar_faixas(df)
    
    # 2. Aplica transformação Weight of Evidence (WOE)
    df_woe = sc.woebin_ply(df, bins_woe)
    
    # 3. Garante que as colunas estejam na ordem exata do modelo e sem NaNs
    df_woe = df_woe.reindex(columns=modelo.feature_names_in_, fill_value=0).fillna(0)
    
    return df_woe