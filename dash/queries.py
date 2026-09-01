from database import get_connection
import pandas as pd


# ============================================================
# TRADUÇÃO DAS CATEGORIAS IUCN
# ============================================================

TRADUCAO_CATEGORIAS = {
    "EX": "Extinta",
    "EW": "Extinta na natureza",
    "CR": "Criticamente em perigo",
    "EN": "Em perigo",
    "VU": "Vulnerável",
    "NT": "Quase ameaçada",
    "LC": "Pouco preocupante",
    "DD": "Dados insuficientes",
    "NE": "Não avaliada"
}


# ============================================================
# EXECUÇÃO DE QUERY SIMPLES
# ============================================================

def executar_query(query):
    """
    Executa uma consulta SQL que retorna um único valor.
    """

    conexao = get_connection()

    try:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchone()

        return resultado[0]

    finally:
        cursor.close()
        conexao.close()


# ============================================================
# PÁGINA 1 — VISÃO GERAL
# ============================================================

def contar_especies():
    return executar_query("""
        SELECT COUNT(*)
        FROM dim_especie;
    """)


def contar_avaliacoes_iucn():
    return executar_query("""
        SELECT COUNT(*)
        FROM fato_avaliacao_iucn;
    """)


def contar_ocorrencias_gbif():
    return executar_query("""
        SELECT COUNT(*)
        FROM fato_ocorrencia_gbif;
    """)


def contar_pans():
    return executar_query("""
        SELECT COUNT(*)
        FROM dim_pan;
    """)


def contar_especies_destaque():
    return executar_query("""
        SELECT COUNT(*)
        FROM especie_destaque;
    """)


# ============================================================
# PÁGINA 2 — CENÁRIO DE CONSERVAÇÃO
# ============================================================

def contar_especies_avaliacao_atual():
    """
    Conta quantas espécies possuem uma avaliação IUCN
    marcada como atual.
    """

    return executar_query("""
        SELECT COUNT(DISTINCT especie_id)
        FROM fato_avaliacao_iucn
        WHERE e_avaliacao_atual = TRUE;
    """)


def contar_especies_possivelmente_extintas():
    """
    Conta quantas espécies possuem registro indicando
    possibilidade de extinção.
    """

    return executar_query("""
        SELECT COUNT(DISTINCT especie_id)
        FROM fato_avaliacao_iucn
        WHERE possivelmente_extinta = TRUE;
    """)


# ============================================================
# AVALIAÇÕES IUCN POR CATEGORIA
# ============================================================

def obter_avaliacoes_por_categoria():
    """
    Retorna a quantidade de avaliações IUCN por categoria.

    Considera somente as categorias modernas da IUCN.
    """

    conexao = get_connection()

    try:

        query = """
            SELECT
                c.codigo,
                c.nome,
                c.peso_numerico,
                COUNT(a.id) AS quantidade_avaliacoes

            FROM dim_categoria_risco c

            LEFT JOIN fato_avaliacao_iucn a
                ON a.categoria_risco_codigo = c.codigo

            WHERE c.sistema = 'moderno'

            GROUP BY
                c.codigo,
                c.nome,
                c.peso_numerico

            ORDER BY
                c.peso_numerico DESC,
                quantidade_avaliacoes DESC;
        """

        df = pd.read_sql_query(
            query,
            conexao
        )

        df["nome_portugues"] = (
            df["codigo"]
            .map(TRADUCAO_CATEGORIAS)
            .fillna(df["nome"])
        )

        return df

    finally:
        conexao.close()


# ============================================================
# ESPÉCIES DISTINTAS POR CATEGORIA
# ============================================================

def obter_especies_por_categoria():
    """
    Retorna a quantidade de espécies distintas associadas
    a cada categoria de risco.

    Uma mesma espécie pode possuir várias avaliações.
    """

    conexao = get_connection()

    try:

        query = """
            SELECT
                c.codigo,
                c.nome,
                c.peso_numerico,
                COUNT(DISTINCT a.especie_id)
                    AS quantidade_especies

            FROM dim_categoria_risco c

            LEFT JOIN fato_avaliacao_iucn a
                ON a.categoria_risco_codigo = c.codigo

            WHERE c.sistema = 'moderno'

            GROUP BY
                c.codigo,
                c.nome,
                c.peso_numerico

            ORDER BY
                c.peso_numerico DESC,
                quantidade_especies DESC;
        """

        df = pd.read_sql_query(
            query,
            conexao
        )

        df["nome_portugues"] = (
            df["codigo"]
            .map(TRADUCAO_CATEGORIAS)
            .fillna(df["nome"])
        )

        return df

    finally:
        conexao.close()


# ============================================================
# ESPÉCIES COM AVALIAÇÃO ATUAL POR CATEGORIA
# ============================================================

def obter_avaliacoes_atuais_por_categoria():
    """
    Retorna a quantidade de espécies distintas que possuem
    uma avaliação atual em cada categoria de risco.
    """

    conexao = get_connection()

    try:

        query = """
            SELECT
                c.codigo,
                c.nome,
                c.peso_numerico,
                COUNT(DISTINCT a.especie_id)
                    AS quantidade_especies

            FROM dim_categoria_risco c

            LEFT JOIN fato_avaliacao_iucn a
                ON a.categoria_risco_codigo = c.codigo
                AND a.e_avaliacao_atual = TRUE

            WHERE c.sistema = 'moderno'

            GROUP BY
                c.codigo,
                c.nome,
                c.peso_numerico

            ORDER BY
                c.peso_numerico DESC,
                quantidade_especies DESC;
        """

        df = pd.read_sql_query(
            query,
            conexao
        )

        df["nome_portugues"] = (
            df["codigo"]
            .map(TRADUCAO_CATEGORIAS)
            .fillna(df["nome"])
        )

        return df

    finally:
        conexao.close()


# ============================================================
# PÁGINA 3 — BRASIL
# ============================================================

def contar_especies_icmbio_avaliadas():
    """
    Conta quantas espécies possuem avaliação no ICMBio.
    """

    return executar_query("""
        SELECT COUNT(DISTINCT especie_id)
        FROM fato_avaliacao_icmbio;
    """)


def contar_especies_icmbio_ameacadas():
    """
    Conta quantas espécies constam como ameaçadas
    nas avaliações do ICMBio.
    """

    return executar_query("""
        SELECT COUNT(DISTINCT especie_id)
        FROM fato_avaliacao_icmbio
        WHERE consta_lista_ameacada = TRUE;
    """)


def contar_dados_sensiveis_icmbio():
    """
    Conta quantos registros do ICMBio estão marcados
    como dados sensíveis.
    """

    return executar_query("""
        SELECT COUNT(*)
        FROM fato_avaliacao_icmbio
        WHERE dado_sensivel = TRUE;
    """)


def obter_especies_por_estado():
    """
    Retorna a quantidade de espécies distintas registradas
    por estado brasileiro, normalizando variações nos nomes.
    """

    conexao = get_connection()

    try:

        query = """
            WITH estados_normalizados AS (

                SELECT
                    fo.especie_id,

                    CASE

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('acre', 'ac')
                            THEN 'Acre'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('alagoas', 'al')
                            THEN 'Alagoas'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('amapá', 'amapa', 'ap')
                            THEN 'Amapá'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('amazonas', 'am')
                            THEN 'Amazonas'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('bahia', 'ba')
                            THEN 'Bahia'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('ceará', 'ceara', 'ce')
                            THEN 'Ceará'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('distrito federal', 'federal dist.', 'df')
                            THEN 'Distrito Federal'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('espírito santo', 'espirito santo', 'es')
                            THEN 'Espírito Santo'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('goiás', 'goias', 'go')
                            THEN 'Goiás'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('maranhão', 'maranhao', 'ma')
                            THEN 'Maranhão'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('mato grosso', 'mt')
                            THEN 'Mato Grosso'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('mato grosso do sul', 'ms')
                            THEN 'Mato Grosso do Sul'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('minas gerais', 'mg')
                            THEN 'Minas Gerais'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('pará', 'para', 'pa')
                            THEN 'Pará'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('paraíba', 'paraiba', 'pb')
                            THEN 'Paraíba'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('paraná', 'parana', 'pr')
                            THEN 'Paraná'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('pernambuco', 'pe')
                            THEN 'Pernambuco'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('piauí', 'piaui', 'pi')
                            THEN 'Piauí'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('rio de janeiro',
                             'rio de janeiro state',
                             'río de janeiro',
                             'rj')
                            THEN 'Rio de Janeiro'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('rio grande do norte', 'rn')
                            THEN 'Rio Grande do Norte'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('rio grande do sul',
                             'río grande do sul',
                             'rs')
                            THEN 'Rio Grande do Sul'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('rondônia', 'rondonia', 'ro')
                            THEN 'Rondônia'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('roraima', 'rr')
                            THEN 'Roraima'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('santa catarina', 'sc')
                            THEN 'Santa Catarina'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('são paulo',
                             'sao paulo',
                             'sp',
                             'estado de sao paulo',
                             'são paulo state')
                            THEN 'São Paulo'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('sergipe', 'se')
                            THEN 'Sergipe'

                        WHEN LOWER(TRIM(dl.estado_provincia)) IN
                            ('tocantins', 'to')
                            THEN 'Tocantins'

                        ELSE NULL

                    END AS estado

                FROM fato_ocorrencia_gbif fo

                JOIN dim_local dl
                    ON fo.local_id = dl.id

                WHERE LOWER(TRIM(dl.pais)) = 'brazil'
            )

            SELECT
                estado,
                COUNT(DISTINCT especie_id) AS quantidade_especies

            FROM estados_normalizados

            WHERE estado IS NOT NULL

            GROUP BY estado

            ORDER BY quantidade_especies DESC;
        """

        return pd.read_sql_query(
            query,
            conexao
        )

    finally:
        conexao.close()


# ============================================================
# PÁGINA 4 — DISTRIBUIÇÃO
# ============================================================

def contar_ocorrencias_por_estado():
    """
    Retorna a quantidade de ocorrências do GBIF
    por estado brasileiro.
    """

    conexao = get_connection()

    try:

        query = """
            SELECT
                dl.estado_provincia AS estado,
                COUNT(*) AS quantidade_ocorrencias

            FROM fato_ocorrencia_gbif fo

            JOIN dim_local dl
                ON fo.local_id = dl.id

            WHERE LOWER(TRIM(dl.pais)) = 'brazil'
              AND dl.estado_provincia IS NOT NULL

            GROUP BY
                dl.estado_provincia

            ORDER BY
                quantidade_ocorrencias DESC;
        """

        return pd.read_sql_query(
            query,
            conexao
        )

    finally:
        conexao.close()


def obter_especies_por_estado_distribuicao():
    """
    Retorna a quantidade de espécies distintas registradas
    por estado brasileiro.

    Esta consulta utiliza os dados de ocorrência do GBIF.
    """

    conexao = get_connection()

    try:

        query = """
            SELECT
                dl.estado_provincia AS estado,
                COUNT(DISTINCT fo.especie_id)
                    AS quantidade_especies

            FROM fato_ocorrencia_gbif fo

            JOIN dim_local dl
                ON fo.local_id = dl.id

            WHERE LOWER(TRIM(dl.pais)) = 'brazil'
              AND dl.estado_provincia IS NOT NULL

            GROUP BY
                dl.estado_provincia

            ORDER BY
                quantidade_especies DESC;
        """

        return pd.read_sql_query(
            query,
            conexao
        )

    finally:
        conexao.close()


def obter_ocorrencias_mapa_brasil():
    """
    Retorna latitude e longitude das ocorrências do GBIF
    localizadas no Brasil.

    Utilizada para visualizações geográficas.
    """

    conexao = get_connection()

    try:

        query = """
            SELECT
                fo.especie_id,
                fo.latitude,
                fo.longitude,
                fo.categoria_iucn,
                de.nome_cientifico,
                de.nome_popular,
                de.grupo_taxonomico,
                dl.estado_provincia

            FROM fato_ocorrencia_gbif fo

            JOIN dim_local dl
                ON fo.local_id = dl.id

            JOIN dim_especie de
                ON fo.especie_id = de.id

            WHERE LOWER(TRIM(dl.pais)) = 'brazil'
              AND fo.latitude IS NOT NULL
              AND fo.longitude IS NOT NULL;
        """

        return pd.read_sql_query(
            query,
            conexao
        )

    finally:
        conexao.close()


def obter_especies_para_filtro():
    """
    Retorna as espécies disponíveis para utilização
    no filtro da página de distribuição.
    """

    conexao = get_connection()

    try:

        query = """
            SELECT DISTINCT
                de.id AS especie_id,
                de.nome_cientifico,
                de.nome_popular,
                de.grupo_taxonomico

            FROM dim_especie de

            JOIN fato_ocorrencia_gbif fo
                ON fo.especie_id = de.id

            JOIN dim_local dl
                ON fo.local_id = dl.id

            WHERE LOWER(TRIM(dl.pais)) = 'brazil'

            ORDER BY
                de.nome_cientifico;
        """

        return pd.read_sql_query(
            query,
            conexao
        )

    finally:
        conexao.close()


def obter_grupos_taxonomicos():
    """
    Retorna os grupos taxonômicos disponíveis
    entre as ocorrências registradas no Brasil.
    """

    conexao = get_connection()

    try:

        query = """
            SELECT DISTINCT
                de.grupo_taxonomico

            FROM dim_especie de

            JOIN fato_ocorrencia_gbif fo
                ON fo.especie_id = de.id

            JOIN dim_local dl
                ON fo.local_id = dl.id

            WHERE LOWER(TRIM(dl.pais)) = 'brazil'
              AND de.grupo_taxonomico IS NOT NULL

            ORDER BY
                de.grupo_taxonomico;
        """

        return pd.read_sql_query(
            query,
            conexao
        )

    finally:
        conexao.close()


# ============================================================
# TESTE DAS QUERIES
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("TESTE DAS QUERIES — BIODATA")
    print("=" * 60)

    print(
        "Espécies:",
        contar_especies()
    )

    print(
        "Avaliações IUCN:",
        contar_avaliacoes_iucn()
    )

    print(
        "Ocorrências GBIF:",
        contar_ocorrencias_gbif()
    )

    print(
        "PANs:",
        contar_pans()
    )

    print(
        "Espécies em destaque:",
        contar_especies_destaque()
    )

    print(
        "Espécies com avaliação atual:",
        contar_especies_avaliacao_atual()
    )

    print(
        "Espécies possivelmente extintas:",
        contar_especies_possivelmente_extintas()
    )

    print("\nAvaliações por categoria:")

    print(
        obter_avaliacoes_por_categoria()
    )

    print("\nEspécies por categoria:")

    print(
        obter_especies_por_categoria()
    )

    print("\nAvaliações atuais por categoria:")

    print(
        obter_avaliacoes_atuais_por_categoria()
    )

    print("\nEspécies ICMBio avaliadas:")

    print(
        contar_especies_icmbio_avaliadas()
    )

    print("\nEspécies ICMBio ameaçadas:")

    print(
        contar_especies_icmbio_ameacadas()
    )

    print("\nDados sensíveis ICMBio:")

    print(
        contar_dados_sensiveis_icmbio()
    )

    print("\nEspécies por estado — Página 3:")

    print(
        obter_especies_por_estado()
    )

    print("\nOcorrências por estado — Página 4:")

    print(
        contar_ocorrencias_por_estado()
    )

    print("\nEspécies por estado — Página 4:")

    print(
        obter_especies_por_estado_distribuicao()
    )

    print("\nOcorrências para mapa — Página 4:")

    print(
        obter_ocorrencias_mapa_brasil().head()
    )

    print("\nEspécies para filtro — Página 4:")

    print(
        obter_especies_para_filtro().head()
    )

    print("\nGrupos taxonômicos — Página 4:")

    print(
        obter_grupos_taxonomicos()
    )