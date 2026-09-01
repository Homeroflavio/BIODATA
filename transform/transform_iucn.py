import json
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_DADOS_BRUTOS = (
    Path(__file__).resolve().parent.parent / "dados_brutos"
)

PASTA_DADOS_TRANSFORMADOS = (
    Path(__file__).resolve().parent.parent / "dados_transformados"
)

ARQUIVO_IUCN_BRUTO = (
    PASTA_DADOS_BRUTOS / "iucn_avaliacoes_raw.jsonl"
)

ARQUIVO_FATO_AVALIACAO = (
    PASTA_DADOS_TRANSFORMADOS / "iucn_fato_avaliacao.csv"
)

ARQUIVO_DIM_CATEGORIA = (
    PASTA_DADOS_TRANSFORMADOS
    / "iucn_dim_categoria_risco.csv"
)

ARQUIVO_NOME_POPULAR = (
    PASTA_DADOS_TRANSFORMADOS
    / "iucn_nome_popular.csv"
)


# ============================================================
# MAPEAMENTO DAS CATEGORIAS DE RISCO
# ============================================================

CATEGORIAS_RISCO = {

    # --------------------------------------------------------
    # SISTEMA MODERNO
    # --------------------------------------------------------

    "LC": {
        "nome": "Least Concern",
        "sistema": "moderno",
        "peso_numerico": 0
    },

    "NT": {
        "nome": "Near Threatened",
        "sistema": "moderno",
        "peso_numerico": 1
    },

    "VU": {
        "nome": "Vulnerable",
        "sistema": "moderno",
        "peso_numerico": 2
    },

    "EN": {
        "nome": "Endangered",
        "sistema": "moderno",
        "peso_numerico": 3
    },

    "CR": {
        "nome": "Critically Endangered",
        "sistema": "moderno",
        "peso_numerico": 4
    },

    "EW": {
        "nome": "Extinct in the Wild",
        "sistema": "moderno",
        "peso_numerico": 5
    },

    "EX": {
        "nome": "Extinct",
        "sistema": "moderno",
        "peso_numerico": 6
    },

    "DD": {
        "nome": "Data Deficient",
        "sistema": "moderno",
        "peso_numerico": None
    },

    "NE": {
        "nome": "Not Evaluated",
        "sistema": "moderno",
        "peso_numerico": None
    },


    # --------------------------------------------------------
    # SISTEMA LEGADO
    # --------------------------------------------------------

    "V": {
        "nome": "Vulnerable",
        "sistema": "legado",
        "peso_numerico": 2
    },

    "E": {
        "nome": "Endangered",
        "sistema": "legado",
        "peso_numerico": 3
    },

    "R": {
        "nome": "Rare",
        "sistema": "legado",
        "peso_numerico": 1
    },

    "I": {
        "nome": "Indeterminate",
        "sistema": "legado",
        "peso_numerico": None
    },

    "T": {
        "nome": "Threatened",
        "sistema": "legado",
        "peso_numerico": 2
    }

}


# ============================================================
# LEITURA DO JSONL
# ============================================================

def carregar_dados_iucn() -> list[dict]:
    """
    Lê o arquivo JSONL bruto da IUCN.

    Cada linha representa uma espécie retornada pela API.

    Retorna uma lista de dicionários.
    """

    if not ARQUIVO_IUCN_BRUTO.exists():

        raise FileNotFoundError(
            "Arquivo bruto da IUCN não encontrado:\n"
            f"{ARQUIVO_IUCN_BRUTO}"
        )

    registros = []

    with open(
        ARQUIVO_IUCN_BRUTO,
        "r",
        encoding="utf-8"
    ) as arquivo:

        for numero_linha, linha in enumerate(
            arquivo,
            start=1
        ):

            linha = linha.strip()

            if not linha:
                continue

            try:

                registro = json.loads(linha)

                registros.append(registro)

            except json.JSONDecodeError:

                print(
                    f"Aviso: linha {numero_linha} "
                    "ignorada por JSON inválido."
                )

    print(
        f"Registros carregados do JSONL: "
        f"{len(registros)}"
    )

    return registros


# ============================================================
# PREPARAÇÃO DO ESCOPO
# ============================================================

def extrair_escopo(
    avaliacao: dict
) -> str | None:
    """
    Extrai o escopo da avaliação.

    Exemplo da API:

        "scopes": [
            {
                "description": {
                    "en": "Global"
                },
                "code": "1"
            }
        ]

    Retornamos a descrição em inglês.

    Se houver mais de um escopo, eles são unidos por "; ".
    """

    scopes = avaliacao.get(
        "scopes",
        []
    )

    escopos = []

    for scope in scopes:

        descricao = scope.get(
            "description",
            {}
        )

        nome = descricao.get("en")

        if nome:

            escopos.append(nome)

    if not escopos:
        return None

    return "; ".join(
        dict.fromkeys(escopos)
    )


# ============================================================
# EXTRAIR NOME POPULAR
# ============================================================

def extrair_nome_popular(
    taxon: dict
) -> str | None:
    """
    Extrai o nome popular em português da espécie.

    Prioridade:

        1. Nome em português marcado como principal (main = True)
        2. Qualquer nome disponível em português
        3. None, caso não exista nome em português

    Não utilizamos nomes em outros idiomas para evitar
    misturar idiomas no dashboard.
    """

    nomes_comuns = taxon.get(
        "common_names",
        []
    )

    if not nomes_comuns:
        return None

    nomes_portugues = []

    for nome in nomes_comuns:

        idioma = nome.get(
            "language"
        )

        nome_popular = nome.get(
            "name"
        )

        if (
            idioma == "por"
            and nome_popular
        ):

            nomes_portugues.append(nome)

    if not nomes_portugues:
        return None

    for nome in nomes_portugues:

        if nome.get("main") is True:

            return str(
                nome["name"]
            ).strip()

    return str(
        nomes_portugues[0]["name"]
    ).strip()


# ============================================================
# TRANSFORMAR NOMES POPULARES
# ============================================================

def transformar_nome_popular(
    registros: list[dict]
) -> pd.DataFrame:
    """
    Cria uma tabela auxiliar contendo:

        nome_cientifico
        nome_popular

    O nome popular é extraído da estrutura:

        taxon
            └── common_names

    Apenas nomes em português são utilizados.
    """

    linhas = []

    for registro in registros:

        nome_cientifico = registro.get(
            "_biodata_nome_consultado"
        )

        taxon = registro.get(
            "taxon",
            {}
        )

        nome_popular = extrair_nome_popular(
            taxon
        )

        linhas.append(
            {
                "nome_cientifico": nome_cientifico,
                "nome_popular": nome_popular
            }
        )

    colunas = [
        "nome_cientifico",
        "nome_popular"
    ]

    df = pd.DataFrame(
        linhas,
        columns=colunas
    )

    # --------------------------------------------------------
    # REMOVER REGISTROS SEM NOME CIENTÍFICO
    # --------------------------------------------------------

    df = df.dropna(
        subset=["nome_cientifico"]
    )

    # --------------------------------------------------------
    # REMOVER DUPLICATAS
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset="nome_cientifico",
        keep="first"
    )

    print(
        f"Espécies preparadas para nomes populares: "
        f"{len(df)}"
    )

    print(
        f"Espécies com nome popular em português: "
        f"{df['nome_popular'].notna().sum()}"
    )

    return df


# ============================================================
# TRANSFORMAR AVALIAÇÕES IUCN
# ============================================================

def transformar_fato_avaliacao(
    registros: list[dict]
) -> pd.DataFrame:
    """
    Transforma assessments_history em registros tabulares.

    Cada avaliação histórica vira uma linha.

    Estrutura gerada:

        assessment_id
        nome_cientifico
        ano_publicacao
        data_avaliacao
        categoria_risco_codigo
        e_avaliacao_atual
        possivelmente_extinta
        criterio
        escopo
    """

    linhas = []

    for registro in registros:

        nome_cientifico = registro.get(
            "_biodata_nome_consultado"
        )

        avaliacoes = registro.get(
            "assessments_history",
            []
        )

        for avaliacao in avaliacoes:

            assessment_id = avaliacao.get(
                "assessment_id"
            )

            # Sem ID único não conseguimos
            # garantir a integridade da fato.
            if assessment_id is None:

                continue

            data_avaliacao = avaliacao.get(
                "assessment_date"
            )

            if data_avaliacao:

                data_avaliacao = (
                    str(data_avaliacao)[:10]
                )

            ano_publicacao = avaliacao.get(
                "year_published"
            )

            if ano_publicacao is not None:

                try:

                    ano_publicacao = int(
                        ano_publicacao
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    ano_publicacao = None

            linha = {

                "assessment_id": assessment_id,

                "nome_cientifico": nome_cientifico,

                "ano_publicacao": ano_publicacao,

                "data_avaliacao": data_avaliacao,

                "categoria_risco_codigo":
                    avaliacao.get(
                        "red_list_category_code"
                    ),

                "e_avaliacao_atual":
                    avaliacao.get(
                        "latest",
                        False
                    ),

                "possivelmente_extinta":
                    avaliacao.get(
                        "possibly_extinct",
                        False
                    ),

                "criterio":
                    avaliacao.get(
                        "criteria"
                    ),

                "escopo":
                    extrair_escopo(
                        avaliacao
                    )

            }

            linhas.append(linha)

    colunas = [

        "assessment_id",
        "nome_cientifico",
        "ano_publicacao",
        "data_avaliacao",
        "categoria_risco_codigo",
        "e_avaliacao_atual",
        "possivelmente_extinta",
        "criterio",
        "escopo"

    ]

    df = pd.DataFrame(
        linhas,
        columns=colunas
    )

    # --------------------------------------------------------
    # REMOVER DUPLICATAS
    # --------------------------------------------------------

    if not df.empty:

        df = df.drop_duplicates(
            subset="assessment_id"
        )

    print(
        f"Avaliações históricas preparadas: "
        f"{len(df)}"
    )

    return df


# ============================================================
# TRANSFORMAR DIMENSÃO DE CATEGORIAS
# ============================================================

def transformar_dim_categoria_risco(
    df_avaliacoes: pd.DataFrame
) -> pd.DataFrame:
    """
    Cria a dimensão dim_categoria_risco.

    Apenas categorias realmente presentes nos dados
    são incluídas no CSV final.
    """

    if df_avaliacoes.empty:

        return pd.DataFrame(
            columns=[
                "codigo",
                "nome",
                "sistema",
                "peso_numerico"
            ]
        )

    codigos = (

        df_avaliacoes[
            "categoria_risco_codigo"
        ]

        .dropna()

        .astype(str)

        .str.strip()

        .unique()

    )

    linhas = []

    for codigo in sorted(codigos):

        dados_categoria = (
            CATEGORIAS_RISCO.get(codigo)
        )

        if dados_categoria is None:

            print(
                f"Aviso: categoria desconhecida "
                f"encontrada: {codigo}"
            )

            linhas.append(
                {
                    "codigo": codigo,
                    "nome": "Unknown",
                    "sistema": "desconhecido",
                    "peso_numerico": None
                }
            )

        else:

            linhas.append(
                {
                    "codigo": codigo,

                    "nome":
                        dados_categoria["nome"],

                    "sistema":
                        dados_categoria["sistema"],

                    "peso_numerico":
                        dados_categoria[
                            "peso_numerico"
                        ]
                }
            )

    df = pd.DataFrame(linhas)

    print(
        f"Categorias de risco preparadas: "
        f"{len(df)}"
    )

    return df


# ============================================================
# VALIDAÇÕES E RESUMO
# ============================================================

def mostrar_resumo(
    df_avaliacoes: pd.DataFrame,
    df_categorias: pd.DataFrame,
    df_nomes_populares: pd.DataFrame
) -> None:
    """
    Mostra resumo dos dados transformados.
    """

    print("\n" + "=" * 60)
    print("RESUMO DA TRANSFORMAÇÃO IUCN")
    print("=" * 60)

    print(
        f"\nRegistros em fato_avaliacao_iucn: "
        f"{len(df_avaliacoes)}"
    )

    print(
        f"Categorias em dim_categoria_risco: "
        f"{len(df_categorias)}"
    )

    print(
        f"Espécies em iucn_nome_popular: "
        f"{len(df_nomes_populares)}"
    )

    print(
        f"Espécies com nome popular em português: "
        f"{df_nomes_populares['nome_popular'].notna().sum()}"
    )

    print(
        f"Espécies sem nome popular em português: "
        f"{df_nomes_populares['nome_popular'].isna().sum()}"
    )

    print(
        "\nEspécies únicas com avaliações: "
        f"{df_avaliacoes['nome_cientifico'].nunique()}"
        if not df_avaliacoes.empty
        else "\nEspécies únicas com avaliações: 0"
    )

    # --------------------------------------------------------
    # NULOS
    # --------------------------------------------------------

    print(
        "\nNulos em fato_avaliacao_iucn:"
    )

    if df_avaliacoes.empty:

        print(
            "Nenhuma avaliação encontrada."
        )

    else:

        print(
            df_avaliacoes
            .isna()
            .sum()
            .to_string()
        )

    print(
        "\nNulos em iucn_nome_popular:"
    )

    print(
        df_nomes_populares
        .isna()
        .sum()
        .to_string()
    )

    # --------------------------------------------------------
    # DISTRIBUIÇÃO DE CATEGORIAS
    # --------------------------------------------------------

    print(
        "\nDistribuição das categorias de risco:"
    )

    if df_avaliacoes.empty:

        print(
            "Nenhuma categoria encontrada."
        )

    else:

        print(
            df_avaliacoes[
                "categoria_risco_codigo"
            ]

            .value_counts(
                dropna=False
            )

            .to_string()
        )

    # --------------------------------------------------------
    # AVALIAÇÕES ATUAIS
    # --------------------------------------------------------

    print(
        "\nQuantidade de avaliações atuais:"
    )

    if df_avaliacoes.empty:

        print(0)

    else:

        quantidade_atuais = (
            df_avaliacoes[
                "e_avaliacao_atual"
            ]

            .fillna(False)

            .astype(bool)

            .sum()
        )

        print(quantidade_atuais)

    # --------------------------------------------------------
    # PRIMEIROS REGISTROS
    # --------------------------------------------------------

    print(
        "\nPrimeiros registros de fato_avaliacao_iucn:"
    )

    if df_avaliacoes.empty:

        print(
            "Nenhum registro."
        )

    else:

        print(
            df_avaliacoes
            .head()
            .to_string()
        )

    print(
        "\nPrimeiros registros de iucn_nome_popular:"
    )

    print(
        df_nomes_populares
        .head(10)
        .to_string()
    )


# ============================================================
# SALVAR DADOS TRANSFORMADOS
# ============================================================

def salvar_dados_transformados(
    df_avaliacoes: pd.DataFrame,
    df_categorias: pd.DataFrame,
    df_nomes_populares: pd.DataFrame
) -> None:
    """
    Salva os CSVs transformados.
    """

    PASTA_DADOS_TRANSFORMADOS.mkdir(
        exist_ok=True
    )

    df_avaliacoes.to_csv(
        ARQUIVO_FATO_AVALIACAO,
        index=False,
        encoding="utf-8"
    )

    df_categorias.to_csv(
        ARQUIVO_DIM_CATEGORIA,
        index=False,
        encoding="utf-8"
    )

    df_nomes_populares.to_csv(
        ARQUIVO_NOME_POPULAR,
        index=False,
        encoding="utf-8"
    )

    print(
        "\nDados transformados salvos:"
    )

    print(
        f"\n - {ARQUIVO_FATO_AVALIACAO}"
    )

    print(
        f" - {ARQUIVO_DIM_CATEGORIA}"
    )

    print(
        f" - {ARQUIVO_NOME_POPULAR}"
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("TRANSFORMAÇÃO IUCN — BIODATA")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. CARREGAR DADOS BRUTOS
    # --------------------------------------------------------

    print(
        "\nCarregando dados brutos da IUCN..."
    )

    registros = carregar_dados_iucn()

    # --------------------------------------------------------
    # 2. TRANSFORMAR AVALIAÇÕES
    # --------------------------------------------------------

    print(
        "\nTransformando histórico de avaliações..."
    )

    df_avaliacoes = (
        transformar_fato_avaliacao(
            registros
        )
    )

    # --------------------------------------------------------
    # 3. TRANSFORMAR CATEGORIAS
    # --------------------------------------------------------

    print(
        "\nTransformando dimensão "
        "de categorias de risco..."
    )

    df_categorias = (
        transformar_dim_categoria_risco(
            df_avaliacoes
        )
    )

    # --------------------------------------------------------
    # 4. TRANSFORMAR NOMES POPULARES
    # --------------------------------------------------------

    print(
        "\nTransformando nomes populares..."
    )

    df_nomes_populares = (
        transformar_nome_popular(
            registros
        )
    )

    # --------------------------------------------------------
    # 5. MOSTRAR RESUMO
    # --------------------------------------------------------

    mostrar_resumo(
        df_avaliacoes=df_avaliacoes,
        df_categorias=df_categorias,
        df_nomes_populares=df_nomes_populares
    )

    # --------------------------------------------------------
    # 6. SALVAR
    # --------------------------------------------------------

    salvar_dados_transformados(
        df_avaliacoes=df_avaliacoes,
        df_categorias=df_categorias,
        df_nomes_populares=df_nomes_populares
    )

    print("\n" + "=" * 60)
    print("TRANSFORMAÇÃO FINALIZADA")
    print("=" * 60)