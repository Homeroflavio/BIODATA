import json
import time
from pathlib import Path

import requests

from extract_icmbio import obter_lista_especies_icmbio


# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL_SPECIES_MATCH = "https://api.gbif.org/v1/species/match"
URL_OCCURRENCE_SEARCH = "https://api.gbif.org/v1/occurrence/search"

PASTA_DADOS_BRUTOS = Path(__file__).resolve().parent.parent / "dados_brutos"

ARQUIVO_OCORRENCIAS = (
    PASTA_DADOS_BRUTOS / "gbif_ocorrencias_raw.jsonl"
)

ARQUIVO_CONTROLE = (
    PASTA_DADOS_BRUTOS / "gbif_extracao_controle.json"
)

# None = processa todas as espécies.
# Para teste, use um número inteiro, por exemplo: 5 ou 100.
LIMITE_ESPECIES_TESTE = None

# Máximo de ocorrências coletadas por espécie.
LIMITE_OCORRENCIAS_POR_ESPECIE = 100

# Pequena pausa entre espécies.
INTERVALO_ENTRE_ESPECIES = 0

# Número máximo de tentativas para cada requisição à API.
MAX_TENTATIVAS = 5


# ============================================================
# ARQUIVO DE CONTROLE
# ============================================================

def carregar_controle() -> dict:
    """
    Carrega o histórico da extração anterior.

    Permite retomar a execução sem repetir espécies já processadas.
    Mantém compatibilidade com arquivos de controle criados por
    versões anteriores do extractor.
    """

    if not ARQUIVO_CONTROLE.exists():
        return {
            "processadas": [],
            "sem_match": [],
            "sem_ocorrencias": [],
            "com_erro": []
        }

    with open(
        ARQUIVO_CONTROLE,
        "r",
        encoding="utf-8"
    ) as arquivo:
        controle = json.load(arquivo)

    controle.setdefault("processadas", [])
    controle.setdefault("sem_match", [])
    controle.setdefault("sem_ocorrencias", [])
    controle.setdefault("com_erro", [])

    return controle


def salvar_controle(controle: dict) -> None:
    """
    Salva imediatamente o estado atual da extração.
    """

    with open(
        ARQUIVO_CONTROLE,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            controle,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# MATCH DE ESPÉCIE
# ============================================================

def encontrar_taxon_key(nome_especie: str) -> int | None:
    """
    Busca o taxonKey da GBIF para um nome científico.

    Retorna:
        int  -> match encontrado.
        None -> consulta realizada com sucesso, mas sem match
                suficientemente confiável.

    Lança RequestException se todas as tentativas falharem.
    """

    for tentativa in range(1, MAX_TENTATIVAS + 1):

        try:
            resposta = requests.get(
                URL_SPECIES_MATCH,
                params={"name": nome_especie},
                timeout=(10, 30)
            )

            resposta.raise_for_status()

            resultado = resposta.json()

            match_type = resultado.get("matchType")
            confidence = resultado.get("confidence", 0)
            taxon_key = resultado.get("usageKey")

            if (
                match_type != "NONE"
                and confidence >= 80
                and taxon_key is not None
            ):
                return taxon_key

            return None

        except (
            requests.exceptions.RequestException,
            KeyboardInterrupt
        ) as erro:

            print(
                f"    Falha no match "
                f"(tentativa {tentativa}/{MAX_TENTATIVAS}): "
                f"{erro.__class__.__name__}"
            )

            if tentativa == MAX_TENTATIVAS:

                raise requests.exceptions.RequestException(
                    f"Falha no match para {nome_especie} "
                    f"após {MAX_TENTATIVAS} tentativas."
                )

            espera = tentativa * 3

            print(
                f"    Tentando novamente em {espera}s..."
            )

            time.sleep(espera)

    return None


# ============================================================
# OCORRÊNCIAS
# ============================================================

def buscar_ocorrencias_especie(
    taxon_key: int,
    limite: int = LIMITE_OCORRENCIAS_POR_ESPECIE
) -> list[dict]:
    """
    Busca até N ocorrências georreferenciadas para uma espécie.

    Retorna uma lista vazia apenas quando a GBIF respondeu
    corretamente, mas não encontrou ocorrências.

    Lança RequestException se todas as tentativas falharem.
    """

    parametros = {
        "taxonKey": taxon_key,
        "hasCoordinate": "true",
        "limit": limite,
        "offset": 0
    }

    for tentativa in range(1, MAX_TENTATIVAS + 1):

        try:
            resposta = requests.get(
                URL_OCCURRENCE_SEARCH,
                params=parametros,
                timeout=(10, 45)
            )

            resposta.raise_for_status()

            dados = resposta.json()

            return dados.get("results", [])

        except (
            requests.exceptions.RequestException,
            KeyboardInterrupt
        ) as erro:

            print(
                f"    Falha ao buscar ocorrências "
                f"(tentativa {tentativa}/{MAX_TENTATIVAS}): "
                f"{erro.__class__.__name__}"
            )

            if tentativa == MAX_TENTATIVAS:

                raise requests.exceptions.RequestException(
                    f"Falha ao buscar ocorrências para "
                    f"taxonKey {taxon_key} após "
                    f"{MAX_TENTATIVAS} tentativas."
                )

            espera = tentativa * 3

            print(
                f"    Tentando novamente em {espera}s..."
            )

            time.sleep(espera)

    return []


# ============================================================
# SALVAMENTO INCREMENTAL
# ============================================================

def salvar_ocorrencias_incrementalmente(
    ocorrencias: list[dict],
    nome_especie: str,
    taxon_key: int
) -> None:
    """
    Adiciona as ocorrências de uma espécie ao arquivo JSONL.

    Usa modo append, portanto registros já salvos não são apagados.
    """

    if not ocorrencias:
        return

    with open(
        ARQUIVO_OCORRENCIAS,
        "a",
        encoding="utf-8"
    ) as arquivo:

        for ocorrencia in ocorrencias:

            ocorrencia["_biodata_nome_consultado"] = nome_especie
            ocorrencia["_biodata_taxon_key_consultado"] = taxon_key

            json.dump(
                ocorrencia,
                arquivo,
                ensure_ascii=False
            )

            arquivo.write("\n")


# ============================================================
# EXTRAÇÃO PRINCIPAL
# ============================================================

def extrair_ocorrencias_gbif(
    especies: list[str]
) -> None:
    """
    Executa a extração incremental da GBIF.

    Para cada espécie:
        1. Busca o taxonKey.
        2. Busca ocorrências georreferenciadas.
        3. Salva os dados imediatamente.
        4. Atualiza o arquivo de controle.

    Em caso de falha temporária, a requisição é repetida.
    Caso todas as tentativas falhem, a espécie é registrada
    em 'com_erro' e a extração continua.
    """

    PASTA_DADOS_BRUTOS.mkdir(exist_ok=True)

    controle = carregar_controle()

    processadas = set(controle["processadas"])

    total = len(especies)

    print(
        f"\nEspécies já processadas anteriormente: "
        f"{len(processadas)}"
    )

    for indice, nome_especie in enumerate(especies, start=1):

        # ----------------------------------------------------
        # PULAR ESPÉCIES JÁ PROCESSADAS
        # ----------------------------------------------------

        if nome_especie in processadas:

            print(
                f"[{indice}/{total}] "
                f"Pulando (já processada): {nome_especie}"
            )

            continue

        print(
            f"\n[{indice}/{total}] "
            f"Processando: {nome_especie}"
        )

        # ----------------------------------------------------
        # 1. MATCH
        # ----------------------------------------------------

        try:
            taxon_key = encontrar_taxon_key(nome_especie)

        except requests.exceptions.RequestException:

            print(
                "    ERRO: não foi possível consultar a GBIF "
                "após todas as tentativas. Pulando espécie."
            )

            if nome_especie not in controle["com_erro"]:
                controle["com_erro"].append(nome_especie)

            salvar_controle(controle)

            time.sleep(INTERVALO_ENTRE_ESPECIES)

            continue

        # ----------------------------------------------------
        # SEM MATCH
        # ----------------------------------------------------

        if taxon_key is None:

            print(
                "    Sem correspondência confiável na GBIF."
            )

            if nome_especie not in controle["sem_match"]:
                controle["sem_match"].append(nome_especie)

            controle["processadas"].append(nome_especie)

            salvar_controle(controle)

            processadas.add(nome_especie)

            time.sleep(INTERVALO_ENTRE_ESPECIES)

            continue

        print(f"    TaxonKey: {taxon_key}")

        # ----------------------------------------------------
        # 2. OCORRÊNCIAS
        # ----------------------------------------------------

        try:
            ocorrencias = buscar_ocorrencias_especie(
                taxon_key=taxon_key
            )

        except requests.exceptions.RequestException:

            print(
                "    ERRO: não foi possível buscar ocorrências "
                "após todas as tentativas. Pulando espécie."
            )

            if nome_especie not in controle["com_erro"]:
                controle["com_erro"].append(nome_especie)

            salvar_controle(controle)

            time.sleep(INTERVALO_ENTRE_ESPECIES)

            continue

        # ----------------------------------------------------
        # 3. SALVAR RESULTADO
        # ----------------------------------------------------

        if ocorrencias:

            salvar_ocorrencias_incrementalmente(
                ocorrencias=ocorrencias,
                nome_especie=nome_especie,
                taxon_key=taxon_key
            )

            print(
                f"    Ocorrências salvas: "
                f"{len(ocorrencias)}"
            )

        else:

            print(
                "    Nenhuma ocorrência com coordenadas."
            )

            if nome_especie not in controle["sem_ocorrencias"]:
                controle["sem_ocorrencias"].append(
                    nome_especie
                )

        # ----------------------------------------------------
        # 4. MARCAR COMO PROCESSADA
        # ----------------------------------------------------

        if nome_especie not in controle["processadas"]:
            controle["processadas"].append(nome_especie)

        salvar_controle(controle)

        processadas.add(nome_especie)

        time.sleep(INTERVALO_ENTRE_ESPECIES)

    # ========================================================
    # RESUMO FINAL
    # ========================================================

    print("\n" + "=" * 60)
    print("RESUMO DA EXTRAÇÃO GBIF")
    print("=" * 60)

    print(
        f"Espécies processadas: "
        f"{len(controle['processadas'])}"
    )

    print(
        f"Espécies sem match: "
        f"{len(controle['sem_match'])}"
    )

    print(
        f"Espécies sem ocorrências georreferenciadas: "
        f"{len(controle['sem_ocorrencias'])}"
    )

    print(
        f"Espécies com erro de consulta: "
        f"{len(controle['com_erro'])}"
    )

    print(
        f"\nArquivo de ocorrências:\n"
        f"{ARQUIVO_OCORRENCIAS}"
    )

    print(
        f"\nArquivo de controle:\n"
        f"{ARQUIVO_CONTROLE}"
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("EXTRAÇÃO GBIF — BIODATA")
    print("=" * 60)

    especies = obter_lista_especies_icmbio()

    print(
        f"\nEspécies obtidas do ICMBio: "
        f"{len(especies)}"
    )

    # --------------------------------------------------------
    # MODO TESTE
    # --------------------------------------------------------

    if LIMITE_ESPECIES_TESTE is not None:

        especies = especies[:LIMITE_ESPECIES_TESTE]

        print(
            f"Modo teste ativado: "
            f"{len(especies)} espécies."
        )

    else:

        print(
            f"Modo completo ativado: "
            f"{len(especies)} espécies."
        )

    # --------------------------------------------------------
    # EXTRAÇÃO
    # --------------------------------------------------------

    extrair_ocorrencias_gbif(especies)