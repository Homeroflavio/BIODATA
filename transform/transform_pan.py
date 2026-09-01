from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_RAIZ = Path(__file__).resolve().parent.parent

PASTA_DADOS_BRUTOS = (
    PASTA_RAIZ / "dados_brutos"
)

PASTA_DADOS_FINAIS = (
    PASTA_RAIZ / "dados_finais"
)


# ------------------------------------------------------------
# ARQUIVOS DE ENTRADA
# ------------------------------------------------------------

ARQUIVO_PAN_DADOS = (
    PASTA_DADOS_BRUTOS
    / "pan_dados_raw.csv"
)

ARQUIVO_PAN_ESPECIES = (
    PASTA_DADOS_BRUTOS
    / "pan_especies_raw.csv"
)

ARQUIVO_PAN_BIOMAS = (
    PASTA_DADOS_BRUTOS
    / "pan_biomas_raw.csv"
)

ARQUIVO_PAN_ESTADOS = (
    PASTA_DADOS_BRUTOS
    / "pan_estados_raw.csv"
)


# ------------------------------------------------------------
# ARQUIVOS DE SAÍDA
# ------------------------------------------------------------

ARQUIVO_DIM_PAN = (
    PASTA_DADOS_FINAIS
    / "dim_pan.csv"
)

ARQUIVO_PAN_ESPECIE = (
    PASTA_DADOS_FINAIS
    / "pan_especie.csv"
)

ARQUIVO_PAN_BIOMA = (
    PASTA_DADOS_FINAIS
    / "pan_bioma.csv"
)

ARQUIVO_PAN_ESTADO = (
    PASTA_DADOS_FINAIS
    / "pan_estado.csv"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def limpar_texto(valor):
    """
    Remove espaços extras de valores textuais.

    Mantém valores nulos como None.
    """

    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if not valor:
        return None

    return valor


def limpar_dataframe_texto(dataframe):
    """
    Aplica limpeza básica a todas as colunas de texto.
    """

    dataframe = dataframe.copy()

    for coluna in dataframe.select_dtypes(
        include="object"
    ).columns:

        dataframe[coluna] = dataframe[coluna].apply(
            limpar_texto
        )

    return dataframe


def converter_data(serie):
    """
    Converte valores para data.

    Datas inválidas são transformadas em NaT.
    """

    return pd.to_datetime(
        serie,
        errors="coerce"
    ).dt.date


def salvar_csv(
    dataframe,
    caminho
):
    """
    Salva dataframe em CSV.
    """

    dataframe.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Salvo: {caminho.name}")


# ============================================================
# CARREGAMENTO
# ============================================================

def carregar_dados():

    print("\nCarregando dados brutos do PAN...")

    df_pan_dados = pd.read_csv(
        ARQUIVO_PAN_DADOS,
        dtype=str
    )

    df_pan_especies = pd.read_csv(
        ARQUIVO_PAN_ESPECIES,
        dtype=str
    )

    df_pan_biomas = pd.read_csv(
        ARQUIVO_PAN_BIOMAS,
        dtype=str
    )

    df_pan_estados = pd.read_csv(
        ARQUIVO_PAN_ESTADOS,
        dtype=str
    )

    print(
        f"Carregado: pan_dados_raw.csv "
        f"({len(df_pan_dados)} registros)"
    )

    print(
        f"Carregado: pan_especies_raw.csv "
        f"({len(df_pan_especies)} registros)"
    )

    print(
        f"Carregado: pan_biomas_raw.csv "
        f"({len(df_pan_biomas)} registros)"
    )

    print(
        f"Carregado: pan_estados_raw.csv "
        f"({len(df_pan_estados)} registros)"
    )

    return (
        df_pan_dados,
        df_pan_especies,
        df_pan_biomas,
        df_pan_estados
    )


# ============================================================
# TRANSFORMAÇÃO — DIM_PAN
# ============================================================

def transformar_dim_pan(dataframe):

    print("\nTransformando dim_pan...")

    dataframe = limpar_dataframe_texto(
        dataframe
    )

    # Seleciona e renomeia as colunas necessárias.
    df_final = dataframe[
        [
            "idPan",
            "panNome",
            "panNomeCompleto",
            "panAbrangenciaTaxonomica",
            "panAbrangenciaGeografica",
            "panCiclo",
            "panStatus",
            "panInicioData",
            "panFimData",
            "panInicioAno",
            "panFimAno",
            "panStatusLegal",
            "panSite"
        ]
    ].copy()

    df_final.columns = [
        "id_pan",
        "nome",
        "nome_completo",
        "abrangencia_taxonomica",
        "abrangencia_geografica",
        "ciclo",
        "status",
        "data_inicio",
        "data_fim",
        "ano_inicio",
        "ano_fim",
        "status_legal",
        "site"
    ]

    # Conversão das datas.
    df_final["data_inicio"] = converter_data(
        df_final["data_inicio"]
    )

    df_final["data_fim"] = converter_data(
        df_final["data_fim"]
    )

    # Conversão dos anos.
    df_final["ano_inicio"] = pd.to_numeric(
        df_final["ano_inicio"],
        errors="coerce"
    ).astype("Int64")

    df_final["ano_fim"] = pd.to_numeric(
        df_final["ano_fim"],
        errors="coerce"
    ).astype("Int64")

    # Remove registros sem identificador de PAN.
    df_final = df_final.dropna(
        subset=["id_pan"]
    )

    # Remove duplicatas.
    df_final = df_final.drop_duplicates(
        subset=["id_pan"]
    )

    print(
        f"PANs preparados: {len(df_final)}"
    )

    return df_final


# ============================================================
# TRANSFORMAÇÃO — PAN_ESPECIE
# ============================================================

def transformar_pan_especie(dataframe):

    print("\nTransformando pan_especie...")

    dataframe = limpar_dataframe_texto(
        dataframe
    )

    # O idTaxon é preservado apenas como dado bruto/original
    # nesta etapa. Para a relação final, utilizaremos o nome
    # científico para encontrar o especie_id durante o load.
    df_final = dataframe[
        [
            "idPan",
            "taxonNome"
        ]
    ].copy()

    df_final.columns = [
        "id_pan",
        "nome_cientifico"
    ]

    # Remove registros sem chave da relação.
    df_final = df_final.dropna(
        subset=[
            "id_pan",
            "nome_cientifico"
        ]
    )

    # Remove duplicatas.
    df_final = df_final.drop_duplicates(
        subset=[
            "id_pan",
            "nome_cientifico"
        ]
    )

    print(
        f"Relações PAN × espécie preparadas: "
        f"{len(df_final)}"
    )

    return df_final


# ============================================================
# TRANSFORMAÇÃO — PAN_BIOMA
# ============================================================

def transformar_pan_bioma(dataframe):

    print("\nTransformando pan_bioma...")

    dataframe = limpar_dataframe_texto(
        dataframe
    )

    df_final = dataframe[
        [
            "idPan",
            "panBioma"
        ]
    ].copy()

    df_final.columns = [
        "id_pan",
        "bioma"
    ]

    df_final = df_final.dropna(
        subset=[
            "id_pan",
            "bioma"
        ]
    )

    df_final = df_final.drop_duplicates(
        subset=[
            "id_pan",
            "bioma"
        ]
    )

    print(
        f"Relações PAN × bioma preparadas: "
        f"{len(df_final)}"
    )

    return df_final


# ============================================================
# TRANSFORMAÇÃO — PAN_ESTADO
# ============================================================

def transformar_pan_estado(dataframe):

    print("\nTransformando pan_estado...")

    dataframe = limpar_dataframe_texto(
        dataframe
    )

    df_final = dataframe[
        [
            "idPan",
            "siglaEstado"
        ]
    ].copy()

    df_final.columns = [
        "id_pan",
        "sigla_estado"
    ]

    df_final = df_final.dropna(
        subset=[
            "id_pan",
            "sigla_estado"
        ]
    )

    # Normaliza siglas.
    df_final["sigla_estado"] = (
        df_final["sigla_estado"]
        .str.upper()
        .str.strip()
    )

    df_final = df_final.drop_duplicates(
        subset=[
            "id_pan",
            "sigla_estado"
        ]
    )

    print(
        f"Relações PAN × estado preparadas: "
        f"{len(df_final)}"
    )

    return df_final


# ============================================================
# VALIDAÇÕES
# ============================================================

def validar_dim_pan(dataframe):

    print("\nValidando dim_pan...")

    duplicados = dataframe[
        "id_pan"
    ].duplicated().sum()

    nulos = dataframe[
        "id_pan"
    ].isna().sum()

    print(f"IDs de PAN duplicados: {duplicados}")
    print(f"IDs de PAN nulos: {nulos}")

    if duplicados > 0 or nulos > 0:

        raise ValueError(
            "Validação de dim_pan falhou."
        )


def validar_relacao(
    dataframe,
    nome,
    colunas_chave
):

    print(f"\nValidando {nome}...")

    nulos = dataframe[
        colunas_chave
    ].isna().sum().sum()

    duplicados = dataframe.duplicated(
        subset=colunas_chave
    ).sum()

    print(f"Chaves nulas: {nulos}")
    print(f"Relações duplicadas: {duplicados}")

    if nulos > 0 or duplicados > 0:

        raise ValueError(
            f"Validação de {nome} falhou."
        )


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def transformar_pan():

    print("=" * 60)
    print("TRANSFORMAÇÃO PAN — BIODATA")
    print("=" * 60)

    # --------------------------------------------------------
    # CARREGAMENTO
    # --------------------------------------------------------

    (
        df_pan_dados_raw,
        df_pan_especies_raw,
        df_pan_biomas_raw,
        df_pan_estados_raw
    ) = carregar_dados()

    # --------------------------------------------------------
    # TRANSFORMAÇÃO
    # --------------------------------------------------------

    df_dim_pan = transformar_dim_pan(
        df_pan_dados_raw
    )

    df_pan_especie = transformar_pan_especie(
        df_pan_especies_raw
    )

    df_pan_bioma = transformar_pan_bioma(
        df_pan_biomas_raw
    )

    df_pan_estado = transformar_pan_estado(
        df_pan_estados_raw
    )

    # --------------------------------------------------------
    # VALIDAÇÕES
    # --------------------------------------------------------

    validar_dim_pan(
        df_dim_pan
    )

    validar_relacao(
        df_pan_especie,
        "pan_especie",
        [
            "id_pan",
            "nome_cientifico"
        ]
    )

    validar_relacao(
        df_pan_bioma,
        "pan_bioma",
        [
            "id_pan",
            "bioma"
        ]
    )

    validar_relacao(
        df_pan_estado,
        "pan_estado",
        [
            "id_pan",
            "sigla_estado"
        ]
    )

    # --------------------------------------------------------
    # SALVAMENTO
    # --------------------------------------------------------

    print("\nSalvando dados finais...")

    PASTA_DADOS_FINAIS.mkdir(
        exist_ok=True
    )

    salvar_csv(
        df_dim_pan,
        ARQUIVO_DIM_PAN
    )

    salvar_csv(
        df_pan_especie,
        ARQUIVO_PAN_ESPECIE
    )

    salvar_csv(
        df_pan_bioma,
        ARQUIVO_PAN_BIOMA
    )

    salvar_csv(
        df_pan_estado,
        ARQUIVO_PAN_ESTADO
    )

    # ========================================================
    # RESUMO
    # ========================================================

    print("\n" + "=" * 60)
    print("RESUMO DA TRANSFORMAÇÃO PAN")
    print("=" * 60)

    print(
        f"\ndim_pan: {len(df_dim_pan)} registros"
    )

    print(
        f"pan_especie: "
        f"{len(df_pan_especie)} registros"
    )

    print(
        f"pan_bioma: "
        f"{len(df_pan_bioma)} registros"
    )

    print(
        f"pan_estado: "
        f"{len(df_pan_estado)} registros"
    )

    print("\nDados finais salvos em:")

    print(
        PASTA_DADOS_FINAIS
    )

    print("\n" + "=" * 60)
    print("TRANSFORMAÇÃO FINALIZADA")
    print("=" * 60)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    transformar_pan()