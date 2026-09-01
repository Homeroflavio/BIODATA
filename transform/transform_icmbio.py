import json
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_PROJETO = Path(__file__).resolve().parent.parent

PASTA_DADOS_BRUTOS = (
    PASTA_PROJETO / "dados_brutos"
)

PASTA_DADOS_TRANSFORMADOS = (
    PASTA_PROJETO / "dados_transformados"
)


ARQUIVO_ICMBIO_BRUTO = (
    PASTA_DADOS_BRUTOS / "icmbio_taxon_raw.csv"
)


ARQUIVO_DIM_ESPECIE = (
    PASTA_DADOS_TRANSFORMADOS
    / "icmbio_dim_especie.csv"
)


ARQUIVO_FATO_AVALIACAO_ICMBIO = (
    PASTA_DADOS_TRANSFORMADOS
    / "icmbio_fato_avaliacao.csv"
)


# ============================================================
# LEITURA DOS DADOS
# ============================================================

def carregar_dados_icmbio() -> pd.DataFrame:
    """
    Carrega os dados brutos extraídos do ICMBio.
    """

    if not ARQUIVO_ICMBIO_BRUTO.exists():

        raise FileNotFoundError(
            "Arquivo bruto do ICMBio não encontrado:\n"
            f"{ARQUIVO_ICMBIO_BRUTO}"
        )

    print("Carregando dados brutos do ICMBio...")

    df = pd.read_csv(
        ARQUIVO_ICMBIO_BRUTO,
        dtype=str
    )

    print(
        f"Registros carregados: {len(df)}"
    )

    return df


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def limpar_texto(valor) -> str | None:
    """
    Remove espaços extras e converte valores nulos
    ou vazios em None.
    """

    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if not valor:
        return None

    return valor


def extrair_dado_sensivel(valor) -> bool | None:
    """
    Extrai o campo sensivel.in_sensivel do JSON
    presente na coluna vernacularName.

    Exemplo:

    {
        "sensivel": {
            "in_sensivel": true
        }
    }
    """

    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if not valor:
        return None

    try:

        dados = json.loads(valor)

        sensivel = dados.get(
            "sensivel",
            {}
        )

        return sensivel.get(
            "in_sensivel"
        )

    except (
        json.JSONDecodeError,
        TypeError
    ):

        return None


def definir_grupo_taxonomico(
    classe: str | None
) -> str | None:
    """
    Cria um agrupamento taxonômico simplificado
    para uso posterior em análises e gráficos.
    """

    if not classe:
        return None

    classe_normalizada = (
        classe
        .strip()
        .lower()
    )

    mapa = {

        # ----------------------------------------------------
        # VERTEBRADOS
        # ----------------------------------------------------

        "aves": "aves",

        "mammalia": "mamiferos",

        "amphibia": "anfibios",

        "reptilia": "repteis",


        # ----------------------------------------------------
        # PEIXES
        # ----------------------------------------------------

        "actinopterygii": "peixes",

        "chondrichthyes": "peixes",

        "elasmobranchii": "peixes",


        # ----------------------------------------------------
        # INVERTEBRADOS
        # ----------------------------------------------------

        "insecta": "insetos",

        "arachnida": "aracnideos",

        "malacostraca": "crustaceos",

        "branchiopoda": "crustaceos",

        "gastropoda": "moluscos",

        "bivalvia": "moluscos"
    }

    return mapa.get(
        classe_normalizada,
        "outros"
    )


# ============================================================
# TRANSFORMAÇÃO
# DIM_ESPECIE
# ============================================================

def transformar_dim_especie(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Prepara os dados do ICMBio compatíveis com
    a tabela dim_especie.

    O arquivo taxon.txt da fonte apresenta um deslocamento
    nas colunas taxonômicas.

    Mapeamento identificado:

        reino   <- phylum
        filo    <- class
        classe  <- order
        ordem   <- family
        familia <- subgenus
        genero  <- specificEpithet

    O nome científico confiável é obtido da coluna
    scientificNameAuthorship.
    """

    print(
        "\nTransformando dados para dim_especie..."
    )

    df_transformado = pd.DataFrame({

        # ----------------------------------------------------
        # NOME CIENTÍFICO
        # ----------------------------------------------------

        "nome_cientifico":
            df[
                "scientificNameAuthorship"
            ].apply(limpar_texto),


        # ----------------------------------------------------
        # TAXONOMIA
        # ----------------------------------------------------

        # A coluna "kingdom" contém "species",
        # portanto usamos "phylum" para o reino real.
        "reino":
            df[
                "phylum"
            ].apply(limpar_texto),

        # A coluna "class" contém o filo real.
        "filo":
            df[
                "class"
            ].apply(limpar_texto),

        # A coluna "order" contém a classe real.
        "classe":
            df[
                "order"
            ].apply(limpar_texto),

        # A coluna "family" contém a ordem real.
        "ordem":
            df[
                "family"
            ].apply(limpar_texto),

        # A coluna "subgenus" contém a família real.
        "familia":
            df[
                "subgenus"
            ].apply(limpar_texto),

        # A coluna "specificEpithet" contém o gênero real.
        "genero":
            df[
                "specificEpithet"
            ].apply(limpar_texto)
    })


    # --------------------------------------------------------
    # GRUPO TAXONÔMICO
    # --------------------------------------------------------

    df_transformado[
        "grupo_taxonomico"
    ] = df_transformado[
        "classe"
    ].apply(
        definir_grupo_taxonomico
    )


    # --------------------------------------------------------
    # REMOVER NOMES INVÁLIDOS
    # --------------------------------------------------------

    df_transformado = df_transformado.dropna(
        subset=[
            "nome_cientifico"
        ]
    )


    # --------------------------------------------------------
    # REMOVER DUPLICATAS
    # --------------------------------------------------------

    df_transformado = (
        df_transformado
        .drop_duplicates(
            subset=[
                "nome_cientifico"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    print(
        f"Espécies preparadas: "
        f"{len(df_transformado)}"
    )

    return df_transformado


# ============================================================
# TRANSFORMAÇÃO
# FATO_AVALIACAO_ICMBIO
# ============================================================

def transformar_fato_avaliacao_icmbio(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Prepara os dados compatíveis com
    fato_avaliacao_icmbio.

    Nesta etapa utilizamos nome_cientifico como chave
    temporária.

    O especie_id será associado posteriormente no processo
    de carga no PostgreSQL, através da dim_especie.
    """

    print(
        "\nTransformando dados para "
        "fato_avaliacao_icmbio..."
    )

    df_transformado = pd.DataFrame({

        # ----------------------------------------------------
        # CHAVE TEMPORÁRIA
        # ----------------------------------------------------

        "nome_cientifico":
            df[
                "scientificNameAuthorship"
            ].apply(limpar_texto),


        # ----------------------------------------------------
        # IDENTIFICADOR ORIGINAL DO ICMBIO
        # ----------------------------------------------------

        "taxon_id_icmbio":
            df[
                "taxonID"
            ].apply(limpar_texto),


        # ----------------------------------------------------
        # A PRESENÇA NO ARQUIVO DA LISTA VERMELHA INDICA
        # QUE A ESPÉCIE CONSTA NA LISTA DE AMEAÇADAS
        # ----------------------------------------------------

        "consta_lista_ameacada":
            True,


        # ----------------------------------------------------
        # FLAG DE SENSIBILIDADE
        # ----------------------------------------------------

        "dado_sensivel":
            df[
                "vernacularName"
            ].apply(
                extrair_dado_sensivel
            )
    })


    # --------------------------------------------------------
    # REMOVER REGISTROS SEM NOME CIENTÍFICO
    # --------------------------------------------------------

    df_transformado = df_transformado.dropna(
        subset=[
            "nome_cientifico"
        ]
    )


    # --------------------------------------------------------
    # REMOVER DUPLICATAS
    # --------------------------------------------------------

    df_transformado = (
        df_transformado
        .drop_duplicates(
            subset=[
                "nome_cientifico"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    print(
        f"Avaliações ICMBio preparadas: "
        f"{len(df_transformado)}"
    )

    return df_transformado


# ============================================================
# VALIDAÇÃO E RESUMO
# ============================================================

def mostrar_resumo(
    dim_especie: pd.DataFrame,
    fato_icmbio: pd.DataFrame
) -> None:
    """
    Mostra informações para validar os dados transformados.
    """

    print("\n" + "=" * 60)
    print("RESUMO DA TRANSFORMAÇÃO ICMBIO")
    print("=" * 60)


    # --------------------------------------------------------
    # QUANTIDADES
    # --------------------------------------------------------

    print(
        f"\nRegistros em dim_especie: "
        f"{len(dim_especie)}"
    )

    print(
        f"Registros em fato_avaliacao_icmbio: "
        f"{len(fato_icmbio)}"
    )


    # --------------------------------------------------------
    # NULOS
    # --------------------------------------------------------

    print(
        "\nNulos em dim_especie:"
    )

    print(
        dim_especie
        .isna()
        .sum()
        .to_string()
    )


    # --------------------------------------------------------
    # DISTRIBUIÇÃO TAXONÔMICA
    # --------------------------------------------------------

    print(
        "\nDistribuição por grupo taxonômico:"
    )

    print(
        dim_especie[
            "grupo_taxonomico"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )


    # --------------------------------------------------------
    # DADOS SENSÍVEIS
    # --------------------------------------------------------

    print(
        "\nDistribuição de dados sensíveis:"
    )

    print(
        fato_icmbio[
            "dado_sensivel"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )


    # --------------------------------------------------------
    # AMOSTRA
    # --------------------------------------------------------

    print(
        "\nPrimeiros registros de dim_especie:"
    )

    print(
        dim_especie
        .head()
        .to_string()
    )


# ============================================================
# SALVAMENTO
# ============================================================

def salvar_dados_transformados(
    dim_especie: pd.DataFrame,
    fato_icmbio: pd.DataFrame
) -> None:
    """
    Salva os dados transformados em CSV.
    """

    PASTA_DADOS_TRANSFORMADOS.mkdir(
        exist_ok=True
    )


    # --------------------------------------------------------
    # DIM_ESPECIE
    # --------------------------------------------------------

    dim_especie.to_csv(
        ARQUIVO_DIM_ESPECIE,
        index=False,
        encoding="utf-8"
    )


    # --------------------------------------------------------
    # FATO_AVALIACAO_ICMBIO
    # --------------------------------------------------------

    fato_icmbio.to_csv(
        ARQUIVO_FATO_AVALIACAO_ICMBIO,
        index=False,
        encoding="utf-8"
    )


    print(
        "\nDados transformados salvos:"
    )

    print(
        f"\n - {ARQUIVO_DIM_ESPECIE}"
    )

    print(
        f" - {ARQUIVO_FATO_AVALIACAO_ICMBIO}"
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("TRANSFORMAÇÃO ICMBIO — BIODATA")
    print("=" * 60)


    # --------------------------------------------------------
    # 1. CARREGAR DADOS BRUTOS
    # --------------------------------------------------------

    df_icmbio = carregar_dados_icmbio()


    # --------------------------------------------------------
    # 2. TRANSFORMAR DIMENSÃO ESPÉCIE
    # --------------------------------------------------------

    df_dim_especie = transformar_dim_especie(
        df_icmbio
    )


    # --------------------------------------------------------
    # 3. TRANSFORMAR FATO DE AVALIAÇÃO ICMBIO
    # --------------------------------------------------------

    df_fato_icmbio = (
        transformar_fato_avaliacao_icmbio(
            df_icmbio
        )
    )


    # --------------------------------------------------------
    # 4. VALIDAR RESULTADO
    # --------------------------------------------------------

    mostrar_resumo(
        dim_especie=df_dim_especie,
        fato_icmbio=df_fato_icmbio
    )


    # --------------------------------------------------------
    # 5. SALVAR DADOS TRANSFORMADOS
    # --------------------------------------------------------

    salvar_dados_transformados(
        dim_especie=df_dim_especie,
        fato_icmbio=df_fato_icmbio
    )


    print("\n" + "=" * 60)
    print("TRANSFORMAÇÃO FINALIZADA")
    print("=" * 60)