import dash
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd

from queries import (
    obter_evolucao_ocorrencias_gbif,
    obter_evolucao_especies_por_ano,
    contar_anos_avaliacoes_iucn,
    obter_periodo_avaliacoes_iucn,
    obter_crescimento_medio_ocorrencias_gbif
)


# ============================================================
# DADOS
# ============================================================

df_ocorrencias = obter_evolucao_ocorrencias_gbif()
df_especies = obter_evolucao_especies_por_ano()

quantidade_anos = contar_anos_avaliacoes_iucn()
df_periodo = obter_periodo_avaliacoes_iucn()

crescimento_medio_ocorrencias = (
    obter_crescimento_medio_ocorrencias_gbif()
)


# ============================================================
# PERÍODO ANALISADO
# ============================================================

primeiro_ano = (
    int(df_periodo.iloc[0]["primeiro_ano"])
    if not df_periodo.empty
    and pd.notna(df_periodo.iloc[0]["primeiro_ano"])
    else "-"
)

ultimo_ano = (
    int(df_periodo.iloc[0]["ultimo_ano"])
    if not df_periodo.empty
    and pd.notna(df_periodo.iloc[0]["ultimo_ano"])
    else "-"
)


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

if not df_ocorrencias.empty:
    df_ocorrencias = df_ocorrencias.sort_values("ano").copy()

if not df_especies.empty:
    df_especies = df_especies.sort_values("ano").copy()


# ============================================================
# CÁLCULO DA VARIAÇÃO MÉDIA DAS OCORRÊNCIAS
# ============================================================

if (
    crescimento_medio_ocorrencias is not None
    and pd.notna(crescimento_medio_ocorrencias)
):

    crescimento_medio_ocorrencias = float(
        crescimento_medio_ocorrencias
    )

else:

    crescimento_medio_ocorrencias = None


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
# GRÁFICO — OCORRÊNCIAS GBIF POR ANO
# ============================================================

fig_ocorrencias = go.Figure()


if not df_ocorrencias.empty:

    fig_ocorrencias.add_trace(
        go.Scatter(
            x=df_ocorrencias["ano"],
            y=df_ocorrencias["quantidade_ocorrencias"],
            mode="lines+markers",
            name="Ocorrências",
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
    )


fig_ocorrencias.update_layout(
    template="plotly_white",
    height=430,
    title="Como o volume de registros de ocorrência mudou ao longo do tempo?",
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
        title="Quantidade de ocorrências",
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

if crescimento_medio_ocorrencias is not None:

    if crescimento_medio_ocorrencias > 0:

        insight_ocorrencias = (
            f"A quantidade de ocorrências registradas no GBIF "
            f"apresentou uma variação média anual de "
            f"{crescimento_medio_ocorrencias:.1f}% "
            f"entre os anos com registros consecutivos disponíveis. "
            f"Esse indicador ajuda a observar como o volume de "
            f"registros foi se comportando ao longo do histórico."
        )

    elif crescimento_medio_ocorrencias < 0:

        insight_ocorrencias = (
            f"A quantidade de ocorrências registradas no GBIF "
            f"apresentou uma variação média anual de "
            f"{abs(crescimento_medio_ocorrencias):.1f}% para baixo "
            f"entre os anos com registros consecutivos disponíveis. "
            f"Esse indicador ajuda a observar como o volume de "
            f"registros foi se comportando ao longo do histórico."
        )

    else:

        insight_ocorrencias = (
            "A quantidade de ocorrências registradas no GBIF "
            "apresentou, em média, pouca variação entre os anos "
            "com registros consecutivos disponíveis."
        )

else:

    insight_ocorrencias = (
        "Não há dados suficientes para calcular "
        "a variação média anual das ocorrências."
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
                            "Como o conhecimento sobre o risco "
                            "das espécies mudou ao longo do tempo?"
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

                html.Span(
                    "Evolução",
                    className="nav-link active"
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
                                            "O histórico das avaliações"
                                        ),

                                        html.P(
                                            "Período analisado na base IUCN",
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
                                            "com avaliações registradas",
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
                                            (
                                                f"{crescimento_medio_ocorrencias:+.1f}%"
                                                if crescimento_medio_ocorrencias
                                                is not None
                                                else "-"
                                            ),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Variação média das ocorrências",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Variação percentual média anual "
                                            "dos registros do GBIF",
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