from dash import html, dcc

from queries import (
    contar_especies_icmbio_avaliadas,
    contar_ocorrencias_no_brasil,
    contar_dados_sensiveis_icmbio,
    obter_top_10_especies_risco_brasil,
)


# ============================================================
# DADOS
# ============================================================

especies_avaliadas = contar_especies_icmbio_avaliadas()
ocorrencias_brasil = contar_ocorrencias_no_brasil()
dados_sensiveis = contar_dados_sensiveis_icmbio()

df_top_especies = obter_top_10_especies_risco_brasil()


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
                            "Um olhar sobre os dados de conservação e "
                            "ocorrência de espécies no Brasil."
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
                    className="nav-link active"
                ),

                dcc.Link(
                    "Distribuição",
                    href="/distribuicao",
                    className="nav-link"
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
                                            "Conservação e ocorrência das espécies no Brasil",
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
                                    "quanto os registros de ocorrência das "
                                    "espécies no território brasileiro."
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
                                            "Principais indicadores dos dados brasileiros",
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
                                            "Espécies analisadas",
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
                                            f"{ocorrencias_brasil:,}".replace(
                                                ",", "."
                                            ),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Ocorrências no Brasil",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Registros de ocorrência do GBIF localizados no Brasil",
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
                # 03 — O QUE OS DADOS REVELAM
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
                                            "O que os dados revelam sobre o Brasil?"
                                        ),

                                        html.P(
                                            "Volume de registros de ocorrência",
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
                                        "Os registros de ocorrência "
                                        "disponíveis para o Brasil "
                                        "representam um volume de dados "
                                        "cerca de ",
                                        html.Strong("20 vezes maior"),
                                        " que o número de espécies analisadas."
                                    ]
                                ),

                                html.P(
                                    [
                                        "Isso representa aproximadamente ",
                                        html.Strong(
                                            "20 ocorrências registradas "
                                            "para cada espécie analisada"
                                        ),
                                        ", criando uma base ampla para "
                                        "contextualizar onde essas espécies "
                                        "são registradas no território brasileiro."
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),

                # ------------------------------------------------
                # 04 — RANKING DE ESPÉCIES
                # ------------------------------------------------

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
                                            "Quais espécies exigem maior atenção?"
                                        ),

                                        html.P(
                                            "Espécies com maior nível de risco entre os registros encontrados no Brasil",
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
                                        "Entre as espécies com ocorrência "
                                        "registrada no Brasil, o ranking "
                                        "abaixo destaca aquelas classificadas "
                                        "nos maiores níveis de risco de extinção."
                                    ]
                                ),

                                html.P(
                                    [
                                        "A classificação considera o nível "
                                        "de risco registrado na base de "
                                        "conservação, priorizando as categorias "
                                        "de maior preocupação."
                                    ]
                                ),
                            ]
                        ),

                        html.Div(
                            className="species-ranking-container",
                            children=[

                                html.Div(
                                    className="species-ranking-list",
                                    children=[

                                        html.Div(
                                            [
                                                html.Div(
                                                    str(i + 1).zfill(2),
                                                    className="species-ranking-number"
                                                ),

                                                html.Div(
                                                    [
                                                        html.Div(
                                                            row["nome_popular"]
                                                            if row["nome_popular"]
                                                            else "Nome popular não informado",
                                                            className="species-ranking-name"
                                                        ),

                                                        html.Div(
                                                            row["nome_cientifico"],
                                                            className="species-ranking-scientific"
                                                        ),
                                                    ],
                                                    className="species-ranking-info"
                                                ),

                                                html.Div(
                                                    row["categoria_risco"],
                                                    className="species-ranking-category"
                                                ),
                                            ],
                                            className="species-ranking-item"
                                        )
                                        for i, row in df_top_especies.iterrows()
                                    ]
                                ),

                                html.Div(
                                    className="species-ranking-highlight",
                                    children=[

                                        html.Div(
                                            "ESPÉCIE EM DESTAQUE",
                                            className="species-highlight-label"
                                        ),

                                        html.Div(
                                            (
                                                df_top_especies.iloc[0]["nome_popular"]
                                                if len(df_top_especies) > 0
                                                and df_top_especies.iloc[0]["nome_popular"]
                                                else "Nome popular não informado"
                                            ),
                                            className="species-highlight-name"
                                        ),

                                        html.Div(
                                            (
                                                df_top_especies.iloc[0]["nome_cientifico"]
                                                if len(df_top_especies) > 0
                                                else ""
                                            ),
                                            className="species-highlight-scientific"
                                        ),

                                        html.Div(
                                            (
                                                df_top_especies.iloc[0]["categoria_risco"]
                                                if len(df_top_especies) > 0
                                                else ""
                                            ),
                                            className="species-highlight-category"
                                        ),

                                        html.Div(
                                            html.Img(
                                                src="/assets/arara-pagina3.jfif",
                                                style={
                                                    "width": "100%",
                                                    "height": "100%",
                                                    "objectFit": "cover",
                                                    "display": "block"
                                                }
                                            ),
                                            className="species-highlight-image"
                                        ),
                                    ]
                                ),
                            ]
                        ),
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