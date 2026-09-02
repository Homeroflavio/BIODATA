import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd

from queries import (
    contar_ocorrencias_por_estado,
    obter_especies_por_estado_distribuicao,
    obter_ocorrencias_mapa_brasil,
    obter_especies_para_filtro,
    obter_grupos_taxonomicos
)


# ============================================================
# DADOS INICIAIS
# ============================================================

df_ocorrencias = obter_ocorrencias_mapa_brasil()
df_estados_ocorrencias = contar_ocorrencias_por_estado()
df_estados_especies = obter_especies_por_estado_distribuicao()
df_especies = obter_especies_para_filtro()
df_grupos = obter_grupos_taxonomicos()


# ============================================================
# TRADUÇÃO DAS CATEGORIAS IUCN
# ============================================================

TRADUCAO_IUCN = {
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
# CORES DAS CATEGORIAS
# ============================================================

CORES_IUCN = {
    "EX": "#000000",
    "EW": "#555555",
    "CR": "#8B0000",
    "EN": "#E53935",
    "VU": "#F39C12",
    "NT": "#F1C40F",
    "LC": "#27AE60",
    "DD": "#95A5A6",
    "NE": "#BDC3C7"
}


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

if not df_ocorrencias.empty:

    df_ocorrencias["categoria_nome"] = (
        df_ocorrencias["categoria_iucn"]
        .map(TRADUCAO_IUCN)
        .fillna(df_ocorrencias["categoria_iucn"])
    )


# ============================================================
# GRÁFICO — OCORRÊNCIAS POR ESTADO
# ============================================================

def criar_grafico_ocorrencias_estado(df):

    if df.empty:
        return px.bar(
            title="Nenhuma ocorrência encontrada"
        )

    df = df.sort_values(
        "quantidade_ocorrencias",
        ascending=True
    )

    fig = px.bar(
        df,
        x="quantidade_ocorrencias",
        y="estado",
        orientation="h",
        title="Ocorrências registradas por estado",
        labels={
            "quantidade_ocorrencias": "Ocorrências",
            "estado": "Estado"
        },
        hover_data={
            "quantidade_ocorrencias": True,
            "estado": False
        }
    )

    fig.update_traces(
        marker_color="#58756A",
        marker_line_color="#3E5A50",
        marker_line_width=0.8,
        hovertemplate="<b>%{y}</b><br>Ocorrências: %{x:,}<extra></extra>"
    )

    fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=20,
            r=30,
            t=60,
            b=20
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Arial",
            color="#24352D"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#E8EDEB",
            zeroline=False,
            title=None
        ),
        yaxis=dict(
            showgrid=False,
            title=None
        ),
        hoverlabel=dict(
            bgcolor="#24352D",
            font=dict(
                color="white",
                size=13
            ),
            bordercolor="#58756A"
        )
    )

    return fig


# ============================================================
# GRÁFICO — ESPÉCIES POR ESTADO
# ============================================================

def criar_grafico_especies_estado(df):

    if df.empty:
        return px.bar(
            title="Nenhuma espécie encontrada"
        )

    df = df.sort_values(
        "quantidade_especies",
        ascending=True
    )

    fig = px.bar(
        df,
        x="quantidade_especies",
        y="estado",
        orientation="h",
        title="Espécies registradas por estado",
        labels={
            "quantidade_especies": "Espécies",
            "estado": "Estado"
        },
        hover_data={
            "quantidade_especies": True,
            "estado": False
        }
    )

    fig.update_traces(
        marker_color="#58756A",
        marker_line_color="#3E5A50",
        marker_line_width=0.8,
        hovertemplate="<b>%{y}</b><br>Espécies: %{x:,}<extra></extra>"
    )

    fig.update_layout(
        template="plotly_white",
        margin=dict(
            l=20,
            r=30,
            t=60,
            b=20
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Arial",
            color="#24352D"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#E8EDEB",
            zeroline=False,
            title=None
        ),
        yaxis=dict(
            showgrid=False,
            title=None
        ),
        hoverlabel=dict(
            bgcolor="#24352D",
            font=dict(
                color="white",
                size=13
            ),
            bordercolor="#58756A"
        )
    )

    return fig


# ============================================================
# MAPA DO BRASIL
# ============================================================

def criar_mapa(df):

    if df.empty:

        fig = px.scatter_geo()

        fig.update_layout(
            title="Nenhuma ocorrência encontrada"
        )

        return fig

    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        color="categoria_iucn",
        hover_name="nome_cientifico",
        hover_data={
            "nome_popular": True,
            "grupo_taxonomico": True,
            "categoria_nome": True,
            "latitude": False,
            "longitude": False,
            "categoria_iucn": False
        },
        color_discrete_map=CORES_IUCN,
        scope="south america",
        projection="natural earth"
    )

    fig.update_geos(
        visible=True,
        showcountries=True,
        countrycolor="lightgray",
        showcoastlines=True,
        coastlinecolor="gray",
        showland=True,
        landcolor="white",
        fitbounds="locations"
    )

    fig.update_layout(
        title="Distribuição das ocorrências no Brasil",
        margin=dict(
            l=0,
            r=0,
            t=50,
            b=0
        ),
        legend_title_text="Categoria IUCN"
    )

    return fig


# ============================================================
# LAYOUT
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
                            "Distribuição das Espécies"
                        ),

                        html.P(
                            "Onde as espécies estão sendo registradas?"
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
                    className="nav-link active"
                ),

                html.Span(
                    "Evolução",
                    className="nav-link disabled"
                ),

                html.Span(
                    "PANs",
                    className="nav-link disabled"
                ),

                html.Span(
                    "Espécies em destaque",
                    className="nav-link disabled"
                ),
            ]
        ),


        # ====================================================
        # CONTEÚDO
        # ====================================================

        html.Main(
            className="main-content",
            children=[

                # ====================================================
                # FILTROS
                # ====================================================

                html.Div(
                    [

                        html.Div(
                            [

                                html.Label(
                                    "Espécie",
                                    className="label-filtro"
                                ),

                                dcc.Dropdown(
                                    id="filtro-especie-pagina4",
                                    options=[
                                        {
                                            "label": "Todas as espécies",
                                            "value": "todas"
                                        }
                                    ] + [
                                        {
                                            "label": (
                                                f"{row['nome_cientifico']}"
                                                + (
                                                    f" — {row['nome_popular']}"
                                                    if pd.notna(row["nome_popular"])
                                                    else ""
                                                )
                                            ),
                                            "value": row["especie_id"]
                                        }

                                        for _, row in df_especies.iterrows()
                                    ],
                                    value="todas",
                                    clearable=False
                                )

                            ],
                            className="filtro-container"
                        ),


                        html.Div(
                            [

                                html.Label(
                                    "Grupo taxonômico",
                                    className="label-filtro"
                                ),

                                dcc.Dropdown(
                                    id="filtro-grupo-pagina4",
                                    options=[
                                        {
                                            "label": "Todos os grupos",
                                            "value": "todos"
                                        }
                                    ] + [
                                        {
                                            "label": row["grupo_taxonomico"],
                                            "value": row["grupo_taxonomico"]
                                        }

                                        for _, row in df_grupos.iterrows()
                                    ],
                                    value="todos",
                                    clearable=False
                                )

                            ],
                            className="filtro-container"
                        )

                    ],
                    className="filtros-pagina4"
                ),


                # ====================================================
                # CARDS
                # ====================================================

                html.Div(
                    [

                        html.Div(
                            [

                                html.H3(
                                    "Ocorrências"
                                ),

                                html.H2(
                                    id="card-ocorrencias-pagina4"
                                )

                            ],
                            className="card"
                        ),


                        html.Div(
                            [

                                html.H3(
                                    "Espécies"
                                ),

                                html.H2(
                                    id="card-especies-pagina4"
                                )

                            ],
                            className="card"
                        ),


                        html.Div(
                            [

                                html.H3(
                                    "Estados"
                                ),

                                html.H2(
                                    id="card-estados-pagina4"
                                )

                            ],
                            className="card"
                        )

                    ],
                    className="cards-pagina4"
                ),


                # ====================================================
                # MAPA
                # ====================================================

                html.Div(
                    [

                        dcc.Graph(
                            id="mapa-brasil-pagina4",
                            figure=criar_mapa(df_ocorrencias),
                            config={
                                "displayModeBar": True,
                                "scrollZoom": True
                            }
                        )

                    ],
                    className="grafico-container"
                ),


                # ====================================================
                # GRÁFICOS INFERIORES
                # ====================================================

                html.Div(
                    [

                        html.Div(
                            [

                                dcc.Graph(
                                    id="grafico-ocorrencias-estado-pagina4",
                                    figure=criar_grafico_ocorrencias_estado(
                                        df_estados_ocorrencias
                                    )
                                )

                            ],
                            className="grafico-container metade"
                        ),


                        html.Div(
                            [

                                dcc.Graph(
                                    id="grafico-especies-estado-pagina4",
                                    figure=criar_grafico_especies_estado(
                                        df_estados_especies
                                    )
                                )

                            ],
                            className="grafico-container metade"
                        )

                    ],
                    className="linha-graficos-pagina4"
                )

            ]
        )
    ]
)


# ============================================================
# CALLBACKS
# ============================================================

@dash.callback(
    Output(
        "mapa-brasil-pagina4",
        "figure"
    ),

    Output(
        "grafico-ocorrencias-estado-pagina4",
        "figure"
    ),

    Output(
        "grafico-especies-estado-pagina4",
        "figure"
    ),

    Output(
        "card-ocorrencias-pagina4",
        "children"
    ),

    Output(
        "card-especies-pagina4",
        "children"
    ),

    Output(
        "card-estados-pagina4",
        "children"
    ),

    Input(
        "filtro-especie-pagina4",
        "value"
    ),

    Input(
        "filtro-grupo-pagina4",
        "value"
    )
)
def atualizar_pagina4(
    especie_id,
    grupo_taxonomico
):

    # ========================================================
    # FILTRO DAS OCORRÊNCIAS
    # ========================================================

    df_filtrado = df_ocorrencias.copy()

    if especie_id != "todas":

        df_filtrado = df_filtrado[
            df_filtrado["especie_id"] == especie_id
        ]


    if grupo_taxonomico != "todos":

        df_filtrado = df_filtrado[
            df_filtrado["grupo_taxonomico"]
            == grupo_taxonomico
        ]


    # ========================================================
    # DADOS POR ESTADO
    # ========================================================

    if not df_filtrado.empty:

        # -----------------------------------------------
        # Ocorrências
        # -----------------------------------------------

        df_estado_ocorrencias = (
            df_filtrado
            .groupby("estado_provincia", dropna=True)
            .size()
            .reset_index(
                name="quantidade_ocorrencias"
            )
            .rename(
                columns={
                    "estado_provincia": "estado"
                }
            )
            .sort_values(
                "quantidade_ocorrencias",
                ascending=False
            )
        )


        # -----------------------------------------------
        # Espécies
        # -----------------------------------------------

        df_estado_especies = (
            df_filtrado
            .groupby("estado_provincia", dropna=True)
            ["especie_id"]
            .nunique()
            .reset_index(
                name="quantidade_especies"
            )
            .rename(
                columns={
                    "estado_provincia": "estado"
                }
            )
            .sort_values(
                "quantidade_especies",
                ascending=False
            )
        )

    else:

        df_estado_ocorrencias = pd.DataFrame(
            columns=[
                "estado",
                "quantidade_ocorrencias"
            ]
        )

        df_estado_especies = pd.DataFrame(
            columns=[
                "estado",
                "quantidade_especies"
            ]
        )


    # ========================================================
    # CARDS
    # ========================================================

    quantidade_ocorrencias = len(
        df_filtrado
    )

    quantidade_especies = (
        df_filtrado["especie_id"]
        .nunique()
        if not df_filtrado.empty
        else 0
    )

    quantidade_estados = (
        df_filtrado["estado_provincia"]
        .nunique()
        if not df_filtrado.empty
        else 0
    )


    # ========================================================
    # RETORNO
    # ========================================================

    return (

        criar_mapa(
            df_filtrado
        ),

        criar_grafico_ocorrencias_estado(
            df_estado_ocorrencias
        ),

        criar_grafico_especies_estado(
            df_estado_especies
        ),

        f"{quantidade_ocorrencias:,}".replace(
            ",",
            "."
        ),

        f"{quantidade_especies:,}".replace(
            ",",
            "."
        ),

        quantidade_estados

    )