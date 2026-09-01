import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÕES
# ============================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# Pasta raiz do projeto
PASTA_PROJETO = Path(__file__).resolve().parent.parent

# Dados finais
PASTA_DADOS = PASTA_PROJETO / "dados_finais"


# ============================================================
# CONEXÃO
# ============================================================

def conectar_banco():
    """
    Cria conexão com o PostgreSQL.
    """

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# ============================================================
# VALIDAÇÃO DAS VARIÁVEIS DE AMBIENTE
# ============================================================

def validar_credenciais():
    """
    Verifica se todas as variáveis necessárias existem.
    """

    variaveis = {
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_NAME": DB_NAME,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD
    }

    faltando = [
        nome
        for nome, valor in variaveis.items()
        if not valor
    ]

    if faltando:

        raise ValueError(
            "Variáveis ausentes no .env: "
            + ", ".join(faltando)
        )


# ============================================================
# CARREGAMENTO DOS CSVs
# ============================================================

def carregar_csv(nome_arquivo: str) -> pd.DataFrame:
    """
    Carrega um CSV da pasta dados_finais.
    """

    caminho = PASTA_DADOS / nome_arquivo

    if not caminho.exists():

        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    df = pd.read_csv(caminho)

    print(
        f"Carregado: {nome_arquivo} "
        f"({len(df)} registros)"
    )

    return df


# ============================================================
# INSERÇÃO DE ESPÉCIES
# ============================================================

def carregar_dim_especie(
    cursor,
    df_especies: pd.DataFrame
):
    """
    Carrega dim_especie.

    O PostgreSQL gera automaticamente o ID SERIAL.
    """

    print("\nCarregando dim_especie...")

    registros = 0

    for _, linha in df_especies.iterrows():

        cursor.execute(
            """
            INSERT INTO dim_especie (
                nome_cientifico,
                nome_popular,
                reino,
                filo,
                classe,
                ordem,
                familia,
                genero,
                grupo_taxonomico
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT (nome_cientifico)
            DO NOTHING
            """,
            (
                linha["nome_cientifico"],
                tratar_nulo(linha.get("nome_popular")),
                tratar_nulo(linha.get("reino")),
                tratar_nulo(linha.get("filo")),
                tratar_nulo(linha.get("classe")),
                tratar_nulo(linha.get("ordem")),
                tratar_nulo(linha.get("familia")),
                tratar_nulo(linha.get("genero")),
                tratar_nulo(linha.get("grupo_taxonomico"))
            )
        )

        registros += 1

    print(
        f"dim_especie processada: "
        f"{registros} registros"
    )


# ============================================================
# INSERÇÃO DE CATEGORIAS DE RISCO
# ============================================================

def carregar_dim_categoria_risco(
    cursor,
    df_categorias: pd.DataFrame
):
    """
    Carrega dim_categoria_risco.

    Linhas sem código são ignoradas porque
    codigo é PRIMARY KEY no PostgreSQL.
    """

    print("\nCarregando dim_categoria_risco...")

    registros = 0
    ignorados = 0

    for _, linha in df_categorias.iterrows():

        codigo = tratar_nulo(linha.get("codigo"))

        # Ignora NaN, NULL e strings vazias
        if codigo is None or str(codigo).strip() == "":

            ignorados += 1
            continue

        cursor.execute(
            """
            INSERT INTO dim_categoria_risco (
                codigo,
                nome,
                sistema,
                peso_numerico
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (codigo)
            DO NOTHING
            """,
            (
                str(codigo).strip(),
                tratar_nulo(linha.get("nome")),
                tratar_nulo(linha.get("sistema")),
                tratar_inteiro(
                    linha.get("peso_numerico")
                )
            )
        )

        registros += 1

    print(
        f"dim_categoria_risco processada: "
        f"{registros} registros"
    )

    print(
        f"Categorias sem código ignoradas: "
        f"{ignorados}"
    )


# ============================================================
# INSERÇÃO DE LOCAIS
# ============================================================

def carregar_dim_local(
    cursor,
    df_locais: pd.DataFrame
):
    """
    Carrega dim_local.

    O PostgreSQL gera automaticamente o ID.
    """

    print("\nCarregando dim_local...")

    registros = 0

    for _, linha in df_locais.iterrows():

        cursor.execute(
            """
            INSERT INTO dim_local (
                pais,
                estado_provincia,
                continente
            )
            VALUES (%s, %s, %s)
            """,
            (
                tratar_nulo(linha.get("pais")),
                tratar_nulo(
                    linha.get("estado_provincia")
                ),
                tratar_nulo(linha.get("continente"))
            )
        )

        registros += 1

    print(
        f"dim_local processada: "
        f"{registros} registros"
    )


# ============================================================
# INSERÇÃO DE PAN
# ============================================================

def carregar_dim_pan(
    cursor,
    df_pan: pd.DataFrame
):
    """
    Carrega os Planos de Ação Nacional.
    """

    print("\nCarregando dim_pan...")

    registros = 0

    for _, linha in df_pan.iterrows():

        cursor.execute(
            """
            INSERT INTO dim_pan (
                id_pan,
                nome,
                nome_completo,
                abrangencia_taxonomica,
                abrangencia_geografica,
                ciclo,
                status,
                data_inicio,
                data_fim,
                ano_inicio,
                ano_fim,
                status_legal,
                site
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            )
            ON CONFLICT (id_pan)
            DO NOTHING
            """,
            (
                tratar_nulo(linha.get("id_pan")),
                tratar_nulo(linha.get("nome")),
                tratar_nulo(
                    linha.get("nome_completo")
                ),
                tratar_nulo(
                    linha.get(
                        "abrangencia_taxonomica"
                    )
                ),
                tratar_nulo(
                    linha.get(
                        "abrangencia_geografica"
                    )
                ),
                tratar_nulo(linha.get("ciclo")),
                tratar_nulo(linha.get("status")),
                tratar_data(
                    linha.get("data_inicio")
                ),
                tratar_data(
                    linha.get("data_fim")
                ),
                tratar_inteiro(
                    linha.get("ano_inicio")
                ),
                tratar_inteiro(
                    linha.get("ano_fim")
                ),
                tratar_nulo(
                    linha.get("status_legal")
                ),
                tratar_nulo(linha.get("site"))
            )
        )

        registros += 1

    print(
        f"dim_pan processada: "
        f"{registros} registros"
    )


# ============================================================
# MAPAS DE IDs
# ============================================================

def buscar_mapa_especies(cursor):
    """
    Cria mapa:

    nome_cientifico -> id da espécie
    """

    cursor.execute(
        """
        SELECT id, nome_cientifico
        FROM dim_especie
        """
    )

    return {
        nome_cientifico: id_especie
        for id_especie, nome_cientifico
        in cursor.fetchall()
    }


def buscar_mapa_locais(cursor):
    """
    Cria mapa:

    (pais, estado_provincia, continente)
    -> id do local
    """

    cursor.execute(
        """
        SELECT
            id,
            pais,
            estado_provincia,
            continente
        FROM dim_local
        """
    )

    mapa = {}

    for (
        id_local,
        pais,
        estado_provincia,
        continente
    ) in cursor.fetchall():

        chave = (
            pais,
            estado_provincia,
            continente
        )

        mapa[chave] = id_local

    return mapa


# ============================================================
# INSERÇÃO DE AVALIAÇÕES IUCN
# ============================================================

def carregar_fato_avaliacao_iucn(
    cursor,
    df_iucn: pd.DataFrame,
    mapa_especies: dict
):
    """
    Carrega avaliações históricas da IUCN.
    """

    print("\nCarregando fato_avaliacao_iucn...")

    registros = 0
    sem_especie = 0

    for _, linha in df_iucn.iterrows():

        nome_cientifico = linha["nome_cientifico"]

        especie_id = mapa_especies.get(
            nome_cientifico
        )

        if especie_id is None:

            sem_especie += 1
            continue

        cursor.execute(
            """
            INSERT INTO fato_avaliacao_iucn (
                assessment_id,
                especie_id,
                ano_publicacao,
                data_avaliacao,
                categoria_risco_codigo,
                e_avaliacao_atual,
                possivelmente_extinta,
                criterio,
                escopo
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT (assessment_id)
            DO NOTHING
            """,
            (
                int(linha["assessment_id"]),
                especie_id,
                int(linha["ano_publicacao"]),
                tratar_data(linha.get("data_avaliacao")),
                tratar_nulo(
                    linha.get(
                        "categoria_risco_codigo"
                    )
                ),
                tratar_booleano(
                    linha.get("e_avaliacao_atual")
                ),
                tratar_booleano(
                    linha.get("possivelmente_extinta")
                ),
                tratar_nulo(linha.get("criterio")),
                tratar_nulo(linha.get("escopo"))
            )
        )

        registros += 1

    print(
        f"fato_avaliacao_iucn processada: "
        f"{registros} registros"
    )

    print(
        f"Avaliações sem espécie correspondente: "
        f"{sem_especie}"
    )


# ============================================================
# INSERÇÃO DE AVALIAÇÕES ICMBIO
# ============================================================

def carregar_fato_avaliacao_icmbio(
    cursor,
    df_icmbio: pd.DataFrame,
    mapa_especies: dict
):
    """
    Carrega avaliações do ICMBio.
    """

    print("\nCarregando fato_avaliacao_icmbio...")

    registros = 0
    sem_especie = 0

    for _, linha in df_icmbio.iterrows():

        nome_cientifico = linha["nome_cientifico"]

        especie_id = mapa_especies.get(
            nome_cientifico
        )

        if especie_id is None:

            sem_especie += 1
            continue

        cursor.execute(
            """
            INSERT INTO fato_avaliacao_icmbio (
                especie_id,
                taxon_id_icmbio,
                consta_lista_ameacada,
                dado_sensivel
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                especie_id,
                tratar_inteiro(
                    linha.get("taxon_id_icmbio")
                ),
                tratar_booleano(
                    linha.get(
                        "consta_lista_ameacada"
                    )
                ),
                tratar_booleano(
                    linha.get("dado_sensivel")
                )
            )
        )

        registros += 1

    print(
        f"fato_avaliacao_icmbio processada: "
        f"{registros} registros"
    )

    print(
        f"Avaliações sem espécie correspondente: "
        f"{sem_especie}"
    )


# ============================================================
# INSERÇÃO DE OCORRÊNCIAS GBIF
# ============================================================

def carregar_fato_ocorrencia_gbif(
    cursor,
    df_ocorrencias: pd.DataFrame,
    mapa_especies: dict,
    mapa_locais: dict
):
    """
    Carrega ocorrências da GBIF.
    """

    print("\nCarregando fato_ocorrencia_gbif...")

    registros = 0
    sem_especie = 0
    sem_local = 0

    for _, linha in df_ocorrencias.iterrows():

        # ----------------------------------------------------
        # ESPÉCIE
        # ----------------------------------------------------

        nome_cientifico = linha[
            "nome_cientifico"
        ]

        especie_id = mapa_especies.get(
            nome_cientifico
        )

        if especie_id is None:

            sem_especie += 1
            continue

        # ----------------------------------------------------
        # LOCAL
        # ----------------------------------------------------

        chave_local = (
            tratar_nulo(linha.get("pais")),
            tratar_nulo(
                linha.get("estado_provincia")
            ),
            tratar_nulo(
                linha.get("continente")
            )
        )

        local_id = mapa_locais.get(
            chave_local
        )

        if local_id is None:

            sem_local += 1
            continue

        # ----------------------------------------------------
        # INSERÇÃO
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO fato_ocorrencia_gbif (
                gbif_id,
                especie_id,
                local_id,
                latitude,
                longitude,
                incerteza_metros,
                categoria_iucn,
                data_observacao,
                tem_alerta_qualidade
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT (gbif_id)
            DO NOTHING
            """,
            (
                int(linha["gbif_id"]),
                especie_id,
                local_id,
                float(linha["latitude"]),
                float(linha["longitude"]),
                tratar_float(
                    linha.get("incerteza_metros")
                ),
                tratar_nulo(
                    linha.get("categoria_iucn")
                ),
                tratar_data(
                    linha.get("data_observacao")
                ),
                tratar_booleano(
                    linha.get(
                        "tem_alerta_qualidade"
                    )
                )
            )
        )

        registros += 1

    print(
        f"fato_ocorrencia_gbif processada: "
        f"{registros} registros"
    )

    print(
        f"Ocorrências sem espécie correspondente: "
        f"{sem_especie}"
    )

    print(
        f"Ocorrências sem local correspondente: "
        f"{sem_local}"
    )


# ============================================================
# INSERÇÃO DA RELAÇÃO PAN × ESPÉCIE
# ============================================================

def carregar_pan_especie(
    cursor,
    df_pan_especie: pd.DataFrame,
    mapa_especies: dict
):
    """
    Carrega a relação entre PAN e espécie.

    O CSV possui o nome científico.
    O especie_id é obtido pelo mapa criado após
    carregar dim_especie.
    """

    print("\nCarregando pan_especie...")

    registros = 0
    sem_especie = 0

    for _, linha in df_pan_especie.iterrows():

        id_pan = tratar_nulo(
            linha.get("id_pan")
        )

        nome_cientifico = tratar_nulo(
            linha.get("nome_cientifico")
        )

        especie_id = mapa_especies.get(
            nome_cientifico
        )

        if especie_id is None:

            sem_especie += 1
            continue

        cursor.execute(
            """
            INSERT INTO pan_especie (
                id_pan,
                especie_id
            )
            VALUES (%s, %s)
            ON CONFLICT (id_pan, especie_id)
            DO NOTHING
            """,
            (
                id_pan,
                especie_id
            )
        )

        registros += 1

    print(
        f"pan_especie processada: "
        f"{registros} relações"
    )

    print(
        f"Relações sem espécie correspondente: "
        f"{sem_especie}"
    )


# ============================================================
# INSERÇÃO DA RELAÇÃO PAN × BIOMA
# ============================================================

def carregar_pan_bioma(
    cursor,
    df_pan_bioma: pd.DataFrame
):
    """
    Carrega relação entre PAN e bioma.
    """

    print("\nCarregando pan_bioma...")

    registros = 0

    for _, linha in df_pan_bioma.iterrows():

        id_pan = tratar_nulo(
            linha.get("id_pan")
        )

        bioma = tratar_nulo(
            linha.get("bioma")
        )

        if id_pan is None or bioma is None:

            continue

        cursor.execute(
            """
            INSERT INTO pan_bioma (
                id_pan,
                bioma
            )
            VALUES (%s, %s)
            ON CONFLICT (id_pan, bioma)
            DO NOTHING
            """,
            (
                id_pan,
                bioma
            )
        )

        registros += 1

    print(
        f"pan_bioma processada: "
        f"{registros} relações"
    )


# ============================================================
# INSERÇÃO DA RELAÇÃO PAN × ESTADO
# ============================================================

def carregar_pan_estado(
    cursor,
    df_pan_estado: pd.DataFrame
):
    """
    Carrega relação entre PAN e estado.
    """

    print("\nCarregando pan_estado...")

    registros = 0

    for _, linha in df_pan_estado.iterrows():

        id_pan = tratar_nulo(
            linha.get("id_pan")
        )

        sigla_estado = tratar_nulo(
            linha.get("sigla_estado")
        )

        if id_pan is None or sigla_estado is None:

            continue

        cursor.execute(
            """
            INSERT INTO pan_estado (
                id_pan,
                sigla_estado
            )
            VALUES (%s, %s)
            ON CONFLICT (id_pan, sigla_estado)
            DO NOTHING
            """,
            (
                id_pan,
                sigla_estado
            )
        )

        registros += 1

    print(
        f"pan_estado processada: "
        f"{registros} relações"
    )

# ============================================================
# ESPÉCIES EM DESTAQUE
# ============================================================

def carregar_especies_destaque(cursor):
    """
    Executa o SQL que popula a tabela especie_destaque.
    """

    print("\nCarregando espécies em destaque...")

    caminho_sql = (
        PASTA_PROJETO
        / "sql"
        / "especie_destaque.sql"
    )

    if not caminho_sql.exists():

        raise FileNotFoundError(
            f"Arquivo SQL não encontrado: {caminho_sql}"
        )

    with open(
        caminho_sql,
        "r",
        encoding="utf-8"
    ) as arquivo:

        sql = arquivo.read()

    cursor.execute(sql)

    print(
        "Espécies em destaque carregadas com sucesso."
    )

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def tratar_nulo(valor):
    """
    Converte NaN/NaT do pandas para None.
    """

    if pd.isna(valor):
        return None

    return valor


def tratar_inteiro(valor):
    """
    Converte valores numéricos para int.
    """

    if pd.isna(valor):
        return None

    return int(valor)


def tratar_float(valor):
    """
    Converte valores numéricos para float.
    """

    if pd.isna(valor):
        return None

    return float(valor)


def tratar_data(valor):
    """
    Converte NaN/NaT para None.
    """

    if pd.isna(valor):
        return None

    return str(valor)


def tratar_booleano(valor):
    """
    Converte valores para booleano.
    """

    if pd.isna(valor):
        return None

    if isinstance(valor, bool):
        return valor

    if isinstance(valor, str):

        return valor.strip().lower() in (
            "true",
            "1",
            "yes",
            "sim"
        )

    return bool(valor)


# ============================================================
# VALIDAÇÃO FINAL
# ============================================================

def mostrar_contagens(cursor):
    """
    Mostra quantidade de registros no banco.
    """

    tabelas = [
        "dim_especie",
        "dim_categoria_risco",
        "dim_local",
        "dim_pan",
        "fato_avaliacao_icmbio",
        "fato_avaliacao_iucn",
        "fato_ocorrencia_gbif",
        "pan_especie",
        "pan_bioma",
        "pan_estado"
    ]

    print("\n" + "=" * 60)
    print("REGISTROS CARREGADOS NO POSTGRESQL")
    print("=" * 60)

    for tabela in tabelas:

        cursor.execute(
            f"SELECT COUNT(*) FROM {tabela}"
        )

        quantidade = cursor.fetchone()[0]

        print(
            f"{tabela}: {quantidade}"
        )


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    print("=" * 60)
    print("LOAD POSTGRESQL — BIODATA")
    print("=" * 60)

    validar_credenciais()

    # --------------------------------------------------------
    # CARREGAR CSVs
    # --------------------------------------------------------

    print("\nCarregando arquivos CSV...")

    df_especies = carregar_csv(
        "dim_especie.csv"
    )

    df_icmbio = carregar_csv(
        "fato_avaliacao_icmbio.csv"
    )

    df_iucn = carregar_csv(
        "fato_avaliacao_iucn.csv"
    )

    df_categorias = carregar_csv(
        "dim_categoria_risco.csv"
    )

    df_locais = carregar_csv(
        "dim_local.csv"
    )

    df_ocorrencias = carregar_csv(
        "fato_ocorrencia_gbif.csv"
    )

    df_pan = carregar_csv(
        "dim_pan.csv"
    )

    df_pan_especie = carregar_csv(
        "pan_especie.csv"
    )

    df_pan_bioma = carregar_csv(
        "pan_bioma.csv"
    )

    df_pan_estado = carregar_csv(
        "pan_estado.csv"
    )

    # --------------------------------------------------------
    # CONECTAR
    # --------------------------------------------------------

    print("\nConectando ao PostgreSQL...")

    conexao = conectar_banco()

    cursor = conexao.cursor()

    print("Conexão estabelecida com sucesso.")

    try:

        # ----------------------------------------------------
        # DIMENSÕES
        # ----------------------------------------------------

        carregar_dim_especie(
            cursor,
            df_especies
        )

        carregar_dim_categoria_risco(
            cursor,
            df_categorias
        )

        carregar_dim_local(
            cursor,
            df_locais
        )

        carregar_dim_pan(
            cursor,
            df_pan
        )
        
      

        carregar_especies_destaque(cursor)

        # ----------------------------------------------------
        # COMMIT DAS DIMENSÕES
        #
        # Agora os IDs SERIAL de dim_especie e dim_local
        # já existem e podem ser usados nos mapas.
        # ----------------------------------------------------

        conexao.commit()

        print(
            "\nDimensões carregadas com sucesso."
        )

        # ----------------------------------------------------
        # MAPAS DE CHAVES
        # ----------------------------------------------------

        print(
            "\nCriando mapas de chaves estrangeiras..."
        )

        mapa_especies = buscar_mapa_especies(
            cursor
        )

        mapa_locais = buscar_mapa_locais(
            cursor
        )

        print(
            f"Mapa de espécies: "
            f"{len(mapa_especies)} espécies"
        )

        print(
            f"Mapa de locais: "
            f"{len(mapa_locais)} locais"
        )

        # ----------------------------------------------------
        # FATOS
        # ----------------------------------------------------

        carregar_fato_avaliacao_icmbio(
            cursor,
            df_icmbio,
            mapa_especies
        )

        carregar_fato_avaliacao_iucn(
            cursor,
            df_iucn,
            mapa_especies
        )

        carregar_fato_ocorrencia_gbif(
            cursor,
            df_ocorrencias,
            mapa_especies,
            mapa_locais
        )

        # ----------------------------------------------------
        # TABELAS PONTE DO PAN
        # ----------------------------------------------------

        carregar_pan_especie(
            cursor,
            df_pan_especie,
            mapa_especies
        )

        carregar_pan_bioma(
            cursor,
            df_pan_bioma
        )

        carregar_pan_estado(
            cursor,
            df_pan_estado
        )

        # ----------------------------------------------------
        # COMMIT FINAL
        # ----------------------------------------------------

        conexao.commit()

        print(
            "\nFatos e relações carregados com sucesso."
        )

        # ----------------------------------------------------
        # VALIDAÇÃO
        # ----------------------------------------------------

        mostrar_contagens(cursor)

        print("\n" + "=" * 60)
        print("LOAD FINALIZADO COM SUCESSO")
        print("=" * 60)

    except Exception as erro:

        conexao.rollback()

        print("\n" + "=" * 60)
        print("ERRO DURANTE O LOAD")
        print("=" * 60)

        print(
            f"{erro.__class__.__name__}: {erro}"
        )

        print(
            "\nTodas as alterações não confirmadas "
            "foram desfeitas."
        )

        raise

    finally:

        cursor.close()
        conexao.close()

        print(
            "\nConexão com PostgreSQL encerrada."
        )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()