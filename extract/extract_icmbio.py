import csv
import io
import zipfile
from pathlib import Path

import pandas as pd
import requests


# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL_ICMBIO = (
    "https://ipt.icmbio.gov.br/archive.do"
    "?r=lista_vermelha&v=1.406"
)

PASTA_DADOS_BRUTOS = (
    Path(__file__).resolve().parent.parent / "dados_brutos"
)

ARQUIVO_ICMBIO = (
    PASTA_DADOS_BRUTOS / "icmbio_taxon_raw.csv"
)


# ============================================================
# EXTRAÇÃO
# ============================================================

def baixar_dados_icmbio() -> pd.DataFrame:
    """
    Baixa o Darwin Core Archive da Lista Vermelha do ICMBio
    e lê o arquivo taxon.txt.

    Retorna o DataFrame completo com os dados brutos.
    """

    print("Baixando dados do ICMBio...")

    resposta = requests.get(
        URL_ICMBIO,
        timeout=60
    )

    resposta.raise_for_status()

    print(
        f"Download concluído. "
        f"Status HTTP: {resposta.status_code}"
    )

    with zipfile.ZipFile(
        io.BytesIO(resposta.content)
    ) as arquivo_zip:

        arquivos = arquivo_zip.namelist()

        print(
            f"Arquivos encontrados no pacote: "
            f"{len(arquivos)}"
        )

        if "taxon.txt" not in arquivos:

            raise FileNotFoundError(
                "O arquivo taxon.txt não foi encontrado "
                "no pacote do ICMBio."
            )

        with arquivo_zip.open("taxon.txt") as arquivo:

            df = pd.read_csv(
                arquivo,
                sep="\t",
                quoting=csv.QUOTE_NONE,
                dtype=str
            )

    return df


# ============================================================
# SALVAMENTO DOS DADOS BRUTOS
# ============================================================

def salvar_dados_brutos(
    df: pd.DataFrame
) -> None:
    """
    Salva o DataFrame completo do ICMBio.

    Os dados são mantidos em formato CSV para facilitar
    a inspeção e as próximas etapas de transformação.
    """

    PASTA_DADOS_BRUTOS.mkdir(
        exist_ok=True
    )

    df.to_csv(
        ARQUIVO_ICMBIO,
        index=False,
        encoding="utf-8"
    )

    print(
        f"\nDados brutos salvos em:\n"
        f"{ARQUIVO_ICMBIO}"
    )


# ============================================================
# LISTA DE ESPÉCIES
# ============================================================

def obter_lista_especies_icmbio() -> list[str]:
    """
    Retorna uma lista de nomes científicos únicos.

    Como o campo 'scientificName' da fonte apresentou
    inconsistências durante a exploração, utilizamos
    'scientificNameAuthorship', removendo valores nulos
    e duplicados.
    """

    # --------------------------------------------------------
    # USA ARQUIVO LOCAL SE ELE JÁ EXISTIR
    # --------------------------------------------------------

    if ARQUIVO_ICMBIO.exists():

        print(
            "Carregando dados do ICMBio "
            "a partir do arquivo local..."
        )

        df = pd.read_csv(
            ARQUIVO_ICMBIO,
            dtype=str
        )

    else:

        print(
            "Arquivo local não encontrado."
        )

        df = baixar_dados_icmbio()

        salvar_dados_brutos(df)

    # --------------------------------------------------------
    # VALIDAR COLUNA
    # --------------------------------------------------------

    coluna_nome = "scientificNameAuthorship"

    if coluna_nome not in df.columns:

        raise KeyError(
            f"A coluna '{coluna_nome}' "
            "não foi encontrada nos dados do ICMBio."
        )

    # --------------------------------------------------------
    # LIMPAR E OBTER NOMES ÚNICOS
    # --------------------------------------------------------

    nomes = (
        df[coluna_nome]
        .dropna()
        .astype(str)
        .str.strip()
    )

    nomes = nomes[
        nomes != ""
    ]

    especies = (
        nomes
        .drop_duplicates()
        .tolist()
    )

    print(
        f"Lista de espécies do ICMBio obtida: "
        f"{len(especies)} espécies únicas"
    )

    return especies


# ============================================================
# EXPLORAÇÃO
# ============================================================

def mostrar_resumo(
    df: pd.DataFrame
) -> None:
    """
    Mostra informações básicas sobre os dados extraídos.
    """

    print("\n" + "=" * 60)
    print("RESUMO DOS DADOS DO ICMBIO")
    print("=" * 60)

    print(
        f"\nTotal de registros: "
        f"{len(df)}"
    )

    print(
        f"\nTotal de colunas: "
        f"{len(df.columns)}"
    )

    print("\nCOLUNAS DISPONÍVEIS:")

    for coluna in df.columns:

        valores_nulos = df[coluna].isna().sum()

        print(
            f" - {coluna} "
            f"(nulos: {valores_nulos})"
        )

    print("\nPRIMEIROS 5 REGISTROS:")

    print(
        df.head().to_string()
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("EXTRAÇÃO ICMBIO — BIODATA")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. BAIXAR DADOS
    # --------------------------------------------------------

    if ARQUIVO_ICMBIO.exists():

        print(
            "\nArquivo bruto já existe."
        )

        print(
            "Carregando arquivo local..."
        )

        df = pd.read_csv(
            ARQUIVO_ICMBIO,
            dtype=str
        )

    else:

        df = baixar_dados_icmbio()

        salvar_dados_brutos(df)

    # --------------------------------------------------------
    # 2. MOSTRAR RESUMO
    # --------------------------------------------------------

    mostrar_resumo(df)

    # --------------------------------------------------------
    # 3. OBTER ESPÉCIES
    # --------------------------------------------------------

    especies = obter_lista_especies_icmbio()

    print("\n" + "=" * 60)
    print("EXTRAÇÃO FINALIZADA")
    print("=" * 60)

    print(
        f"\nEspécies únicas obtidas: "
        f"{len(especies)}"
    )

    print("\nPrimeiras 10 espécies:")

    for especie in especies[:10]:

        print(f" - {especie}")