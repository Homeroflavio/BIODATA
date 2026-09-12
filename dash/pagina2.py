from dash import html, dcc, Input, Output, callback, ctx
import plotly.graph_objects as go

from queries import (
    contar_especies_avaliacao_atual,
    contar_especies_possivelmente_extintas,
    obter_especies_por_categoria,
)


# ============================================================
# COMPONENTES
# ============================================================

def criar_card(numero, titulo, descricao):
    return html.Div(
        className="stat-card",
        children=[
            html.Div(
                numero,
                className="stat-number"
            ),

            html.Div(
                titulo,
                className="stat-title"
            ),

            html.Div(
                descricao,
                className="stat-description"
            ),
        ]
    )


# ============================================================
# DADOS
# ============================================================

avaliacao_atual = contar_especies_avaliacao_atual()
possivelmente_extintas = contar_especies_possivelmente_extintas()

df_categorias = obter_especies_por_categoria()


# ============================================================
# TRADUÇÃO DAS CATEGORIAS
# ============================================================

traducoes = {
    "EX": "Extinta",
    "EW": "Extinta na natureza",
    "CR": "Criticamente em perigo",
    "EN": "Em perigo",
    "VU": "Vulnerável",
    "NT": "Quase ameaçada",
    "LC": "Pouco preocupante",
    "DD": "Dados insuficientes",
    "NE": "Não avaliada",
}


df_categorias["categoria_pt"] = df_categorias["codigo"].map(
    traducoes
).fillna(df_categorias["nome"])


# ============================================================
# PALETA DAS CATEGORIAS
# ============================================================

CORES_CATEGORIAS = {
    "EX": "#292D32",
    "EW": "#626D75",
    "CR": "#8F1D2C",
    "EN": "#C13E32",
    "VU": "#D07A24",
    "NT": "#C2A02D",
    "LC": "#2D7B59",
    "DD": "#75828A",
    "NE": "#A8AFB5",
}


# ============================================================
# DESCRIÇÕES DAS CATEGORIAS
# ============================================================

descricoes_categorias = {
    "EX": "A espécie é considerada extinta.",

    "EW": (
        "A espécie não existe mais em estado selvagem."
    ),

    "CR": (
        "Categoria associada a um risco extremamente elevado."
    ),

    "EN": (
        "Categoria associada a um risco elevado de extinção."
    ),

    "VU": (
        "Categoria que indica vulnerabilidade ao risco."
    ),

    "NT": (
        "A espécie ainda não está em uma categoria ameaçada, "
        "mas pode se aproximar dela."
    ),

    "LC": (
        "Categoria de menor preocupação entre as apresentadas."
    ),

    "DD": (
        "Não existem informações suficientes para determinar "
        "adequadamente a categoria."
    ),

    "NE": (
        "A espécie ainda não possui uma avaliação."
    ),
}


# ============================================================
# DADOS DOS GRÁFICOS
# ============================================================

df_grafico = df_categorias[
    df_categorias["quantidade_especies"] > 0
].copy()


total_categorias = df_grafico[
    "quantidade_especies"
].sum()


df_grafico["percentual"] = (
    df_grafico["quantidade_especies"]
    / total_categorias
    * 100
)


# ============================================================
# FUNÇÃO — GRÁFICO DE BARRAS
# ============================================================

def criar_figura_categorias(categoria_selecionada=None):

    customdata = []

    cores = []

    larguras = []

    linhas = []

    cores_linhas = []


    for _, row in df_grafico.iterrows():

        codigo = row["codigo"]

        customdata.append([
            codigo,
            row["percentual"],
            descricoes_categorias.get(
                codigo,
                ""
            )
        ])


        cores.append(
            CORES_CATEGORIAS.get(
                codigo,
                "#12372a"
            )
        )


        # ====================================================
        # CATEGORIA DESTACADA
        # ====================================================

        if codigo == categoria_selecionada:

            larguras.append(0.82)

            linhas.append(3)

            cores_linhas.append(
                "#12372a"
            )

        else:

            larguras.append(0.66)

            linhas.append(1)

            cores_linhas.append(
                CORES_CATEGORIAS.get(
                    codigo,
                    "#12372a"
                )
            )


    # ========================================================
    # FIGURA
    # ========================================================

    fig = go.Figure()


    fig.add_trace(
        go.Bar(

            x=df_grafico["categoria_pt"],

            y=df_grafico["quantidade_especies"],

            text=df_grafico["quantidade_especies"],

            textposition="outside",

            customdata=customdata,

            width=larguras,

            marker=dict(

                color=cores,

                line=dict(

                    color=cores_linhas,

                    width=linhas
                )
            ),

            hovertemplate=(

                "<b>%{x}</b>"

                "<br><br>"

                "<b>%{y} espécies</b>"

                "<br>"

                "%{customdata[1]:.1f}% das espécies avaliadas"

                "<br><br>"

                "%{customdata[2]}"

                "<br><br>"

                "<span style='font-size:11px'>"

                "<b>Sigla:</b> %{customdata[0]}"

                "</span>"

                "<extra></extra>"
            ),
        )
    )


    # ========================================================
    # CONFIGURAÇÃO VISUAL
    # ========================================================

    fig.update_layout(

        title=dict(

            text=(
                "Quantas espécies estão associadas a cada "
                "categoria de conservação?"
            ),

            x=0.02,

            xanchor="left",

            font=dict(
                size=17,
                color="#12372a"
            )
        ),

        xaxis_title="Categoria de conservação",

        yaxis_title="Quantidade de espécies",

        template="plotly_white",

        height=520,

        bargap=0.22,

        hoverlabel=dict(

            bgcolor="#12372a",

            bordercolor="#12372a",

            font=dict(
                color="white",
                size=13
            ),

            align="left"
        ),

        transition=dict(

            duration=450,

            easing="cubic-in-out"
        ),

        plot_bgcolor="white",

        paper_bgcolor="white",

        margin=dict(

            l=60,

            r=35,

            t=85,

            b=110
        ),

        uirevision="categorias-pagina2",
    )


    fig.update_yaxes(

        gridcolor="#E5EBE7",

        zeroline=False,

        rangemode="tozero"
    )


    fig.update_xaxes(

        showgrid=False
    )


    return fig


# ============================================================
# FUNÇÃO — GRÁFICO DE ROSCA
# ============================================================

def criar_figura_distribuicao(
    categoria_selecionada=None
):

    customdata = []

    cores = []

    pulls = []


    for _, row in df_grafico.iterrows():

        codigo = row["codigo"]


        customdata.append([
            codigo,
            row["percentual"],
            descricoes_categorias.get(
                codigo,
                ""
            )
        ])


        cores.append(
            CORES_CATEGORIAS.get(
                codigo,
                "#12372a"
            )
        )


        # ====================================================
        # DESTAQUE DA FATIA
        # ====================================================

        if codigo == categoria_selecionada:

            pulls.append(0.075)

        else:

            pulls.append(0)


    # ========================================================
    # TEXTO CENTRAL
    # ========================================================

    if categoria_selecionada:

        linha = df_grafico[
            df_grafico["codigo"]
            == categoria_selecionada
        ]


        if not linha.empty:

            quantidade = int(
                linha.iloc[0]["quantidade_especies"]
            )


            nome = linha.iloc[0]["categoria_pt"]


            percentual = float(
                linha.iloc[0]["percentual"]
            )


            texto_centro = (

                f"<span style='font-size:13px'>"

                f"<b>{nome.upper()}</b>"

                "</span>"

                "<br><br>"

                f"<span style='font-size:30px'>"

                f"<b>{quantidade}</b>"

                "</span>"

                "<br>"

                f"<span style='font-size:13px'>"

                f"{percentual:.1f}% do total"

                "</span>"
            )

        else:

            texto_centro = (

                f"<span style='font-size:31px'>"

                f"<b>{avaliacao_atual}</b>"

                "</span>"

                "<br>"

                "<span style='font-size:13px'>"

                "espécies avaliadas"

                "</span>"
            )

    else:

        texto_centro = (

            f"<span style='font-size:31px'>"

            f"<b>{avaliacao_atual}</b>"

            "</span>"

            "<br>"

            "<span style='font-size:13px'>"

            "espécies avaliadas"

            "</span>"

            "<br><br>"

            "<span style='font-size:10px'>"

            "Passe o mouse para explorar"

            "</span>"
        )


    # ========================================================
    # FIGURA
    # ========================================================

    fig = go.Figure()


    fig.add_trace(
        go.Pie(

            labels=df_grafico["categoria_pt"],

            values=df_grafico[
                "quantidade_especies"
            ],

            hole=0.60,

            pull=pulls,

            customdata=customdata,

            marker=dict(

                colors=cores,

                line=dict(

                    color="white",

                    width=3
                )
            ),

            hovertemplate=(

                "<b>%{label}</b>"

                "<br><br>"

                "<b>%{value} espécies</b>"

                "<br>"

                "%{customdata[1]:.1f}% das espécies avaliadas"

                "<br><br>"

                "%{customdata[2]}"

                "<br><br>"

                "<span style='font-size:11px'>"

                "<b>Sigla:</b> %{customdata[0]}"

                "</span>"

                "<extra></extra>"
            ),

            textinfo="percent",

            textposition="inside",

            insidetextorientation="horizontal",

            sort=False,
        )
    )


    # ========================================================
    # LAYOUT
    # ========================================================

    fig.update_layout(

        title=dict(

            text=(
                "Como as espécies avaliadas se distribuem "
                "entre as categorias?"
            ),

            x=0.02,

            xanchor="left",

            font=dict(
                size=17,
                color="#12372a"
            )
        ),

        template="plotly_white",

        height=540,

        hoverlabel=dict(

            bgcolor="#12372a",

            bordercolor="#12372a",

            font=dict(

                color="white",

                size=13
            ),

            align="left"
        ),

        transition=dict(

            duration=450,

            easing="cubic-in-out"
        ),

        uirevision="distribuicao-pagina2",

        annotations=[

            dict(

                text=texto_centro,

                x=0.5,

                y=0.5,

                xref="paper",

                yref="paper",

                showarrow=False,

                align="center",

                font=dict(

                    color="#12372a"
                )
            )
        ],

        paper_bgcolor="white",

        plot_bgcolor="white",

        margin=dict(

            l=30,

            r=30,

            t=85,

            b=30
        ),
    )


    return fig


# ============================================================
# FIGURAS INICIAIS
# ============================================================

fig_categorias = criar_figura_categorias()

fig_distribuicao = criar_figura_distribuicao()


# ============================================================
# LAYOUT DA PÁGINA
# ============================================================

layout = html.Div(

    className="app-container",

    children=[

        # ====================================================
        # CABEÇALHO
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
                            "Cenário de conservação"
                        ),

                        html.P(

                            "O que os dados indicam sobre o estado "
                            "de conservação das espécies avaliadas?"
                        ),
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

                    className="nav-link active"
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
                    className="nav-link"
                ),
            ]
        ),


        # ====================================================
        # CONTEÚDO
        # ====================================================

        html.Main(

            className="main-content",

            children=[

                # =================================================
                # STORE DA CATEGORIA FIXADA
                # =================================================

                dcc.Store(

                    id="categoria-fixada-pagina2",

                    data=None
                ),


                # -------------------------------------------------
                # CONTEXTO
                # -------------------------------------------------

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
                                            "O que estamos medindo?"
                                        ),

                                        html.P(

                                            "Entendendo as avaliações de conservação",

                                            className="section-subtitle"
                                        ),
                                    ]
                                )
                            ]
                        ),


                        html.Div(

                            className="context-box",

                            children=[

                                html.P(

                                    [

                                        "A classificação de conservação "
                                        "organiza as espécies de acordo "
                                        "com seu nível de risco. Neste "
                                        "dashboard, utilizamos as categorias "
                                        "presentes nas avaliações da "
                                        "IUCN."
                                    ]
                                ),


                                html.P(

                                    [

                                        "Para evitar interpretações "
                                        "equivocadas, os gráficos mostram "
                                        "tanto as ",

                                        html.Strong(
                                            "siglas originais"
                                        ),

                                        " quanto suas respectivas "
                                        "descrições em português."
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),


                # -------------------------------------------------
                # INDICADORES
                # -------------------------------------------------

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
                                            "Qual é o cenário atual?"
                                        ),

                                        html.P(

                                            "Principais indicadores da base",

                                            className="section-subtitle"
                                        ),
                                    ]
                                )
                            ]
                        ),


                        html.Div(

                            className="stats-grid",

                            children=[

                                criar_card(

                                    f"{avaliacao_atual:,}".replace(
                                        ",",
                                        "."
                                    ),

                                    "Espécies com avaliação atual",

                                    (
                                        "Espécies que possuem uma "
                                        "avaliação IUCN marcada como atual"
                                    )
                                ),


                                criar_card(

                                    f"{possivelmente_extintas:,}".replace(
                                        ",",
                                        "."
                                    ),

                                    "Possivelmente extintas",

                                    (
                                        "Espécies com registro indicando "
                                        "possibilidade de extinção"
                                    )
                                ),
                            ]
                        ),
                    ]
                ),


                # -------------------------------------------------
                # GRÁFICO PRINCIPAL
                # -------------------------------------------------

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

                                            "Onde estão concentradas "
                                            "as espécies?"
                                        ),

                                        html.P(

                                            (
                                                "Distribuição das espécies "
                                                "por categoria de conservação"
                                            ),

                                            className="section-subtitle"
                                        ),
                                    ]
                                )
                            ]
                        ),


                        html.Div(

                            className="chart-container",

                            children=[

                                dcc.Graph(

                                    id="grafico-categorias-pagina2",

                                    clear_on_unhover=True,

                                    figure=fig_categorias,

                                    animate=True,

                                    className=(
                                        "biodata-bar-graph"
                                    ),

                                    config={

                                        "displayModeBar": False,

                                        "responsive": True,

                                        "scrollZoom": False
                                    }
                                ),
                            ]
                        ),
                    ]
                ),


                # -------------------------------------------------
                # DISTRIBUIÇÃO
                # -------------------------------------------------

                html.Section(

                    className="section",

                    children=[

                        html.Div(

                            className="chart-container",

                            children=[

                                dcc.Graph(

                                    id="grafico-distribuicao-pagina2",

                                    clear_on_unhover=True,

                                    figure=fig_distribuicao,

                                    animate=True,

                                    className=(
                                        "biodata-donut-graph"
                                    ),

                                    config={

                                        "displayModeBar": False,

                                        "responsive": True,

                                        "scrollZoom": False
                                    }
                                ),
                            ]
                        ),
                    ]
                ),


                # -------------------------------------------------
                # LEGENDA
                # -------------------------------------------------

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
                                            "O que significam as siglas?"
                                        ),

                                        html.P(

                                            "Legenda das categorias "
                                            "de conservação",

                                            className="section-subtitle"
                                        ),
                                    ]
                                )
                            ]
                        ),


                        html.Div(

                            className="concepts-grid",

                            children=[

                                html.Div(

                                    className="concept-card",

                                    children=[

                                        html.H3(
                                            "EX — Extinta"
                                        ),

                                        html.P(

                                            "A espécie é considerada extinta."
                                        ),
                                    ]
                                ),


                                html.Div(

                                    className="concept-card",

                                    children=[

                                        html.H3(
                                            "EW — Extinta na natureza"
                                        ),

                                        html.P(

                                            "A espécie não existe mais "
                                            "em estado selvagem."
                                        ),
                                    ]
                                ),


                                html.Div(

                                    className="concept-card",

                                    children=[

                                        html.H3(
                                            "CR — Criticamente em perigo"
                                        ),

                                        html.P(

                                            "Categoria associada a um "
                                            "risco extremamente elevado."
                                        ),
                                    ]
                                ),


                                html.Div(

                                    className="concept-card",

                                    children=[

                                        html.H3(
                                            "EN — Em perigo"
                                        ),

                                        html.P(

                                            "Categoria associada a um "
                                            "risco elevado de extinção."
                                        ),
                                    ]
                                ),


                                html.Div(

                                    className="concept-card",

                                    children=[

                                        html.H3(
                                            "VU — Vulnerável"
                                        ),

                                        html.P(

                                            "Categoria que indica "
                                            "vulnerabilidade ao risco."
                                        ),
                                    ]
                                ),


                                html.Div(

                                    className="concept-card",

                                    children=[

                                        html.H3(
                                            "NT — Quase ameaçada"
                                        ),

                                        html.P(

                                            "A espécie ainda não está "
                                            "em uma categoria ameaçada, "
                                            "mas pode se aproximar dela."
                                        ),
                                    ]
                                ),


                                html.Div(

                                    className="concept-card",

                                    children=[

                                        html.H3(
                                            "LC — Pouco preocupante"
                                        ),

                                        html.P(

                                            "Categoria de menor preocupação "
                                            "entre as apresentadas."
                                        ),
                                    ]
                                ),


                                html.Div(

                                    className="concept-card",

                                    children=[

                                        html.H3(
                                            "DD — Dados insuficientes"
                                        ),

                                        html.P(

                                            "Não existem informações "
                                            "suficientes para determinar "
                                            "adequadamente a categoria."
                                        ),
                                    ]
                                ),


                                html.Div(

                                    className="concept-card",

                                    children=[

                                        html.H3(
                                            "NE — Não avaliada"
                                        ),

                                        html.P(

                                            "A espécie ainda não possui "
                                            "uma avaliação."
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),


                # -------------------------------------------------
                # INSIGHT
                # -------------------------------------------------

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
                                            "O que os dados mostram?"
                                        ),

                                        html.P(

                                            "Principais observações",

                                            className="section-subtitle"
                                        ),
                                    ]
                                )
                            ]
                        ),


                        html.Div(

                            className="context-box",

                            children=[

                                html.P(

                                    [

                                        "A base possui ",

                                        html.Strong(

                                            f"{avaliacao_atual:,}".replace(
                                                ",",
                                                "."
                                            )
                                        ),

                                        " espécies com avaliação IUCN "
                                        "marcada como atual."
                                    ]
                                ),


                                html.P(

                                    [

                                        "Também existem ",

                                        html.Strong(

                                            f"{possivelmente_extintas:,}".replace(
                                                ",",
                                                "."
                                            )
                                        ),

                                        " espécies com registro indicando "
                                        "possibilidade de extinção."
                                    ]
                                ),


                                html.P(

                                    [

                                        "A distribuição entre as categorias "
                                        "permite observar onde está "
                                        "concentrada a maior quantidade de "
                                        "espécies e comparar diferentes "
                                        "níveis de risco."
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        ),


        # ====================================================
        # RODAPÉ
        # ====================================================

        html.Footer(

            className="footer",

            children=[

                html.P(
                    "BIODATA · Cenário de conservação"
                )
            ]
        ),
    ]
)


# ============================================================
# CALLBACK — FIXAR / DESFIXAR CATEGORIA
# ============================================================

@callback(

    Output(
        "categoria-fixada-pagina2",
        "data"
    ),

    Input(
        "grafico-categorias-pagina2",
        "clickData"
    ),

    Input(
        "grafico-distribuicao-pagina2",
        "clickData"
    ),

    prevent_initial_call=True
)
def controlar_categoria_fixa(
    click_categorias,
    click_distribuicao
):

    origem = ctx.triggered_id

    dados = None


    # ========================================================
    # QUAL GRÁFICO FOI CLICADO?
    # ========================================================

    if origem == "grafico-categorias-pagina2":

        dados = click_categorias

    elif origem == "grafico-distribuicao-pagina2":

        dados = click_distribuicao


    if not dados:

        return None


    # ========================================================
    # OBTÉM A CATEGORIA
    # ========================================================

    try:

        categoria = (
            dados["points"][0]
            ["customdata"][0]
        )

    except (
        KeyError,
        IndexError,
        TypeError
    ):

        return None


    return categoria


# ============================================================
# CALLBACK — HOVER + CATEGORIA FIXADA
# ============================================================

@callback(

    Output(
        "grafico-categorias-pagina2",
        "figure"
    ),

    Output(
        "grafico-distribuicao-pagina2",
        "figure"
    ),

    Input(
        "grafico-categorias-pagina2",
        "hoverData"
    ),

    Input(
        "grafico-distribuicao-pagina2",
        "hoverData"
    ),

    Input(
        "categoria-fixada-pagina2",
        "data"
    ),
)
def atualizar_graficos(

    hover_categorias,

    hover_distribuicao,

    categoria_fixa

):

    categoria_selecionada = categoria_fixa


    # ========================================================
    # HOVER TEM PRIORIDADE
    # ========================================================

    if hover_categorias:

        try:

            categoria_selecionada = (
                hover_categorias["points"][0]
                ["customdata"][0]
            )

        except (
            KeyError,
            IndexError,
            TypeError
        ):

            pass


    elif hover_distribuicao:

        try:

            categoria_selecionada = (
                hover_distribuicao["points"][0]
                ["customdata"][0]
            )

        except (
            KeyError,
            IndexError,
            TypeError
        ):

            pass


    # ========================================================
    # ATUALIZA OS DOIS GRÁFICOS
    # ========================================================

    return (

        criar_figura_categorias(
            categoria_selecionada
        ),

        criar_figura_distribuicao(
            categoria_selecionada
        )
    )