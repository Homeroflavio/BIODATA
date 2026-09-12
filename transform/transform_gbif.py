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

ARQUIVO_GBIF_RAW = (
    PASTA_DADOS_BRUTOS / "gbif_ocorrencias_raw.jsonl"
)

ARQUIVO_DIM_LOCAL = (
    PASTA_DADOS_TRANSFORMADOS / "gbif_dim_local.csv"
)

ARQUIVO_FATO_OCORRENCIA = (
    PASTA_DADOS_TRANSFORMADOS
    / "gbif_fato_ocorrencia.csv"
)


# ============================================================
# CARREGAMENTO
# ============================================================

def carregar_dados_gbif() -> list[dict]:
    """
    Carrega os registros JSONL extraídos da GBIF.

    Cada linha do arquivo representa uma ocorrência.
    """

    registros = []

    with open(
        ARQUIVO_GBIF_RAW,
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
                    f"ignorada por JSON inválido."
                )

    return registros


# ============================================================
# TRANSFORMAÇÃO — DIM_LOCAL
# ============================================================

def transformar_dim_local(
    registros: list[dict]
) -> pd.DataFrame:
    """
    Cria a dimensão de localização.

    Estrutura esperada:

        pais
        estado_provincia
        continente

    A localização é extraída principalmente dos campos:

        country
        gadm.level1.name
        continent
    """

    locais = []

    for registro in registros:

        gadm = registro.get(
            "gadm",
            {}
        )

        level0 = gadm.get(
            "level0",
            {}
        )

        level1 = gadm.get(
            "level1",
            {}
        )

        pais = (
            registro.get("country")
            or level0.get("name")
        )

        estado_provincia = (
            level1.get("name")
            or registro.get(
                "stateProvince"
            )
        )

        continente = registro.get(
            "continent"
        )

        locais.append(
            {
                "pais": pais,
                "estado_provincia": estado_provincia,
                "continente": continente
            }
        )

    df_local = pd.DataFrame(locais)

    # Remove duplicatas de localização.
    df_local = df_local.drop_duplicates()

    # Remove registros completamente vazios.
    df_local = df_local.dropna(
        how="all"
    )

    # Padroniza valores ausentes.
    df_local = df_local.where(
        pd.notna(df_local),
        None
    )

    return df_local


# ============================================================
# TRANSFORMAÇÃO — FATO_OCORRENCIA_GBIF
# ============================================================

def transformar_fato_ocorrencia(
    registros: list[dict]
) -> pd.DataFrame:
    """
    Cria a tabela fato de ocorrências da GBIF.

    O especie_id e local_id ainda NÃO são criados aqui.

    Isso acontece posteriormente no LOAD, depois que:

        1. dim_especie estiver carregada
        2. dim_local estiver carregada

    Por enquanto mantemos:

        nome_cientifico

    e os dados de localização necessários para
    encontrar posteriormente o local_id.
    """

    ocorrencias = []

    for registro in registros:

        issues = registro.get(
            "issues",
            []
        )

        # Garante que issues seja uma lista.
        if not isinstance(
            issues,
            list
        ):
            issues = []

        gadm = registro.get(
            "gadm",
            {}
        )

        level0 = gadm.get(
            "level0",
            {}
        )

        level1 = gadm.get(
            "level1",
            {}
        )

        pais = (
            registro.get("country")
            or level0.get("name")
        )

        estado_provincia = (
            level1.get("name")
            or registro.get(
                "stateProvince"
            )
        )

        continente = registro.get(
            "continent"
        )

        ocorrencias.append(
            {
                # Identificador único da ocorrência
                "gbif_id": registro.get(
                    "key"
                ),

                # Chave temporária para encontrar especie_id
                # durante o LOAD.
                "nome_cientifico": (
                    registro.get(
                        "_biodata_nome_consultado"
                    )
                    or registro.get(
                        "canonicalName"
                    )
                    or registro.get(
                        "species"
                    )
                ),

                # Dados para encontrar local_id
                # durante o LOAD.
                "pais": pais,

                "estado_provincia": (
                    estado_provincia
                ),

                "continente": continente,

                # Coordenadas
                "latitude": registro.get(
                    "decimalLatitude"
                ),

                "longitude": registro.get(
                    "decimalLongitude"
                ),

                "incerteza_metros": (
                    registro.get(
                        "coordinateUncertaintyInMeters"
                    )
                ),

                # Categoria IUCN eventualmente
                # disponibilizada pela GBIF.
                "categoria_iucn": (
                    registro.get(
                        "iucnRedListCategory"
                    )
                ),

                # Data do registro.
                "data_observacao": (
                    registro.get(
                        "eventDate"
                    )
                ),
                
                # Ano da observação, extraído do campo "year" da ocorrência.
                "ano_observacao": (
                    registro.get(
                        "year"
                    )
                ),

                # Se houver qualquer issue, marcamos
                # alerta de qualidade como True.
                "tem_alerta_qualidade": (
                    len(issues) > 0
                )
            }
        )

    df_ocorrencias = pd.DataFrame(
        ocorrencias
    )

    # --------------------------------------------------------
    # REMOVER DUPLICATAS
    # --------------------------------------------------------

    df_ocorrencias = (
        df_ocorrencias
        .drop_duplicates(
            subset="gbif_id",
            keep="first"
        )
    )

    # --------------------------------------------------------
    # CONVERSÕES DE TIPO
    # --------------------------------------------------------

    df_ocorrencias["gbif_id"] = (
        pd.to_numeric(
            df_ocorrencias["gbif_id"],
            errors="coerce"
        )
        .astype("Int64")
    )

    df_ocorrencias["latitude"] = (
        pd.to_numeric(
            df_ocorrencias["latitude"],
            errors="coerce"
        )
    )

    df_ocorrencias["longitude"] = (
        pd.to_numeric(
            df_ocorrencias["longitude"],
            errors="coerce"
        )
    )

    df_ocorrencias["incerteza_metros"] = (
        pd.to_numeric(
            df_ocorrencias[
                "incerteza_metros"
            ],
            errors="coerce"
        )
    )

    df_ocorrencias["data_observacao"] = (
        pd.to_datetime(
            df_ocorrencias[
                "data_observacao"
            ],
            errors="coerce",
            utc=True
        )
        .dt.date
    )
    
    df_ocorrencias["ano_observacao"] = (
    pd.to_numeric(
        df_ocorrencias[
                "ano_observacao"
            ],
            errors="coerce"
        )
        .astype("Int64")
    )

    # --------------------------------------------------------
    # PADRONIZA NULOS
    # --------------------------------------------------------

    df_ocorrencias = (
        df_ocorrencias.where(
            pd.notna(df_ocorrencias),
            None
        )
    )

    return df_ocorrencias


# ============================================================
# VALIDAÇÃO BÁSICA
# ============================================================

def validar_dados(
    df_local: pd.DataFrame,
    df_ocorrencias: pd.DataFrame
) -> None:
    """
    Executa validações básicas antes do salvamento.
    """

    print(
        "\nValidando dados transformados..."
    )

    # --------------------------------------------------------
    # GBIF ID DUPLICADO
    # --------------------------------------------------------

    duplicados_gbif = (
        df_ocorrencias[
            "gbif_id"
        ]
        .duplicated()
        .sum()
    )

    print(
        f"GBIF IDs duplicados: "
        f"{duplicados_gbif}"
    )

    # --------------------------------------------------------
    # COORDENADAS AUSENTES
    # --------------------------------------------------------

    coordenadas_nulas = (
        df_ocorrencias[
            ["latitude", "longitude"]
        ]
        .isna()
        .any(axis=1)
        .sum()
    )

    print(
        f"Ocorrências sem coordenadas: "
        f"{coordenadas_nulas}"
    )

    # --------------------------------------------------------
    # COORDENADAS FORA DO INTERVALO
    # --------------------------------------------------------

    latitude_invalida = (
        (
            df_ocorrencias["latitude"] < -90
        )
        |
        (
            df_ocorrencias["latitude"] > 90
        )
    ).sum()

    longitude_invalida = (
        (
            df_ocorrencias["longitude"] < -180
        )
        |
        (
            df_ocorrencias["longitude"] > 180
        )
    ).sum()

    print(
        f"Latitudes inválidas: "
        f"{latitude_invalida}"
    )

    print(
        f"Longitudes inválidas: "
        f"{longitude_invalida}"
    )

    # --------------------------------------------------------
    # NOME CIENTÍFICO AUSENTE
    # --------------------------------------------------------

    especies_nulas = (
        df_ocorrencias[
            "nome_cientifico"
        ]
        .isna()
        .sum()
    )

    print(
        f"Ocorrências sem nome científico: "
        f"{especies_nulas}"
    )

    # --------------------------------------------------------
    # RESUMO
    # --------------------------------------------------------

    print(
        f"\nLocais únicos preparados: "
        f"{len(df_local)}"
    )

    print(
        f"Ocorrências preparadas: "
        f"{len(df_ocorrencias)}"
    )


# ============================================================
# SALVAMENTO
# ============================================================

def salvar_dados_transformados(
    df_local: pd.DataFrame,
    df_ocorrencias: pd.DataFrame
) -> None:
    """
    Salva os DataFrames transformados em CSV.
    """

    PASTA_DADOS_TRANSFORMADOS.mkdir(
        exist_ok=True
    )

    df_local.to_csv(
        ARQUIVO_DIM_LOCAL,
        index=False,
        encoding="utf-8"
    )

    df_ocorrencias.to_csv(
        ARQUIVO_FATO_OCORRENCIA,
        index=False,
        encoding="utf-8"
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("TRANSFORMAÇÃO GBIF — BIODATA")
    print("=" * 60)

    # --------------------------------------------------------
    # CARREGAMENTO
    # --------------------------------------------------------

    print(
        "\nCarregando dados brutos da GBIF..."
    )

    registros = carregar_dados_gbif()

    print(
        f"Registros carregados: "
        f"{len(registros)}"
    )

    # --------------------------------------------------------
    # DIM_LOCAL
    # --------------------------------------------------------

    print(
        "\nTransformando dados para dim_local..."
    )

    df_local = transformar_dim_local(
        registros
    )

    print(
        f"Locais únicos preparados: "
        f"{len(df_local)}"
    )

    # --------------------------------------------------------
    # FATO_OCORRENCIA_GBIF
    # --------------------------------------------------------

    print(
        "\nTransformando dados para "
        "fato_ocorrencia_gbif..."
    )

    df_ocorrencias = (
        transformar_fato_ocorrencia(
            registros
        )
    )

    print(
        f"Ocorrências preparadas: "
        f"{len(df_ocorrencias)}"
    )

    # --------------------------------------------------------
    # VALIDAÇÃO
    # --------------------------------------------------------

    validar_dados(
        df_local=df_local,
        df_ocorrencias=df_ocorrencias
    )

    # --------------------------------------------------------
    # RESUMO
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("RESUMO DA TRANSFORMAÇÃO GBIF")
    print("=" * 60)

    print(
        f"\nRegistros em dim_local: "
        f"{len(df_local)}"
    )

    print(
        f"Registros em fato_ocorrencia_gbif: "
        f"{len(df_ocorrencias)}"
    )

    print(
        "\nNulos em dim_local:"
    )

    print(
        df_local.isnull().sum()
        .to_string()
    )

    print(
        "\nNulos em fato_ocorrencia_gbif:"
    )

    print(
        df_ocorrencias.isnull().sum()
        .to_string()
    )

    print(
        "\nOcorrências com alerta de qualidade:"
    )

    print(
        df_ocorrencias[
            "tem_alerta_qualidade"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    print(
        "\nPrimeiros registros de dim_local:"
    )

    print(
        df_local.head().to_string()
    )

    print(
        "\nPrimeiros registros de "
        "fato_ocorrencia_gbif:"
    )

    print(
        df_ocorrencias.head().to_string()
    )

    # --------------------------------------------------------
    # SALVAMENTO
    # --------------------------------------------------------

    salvar_dados_transformados(
        df_local=df_local,
        df_ocorrencias=df_ocorrencias
    )

    print(
        "\nDados transformados salvos:"
    )

    print(
        f"\n - {ARQUIVO_DIM_LOCAL}"
    )

    print(
        f"\n - {ARQUIVO_FATO_OCORRENCIA}"
    )

    print("\n" + "=" * 60)
    print("TRANSFORMAÇÃO FINALIZADA")
    print("=" * 60)