import dash
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
import math

from queries import (
    obter_evolucao_ocorrencias_gbif,
    obter_evolucao_especies_por_ano,
    contar_ocorrencias_gbif
)


# ============================================================
# DADOS
# ============================================================

df_ocorrencias = obter_evolucao_ocorrencias_gbif()
df_especies = obter_evolucao_especies_por_ano()

total_ocorrencias_gbif = contar_ocorrencias_gbif()


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

if not df_ocorrencias.empty:
    df_ocorrencias = df_ocorrencias.sort_values("ano").copy()

if not df_especies.empty:
    df_especies = df_especies.sort_values("ano").copy()


# ============================================================
# PERÍODO ANALISADO — GBIF
# ============================================================

if not df_ocorrencias.empty:

    quantidade_anos = int(
        df_ocorrencias["ano"].nunique()
    )

    primeiro_ano = int(
        df_ocorrencias["ano"].min()
    )

    ultimo_ano = int(
        df_ocorrencias["ano"].max()
    )

else:

    quantidade_anos = 0
    primeiro_ano = "-"
    ultimo_ano = "-"


# ============================================================
# MAIOR VOLUME DE OCORRÊNCIAS
# ============================================================

if not df_ocorrencias.empty:

    registro_maior_ano = df_ocorrencias.loc[
        df_ocorrencias["quantidade_ocorrencias"].idxmax()
    ]

    ano_maior_volume = int(
        registro_maior_ano["ano"]
    )

    maior_volume_ocorrencias = int(
        registro_maior_ano["quantidade_ocorrencias"]
    )

else:

    ano_maior_volume = "-"
    maior_volume_ocorrencias = 0


# ============================================================
# MAIOR COBERTURA DE ESPÉCIES
# ============================================================

if not df_especies.empty:

    registro_maior_cobertura = df_especies.loc[
        df_especies["quantidade_especies"].idxmax()
    ]

    ano_maior_cobertura = int(
        registro_maior_cobertura["ano"]
    )

    maior_cobertura_especies = int(
        registro_maior_cobertura["quantidade_especies"]
    )

else:

    ano_maior_cobertura = "-"
    maior_cobertura_especies = 0


# ============================================================
# MARCOS DE OCORRÊNCIAS
# ============================================================

marcos_ocorrencias = [
    10,
    100,
    1000,
    10000
]

anos_marcos = {}

for marco in marcos_ocorrencias:

    if not df_ocorrencias.empty:

        registros_marco = df_ocorrencias[
            df_ocorrencias["quantidade_ocorrencias"] >= marco
        ]

        if not registros_marco.empty:

            anos_marcos[marco] = int(
                registros_marco.iloc[0]["ano"]
            )

        else:

            anos_marcos[marco] = "-"

    else:

        anos_marcos[marco] = "-"


# ============================================================
# FUNÇÃO — ANOTAÇÕES DOS MARCOS
# ============================================================

def criar_anotacoes_marcos(ano_atual=None):

    anotacoes = []

    # --------------------------------------------------------
    # POSIÇÕES FIXAS E COMPACTAS
    # --------------------------------------------------------

    posicoes = {
        10: 0.19,
        100: 0.29,
        1000: 0.39,
        10000: 0.49
    }

    # --------------------------------------------------------
    # TÍTULO "MARCOS"
    # --------------------------------------------------------

    anotacoes.append(
        dict(
            x=0.075,
            y=0.94,
            xref="paper",
            yref="paper",

            text="<b>MARCOS:</b>",

            showarrow=False,

            font=dict(
                family="Inter, Segoe UI, Arial, sans-serif",
                size=13,
                color="white"
            ),

            align="left",

            xanchor="left",
            yanchor="middle"
        )
    )

    # --------------------------------------------------------
    # MARCOS ATINGIDOS
    # --------------------------------------------------------

    if ano_atual is not None:

        for marco in marcos_ocorrencias:

            ano_marco = anos_marcos.get(marco)

            if (
                ano_marco != "-"
                and ano_atual >= ano_marco
            ):

                if marco == 1000:
                    texto_marco = "1.000"
                elif marco == 10000:
                    texto_marco = "10.000"
                else:
                    texto_marco = f"{marco:,}".replace(",", ".")

                anotacoes.append(
                    dict(
                        x=posicoes[marco],
                        y=0.947,
                        xref="paper",
                        yref="paper",

                        text=(
                            f"<b>{texto_marco}</b>"
                            f"<br>"
                            f"<span style='font-size:10px; "
                            f"font-weight:400; opacity:0.82'>"
                            f"{ano_marco}"
                            f"</span>"
                        ),

                        showarrow=False,

                        font=dict(
                            family="Inter, Segoe UI, Arial, sans-serif",
                            size=13,
                            color="white"
                        ),

                        align="center",

                        xanchor="center",
                        yanchor="middle"
                    )
                )

    return anotacoes


# ============================================================
# PAINEL DOS MARCOS
# ============================================================

shape_marcos = dict(

    type="path",

    xref="paper",
    yref="paper",

    path=(
        "M 0.055,0.85 "
        "L 0.515,0.85 "
        "Q 0.525,0.85 0.525,0.865 "
        "L 0.525,0.975 "
        "Q 0.525,0.99 0.515,0.99 "
        "L 0.055,0.99 "
        "Q 0.045,0.99 0.045,0.975 "
        "L 0.045,0.865 "
        "Q 0.045,0.85 0.055,0.85 "
        "Z"
    ),

    fillcolor="#12372A",

    line=dict(
        color="#12372A",
        width=1
    ),

    layer="above"
)


# ============================================================
# GRÁFICO — OCORRÊNCIAS GBIF POR ANO
# ============================================================

fig_ocorrencias = go.Figure()


if not df_ocorrencias.empty:

    # --------------------------------------------------------
    # LIMITES FIXOS PARA MOSTRAR TODA A SÉRIE
    # --------------------------------------------------------

    menor_ano_ocorrencias = int(
        df_ocorrencias["ano"].min()
    )

    maior_ano_ocorrencias = int(
        df_ocorrencias["ano"].max()
    )

    menor_ocorrencia = max(
        1,
        int(df_ocorrencias["quantidade_ocorrencias"].min())
    )

    maior_ocorrencia = int(
        df_ocorrencias["quantidade_ocorrencias"].max()
    )

    margem_anos = max(
        8,
        int(
            (maior_ano_ocorrencias - menor_ano_ocorrencias) * 0.03
        )
    )

    limite_inferior_x = (
        menor_ano_ocorrencias - margem_anos
    )

    limite_superior_x = (
        maior_ano_ocorrencias + margem_anos
    )

    limite_superior_y = maior_ocorrencia * 1.8

    # --------------------------------------------------------
    # TRAÇO INICIAL
    # --------------------------------------------------------

    primeiro_registro = df_ocorrencias.iloc[0]

    fig_ocorrencias.add_trace(
        go.Scatter(
            x=[primeiro_registro["ano"]],
            y=[primeiro_registro["quantidade_ocorrencias"]],
            mode="lines+markers",
            name="Ocorrências",
            line=dict(
                color="#58756A",
                width=3
            ),
            marker=dict(
                size=8,
                color="#24352D",
                line=dict(
                    color="white",
                    width=1
                )
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Ocorrências: %{y:,}"
                "<extra></extra>"
            )
        )
    )

    # --------------------------------------------------------
    # FRAMES DA ANIMAÇÃO
    # --------------------------------------------------------

    frames = []

    for i in range(1, len(df_ocorrencias) + 1):

        dados_frame = df_ocorrencias.iloc[:i]

        ano_atual = int(
            dados_frame.iloc[-1]["ano"]
        )

        frames.append(
            go.Frame(

                name=str(ano_atual),

                data=[
                    go.Scatter(
                        x=dados_frame["ano"],
                        y=dados_frame["quantidade_ocorrencias"],
                        mode="lines+markers",

                        line=dict(
                            color="#58756A",
                            width=3
                        ),

                        marker=dict(
                            size=7,
                            color="#24352D",
                            line=dict(
                                color="white",
                                width=1
                            )
                        ),

                        hovertemplate=(
                            "<b>%{x}</b><br>"
                            "Ocorrências: %{y:,}"
                            "<extra></extra>"
                        )
                    )
                ],

                # ------------------------------------------------
                # MARCOS CONTROLADOS PELA ANIMAÇÃO
                # ------------------------------------------------

                layout=go.Layout(

                    shapes=[
                        shape_marcos
                    ],

                    annotations=criar_anotacoes_marcos(
                        ano_atual
                    )
                )
            )
        )

    fig_ocorrencias.frames = frames

    # --------------------------------------------------------
    # SLIDER
    # --------------------------------------------------------

    slider_steps = []

    for ano in df_ocorrencias["ano"]:

        ano = int(ano)

        slider_steps.append(
            {
                "args": [
                    [str(ano)],
                    {
                        "frame": {
                            "duration": 350,
                            "redraw": True
                        },
                        "mode": "immediate",
                        "transition": {
                            "duration": 250
                        }
                    }
                ],
                "label": str(ano),
                "method": "animate"
            }
        )

    # --------------------------------------------------------
    # CONFIGURAÇÃO DO GRÁFICO
    # --------------------------------------------------------

    fig_ocorrencias.update_layout(

        template="plotly_white",

        height=500,

        title=(
            "Como o conhecimento sobre as ocorrências "
            "foi construído ao longo do tempo?"
        ),

        margin=dict(
            l=55,
            r=30,
            t=70,
            b=95
        ),

        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            family="Arial",
            color="#24352D"
        ),

        # ----------------------------------------------------
        # NÃO COLOCAMOS MARCOS AQUI.
        #
        # Eles entram somente nos FRAMES.
        # ----------------------------------------------------

        shapes=[],

        annotations=[],

        # ----------------------------------------------------
        # EIXO X
        # ----------------------------------------------------

        xaxis=dict(
            title="Ano",
            showgrid=False,
            zeroline=False,
            range=[
                limite_inferior_x,
                limite_superior_x
            ],
            autorange=False
        ),

        # ----------------------------------------------------
        # EIXO Y
        # ----------------------------------------------------

        yaxis=dict(
            title="Quantidade de ocorrências",
            type="log",
            showgrid=True,
            gridcolor="#E8EDEB",
            zeroline=False,
            range=[
                math.log10(menor_ocorrencia),
                math.log10(limite_superior_y)
            ],
            autorange=False
        ),

        hoverlabel=dict(
            bgcolor="#24352D",
            font=dict(
                color="white",
                size=13
            ),
            bordercolor="#58756A"
        ),

        # ----------------------------------------------------
        # CONTROLES DE ANIMAÇÃO
        # ----------------------------------------------------

        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "showactive": False,

                "x": 0,
                "y": -0.18,

                "xanchor": "left",
                "yanchor": "top",

                "buttons": [

                    {
                        "label": "▶ Reproduzir",
                        "method": "animate",

                        "args": [
                            None,
                            {
                                "frame": {
                                    "duration": 350,
                                    "redraw": True
                                },

                                "fromcurrent": True,

                                "transition": {
                                    "duration": 250
                                }
                            }
                        ]
                    },

                    {
                        "label": "⏸ Pausar",
                        "method": "animate",

                        "args": [
                            [None],
                            {
                                "frame": {
                                    "duration": 0,
                                    "redraw": False
                                },

                                "mode": "immediate",

                                "transition": {
                                    "duration": 0
                                }
                            }
                        ]
                    }

                ]
            }
        ],

        # ----------------------------------------------------
        # LINHA DO TEMPO
        # ----------------------------------------------------

        sliders=[
            {
                "active": 0,

                "x": 0,
                "y": -0.08,
                "len": 1,

                "xanchor": "left",
                "yanchor": "top",

                "currentvalue": {
                    "prefix": "Ano: ",

                    "font": {
                        "size": 14,
                        "color": "#24352D"
                    }
                },

                "transition": {
                    "duration": 250,
                    "easing": "cubic-in-out"
                },

                "steps": slider_steps
            }
        ]

    )


# ============================================================
# GRÁFICO — ESPÉCIES DISTINTAS AVALIADAS POR ANO
# ============================================================

fig_especies = go.Figure()


if not df_especies.empty:

    fig_especies.add_trace(
        go.Scatter(
            x=df_especies["ano"],
            y=df_especies["quantidade_especies"],
            mode="lines+markers",
            name="Espécies",
            line=dict(
                color="#3E5A50",
                width=3
            ),
            marker=dict(
                size=7,
                color="#58756A",
                line=dict(
                    color="white",
                    width=1
                )
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Espécies distintas: %{y:,}"
                "<extra></extra>"
            )
        )
    )


fig_especies.update_layout(
    template="plotly_white",
    height=430,
    title="Quantas espécies diferentes foram avaliadas ao longo do tempo?",
    margin=dict(
        l=30,
        r=30,
        t=70,
        b=40
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Arial",
        color="#24352D"
    ),
    xaxis=dict(
        title="Ano",
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        title="Espécies distintas",
        showgrid=True,
        gridcolor="#E8EDEB",
        zeroline=False
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


# ============================================================
# TEXTO DOS INSIGHTS
# ============================================================

insight_ocorrencias = (
    f"A base analisada reúne "
    f"{total_ocorrencias_gbif:,} registros de ocorrência do GBIF. "
    f"Esses registros permitem observar como a documentação da "
    f"presença das espécies foi distribuída ao longo do tempo."
)


# ------------------------------------------------------------
# INSIGHT DE COBERTURA
# ------------------------------------------------------------

if ano_maior_cobertura != "-":

    insight_cobertura = (
        f"A maior quantidade de espécies distintas avaliadas "
        f"em um único ano ocorreu em {ano_maior_cobertura}, "
        f"com {maior_cobertura_especies:,} espécies. "
        f"Esse indicador mostra os momentos em que a cobertura "
        f"das espécies avaliadas foi maior na base IUCN."
    )

else:

    insight_cobertura = (
        "Não foi possível identificar o maior nível "
        "de cobertura de espécies na série."
    )


# ------------------------------------------------------------
# INSIGHT DO MAIOR VOLUME DE OCORRÊNCIAS
# ------------------------------------------------------------

if ano_maior_volume != "-":

    insight_pico = (
        f"O maior volume de ocorrências registrado na série "
        f"ocorreu em {ano_maior_volume}, com "
        f"{maior_volume_ocorrencias:,} registros. "
        f"Picos como esse podem estar relacionados ao esforço "
        f"de coleta, à disponibilidade de dados ou à quantidade "
        f"de observações incorporadas ao GBIF naquele período."
    )

else:

    insight_pico = (
        "Não foi possível identificar um ano de maior volume "
        "de ocorrências."
    )


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
                            "Evolução"
                        ),

                        html.P(
                            "Como o conhecimento sobre as espécies "
                            "foi construído ao longo do tempo?"
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
                    className="nav-link"
                ),

                dcc.Link(
                    "Evolução",
                    href="/evolucao",
                    className="nav-link active"
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


                # ====================================================
                # 01 — HISTÓRICO
                # ====================================================

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
                                            "O histórico das ocorrências"
                                        ),

                                        html.P(
                                            "Período analisado na base GBIF",
                                            className="section-subtitle"
                                        ),

                                    ]
                                )

                            ]
                        ),


                        html.Div(
                            className="stats-grid",
                            children=[

                                html.Div(
                                    className="stat-card",
                                    children=[

                                        html.Div(
                                            f"{quantidade_anos:,}".replace(
                                                ",",
                                                "."
                                            ),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Anos analisados",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Quantidade de anos distintos "
                                            "com ocorrências registradas",
                                            className="stat-description"
                                        ),

                                    ]
                                ),


                                html.Div(
                                    className="stat-card",
                                    children=[

                                        html.Div(
                                            str(primeiro_ano),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Primeiro ano",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Primeiro ano disponível "
                                            "no histórico analisado",
                                            className="stat-description"
                                        ),

                                    ]
                                ),


                                html.Div(
                                    className="stat-card",
                                    children=[

                                        html.Div(
                                            str(ultimo_ano),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Último ano",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Ano mais recente disponível "
                                            "na base analisada",
                                            className="stat-description"
                                        ),

                                    ]
                                ),


                                html.Div(
                                    className="stat-card",
                                    children=[

                                        html.Div(
                                            f"{total_ocorrencias_gbif:,}".replace(
                                                ",",
                                                "."
                                            ),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Registros de ocorrência",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Total de ocorrências "
                                            "disponíveis na base GBIF",
                                            className="stat-description"
                                        ),

                                    ]
                                ),

                            ]
                        ),

                    ]
                ),


                # ====================================================
                # 02 — OCORRÊNCIAS GBIF
                # ====================================================

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
                                            "O volume de ocorrências"
                                        ),

                                        html.P(
                                            "Registros de ocorrência do GBIF ao longo do tempo",
                                            className="section-subtitle"
                                        ),

                                    ]
                                )

                            ]
                        ),


                        dcc.Graph(
                            figure=fig_ocorrencias,
                            className="chart"
                        ),


                        html.Div(
                            className="context-box",
                            children=[

                                html.P(
                                    [
                                        html.Strong(
                                            "O que esse histórico mostra? "
                                        ),
                                        "Os registros de ocorrência ajudam "
                                        "a observar como o volume de dados "
                                        "sobre a presença das espécies foi "
                                        "sendo documentado ao longo do tempo."
                                    ]
                                ),

                                html.P(
                                    insight_ocorrencias
                                ),

                                html.P(
                                    "Esse histórico representa os registros "
                                    "presentes na base utilizada pelo Biodata "
                                    "e não deve ser interpretado como uma "
                                    "medida direta da quantidade real de "
                                    "espécies existentes em cada período."
                                ),

                            ]
                        ),

                    ]
                ),


                # ====================================================
                # 03 — COBERTURA DAS ESPÉCIES
                # ====================================================

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
                                            "A cobertura das espécies"
                                        ),

                                        html.P(
                                            "Quantidade de espécies distintas avaliadas pela IUCN em cada ano",
                                            className="section-subtitle"
                                        ),

                                    ]
                                )

                            ]
                        ),


                        dcc.Graph(
                            figure=fig_especies,
                            className="chart"
                        ),


                        html.Div(
                            className="context-box",
                            children=[

                                html.P(
                                    [
                                        html.Strong(
                                            "Por que isso importa? "
                                        ),
                                        "Observar espécies distintas ajuda "
                                        "a entender a cobertura das avaliações "
                                        "ao longo do tempo, evitando confundir "
                                        "o número de avaliações com a quantidade "
                                        "de espécies avaliadas."
                                    ]
                                ),

                                html.P(
                                    insight_cobertura
                                ),

                                html.P(
                                    "Assim como os registros de ocorrência, "
                                    "esse indicador representa o que está "
                                    "documentado na base analisada e não "
                                    "constitui, isoladamente, uma medida "
                                    "da biodiversidade existente."
                                ),

                            ]
                        ),

                    ]
                ),


                # ====================================================
                # 04 — O QUE OS DADOS REVELAM?
                # ====================================================

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
                                            "O que os dados revelam?"
                                        ),

                                        html.P(
                                            "Principais insights encontrados no histórico",
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
                                        html.Strong(
                                            "01 · Registros de ocorrência — "
                                        ),
                                        insight_ocorrencias
                                    ]
                                ),

                                html.P(
                                    [
                                        html.Strong(
                                            "02 · Cobertura das espécies — "
                                        ),
                                        insight_cobertura
                                    ]
                                ),

                                html.P(
                                    [
                                        html.Strong(
                                            "03 · Maior volume de registros — "
                                        ),
                                        insight_pico
                                    ]
                                ),

                            ]
                        ),


                        html.Div(
                            className="context-box",
                            children=[

                                html.P(
                                    [
                                        html.Strong(
                                            "Uma leitura mais ampla: "
                                        ),
                                        "o histórico de registros e avaliações "
                                        "ajuda a entender como o conhecimento "
                                        "sobre as espécies foi sendo construído "
                                        "e documentado ao longo do tempo."
                                    ]
                                ),

                                html.P(
                                    "Mais registros não significam necessariamente "
                                    "mais biodiversidade. A quantidade de dados "
                                    "pode ser influenciada pelo esforço de coleta, "
                                    "pela disponibilidade de informações, pela "
                                    "cobertura geográfica e por mudanças na forma "
                                    "como os dados são registrados."
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
                    "BIODATA · Conservação e biodiversidade no Brasil"
                )

            ]
        ),

    ]
)