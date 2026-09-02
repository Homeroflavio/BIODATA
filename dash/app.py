from dash import Dash, html, dcc, Input, Output

from queries import (
    contar_especies,
    contar_avaliacoes_iucn,
    contar_ocorrencias_gbif,
    contar_pans,
    
)

from pagina2 import layout as pagina2_layout
from pagina3 import layout as pagina3_layout
from pagina4 import layout as pagina4_layout
from pagina5 import layout as pagina5_layout



# ============================================================
# CONFIGURAÇÃO
# ============================================================

app = Dash(
    __name__,
    suppress_callback_exceptions=True
)

app.title = "Biodata | Biodiversidade"


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


def criar_fonte(sigla, nome, descricao):
    return html.Div(
        className="source-card",
        children=[
            html.Div(
                sigla,
                className="source-sigla"
            ),

            html.H3(nome),

            html.P(descricao),
        ]
    )


# ============================================================
# PÁGINA 1 — SOBRE O PROJETO
# ============================================================

pagina1_layout = html.Div(
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
                            "Explorando os dados da biodiversidade"
                        ),

                        html.P(
                            "Uma visão integrada sobre espécies, "
                            "conservação, distribuição geográfica "
                            "e ações de proteção."
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
                    className="nav-link active"
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
                # 01 — O QUE É
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
                                            "O que é o Biodata?"
                                        ),

                                        html.P(
                                            "Contexto e objetivo do projeto",
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
                                        "O ",
                                        html.Strong("Biodata"),
                                        " é um projeto de integração, "
                                        "análise e engenharia de dados aplicado "
                                        "à biodiversidade. A pipeline reúne "
                                        "informações de diferentes fontes para "
                                        "permitir uma visão mais ampla sobre "
                                        "as espécies, seu estado de conservação, "
                                        "sua distribuição e as ações destinadas "
                                        "à sua proteção."
                                    ]
                                ),

                                html.P(
                                    [
                                        "Além da análise dos dados, o projeto "
                                        "também possui uma abordagem de ",
                                        html.Strong("Engenharia de Dados"),
                                        ", utilizando uma pipeline com ",
                                        html.Strong("Airflow"),
                                        " e ",
                                        html.Strong("Docker"),
                                        " para organizar e automatizar o "
                                        "processamento dos dados."
                                    ]
                                ),

                                html.P(
                                    [
                                        "A pipeline utiliza o conceito de "
                                        "camadas ",
                                        html.Strong("Bronze"),
                                        ", ",
                                        html.Strong("Prata"),
                                        " e ",
                                        html.Strong("Ouro"),
                                        ": os dados brutos são coletados na "
                                        "Bronze, tratados e padronizados na "
                                        "Prata e preparados para análise e "
                                        "visualização na Ouro."
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),

                # ------------------------------------------------
                # 02 — FONTES
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
                                            "De onde vêm os dados?"
                                        ),

                                        html.P(
                                            "Fontes utilizadas na pipeline",
                                            className="section-subtitle"
                                        ),
                                    ]
                                )
                            ]
                        ),

                        html.Div(
                            className="sources-grid",
                            children=[

                                criar_fonte(
                                    "GBIF",
                                    "Global Biodiversity "
                                    "Information Facility",
                                    "Registros de ocorrência de espécies, "
                                    "incluindo localização geográfica."
                                ),

                                criar_fonte(
                                    "IUCN",
                                    "International Union "
                                    "for Conservation of Nature",
                                    "Avaliações sobre o estado de "
                                    "conservação das espécies."
                                ),

                                criar_fonte(
                                    "ICMBio",
                                    "Instituto Chico Mendes",
                                    "Informações relacionadas à avaliação "
                                    "e conservação de espécies no Brasil."
                                ),

                                criar_fonte(
                                    "PAN",
                                    "Planos de Ação Nacional",
                                    "Informações sobre planos e ações "
                                    "voltados à conservação."
                                ),
                            ]
                        ),
                    ]
                ),

                # ------------------------------------------------
                # 03 — CONCEITOS
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
                                            "Como interpretar os dados?"
                                        ),

                                        html.P(
                                            "Alguns conceitos importantes",
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
                                            "Ocorrência"
                                        ),

                                        html.P(
                                            "Um registro de ocorrência "
                                            "representa uma espécie "
                                            "registrada em determinado "
                                            "local. Neste projeto, esses "
                                            "registros são obtidos a partir "
                                            "do GBIF."
                                        ),
                                    ]
                                ),

                                html.Div(
                                    className="concept-card",
                                    children=[

                                        html.H3(
                                            "Avaliação de conservação"
                                        ),

                                        html.P(
                                            "Uma avaliação representa um "
                                            "registro utilizado para "
                                            "classificar o estado de "
                                            "conservação de uma espécie."
                                        ),
                                    ]
                                ),

                                html.Div(
                                    className="concept-card",
                                    children=[

                                        html.H3(
                                            "PAN"
                                        ),

                                        html.P(
                                            "Plano de Ação Nacional voltado "
                                            "à conservação de espécies ou "
                                            "grupos considerados prioritários."
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),

                # ------------------------------------------------
                # 04 — DADOS SENSÍVEIS
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
                                            "Por que alguns dados não "
                                            "estão disponíveis?"
                                        ),

                                        html.P(
                                            "Proteção de informações sensíveis",
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
                                        "Alguns registros podem conter ",
                                        html.Strong(
                                            "dados sensíveis"
                                        ),
                                        " relacionados à localização "
                                        "ou ocorrência de determinadas "
                                        "espécies."
                                    ]
                                ),

                                html.P(
                                    [
                                        "Essas informações podem ter sua "
                                        "disponibilidade limitada para "
                                        "reduzir riscos à conservação das "
                                        "espécies. Portanto, a ausência de "
                                        "uma informação no conjunto de dados "
                                        "não significa necessariamente que "
                                        "a espécie não ocorra naquele local."
                                    ]
                                ),

                                html.P(
                                    [
                                        html.Strong(
                                            "Importante: "
                                        ),
                                        "essa limitação tem como objetivo "
                                        "proteger as espécies e evitar que "
                                        "informações potencialmente sensíveis "
                                        "sejam utilizadas de forma inadequada."
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),

                # ------------------------------------------------
                # 05 — PIPELINE
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
                                            "Como os dados chegam ao dashboard?"
                                        ),

                                        html.P(
                                            "Arquitetura simplificada da pipeline",
                                            className="section-subtitle"
                                        ),
                                    ]
                                )
                            ]
                        ),

                        html.Div(
                            className="pipeline",
                            children=[

                                # FONTES

                                html.Div(
                                    className="pipeline-step pipeline-fontes",
                                    children=[

                                        html.Strong(
                                            "FONTES"
                                        ),

                                        html.Span(
                                            "GBIF · IUCN · ICMBio · PAN"
                                        ),
                                    ]
                                ),

                                html.Div(
                                    "→",
                                    className="pipeline-arrow"
                                ),

                                # EXTRACT — BRONZE

                                html.Div(
                                    className=(
                                        "pipeline-step "
                                        "pipeline-bronze"
                                    ),
                                    children=[

                                        html.Div(
                                            "BRONZE",
                                            className="pipeline-layer"
                                        ),

                                        html.Strong(
                                            "EXTRACT"
                                        ),

                                        html.Span(
                                            "Coleta dos dados"
                                        ),
                                    ]
                                ),

                                html.Div(
                                    "→",
                                    className="pipeline-arrow"
                                ),

                                # TRANSFORM — PRATA

                                html.Div(
                                    className=(
                                        "pipeline-step "
                                        "pipeline-prata"
                                    ),
                                    children=[

                                        html.Div(
                                            "PRATA",
                                            className="pipeline-layer"
                                        ),

                                        html.Strong(
                                            "TRANSFORM"
                                        ),

                                        html.Span(
                                            "Limpeza e padronização"
                                        ),
                                    ]
                                ),

                                html.Div(
                                    "→",
                                    className="pipeline-arrow"
                                ),

                                # LOAD — OURO

                                html.Div(
                                    className=(
                                        "pipeline-step "
                                        "pipeline-ouro"
                                    ),
                                    children=[

                                        html.Div(
                                            "OURO",
                                            className="pipeline-layer"
                                        ),

                                        html.Strong(
                                            "LOAD"
                                        ),

                                        html.Span(
                                            "PostgreSQL"
                                        ),
                                    ]
                                ),

                                html.Div(
                                    "→",
                                    className="pipeline-arrow"
                                ),

                                # BIODATA / DASH

                                html.Div(
                                    className=(
                                        "pipeline-step "
                                        "pipeline-final"
                                    ),
                                    children=[

                                        html.Strong(
                                            "BIODATA"
                                        ),

                                        html.Span(
                                            "Dash"
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),

                # ------------------------------------------------
                # 06 — NÚMEROS
                # ------------------------------------------------

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
                                            "O que existe atualmente na base?"
                                        ),

                                        html.P(
                                            "Dados carregados no PostgreSQL",
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
                                    f"{contar_especies():,}".replace(
                                        ",",
                                        "."
                                    ),
                                    "Espécies",
                                    "Espécies analisadas"
                                ),

                                criar_card(
                                    f"{contar_avaliacoes_iucn():,}".replace(
                                        ",",
                                        "."
                                    ),
                                    "Avaliações IUCN",
                                    "Registros de avaliações"
                                ),

                                criar_card(
                                    f"{contar_ocorrencias_gbif():,}".replace(
                                        ",",
                                        "."
                                    ),
                                    "Ocorrências GBIF",
                                    "Registros de ocorrência"
                                ),

                                criar_card(
                                    f"{contar_pans():,}".replace(
                                        ",",
                                        "."
                                    ),
                                    "PANs",
                                    "Planos de Ação Nacional"
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
                    "BIODATA · Projeto de integração e análise de "
                    "dados sobre biodiversidade"
                )
            ]
        ),
    ]
)


# ============================================================
# LAYOUT PRINCIPAL
# ============================================================

app.layout = html.Div(
    [
        dcc.Location(
            id="url",
            refresh=False
        ),

        html.Div(
            id="page-content"
        )
    ]
)


# ============================================================
# ROTEAMENTO
# ============================================================

@app.callback(
    Output(
        "page-content",
        "children"
    ),
    Input(
        "url",
        "pathname"
    )
)
def renderizar_pagina(pathname):

    if pathname == "/conservacao":
        return pagina2_layout

    elif pathname == "/brasil":
        return pagina3_layout

    elif pathname == "/distribuicao":
        return pagina4_layout

    elif pathname == "/evolucao":
        return pagina5_layout

    else:
        return pagina1_layout


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=8050
    )