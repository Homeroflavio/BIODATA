import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from extract_icmbio import obter_lista_especies_icmbio


# ============================================================
# CONFIGURAÇÕES
# ============================================================

load_dotenv()

IUCN_API_KEY = os.getenv("IUCN_API_KEY")

URL_IUCN_TAXON = (
    "https://api.iucnredlist.org/api/v4/taxa/scientific_name"
)

PASTA_DADOS_BRUTOS = (
    Path(__file__).resolve().parent.parent / "dados_brutos"
)

ARQUIVO_IUCN = (
    PASTA_DADOS_BRUTOS / "iucn_avaliacoes_raw.jsonl"
)

ARQUIVO_CONTROLE = (
    PASTA_DADOS_BRUTOS / "iucn_extracao_controle.json"
)


# None = processa todas as espécies.
# Para teste, use um número inteiro, por exemplo: 5 ou 100.
LIMITE_ESPECIES_TESTE = None


# Intervalo entre espécies.
INTERVALO_ENTRE_ESPECIES = 2


# Número máximo de tentativas apenas para erros temporários.
MAX_TENTATIVAS = 5


# ============================================================
# ARQUIVO DE CONTROLE
# ============================================================

def carregar_controle() -> dict:
    """
    Carrega o histórico das espécies já processadas.

    Permite retomar a execução caso o script seja interrompido.
    """

    if not ARQUIVO_CONTROLE.exists():

        return {
            "processadas": [],
            "sem_resultado": [],
            "com_erro": []
        }

    with open(
        ARQUIVO_CONTROLE,
        "r",
        encoding="utf-8"
    ) as arquivo:

        controle = json.load(arquivo)

    controle.setdefault("processadas", [])
    controle.setdefault("sem_resultado", [])
    controle.setdefault("com_erro", [])

    return controle


def salvar_controle(controle: dict) -> None:
    """
    Salva imediatamente o progresso da extração.
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
# PREPARAÇÃO DO NOME CIENTÍFICO
# ============================================================

def separar_nome_especie(
    nome_especie: str
) -> tuple[str, str] | None:
    """
    Separa o nome científico em gênero e espécie.

    Exemplo:

        Amazona pretrei
        ↓
        ("Amazona", "pretrei")
    """

    partes = nome_especie.strip().split()

    if len(partes) < 2:
        return None

    genero = partes[0]
    especie = partes[1]

    return genero, especie


# ============================================================
# CONSULTA À IUCN
# ============================================================

def consultar_iucn(
    genero: str,
    especie: str
) -> dict | None:
    """
    Consulta a API da IUCN pelo gênero e espécie.

    Retorna:
        dict -> dados encontrados
        None -> espécie não encontrada na IUCN

    Erros temporários fazem novas tentativas.

    Erros 404 NÃO fazem retry, pois significam que o táxon
    não foi encontrado no endpoint.
    """

    headers = {
        "Authorization": f"Bearer {IUCN_API_KEY}",
        "Accept": "application/json"
    }

    parametros = {
        "genus_name": genero,
        "species_name": especie
    }

    for tentativa in range(1, MAX_TENTATIVAS + 1):

        try:

            resposta = requests.get(
                URL_IUCN_TAXON,
                headers=headers,
                params=parametros,
                timeout=(10, 45)
            )

            # ------------------------------------------------
            # ESPÉCIE NÃO ENCONTRADA
            # ------------------------------------------------

            if resposta.status_code == 404:

                return None

            # ------------------------------------------------
            # RATE LIMIT
            # ------------------------------------------------

            if resposta.status_code == 429:

                espera = tentativa * 10

                print(
                    f"    Limite de requisições atingido "
                    f"(429)."
                )

                if tentativa == MAX_TENTATIVAS:

                    resposta.raise_for_status()

                print(
                    f"    Tentando novamente em "
                    f"{espera}s..."
                )

                time.sleep(espera)

                continue

            # ------------------------------------------------
            # OUTROS ERROS HTTP
            # ------------------------------------------------

            resposta.raise_for_status()

            dados = resposta.json()

            if not dados:
                return None

            return dados

        except requests.exceptions.Timeout:

            print(
                f"    Timeout "
                f"(tentativa {tentativa}/{MAX_TENTATIVAS})."
            )

        except requests.exceptions.ConnectionError:

            print(
                f"    Erro de conexão "
                f"(tentativa {tentativa}/{MAX_TENTATIVAS})."
            )

        except requests.exceptions.HTTPError as erro:

            status_code = erro.response.status_code

            print(
                f"    Erro HTTP {status_code} "
                f"(tentativa {tentativa}/{MAX_TENTATIVAS})."
            )

        except requests.exceptions.RequestException as erro:

            print(
                f"    Falha na consulta "
                f"(tentativa {tentativa}/{MAX_TENTATIVAS}): "
                f"{erro.__class__.__name__}"
            )

        # ----------------------------------------------------
        # SE TODAS AS TENTATIVAS FALHARAM
        # ----------------------------------------------------

        if tentativa == MAX_TENTATIVAS:
            raise requests.exceptions.RequestException(
                "Não foi possível consultar a IUCN "
                "após todas as tentativas."
            )

        espera = tentativa * 5

        print(
            f"    Tentando novamente em {espera}s..."
        )

        time.sleep(espera)


# ============================================================
# SELECIONAR AVALIAÇÃO MAIS RECENTE
# ============================================================

def obter_avaliacao_mais_recente(
    dados_iucn: dict
) -> dict | None:
    """
    Procura a avaliação marcada como latest = True.
    """

    avaliacoes = dados_iucn.get(
        "assessments",
        []
    )

    for avaliacao in avaliacoes:

        if avaliacao.get("latest") is True:
            return avaliacao

    return None


# ============================================================
# PREPARAR REGISTRO
# ============================================================

def preparar_registro_iucn(
    dados_iucn: dict,
    nome_consultado: str
) -> dict:
    """
    Monta um registro bruto contendo:

        - espécie consultada
        - dados taxonômicos
        - avaliação mais recente
        - histórico completo de avaliações
    """

    taxon = dados_iucn.get(
        "taxon",
        {}
    )

    avaliacao_atual = obter_avaliacao_mais_recente(
        dados_iucn
    )

    registro = {
        "_biodata_nome_consultado": nome_consultado,

        "taxon": taxon,

        "assessment_latest": avaliacao_atual,

        "assessments_history": dados_iucn.get(
            "assessments",
            []
        )
    }

    return registro


# ============================================================
# SALVAMENTO INCREMENTAL
# ============================================================

def salvar_registro_iucn(
    registro: dict
) -> None:
    """
    Adiciona um registro ao JSONL.
    """

    with open(
        ARQUIVO_IUCN,
        "a",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            registro,
            arquivo,
            ensure_ascii=False
        )

        arquivo.write("\n")


# ============================================================
# EXTRAÇÃO PRINCIPAL
# ============================================================

def extrair_dados_iucn(
    especies: list[str]
) -> None:
    """
    Executa a extração incremental da IUCN.

    Para cada espécie:

        espécie
          ↓
        separa gênero e espécie
          ↓
        consulta API
          ↓
        salva resultado
          ↓
        atualiza controle

    Espécies já processadas são ignoradas.

    Espécies não encontradas recebem 404 e são marcadas
    como sem_resultado.

    Erros temporários são tentados novamente.
    """

    PASTA_DADOS_BRUTOS.mkdir(
        exist_ok=True
    )

    controle = carregar_controle()

    processadas = set(
        controle["processadas"]
    )

    total = len(especies)

    print(
        f"\nEspécies já processadas anteriormente: "
        f"{len(processadas)}"
    )

    for indice, nome_especie in enumerate(
        especies,
        start=1
    ):

        # ----------------------------------------------------
        # PULAR ESPÉCIES JÁ PROCESSADAS
        # ----------------------------------------------------

        if nome_especie in processadas:

            print(
                f"[{indice}/{total}] "
                f"Pulando (já processada): "
                f"{nome_especie}"
            )

            continue

        print(
            f"\n[{indice}/{total}] "
            f"Processando: {nome_especie}"
        )

        # ----------------------------------------------------
        # 1. SEPARAR NOME
        # ----------------------------------------------------

        nome_separado = separar_nome_especie(
            nome_especie
        )

        if nome_separado is None:

            print(
                "    Nome científico inválido."
            )

            if (
                nome_especie
                not in controle["sem_resultado"]
            ):
                controle["sem_resultado"].append(
                    nome_especie
                )

            controle["processadas"].append(
                nome_especie
            )

            salvar_controle(controle)

            processadas.add(nome_especie)

            continue

        genero, especie = nome_separado

        print(
            f"    Consulta: "
            f"{genero} {especie}"
        )

        # ----------------------------------------------------
        # 2. CONSULTAR IUCN
        # ----------------------------------------------------

        try:

            dados_iucn = consultar_iucn(
                genero=genero,
                especie=especie
            )

        except requests.exceptions.RequestException:

            print(
                "    ERRO: não foi possível "
                "consultar a IUCN após todas "
                "as tentativas."
            )

            if (
                nome_especie
                not in controle["com_erro"]
            ):
                controle["com_erro"].append(
                    nome_especie
                )

            salvar_controle(controle)

            time.sleep(
                INTERVALO_ENTRE_ESPECIES
            )

            continue

        # ----------------------------------------------------
        # 3. SEM RESULTADO / 404
        # ----------------------------------------------------

        if dados_iucn is None:

            print(
                "    Nenhum resultado encontrado "
                "na IUCN."
            )

            if (
                nome_especie
                not in controle["sem_resultado"]
            ):
                controle["sem_resultado"].append(
                    nome_especie
                )

            controle["processadas"].append(
                nome_especie
            )

            salvar_controle(controle)

            processadas.add(nome_especie)

            time.sleep(
                INTERVALO_ENTRE_ESPECIES
            )

            continue

        # ----------------------------------------------------
        # 4. PREPARAR E SALVAR
        # ----------------------------------------------------

        registro = preparar_registro_iucn(
            dados_iucn=dados_iucn,
            nome_consultado=nome_especie
        )

        salvar_registro_iucn(registro)

        avaliacao_atual = registro.get(
            "assessment_latest"
        )

        if avaliacao_atual:

            categoria = avaliacao_atual.get(
                "red_list_category_code"
            )

            ano = avaliacao_atual.get(
                "year_published"
            )

            print(
                f"    Avaliação atual: "
                f"{categoria} ({ano})"
            )

        else:

            print(
                "    Resultado encontrado, "
                "mas sem avaliação latest."
            )

        # ----------------------------------------------------
        # 5. MARCAR COMO PROCESSADA
        # ----------------------------------------------------

        controle["processadas"].append(
            nome_especie
        )

        salvar_controle(controle)

        processadas.add(nome_especie)

        time.sleep(
            INTERVALO_ENTRE_ESPECIES
        )

    # ========================================================
    # RESUMO FINAL
    # ========================================================

    print("\n" + "=" * 60)
    print("RESUMO DA EXTRAÇÃO IUCN")
    print("=" * 60)

    print(
        f"Espécies processadas: "
        f"{len(controle['processadas'])}"
    )

    print(
        f"Espécies sem resultado: "
        f"{len(controle['sem_resultado'])}"
    )

    print(
        f"Espécies com erro de consulta: "
        f"{len(controle['com_erro'])}"
    )

    print(
        f"\nArquivo de dados:\n"
        f"{ARQUIVO_IUCN}"
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
    print("EXTRAÇÃO IUCN — BIODATA")
    print("=" * 60)

    # --------------------------------------------------------
    # VALIDAR API KEY
    # --------------------------------------------------------

    if not IUCN_API_KEY:

        raise ValueError(
            "IUCN_API_KEY não encontrada no arquivo .env"
        )

    # --------------------------------------------------------
    # OBTER ESPÉCIES
    # --------------------------------------------------------

    especies = obter_lista_especies_icmbio()

    print(
        f"\nEspécies obtidas do ICMBio: "
        f"{len(especies)}"
    )

    # --------------------------------------------------------
    # MODO TESTE
    # --------------------------------------------------------

    if LIMITE_ESPECIES_TESTE is not None:

        especies = especies[
            :LIMITE_ESPECIES_TESTE
        ]

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

    extrair_dados_iucn(especies)