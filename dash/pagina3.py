from dash import html, dcc
import plotly.graph_objects as go

from queries import (
    contar_especies_icmbio_avaliadas,
    contar_especies_icmbio_ameacadas,
    contar_dados_sensiveis_icmbio,
    obter_especies_por_estado,
)


# ============================================================
# DADOS
# ============================================================

especies_avaliadas = contar_especies_icmbio_avaliadas()
especies_ameacadas = contar_especies_icmbio_ameacadas()
dados_sensiveis = contar_dados_sensiveis_icmbio()

df_estados = obter_especies_por_estado()


# ============================================================
# GRÁFICO — DISTRIBUIÇÃO POR ESTADO
# ============================================================

fig_estados = go.Figure()

fig_estados.add_trace(
    go.Bar(
        x=df_estados["estado"],
        y=df_estados["quantidade_especies"],
        text=df_estados["quantidade_especies"],
        textposition="outside",
    )
)

fig_estados.update_layout(
    title="Quantas espécies estão registradas em cada estado?",
    xaxis_title="Estado / Província",
    yaxis_title="Quantidade de espécies",
    xaxis_tickangle=-45,
    height=550,
    margin=dict(
        l=60,
        r=30,
        t=80,
        b=140
    ),
)


# ============================================================
# GRÁFICO — ICMBio
# ============================================================

fig_icmbio = go.Figure()

fig_icmbio.add_trace(
    go.Bar(
        x=[
            "Espécies avaliadas",
            "Espécies ameaçadas"
        ],
        y=[
            especies_avaliadas,
            especies_ameacadas
        ],
        text=[
            especies_avaliadas,
            especies_ameacadas
        ],
        textposition="outside",
    )
)

fig_icmbio.update_layout(
    title="Qual é a dimensão das avaliações de conservação no Brasil?",
    xaxis_title="Indicador",
    yaxis_title="Quantidade de espécies",
    height=450,
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
                            "Brasil"
                        ),

                        html.P(
                            "Um olhar sobre a conservação e a "
                            "distribuição das espécies no território brasileiro."
                        ),
                    ]
                )
            ]
        ),

        # ============================================================
        # NAVEGAÇÃO
        # ============================================================

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
            className="nav-link active"
        ),

        dcc.Link(
            "Distribuição",
            href="/distribuicao",
            className="nav-link"
        ),

        # Futuras páginas continuam desabilitadas
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

                # ------------------------------------------------
                # 01 — CONTEXTO
                # ------------------------------------------------

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
                                            "O que estamos analisando?"
                                        ),

                                        html.P(
                                            "Conservação das espécies no Brasil",
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
                                        "Nesta página, o foco está nos "
                                        "dados relacionados ao ",
                                        html.Strong("Brasil"),
                                        ", utilizando principalmente "
                                        "informações de avaliação do ",
                                        html.Strong("ICMBio"),
                                        " e registros de ocorrência "
                                        "do GBIF."
                                    ]
                                ),

                                html.P(
                                    "A combinação dessas fontes permite "
                                    "observar tanto a situação de conservação "
                                    "quanto a distribuição das espécies "
                                    "registradas no território brasileiro."
                                ),
                            ]
                        ),
                    ]
                ),

                # ------------------------------------------------
                # 02 — INDICADORES
                # ------------------------------------------------

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
                                            "Qual é a dimensão do cenário?"
                                        ),

                                        html.P(
                                            "Principais indicadores do ICMBio",
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
                                            f"{especies_avaliadas:,}".replace(
                                                ",", "."
                                            ),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Espécies avaliadas",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Espécies com registro de avaliação no ICMBio",
                                            className="stat-description"
                                        ),
                                    ]
                                ),

                                html.Div(
                                    className="stat-card",
                                    children=[

                                        html.Div(
                                            f"{especies_ameacadas:,}".replace(
                                                ",", "."
                                            ),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Espécies ameaçadas",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Espécies que constam na lista de ameaçadas",
                                            className="stat-description"
                                        ),
                                    ]
                                ),

                                html.Div(
                                    className="stat-card",
                                    children=[

                                        html.Div(
                                            f"{dados_sensiveis:,}".replace(
                                                ",", "."
                                            ),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Registros sensíveis",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Registros marcados como dados sensíveis",
                                            className="stat-description"
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),

                # ------------------------------------------------
                # 03 — ICMBio
                # ------------------------------------------------

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
                                            "O que os dados do ICMBio indicam?"
                                        ),

                                        html.P(
                                            "Avaliação das espécies no Brasil",
                                            className="section-subtitle"
                                        ),
                                    ]
                                )
                            ]
                        ),

                        dcc.Graph(
                            figure=fig_icmbio,
                            className="chart"
                        ),

                        html.Div(
                            className="context-box",
                            children=[

                                html.P(
                                    [
                                        "O indicador de espécies ameaçadas "
                                        "representa espécies que possuem "
                                        "registro no ICMBio com ",
                                        html.Strong(
                                            "consta_lista_ameacada = TRUE"
                                        ),
                                        "."
                                    ]
                                ),

                                html.P(
                                    [
                                        "Esses dados devem ser interpretados "
                                        "como registros presentes na base "
                                        "utilizada pelo projeto, e não como "
                                        "uma estimativa absoluta de todas as "
                                        "espécies existentes no Brasil."
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),

                # ------------------------------------------------
                # 04 — DISTRIBUIÇÃO
                # ------------------------------------------------

                html.Section(
                    className="section",
                    children=[

                        html.Div(
    className="context-box",
    children=[

        html.P(
            [
                "A quantidade apresentada representa "
                "espécies distintas registradas em "
                "ocorrências do GBIF por estado ou província."
            ]
        ),

        html.P(
            "Os dados também podem apresentar variações "
            "na forma como os locais são registrados. "
            "Durante a etapa de transformação, esses valores "
            "são padronizados para facilitar a análise e a "
            "comparação entre os estados."
        ),

        html.P(
            "Além disso, um estado com mais registros não "
            "significa necessariamente que possua maior "
            "biodiversidade. A quantidade de registros também "
            "depende do esforço e da disponibilidade de observações."
        ),
    ]
)
                    ]
                ),

                # ------------------------------------------------
                # 05 — DADOS SENSÍVEIS
                # ------------------------------------------------

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
                                            "Por que alguns registros "
                                            "podem ser limitados?"
                                        ),

                                        html.P(
                                            "Proteção das espécies",
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
                                        "A base também identifica registros "
                                        "como ",
                                        html.Strong("dados sensíveis"),
                                        ". Essas informações podem exigir "
                                        "tratamento ou restrição de acesso "
                                        "quando sua divulgação representar "
                                        "risco para a conservação das espécies."
                                    ]
                                ),

                                html.P(
                                    [
                                        "Por isso, uma ausência de informação "
                                        "não deve ser interpretada automaticamente "
                                        "como ausência da espécie naquele local."
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
                    "BIODATA · Conservação e biodiversidade no Brasil"
                )
            ]
        ),
    ]
)