import time
from pathlib import Path

import pandas as pd
import requests
# tentativa de enriquecimento dos dados , encontrando tradução para nomes populares
 
# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL_SPECIES_MATCH = (
    "https://api.gbif.org/v1/species/match"
)

URL_VERNACULAR_NAMES = (
    "https://api.gbif.org/v1/species"
)

PASTA_PROJETO = (
    Path(__file__).resolve().parent.parent
)

PASTA_DADOS_FINAIS = (
    PASTA_PROJETO / "dados_finais"
)

ARQUIVO_DIM_ESPECIE = (
    PASTA_DADOS_FINAIS / "dim_especie.csv"
)

# Arquivo de backup antes do enriquecimento.
ARQUIVO_BACKUP = (
    PASTA_DADOS_FINAIS / "dim_especie_antes_gbif.csv"
)

# Pequena pausa entre espécies para evitar excesso de requisições.
INTERVALO_ENTRE_REQUISICOES = 0.1

# Número máximo de tentativas em caso de erro temporário.
MAX_TENTATIVAS = 3

# Confiança mínima aceita no match da espécie.
CONFIANCA_MINIMA = 80


# ============================================================
# FUNÇÃO PARA FAZER REQUISIÇÕES COM RETRY
# ============================================================

def fazer_requisicao(url, params=None):
    """
    Faz uma requisição GET com tentativas adicionais
    em caso de erro temporário.
    """

    for tentativa in range(1, MAX_TENTATIVAS + 1):

        try:

            resposta = requests.get(
                url,
                params=params,
                timeout=(10, 30)
            )

            resposta.raise_for_status()

            return resposta.json()

        except requests.exceptions.RequestException as erro:

            print(
                f"    Erro na requisição "
                f"(tentativa {tentativa}/{MAX_TENTATIVAS}): "
                f"{erro.__class__.__name__}"
            )

            if tentativa == MAX_TENTATIVAS:

                return None

            espera = tentativa * 2

            print(
                f"    Tentando novamente em {espera}s..."
            )

            time.sleep(espera)

    return None


# ============================================================
# ENCONTRAR TAXON KEY
# ============================================================

def encontrar_taxon_key(nome_cientifico):
    """
    Busca o taxonKey da espécie no GBIF.

    Retorna None quando não houver um match suficientemente
    confiável.
    """

    dados = fazer_requisicao(
        URL_SPECIES_MATCH,
        params={
            "name": nome_cientifico
        }
    )

    if dados is None:

        return None

    match_type = dados.get("matchType")

    confidence = dados.get("confidence", 0)

    taxon_key = dados.get("usageKey")

    if (
        match_type != "NONE"
        and confidence >= CONFIANCA_MINIMA
        and taxon_key is not None
    ):

        return taxon_key

    return None


# ============================================================
# BUSCAR NOMES VERNACULARES
# ============================================================

def buscar_nomes_vernaculares(taxon_key):
    """
    Busca os nomes vernaculares associados ao taxonKey
    na API da GBIF.

    Retorna uma lista de registros.
    """

    url = (
        f"{URL_VERNACULAR_NAMES}/"
        f"{taxon_key}/"
        f"vernacularNames"
    )

    dados = fazer_requisicao(
        url,
        params={
            "limit": 100
        }
    )

    if dados is None:

        return []

    return dados.get("results", [])


# ============================================================
# ESCOLHER MELHOR NOME EM PORTUGUÊS
# ============================================================

def escolher_nome_portugues(nomes):
    """
    Seleciona um nome vernacular em português.

    Prioridade:

    1. Nome em português marcado como preferred.
    2. Nome em português associado ao Brasil.
    3. Qualquer outro nome em português.

    A API pode retornar códigos ISO de idioma diferentes
    dependendo da fonte, então aceitamos 'pt' e 'por'.
    """

    nomes_portugues = []

    for nome in nomes:

        idioma = str(
            nome.get("language", "")
        ).lower()

        nome_vernacular = nome.get(
            "vernacularName"
        )

        if (
            idioma in ["pt", "por"]
            and nome_vernacular
        ):

            nomes_portugues.append(nome)

    if not nomes_portugues:

        return None

    # --------------------------------------------------------
    # 1. PREFERIDO
    # --------------------------------------------------------

    for nome in nomes_portugues:

        if nome.get("preferred") is True:

            return nome.get("vernacularName")

    # --------------------------------------------------------
    # 2. ASSOCIADO AO BRASIL
    # --------------------------------------------------------

    for nome in nomes_portugues:

        pais = str(
            nome.get("country", "")
        ).upper()

        if pais in ["BR", "BRA", "BRAZIL"]:

            return nome.get("vernacularName")

    # --------------------------------------------------------
    # 3. QUALQUER NOME EM PORTUGUÊS
    # --------------------------------------------------------

    return nomes_portugues[0].get(
        "vernacularName"
    )


# ============================================================
# ENRIQUECIMENTO PRINCIPAL
# ============================================================

def enriquecer_nomes_populares():
    """
    Preenche nomes populares ausentes na dim_especie
    utilizando nomes vernaculares em português da GBIF.

    Nomes já existentes são preservados.
    """

    print("=" * 60)
    print("ENRIQUECIMENTO DE NOMES POPULARES — GBIF")
    print("=" * 60)

    # --------------------------------------------------------
    # CARREGAR DADOS
    # --------------------------------------------------------

    print(
        "\nCarregando dim_especie..."
    )

    df = pd.read_csv(
        ARQUIVO_DIM_ESPECIE
    )

    print(
        f"Espécies carregadas: {len(df)}"
    )

    # --------------------------------------------------------
    # GARANTIR COLUNA
    # --------------------------------------------------------

    if "nome_popular" not in df.columns:

        df["nome_popular"] = pd.NA

    # --------------------------------------------------------
    # NORMALIZAR VALORES VAZIOS
    # --------------------------------------------------------

    df["nome_popular"] = (
        df["nome_popular"]
        .replace("", pd.NA)
        .replace("nan", pd.NA)
        .replace("None", pd.NA)
    )

    # --------------------------------------------------------
    # CRIAR BACKUP
    # --------------------------------------------------------

    if not ARQUIVO_BACKUP.exists():

        df.to_csv(
            ARQUIVO_BACKUP,
            index=False,
            encoding="utf-8-sig"
        )

        print(
            f"Backup criado:\n"
            f"{ARQUIVO_BACKUP}"
        )

    else:

        print(
            "\nBackup já existente. "
            "Mantendo arquivo anterior."
        )

    # --------------------------------------------------------
    # IDENTIFICAR ESPÉCIES SEM NOME POPULAR
    # --------------------------------------------------------

    sem_nome = df[
        df["nome_popular"].isna()
    ]

    total_sem_nome = len(sem_nome)

    total_com_nome_inicial = (
        len(df) - total_sem_nome
    )

    print(
        f"\nEspécies com nome popular antes: "
        f"{total_com_nome_inicial}"
    )

    print(
        f"Espécies sem nome popular: "
        f"{total_sem_nome}"
    )

    if total_sem_nome == 0:

        print(
            "\nTodas as espécies já possuem "
            "nome popular."
        )

        return

    # --------------------------------------------------------
    # CONTADORES
    # --------------------------------------------------------

    nomes_adicionados = 0
    sem_match = 0
    sem_nome_portugues = 0
    erros = 0

    # --------------------------------------------------------
    # PROCESSAR ESPÉCIES
    # --------------------------------------------------------

    print(
        "\nIniciando consultas à GBIF..."
    )

    for contador, (indice, linha) in enumerate(
        sem_nome.iterrows(),
        start=1
    ):

        nome_cientifico = linha[
            "nome_cientifico"
        ]

        print(
            f"\n[{contador}/{total_sem_nome}] "
            f"{nome_cientifico}"
        )

        # ----------------------------------------------------
        # 1. ENCONTRAR TAXON KEY
        # ----------------------------------------------------

        taxon_key = encontrar_taxon_key(
            nome_cientifico
        )

        if taxon_key is None:

            print(
                "    Sem match confiável."
            )

            sem_match += 1

            time.sleep(
                INTERVALO_ENTRE_REQUISICOES
            )

            continue

        print(
            f"    TaxonKey: {taxon_key}"
        )

        # ----------------------------------------------------
        # 2. BUSCAR NOMES VERNACULARES
        # ----------------------------------------------------

        nomes = buscar_nomes_vernaculares(
            taxon_key
        )

        if not nomes:

            print(
                "    Nenhum nome vernacular encontrado."
            )

            sem_nome_portugues += 1

            time.sleep(
                INTERVALO_ENTRE_REQUISICOES
            )

            continue

        # ----------------------------------------------------
        # 3. ESCOLHER NOME EM PORTUGUÊS
        # ----------------------------------------------------

        nome_popular = escolher_nome_portugues(
            nomes
        )

        if nome_popular is None:

            print(
                "    Nenhum nome em português."
            )

            sem_nome_portugues += 1

            time.sleep(
                INTERVALO_ENTRE_REQUISICOES
            )

            continue

        # ----------------------------------------------------
        # 4. ATUALIZAR DATAFRAME
        # ----------------------------------------------------

        df.at[
            indice,
            "nome_popular"
        ] = nome_popular

        nomes_adicionados += 1

        print(
            f"    Nome encontrado: "
            f"{nome_popular}"
        )

        time.sleep(
            INTERVALO_ENTRE_REQUISICOES
        )

    # ========================================================
    # SALVAR RESULTADO
    # ========================================================

    print(
        "\nSalvando dim_especie atualizada..."
    )

    df.to_csv(
        ARQUIVO_DIM_ESPECIE,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # RESUMO
    # ========================================================

    total_com_nome_final = (
        df["nome_popular"].notna().sum()
    )

    total_sem_nome_final = (
        df["nome_popular"].isna().sum()
    )

    print("\n" + "=" * 60)
    print("RESUMO DO ENRIQUECIMENTO")
    print("=" * 60)

    print(
        f"\nTotal de espécies: {len(df)}"
    )

    print(
        f"Com nome popular antes: "
        f"{total_com_nome_inicial}"
    )

    print(
        f"Nomes adicionados pela GBIF: "
        f"{nomes_adicionados}"
    )

    print(
        f"Com nome popular depois: "
        f"{total_com_nome_final}"
    )

    print(
        f"Sem nome popular depois: "
        f"{total_sem_nome_final}"
    )

    print(
        f"\nSem match confiável: "
        f"{sem_match}"
    )

    print(
        f"Sem nome em português encontrado: "
        f"{sem_nome_portugues}"
    )

    print(
        f"Falhas/erros de consulta: "
        f"{erros}"
    )

    print(
        f"\nArquivo atualizado:\n"
        f"{ARQUIVO_DIM_ESPECIE}"
    )

    print(
        f"\nBackup original:\n"
        f"{ARQUIVO_BACKUP}"
    )

    print("\n" + "=" * 60)
    print("ENRIQUECIMENTO FINALIZADO")
    print("=" * 60)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    enriquecer_nomes_populares()