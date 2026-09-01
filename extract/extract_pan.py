from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS_BRUTOS = PASTA_RAIZ / "dados_brutos"

ARQUIVO_ODS = (
    PASTA_DADOS_BRUTOS
    / "20251112_tabelapandadosabertos.ods"
)

# Abas do arquivo ODS que serão utilizadas
ABA_PAN_DADOS = "20251112-tabelaPanDados"
ABA_PAN_ESPECIES = "20251112-tabelaPanEspecies"
ABA_PAN_BIOMAS = "20251112-tabelaPanBiomas"
ABA_PAN_ESTADOS = "20251112-tabelaPanEstados"

# Arquivos brutos de saída
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


# ============================================================
# LEITURA DAS ABAS
# ============================================================

def carregar_aba(nome_aba: str) -> pd.DataFrame:
    """
    Lê uma aba específica do arquivo ODS.

    Nenhuma transformação é feita nesta etapa.
    Os dados são mantidos como extraídos da fonte.
    """

    print(f"Carregando aba: {nome_aba}")

    try:

        dataframe = pd.read_excel(
            ARQUIVO_ODS,
            sheet_name=nome_aba,
            engine="odf"
        )

        print(
            f"    Registros carregados: "
            f"{len(dataframe)}"
        )

        print(
            f"    Colunas encontradas: "
            f"{len(dataframe.columns)}"
        )

        return dataframe

    except ValueError as erro:

        raise ValueError(
            f"Não foi possível encontrar ou ler a aba "
            f"'{nome_aba}'."
        ) from erro


# ============================================================
# SALVAMENTO
# ============================================================

def salvar_csv(
    dataframe: pd.DataFrame,
    caminho_saida: Path
) -> None:
    """
    Salva os dados brutos em CSV.
    """

    dataframe.to_csv(
        caminho_saida,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"    Salvo: {caminho_saida.name}"
    )


# ============================================================
# EXTRAÇÃO PRINCIPAL
# ============================================================

def extrair_pan() -> None:

    print("=" * 60)
    print("EXTRAÇÃO PAN — BIODATA")
    print("=" * 60)

    # --------------------------------------------------------
    # VERIFICAR ARQUIVO DE ORIGEM
    # --------------------------------------------------------

    if not ARQUIVO_ODS.exists():

        raise FileNotFoundError(
            "\nArquivo ODS não encontrado:\n"
            f"{ARQUIVO_ODS}\n\n"
            "Verifique se o arquivo está dentro da pasta "
            "'dados_brutos'."
        )

    print(
        f"\nArquivo de origem encontrado:\n"
        f"{ARQUIVO_ODS.name}"
    )

    # --------------------------------------------------------
    # 1. DADOS DOS PANS
    # --------------------------------------------------------

    print("\nExtraindo dados dos PANs...")

    df_pan_dados = carregar_aba(
        ABA_PAN_DADOS
    )

    salvar_csv(
        df_pan_dados,
        ARQUIVO_PAN_DADOS
    )

    # --------------------------------------------------------
    # 2. ESPÉCIES DOS PANS
    # --------------------------------------------------------

    print("\nExtraindo espécies dos PANs...")

    df_pan_especies = carregar_aba(
        ABA_PAN_ESPECIES
    )

    salvar_csv(
        df_pan_especies,
        ARQUIVO_PAN_ESPECIES
    )

    # --------------------------------------------------------
    # 3. BIOMAS DOS PANS
    # --------------------------------------------------------

    print("\nExtraindo biomas dos PANs...")

    df_pan_biomas = carregar_aba(
        ABA_PAN_BIOMAS
    )

    salvar_csv(
        df_pan_biomas,
        ARQUIVO_PAN_BIOMAS
    )

    # --------------------------------------------------------
    # 4. ESTADOS DOS PANS
    # --------------------------------------------------------

    print("\nExtraindo estados dos PANs...")

    df_pan_estados = carregar_aba(
        ABA_PAN_ESTADOS
    )

    salvar_csv(
        df_pan_estados,
        ARQUIVO_PAN_ESTADOS
    )

    # ========================================================
    # RESUMO FINAL
    # ========================================================

    print("\n" + "=" * 60)
    print("RESUMO DA EXTRAÇÃO PAN")
    print("=" * 60)

    print(
        f"\nRegistros em pan_dados_raw: "
        f"{len(df_pan_dados)}"
    )

    print(
        f"Registros em pan_especies_raw: "
        f"{len(df_pan_especies)}"
    )

    print(
        f"Registros em pan_biomas_raw: "
        f"{len(df_pan_biomas)}"
    )

    print(
        f"Registros em pan_estados_raw: "
        f"{len(df_pan_estados)}"
    )

    print("\nArquivos brutos salvos:")

    print(f"\n - {ARQUIVO_PAN_DADOS}")
    print(f" - {ARQUIVO_PAN_ESPECIES}")
    print(f" - {ARQUIVO_PAN_BIOMAS}")
    print(f" - {ARQUIVO_PAN_ESTADOS}")

    print("\n" + "=" * 60)
    print("EXTRAÇÃO FINALIZADA")
    print("=" * 60)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    extrair_pan()