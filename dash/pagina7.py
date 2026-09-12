from dash import html, dcc, Input, Output
import pandas as pd
from pathlib import Path

from queries import (
    obter_especies_destaque,
    obter_detalhes_especie_destaque
)


# ============================================================
# DADOS
# ============================================================

df_especies = obter_especies_destaque()


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def formatar_numero(valor):
    """
    Formata números no padrão brasileiro.
    """

    if valor is None or pd.isna(valor):
        return "0"

    return f"{int(valor):,}".replace(",", ".")


def obter_nome_especie(dados):
    """
    Retorna o nome preferencial para apresentação.
    """

    nome_popular = dados.get("nome_popular")

    if (
        nome_popular
        and not pd.isna(nome_popular)
        and str(nome_popular).strip()
    ):
        return str(nome_popular).replace("Avejá", "Avejão")

    nome_cientifico = dados.get("nome_cientifico")

    if (
        nome_cientifico
        and not pd.isna(nome_cientifico)
        and str(nome_cientifico).strip()
    ):
        return str(nome_cientifico)

    return "Espécie"


def criar_imagem_especie(especie_id, numero_foto, nome):
    """
    Cria uma imagem utilizando os arquivos da pasta assets/especies.

    Estrutura:
        assets/especies/
            nome-da-especie/
                nome-da-especie1.jpg
                nome-da-especie2.jpg
                nome-da-especie3.jpg

    Aceita .jpg, .jpeg, .png, .webp e .jfif.
    """

    import unicodedata

    def normalizar_nome(texto):
        texto = str(texto).strip().lower()

        texto = unicodedata.normalize(
            "NFD",
            texto
        )

        texto = "".join(
            caractere
            for caractere in texto
            if unicodedata.category(caractere) != "Mn"
        )

        texto = texto.replace(" ", "-")

        return texto

    nome_normalizado = normalizar_nome(nome)

    # Ajuste específico do nome da pasta
    nome_normalizado = nome_normalizado.replace(
        "viajero",
        "viageiro"
    )

    pasta_base = (
        Path(__file__).resolve().parent
        / "assets"
        / "especies"
    )

    pasta_especie = None

    # Procura a pasta ignorando diferenças de acentos
    for pasta in pasta_base.iterdir():

        if not pasta.is_dir():
            continue

        nome_pasta_normalizado = normalizar_nome(
            pasta.name
        )

        nome_pasta_normalizado = (
            nome_pasta_normalizado
            .replace("viajero", "viageiro")
        )

        if nome_pasta_normalizado == nome_normalizado:
            pasta_especie = pasta
            break

    if pasta_especie is None:
        return html.Div(
            "Imagem não encontrada",
            className="especie-vazio"
        )

    # Procura a imagem independentemente da extensão
    extensoes = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".jfif"
    ]

    arquivo = None

    for extensao in extensoes:

        candidato = (
            pasta_especie
            / f"{pasta_especie.name}{numero_foto}{extensao}"
        )

        if candidato.exists():
            arquivo = candidato
            break

    if arquivo is None:
        return html.Div(
            "Imagem não encontrada",
            className="especie-vazio"
        )

    caminho = (
        f"/assets/especies/"
        f"{pasta_especie.name}/"
        f"{arquivo.name}"
    )

    return html.Img(
        src=caminho,
        alt=f"{nome} — fotografia {numero_foto}",
        className=(
            "especie-imagem-principal"
            if numero_foto == 1
            else "especie-imagem-secundaria"
        )
    )


def criar_card_informacao(titulo, valor):
    """
    Cria uma informação dentro do card da espécie.
    """

    return html.Div(
        className="especie-informacao",
        children=[

            html.Div(
                titulo,
                className="especie-informacao-titulo"
            ),

            html.Div(
                valor,
                className="especie-informacao-valor"
            )

        ]
    )


def criar_info_especie(dados):
    """
    Cria o card principal de informações da espécie.
    """

    if dados is None:
        return html.Div(
            "Selecione uma espécie para visualizar suas informações.",
            className="especie-vazio"
        )

    nome_popular = dados.get("nome_popular")
    nome_cientifico = dados.get("nome_cientifico")
    grupo = dados.get("grupo_taxonomico")
    categoria = dados.get("categoria_risco")

    if (
        not nome_popular
        or pd.isna(nome_popular)
    ):
        nome_popular = "Nome popular não informado"
    else:
        # CORREÇÃO: Avejá → Avejão
        nome_popular = str(nome_popular).replace(
            "Avejá",
            "Avejão"
        )

    if (
        not nome_cientifico
        or pd.isna(nome_cientifico)
    ):
        nome_cientifico = "Nome científico não informado"

    if (
        not grupo
        or pd.isna(grupo)
    ):
        grupo = "Não informado"

    if (
        not categoria
        or pd.isna(categoria)
    ):
        categoria = "Não avaliada"

    ultima = dados.get(
        "ultima_ocorrencia"
    )

    if (
        ultima is not None
        and not pd.isna(ultima)
    ):
        ultima = str(int(ultima))
    else:
        ultima = "Não informado"

    return html.Div(
        className="especie-card-informacoes",
        children=[

            html.Div(
                nome_popular,
                className="especie-nome-popular"
            ),

            html.Div(
                nome_cientifico,
                className="especie-nome-cientifico"
            ),

            html.Div(
                className="especie-informacoes",
                children=[

                    criar_card_informacao(
                        "Grupo taxonômico",
                        grupo
                    ),

                    criar_card_informacao(
                        "Categoria IUCN",
                        categoria
                    ),

                    criar_card_informacao(
                        "Ocorrências no GBIF",
                        formatar_numero(
                            dados.get(
                                "quantidade_ocorrencias"
                            )
                        )
                    ),

                    criar_card_informacao(
                        "Último registro",
                        ultima
                    )

                ]
            )

        ]
    )


# ============================================================
# INDICADORES
# ============================================================

def criar_indicadores(dados):
    """
    Cria os indicadores da espécie selecionada.
    """

    if dados is None:
        return []

    quantidade = dados.get(
        "quantidade_ocorrencias"
    )

    categoria = dados.get(
        "categoria_risco"
    )

    ultima = dados.get(
        "ultima_ocorrencia"
    )

    if (
        not categoria
        or pd.isna(categoria)
    ):
        categoria = "Não avaliada"

    if (
        ultima is not None
        and not pd.isna(ultima)
    ):
        ultima = str(int(ultima))
    else:
        ultima = "Não informado"

    return [

        html.Div(
            className="stat-card",
            children=[

                html.Div(
                    formatar_numero(
                        quantidade
                    ),
                    className="stat-number"
                ),

                html.Div(
                    "Ocorrências GBIF",
                    className="stat-title"
                ),

                html.Div(
                    "Registros disponíveis "
                    "para a espécie",
                    className="stat-description"
                )

            ]
        ),

        html.Div(
            className="stat-card",
            children=[

                html.Div(
                    categoria,
                    className="stat-number especie-categoria-indicador"
                ),

                html.Div(
                    "Categoria IUCN",
                    className="stat-title"
                ),

                html.Div(
                    "Classificação de risco "
                    "disponível na base",
                    className="stat-description"
                )

            ]
        ),

        html.Div(
            className="stat-card",
            children=[

                html.Div(
                    ultima,
                    className="stat-number"
                ),

                html.Div(
                    "Último registro",
                    className="stat-title"
                ),

                html.Div(
                    "Ano mais recente de "
                    "ocorrência disponível",
                    className="stat-description"
                )

            ]
        )

    ]


# ============================================================
# LAYOUT
# ============================================================

layout = html.Div(
    className="app-container pagina7",
    children=[

        # ====================================================
        # HERO
        # ====================================================

        html.Header(
            className="hero",
            children=[

                html.Div(
                    className="hero-content",
                    children=[

                        html.Div(
                            "BIODATA",
                            className="hero-label"
                        ),

                        html.H1(
                            "Conheça algumas espécies "
                            "da biodiversidade brasileira"
                        ),

                        html.P(
                            "Uma seleção de espécies para "
                            "descobrir suas características, "
                            "habitats e os desafios que "
                            "enfrentam para sobreviver."
                        )

                    ]
                )

            ]
        ),


        # ====================================================
        # NAVEGAÇÃO
        # ====================================================

        html.Nav(
            className="navigation",
            children=[

                dcc.Link(
                    "Sobre o projeto",
                    href="/",
                    className="nav-link"
                ),

                dcc.Link(
                    "Cenário de conservação",
                    href="/conservacao",
                    className="nav-link"
                ),

                dcc.Link(
                    "Brasil",
                    href="/brasil",
                    className="nav-link"
                ),

                dcc.Link(
                    "Distribuição",
                    href="/distribuicao",
                    className="nav-link"
                ),

                dcc.Link(
                    "Evolução",
                    href="/evolucao",
                    className="nav-link"
                ),

                dcc.Link(
                    "PANs",
                    href="/pans",
                    className="nav-link"
                ),

                dcc.Link(
                    "Espécies em destaque",
                    href="/destaques",
                    className="nav-link active"
                )

            ]
        ),


        # ====================================================
        # CONTEÚDO
        # ====================================================

        html.Main(
            className="main-content",
            children=[

                # =================================================
                # 01 — ESCOLHA
                # =================================================

                html.Section(
                    className="section",
                    children=[

                        html.Div(
                            className="section-heading",
                            children=[

                                html.Div(
                                    "01",
                                    className="section-number"
                                ),

                                html.Div(
                                    children=[

                                        html.H2(
                                            "Escolha uma espécie"
                                        ),

                                        html.P(
                                            "Explore individualmente "
                                            "as espécies selecionadas",
                                            className="section-subtitle"
                                        )

                                    ]
                                )

                            ]
                        ),

                        html.Div(
                            className="filtro-container",
                            children=[

                                html.Label(
                                    "Espécie",
                                    className="label-filtro"
                                ),

                                dcc.Dropdown(
                                    id="dropdown-especie-destaque",

                                    options=[
                                        {
                                            "label": (
                                                str(row["nome_popular"]).replace(
                                                    "Avejá",
                                                    "Avejão"
                                                )
                                                if (
                                                    pd.notna(row["nome_popular"])
                                                    and str(row["nome_popular"]).strip()
                                                )
                                                else row["nome_cientifico"]
                                            ),

                                            "value": row["especie_id"]
                                        }

                                        for _, row
                                        in df_especies.iterrows()
                                    ],

                                    placeholder=(
                                        "Selecione uma espécie..."
                                    ),

                                    clearable=False
                                )

                            ]
                        )

                    ]
                ),


                # =================================================
                # 02 — ESPÉCIE SELECIONADA
                # =================================================

                html.Section(
                    className="section",
                    children=[

                        html.Div(
                            className="section-heading",
                            children=[

                                html.Div(
                                    "02",
                                    className="section-number"
                                ),

                                html.Div(
                                    children=[

                                        html.H2(
                                            "A espécie selecionada"
                                        ),

                                        html.P(
                                            "Conheça a espécie "
                                            "a partir dos dados disponíveis",
                                            className="section-subtitle"
                                        )

                                    ]
                                )

                            ]
                        ),

                        html.Div(
                            className="especie-apresentacao",
                            children=[

                                html.Div(
                                    id="especie-foto-principal",
                                    className="especie-foto-principal"
                                ),

                                html.Div(
                                    id="especie-informacoes-principais",
                                    className="especie-informacoes-principais"
                                )

                            ]
                        )

                    ]
                ),


                # =================================================
                # 03 — CONHECENDO A ESPÉCIE
                # =================================================

                html.Section(
                    className="section",
                    children=[

                        html.Div(
                            className="section-heading",
                            children=[

                                html.Div(
                                    "03",
                                    className="section-number"
                                ),

                                html.Div(
                                    children=[

                                        html.H2(
                                            "Conhecendo a espécie"
                                        ),

                                        html.P(
                                            "Contexto sobre a espécie "
                                            "selecionada",
                                            className="section-subtitle"
                                        )

                                    ]
                                )

                            ]
                        ),

                        html.Div(
                            id="especie-contexto",
                            className="context-box"
                        )

                    ]
                ),


                # =================================================
                # 04 — DADOS
                # =================================================

                html.Section(
                    className="section",
                    children=[

                        html.Div(
                            className="section-heading",
                            children=[

                                html.Div(
                                    "04",
                                    className="section-number"
                                ),

                                html.Div(
                                    children=[

                                        html.H2(
                                            "O que os dados mostram?"
                                        ),

                                        html.P(
                                            "Indicadores encontrados "
                                            "na base do Biodata",
                                            className="section-subtitle"
                                        )

                                    ]
                                )

                            ]
                        ),

                        html.Div(
                            id="especie-indicadores",
                            className="stats-grid"
                        ),

                        html.Div(
                            id="especie-leitura-dados",
                            className="context-box"
                        )

                    ]
                ),


                # =================================================
                # 05 — FOTOS
                # =================================================

                html.Section(
                    className="section",
                    children=[

                        html.Div(
                            className="section-heading",
                            children=[

                                html.Div(
                                    "05",
                                    className="section-number"
                                ),

                                html.Div(
                                    children=[

                                        html.H2(
                                            "Veja a espécie"
                                        ),

                                        html.P(
                                            "Imagens complementares "
                                            "da espécie selecionada",
                                            className="section-subtitle"
                                        )

                                    ]
                                )

                            ]
                        ),

                        html.Div(
                            className="especie-galeria",
                            children=[

                                html.Div(
                                    id="especie-foto-2",
                                    className="especie-foto-secundaria"
                                ),

                                html.Div(
                                    id="especie-foto-3",
                                    className="especie-foto-secundaria"
                                )

                            ]
                        )

                    ]
                ),


                # =================================================
                # 06 — CONCLUSÃO
                # =================================================

                html.Section(
                    className="section",
                    children=[

                        html.Div(
                            className="section-heading",
                            children=[

                                html.Div(
                                    "06",
                                    className="section-number"
                                ),

                                html.Div(
                                    children=[

                                        html.H2(
                                            "Conhecer também é uma "
                                            "forma de conservar"
                                        ),

                                        html.P(
                                            "Conclusão do Biodata",
                                            className="section-subtitle"
                                        )

                                    ]
                                )

                            ]
                        ),

                        html.Div(
                            className="context-box",
                            children=[

                                html.P(
                                    [
                                        
                                    ]
                                ),

                                html.P(
                                    [
                                        "Ao longo do Biodata, diferentes fontes de dados foram integradas para construir uma visão mais ampla sobre a biodiversidade."
                                        
                                        "Os dados de conservação, ocorrência, distribuição e ações de proteção permitem observar diferentes dimensões do desafio de compreender e preservar as espécies."
                                        
                                        "Mais do que apresentar números, o projeto busca transformar dados dispersos em informações que possam ser exploradas, comparadas e compreendidas."
                                        
                                        "Por trás de cada espécie e de cada registro, existe uma vida que pode estar desaparecendo sem que muitas pessoas sequer saibam. Conhecer essas espécies, entender os riscos que enfrentam e reconhecer a importância de sua conservação é também um passo para que elas não sejam esquecidas."
                                        
                                        "Porque, antes de conservar, é preciso conhecer."
                                    ]
                                ),

                                html.P(
                                    [
                                        "Mais do que apresentar números, "
                                        "o projeto busca transformar dados "
                                        "dispersos em informações que "
                                        "possam ser exploradas, "
                                        "comparadas e compreendidas."
                                    ]
                                ),

                                html.P(
                                    [
                                        "Conhecer essas espécies e os "
                                        "dados que ajudam a descrevê-las "
                                        "é também compreender melhor a "
                                        "biodiversidade do nosso planeta."
                                    ]
                                )

                            ]
                        )

                    ]
                )

            ]
        ),


        # ====================================================
        # RODAPÉ
        # ====================================================

        html.Footer(
            className="footer",
            children=[

                html.P(
                    "BIODATA · Projeto de integração e análise de "
                    "dados sobre biodiversidade"
                )

            ]
        )

    ]
)


# ============================================================
# CALLBACK PRINCIPAL
# ============================================================

def atualizar_especie(especie_id):
    """
    Atualiza todas as informações da espécie selecionada.
    """

    if especie_id is None:

        mensagem = (
            "Selecione uma espécie acima para começar "
            "a exploração."
        )

        return (

            html.Div(
                mensagem,
                className="especie-vazio"
            ),

            html.Div(
                "Selecione uma espécie para visualizar "
                "as informações.",
                className="especie-vazio"
            ),

            html.Div(
                "Selecione uma espécie para visualizar "
                "os dados.",
                className="especie-vazio"
            ),

            [],

            html.Div(
                "Selecione uma espécie para visualizar "
                "as informações.",
                className="especie-vazio"
            ),

            html.Div(
                "Selecione uma espécie para visualizar "
                "as informações.",
                className="especie-vazio"
            ),

            html.Div(
                "Selecione uma espécie para visualizar "
                "as informações.",
                className="especie-vazio"
            )

        )

    dados = obter_detalhes_especie_destaque(
        especie_id
    )

    if dados is None:

        mensagem = (
            "Não foi possível encontrar os dados "
            "da espécie selecionada."
        )

        return (

            html.Div(
                mensagem,
                className="especie-vazio"
            ),

            html.Div(
                mensagem,
                className="especie-vazio"
            ),

            html.Div(
                mensagem,
                className="especie-vazio"
            ),

            [],

            html.Div(
                mensagem,
                className="especie-vazio"
            ),

            html.Div(
                mensagem,
                className="especie-vazio"
            ),

            html.Div(
                mensagem,
                className="especie-vazio"
            )

        )

    nome = obter_nome_especie(
        dados
    )

    # --------------------------------------------------------
    # FOTO PRINCIPAL
    # --------------------------------------------------------

    foto_principal = criar_imagem_especie(
        especie_id,
        1,
        nome
    )

    # --------------------------------------------------------
    # FOTOS SECUNDÁRIAS
    # --------------------------------------------------------

    foto_2 = criar_imagem_especie(
        especie_id,
        2,
        nome
    )

    foto_3 = criar_imagem_especie(
        especie_id,
        3,
        nome
    )

    # --------------------------------------------------------
    # INFORMAÇÕES
    # --------------------------------------------------------

    informacoes = criar_info_especie(
        dados
    )

    # --------------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------------

    nome_cientifico = dados.get(
        "nome_cientifico"
    )

    grupo = dados.get(
        "grupo_taxonomico"
    )

    categoria = dados.get(
        "categoria_risco"
    )

    if (
        not nome_cientifico
        or pd.isna(nome_cientifico)
    ):
        nome_cientifico = "Não informado"

    if (
        not grupo
        or pd.isna(grupo)
    ):
        grupo = "Não informado"

    if (
        not categoria
        or pd.isna(categoria)
    ):
        categoria = "Não avaliada"

    contexto = [

        html.P(
            [
                html.Strong(nome),
                " é apresentada nesta página "
                "a partir das informações disponíveis "
                "na base do Biodata."
            ]
        ),

        html.P(
            [
                "A espécie pertence ao grupo taxonômico ",
                html.Strong(str(grupo)),
                " e possui classificação IUCN ",
                html.Strong(str(categoria)),
                "."
            ]
        ),

        html.P(
            [
                "O nome científico registrado na base é ",
                html.Strong(str(nome_cientifico)),
                "."
            ]
        ),

        html.P(
            "Informações complementares sobre habitat, "
            "características e fatores de ameaça serão "
            "apresentadas somente quando houver fonte "
            "adequada para sustentá-las."
        )

    ]

    # --------------------------------------------------------
    # INDICADORES
    # --------------------------------------------------------

    indicadores = criar_indicadores(
        dados
    )

    # --------------------------------------------------------
    # LEITURA DOS DADOS
    # --------------------------------------------------------

    quantidade = formatar_numero(
        dados.get(
            "quantidade_ocorrencias"
        )
    )

    ultima = dados.get(
        "ultima_ocorrencia"
    )

    if (
        ultima is not None
        and not pd.isna(ultima)
    ):
        ultima = str(int(ultima))
    else:
        ultima = "Não informado"

    leitura_dados = [

        html.P(
            [
                "A base do Biodata possui ",
                html.Strong(
                    f"{quantidade} registros"
                ),
                " de ocorrência dessa espécie "
                "no GBIF."
            ]
        ),

        html.P(
            [
                "O registro mais recente encontrado "
                "corresponde ao ano de ",
                html.Strong(str(ultima)),
                "."
            ]
        ),

        html.P(
            "A quantidade de ocorrências representa "
            "os registros disponíveis na base e não "
            "deve ser interpretada isoladamente como "
            "uma medida direta do tamanho ou da "
            "abundância da população."
        )

    ]

    return (

        foto_principal,

        informacoes,

        contexto,

        indicadores,

        leitura_dados,

        foto_2,

        foto_3

    )


# ============================================================
# CALLBACK
# ============================================================

from dash import callback

callback(

    Output(
        "especie-foto-principal",
        "children"
    ),

    Output(
        "especie-informacoes-principais",
        "children"
    ),

    Output(
        "especie-contexto",
        "children"
    ),

    Output(
        "especie-indicadores",
        "children"
    ),

    Output(
        "especie-leitura-dados",
        "children"
    ),

    Output(
        "especie-foto-2",
        "children"
    ),

    Output(
        "especie-foto-3",
        "children"
    ),

    Input(
        "dropdown-especie-destaque",
        "value"
    )

)(atualizar_especie)