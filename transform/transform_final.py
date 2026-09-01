import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_PROJETO = Path(__file__).resolve().parent.parent

PASTA_TRANSFORMADOS = (
    PASTA_PROJETO / "dados_transformados"
)

PASTA_FINAL = (
    PASTA_PROJETO / "dados_finais"
)


# ------------------------------------------------------------
# ARQUIVOS DE ENTRADA
# ------------------------------------------------------------

ARQUIVO_ICMBIO_DIM_ESPECIE = (
    PASTA_TRANSFORMADOS / "icmbio_dim_especie.csv"
)

ARQUIVO_ICMBIO_FATO_AVALIACAO = (
    PASTA_TRANSFORMADOS / "icmbio_fato_avaliacao.csv"
)

ARQUIVO_IUCN_FATO_AVALIACAO = (
    PASTA_TRANSFORMADOS / "iucn_fato_avaliacao.csv"
)

ARQUIVO_IUCN_DIM_CATEGORIA = (
    PASTA_TRANSFORMADOS / "iucn_dim_categoria_risco.csv"
)

ARQUIVO_IUCN_NOME_POPULAR = (
    PASTA_TRANSFORMADOS / "iucn_nome_popular.csv"
)

ARQUIVO_GBIF_DIM_LOCAL = (
    PASTA_TRANSFORMADOS / "gbif_dim_local.csv"
)

ARQUIVO_GBIF_FATO_OCORRENCIA = (
    PASTA_TRANSFORMADOS / "gbif_fato_ocorrencia.csv"
)


# ------------------------------------------------------------
# ARQUIVOS DE SAÍDA
# ------------------------------------------------------------

ARQUIVO_FINAL_DIM_ESPECIE = (
    PASTA_FINAL / "dim_especie.csv"
)

ARQUIVO_FINAL_FATO_AVALIACAO_ICMBIO = (
    PASTA_FINAL / "fato_avaliacao_icmbio.csv"
)

ARQUIVO_FINAL_FATO_AVALIACAO_IUCN = (
    PASTA_FINAL / "fato_avaliacao_iucn.csv"
)

ARQUIVO_FINAL_DIM_CATEGORIA_RISCO = (
    PASTA_FINAL / "dim_categoria_risco.csv"
)

ARQUIVO_FINAL_DIM_LOCAL = (
    PASTA_FINAL / "dim_local.csv"
)

ARQUIVO_FINAL_FATO_OCORRENCIA_GBIF = (
    PASTA_FINAL / "fato_ocorrencia_gbif.csv"
)


# ============================================================
# CARREGAR CSV
# ============================================================

def carregar_csv(caminho: Path) -> pd.DataFrame:
    """
    Carrega um arquivo CSV e exibe informações básicas.
    """

    if not caminho.exists():

        raise FileNotFoundError(
            f"Arquivo não encontrado:\n{caminho}"
        )

    dataframe = pd.read_csv(caminho)

    print(
        f"Carregado: {caminho.name} "
        f"({len(dataframe)} registros)"
    )

    return dataframe


# ============================================================
# TRANSFORMAR DIMENSÃO DE ESPÉCIE FINAL
# ============================================================

def criar_dim_especie_final(
    df_icmbio_especie: pd.DataFrame,
    df_iucn_nome_popular: pd.DataFrame
) -> pd.DataFrame:
    """
    Cria a dimensão final de espécies.

    Utiliza o ICMBio como fonte principal da taxonomia
    e adiciona o nome popular obtido nos dados da IUCN.

    Não cria id_especie.

    O PostgreSQL será responsável pela geração do ID
    durante o processo de Load.
    """

    print(
        "\nCriando dim_especie final..."
    )

    # --------------------------------------------------------
    # CÓPIA PARA EVITAR ALTERAR O DATAFRAME ORIGINAL
    # --------------------------------------------------------

    df_especie = df_icmbio_especie.copy()

    df_nome_popular = (
        df_iucn_nome_popular.copy()
    )

    # --------------------------------------------------------
    # PADRONIZAR NOME CIENTÍFICO
    # --------------------------------------------------------

    df_especie[
        "nome_cientifico"
    ] = (
        df_especie[
            "nome_cientifico"
        ]
        .astype(str)
        .str.strip()
    )

    df_nome_popular[
        "nome_cientifico"
    ] = (
        df_nome_popular[
            "nome_cientifico"
        ]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # TRATAR NOME POPULAR VAZIO
    # --------------------------------------------------------

    df_nome_popular[
        "nome_popular"
    ] = (
        df_nome_popular[
            "nome_popular"
        ]
        .replace("", pd.NA)
    )

    # --------------------------------------------------------
    # REMOVER DUPLICATAS DO CSV DE NOMES POPULARES
    # --------------------------------------------------------

    df_nome_popular = (
        df_nome_popular
        .drop_duplicates(
            subset=["nome_cientifico"],
            keep="first"
        )
    )

    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    df_final = df_especie.merge(
        df_nome_popular[
            [
                "nome_cientifico",
                "nome_popular"
            ]
        ],
        on="nome_cientifico",
        how="left"
    )

    # --------------------------------------------------------
    # GARANTIR UMA ESPÉCIE POR LINHA
    # --------------------------------------------------------

    df_final = (
        df_final
        .drop_duplicates(
            subset=["nome_cientifico"],
            keep="first"
        )
    )

    # --------------------------------------------------------
    # ORGANIZAR COLUNAS
    # --------------------------------------------------------

    colunas_esperadas = [

        "nome_cientifico",

        "nome_popular",

        "reino",

        "filo",

        "classe",

        "ordem",

        "familia",

        "genero",

        "grupo_taxonomico"
    ]

    df_final = df_final[
        colunas_esperadas
    ]

    # --------------------------------------------------------
    # RESETAR ÍNDICE
    # --------------------------------------------------------

    df_final = df_final.reset_index(
        drop=True
    )

    print(
        f"Espécies na dimensão final: "
        f"{len(df_final)}"
    )

    print(
        f"Espécies com nome popular: "
        f"{df_final['nome_popular'].notna().sum()}"
    )

    print(
        f"Espécies sem nome popular: "
        f"{df_final['nome_popular'].isna().sum()}"
    )

    return df_final


# ============================================================
# VALIDAR DIM_ESPECIE FINAL
# ============================================================

def validar_dim_especie_final(
    df_dim_especie: pd.DataFrame
) -> None:
    """
    Executa validações básicas na dimensão final.
    """

    print(
        "\nValidando dim_especie final..."
    )

    duplicados = (
        df_dim_especie[
            "nome_cientifico"
        ]
        .duplicated()
        .sum()
    )

    nulos_nome_cientifico = (
        df_dim_especie[
            "nome_cientifico"
        ]
        .isna()
        .sum()
    )

    print(
        f"Nome científico duplicado: "
        f"{duplicados}"
    )

    print(
        f"Nome científico nulo: "
        f"{nulos_nome_cientifico}"
    )

    if duplicados > 0:

        raise ValueError(
            "Existem nomes científicos duplicados "
            "na dim_especie final."
        )

    if nulos_nome_cientifico > 0:

        raise ValueError(
            "Existem nomes científicos nulos "
            "na dim_especie final."
        )

    print(
        "Validação concluída com sucesso."
    )


# ============================================================
# SALVAR DATAFRAME
# ============================================================

def salvar_csv(
    dataframe: pd.DataFrame,
    caminho: Path
) -> None:
    """
    Salva um DataFrame em CSV.
    """

    dataframe.to_csv(
        caminho,
        index=False,
        encoding="utf-8"
    )

    print(
        f"Salvo: {caminho}"
    )


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def executar_transformacao_final() -> None:

    print("=" * 60)
    print("TRANSFORMAÇÃO FINAL — BIODATA")
    print("=" * 60)

    # --------------------------------------------------------
    # CRIAR PASTA FINAL
    # --------------------------------------------------------

    PASTA_FINAL.mkdir(
        exist_ok=True
    )

    print(
        "\nCarregando dados transformados..."
    )

    # --------------------------------------------------------
    # ICMBIO
    # --------------------------------------------------------

    df_icmbio_dim_especie = carregar_csv(
        ARQUIVO_ICMBIO_DIM_ESPECIE
    )

    df_icmbio_fato_avaliacao = carregar_csv(
        ARQUIVO_ICMBIO_FATO_AVALIACAO
    )

    # --------------------------------------------------------
    # IUCN
    # --------------------------------------------------------

    df_iucn_fato_avaliacao = carregar_csv(
        ARQUIVO_IUCN_FATO_AVALIACAO
    )

    df_iucn_dim_categoria = carregar_csv(
        ARQUIVO_IUCN_DIM_CATEGORIA
    )

    df_iucn_nome_popular = carregar_csv(
        ARQUIVO_IUCN_NOME_POPULAR
    )

    # --------------------------------------------------------
    # GBIF
    # --------------------------------------------------------

    df_gbif_dim_local = carregar_csv(
        ARQUIVO_GBIF_DIM_LOCAL
    )

    df_gbif_fato_ocorrencia = carregar_csv(
        ARQUIVO_GBIF_FATO_OCORRENCIA
    )

    # ========================================================
    # CRIAR DIMENSÃO FINAL DE ESPÉCIE
    # ========================================================

    df_dim_especie_final = (
        criar_dim_especie_final(
            df_icmbio_especie=df_icmbio_dim_especie,
            df_iucn_nome_popular=df_iucn_nome_popular
        )
    )

    # ========================================================
    # VALIDAR
    # ========================================================

    validar_dim_especie_final(
        df_dim_especie_final
    )

    # ========================================================
    # SALVAR DIM_ESPECIE FINAL
    # ========================================================

    print(
        "\nSalvando dados finais..."
    )

    salvar_csv(
        dataframe=df_dim_especie_final,
        caminho=ARQUIVO_FINAL_DIM_ESPECIE
    )

    # ========================================================
    # SALVAR DEMAIS TABELAS
    # ========================================================

    salvar_csv(
        dataframe=df_icmbio_fato_avaliacao,
        caminho=ARQUIVO_FINAL_FATO_AVALIACAO_ICMBIO
    )

    salvar_csv(
        dataframe=df_iucn_fato_avaliacao,
        caminho=ARQUIVO_FINAL_FATO_AVALIACAO_IUCN
    )

    salvar_csv(
        dataframe=df_iucn_dim_categoria,
        caminho=ARQUIVO_FINAL_DIM_CATEGORIA_RISCO
    )

    salvar_csv(
        dataframe=df_gbif_dim_local,
        caminho=ARQUIVO_FINAL_DIM_LOCAL
    )

    salvar_csv(
        dataframe=df_gbif_fato_ocorrencia,
        caminho=ARQUIVO_FINAL_FATO_OCORRENCIA_GBIF
    )

    # ========================================================
    # RESUMO FINAL
    # ========================================================

    print("\n" + "=" * 60)
    print("RESUMO DA TRANSFORMAÇÃO FINAL")
    print("=" * 60)

    print(
        f"\ndim_especie: "
        f"{len(df_dim_especie_final)} registros"
    )

    print(
        f"fato_avaliacao_icmbio: "
        f"{len(df_icmbio_fato_avaliacao)} registros"
    )

    print(
        f"fato_avaliacao_iucn: "
        f"{len(df_iucn_fato_avaliacao)} registros"
    )

    print(
        f"dim_categoria_risco: "
        f"{len(df_iucn_dim_categoria)} registros"
    )

    print(
        f"dim_local: "
        f"{len(df_gbif_dim_local)} registros"
    )

    print(
        f"fato_ocorrencia_gbif: "
        f"{len(df_gbif_fato_ocorrencia)} registros"
    )

    print(
        f"\nEspécies com nome popular: "
        f"{df_dim_especie_final['nome_popular'].notna().sum()}"
    )

    print(
        f"Espécies sem nome popular: "
        f"{df_dim_especie_final['nome_popular'].isna().sum()}"
    )

    print(
        f"\nDados finais salvos em:\n"
        f"{PASTA_FINAL}"
    )

    print("\n" + "=" * 60)
    print("TRANSFORMAÇÃO FINALIZADA")
    print("=" * 60)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    executar_transformacao_final()