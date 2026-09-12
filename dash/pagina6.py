import os

import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ============================================================
# CONEXÃO
# ============================================================

def conectar_banco():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# ============================================================
# CONSULTAS
# ============================================================

def consultar_dataframe(sql):
    conexao = conectar_banco()

    try:
        return pd.read_sql_query(sql, conexao)
    finally:
        conexao.close()


# ------------------------------------------------------------
# DIMENSÃO DOS PANs
# ------------------------------------------------------------

df_pan = consultar_dataframe(
    """
    SELECT
        id_pan,
        nome,
        nome_completo,
        abrangencia_taxonomica,
        abrangencia_geografica,
        ciclo,
        status,
        ano_inicio,
        ano_fim
    FROM dim_pan
    ORDER BY nome
    """
)


# ------------------------------------------------------------
# RELAÇÃO PAN × ESPÉCIE
# ------------------------------------------------------------

df_pan_especie = consultar_dataframe(
    """
    SELECT
        pe.id_pan,
        pe.especie_id
    FROM pan_especie pe
    """
)


# ------------------------------------------------------------
# RELAÇÃO PAN × BIOMA
# ------------------------------------------------------------

df_pan_bioma = consultar_dataframe(
    """
    SELECT
        id_pan,
        bioma
    FROM pan_bioma
    """
)


# ------------------------------------------------------------
# RELAÇÃO PAN × ESTADO
# ------------------------------------------------------------

df_pan_estado = consultar_dataframe(
    """
    SELECT
        id_pan,
        sigla_estado
    FROM pan_estado
    """
)


# ============================================================
# INDICADORES
# ============================================================

total_pans = len(df_pan)

total_especies = int(
    df_pan_especie["especie_id"].nunique()
)

total_biomas = int(
    df_pan_bioma["bioma"].nunique()
)

total_estados = int(
    df_pan_estado["sigla_estado"].nunique()
)


# ============================================================
# SITUAÇÃO DOS PANs
# ============================================================

df_status = (
    df_pan
    .groupby("status")
    .size()
    .reset_index(name="quantidade")
)

ordem_status = [
    "Em execução",
    "Finalizado",
    "Elaborado",
    "Previsto"
]

df_status["ordem"] = df_status["status"].apply(
    lambda x: (
        ordem_status.index(x)
        if x in ordem_status
        else len(ordem_status)
    )
)

df_status = (
    df_status
    .sort_values("ordem")
    .drop(columns="ordem")
)


# ============================================================
# PANs COM MAIS ESPÉCIES
# ============================================================

df_top_pans = (
    df_pan_especie
    .groupby("id_pan")
    .agg(
        quantidade_especies=("especie_id", "nunique")
    )
    .reset_index()
    .merge(
        df_pan[["id_pan", "nome"]],
        on="id_pan",
        how="left"
    )
    .sort_values(
        "quantidade_especies",
        ascending=False
    )
    .head(10)
)

df_top_pans = df_top_pans.sort_values(
    "quantidade_especies",
    ascending=True
)


# ============================================================
# PANs POR BIOMA
# ============================================================

df_biomas = (
    df_pan_bioma
    .groupby("bioma")
    .size()
    .reset_index(name="quantidade")
    .sort_values(
        "quantidade",
        ascending=True
    )
)


# ============================================================
# PANs POR ESTADO
# ============================================================

df_estados = (
    df_pan_estado
    .groupby("sigla_estado")
    .size()
    .reset_index(name="quantidade")
    .sort_values(
        "quantidade",
        ascending=True
    )
)


# ============================================================
# GRÁFICO — SITUAÇÃO DOS PANs
# ============================================================

fig_status = go.Figure()

fig_status.add_trace(
    go.Bar(
        x=df_status["quantidade"],
        y=df_status["status"],
        orientation="h",
        text=df_status["quantidade"],
        textposition="outside",
        marker=dict(
            color="#3F7D5E"
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "PANs: %{x}"
            "<extra></extra>"
        )
    )
)

fig_status.update_layout(
    template="plotly_white",
    height=360,
    margin=dict(
        l=20,
        r=55,
        t=55,
        b=30
    ),
    title="Situação atual dos PANs",
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Arial",
        color="#24352D"
    ),
    xaxis=dict(
        title="Quantidade de PANs",
        showgrid=True,
        gridcolor="#E8EDEB",
        zeroline=False
    ),
    yaxis=dict(
        title="",
        showgrid=False
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
# GRÁFICO — TOP PANs
# ============================================================

fig_top_pans = go.Figure()

fig_top_pans.add_trace(
    go.Bar(
        x=df_top_pans["quantidade_especies"],
        y=df_top_pans["nome"],
        orientation="h",
        text=df_top_pans["quantidade_especies"],
        textposition="outside",
        marker=dict(
            color="#58756A"
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Espécies contempladas: %{x}"
            "<extra></extra>"
        )
    )
)

fig_top_pans.update_layout(
    template="plotly_white",
    height=520,
    margin=dict(
        l=20,
        r=60,
        t=55,
        b=30
    ),
    title=(
        "PANs com maior número de espécies contempladas"
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Arial",
        color="#24352D"
    ),
    xaxis=dict(
        title="Espécies contempladas",
        showgrid=True,
        gridcolor="#E8EDEB",
        zeroline=False
    ),
    yaxis=dict(
        title="",
        showgrid=False
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
# GRÁFICO — BIOMAS
# ============================================================

fig_biomas = go.Figure()

fig_biomas.add_trace(
    go.Bar(
        x=df_biomas["quantidade"],
        y=df_biomas["bioma"],
        orientation="h",
        text=df_biomas["quantidade"],
        textposition="outside",
        marker=dict(
            color="#6D9B82"
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "PANs associados: %{x}"
            "<extra></extra>"
        )
    )
)

fig_biomas.update_layout(
    template="plotly_white",
    height=430,
    margin=dict(
        l=20,
        r=55,
        t=55,
        b=30
    ),
    title="Distribuição dos PANs por bioma",
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Arial",
        color="#24352D"
    ),
    xaxis=dict(
        title="Quantidade de PANs",
        showgrid=True,
        gridcolor="#E8EDEB",
        zeroline=False
    ),
    yaxis=dict(
        title="",
        showgrid=False
    ),
    hoverlabel=dict(
        bgcolor="#24352D",
        font=dict(
            color="white"
        ),
        bordercolor="#58756A"
    )
)


# ============================================================
# GRÁFICO — ESTADOS
# ============================================================

fig_estados = go.Figure()

fig_estados.add_trace(
    go.Bar(
        x=df_estados["quantidade"],
        y=df_estados["sigla_estado"],
        orientation="h",
        text=df_estados["quantidade"],
        textposition="outside",
        marker=dict(
            color="#3F7D5E"
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "PANs associados: %{x}"
            "<extra></extra>"
        )
    )
)

fig_estados.update_layout(
    template="plotly_white",
    height=650,
    margin=dict(
        l=20,
        r=55,
        t=55,
        b=30
    ),
    title="Estados envolvidos pelos PANs",
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Arial",
        color="#24352D"
    ),
    xaxis=dict(
        title="Quantidade de PANs",
        showgrid=True,
        gridcolor="#E8EDEB",
        zeroline=False
    ),
    yaxis=dict(
        title="",
        showgrid=False
    ),
    hoverlabel=dict(
        bgcolor="#24352D",
        font=dict(
            color="white"
        ),
        bordercolor="#58756A"
    )
)


# ============================================================
# FUNÇÃO — DETALHES DO PAN
# ============================================================

def obter_detalhes_pan(id_pan):

    pan = df_pan[
        df_pan["id_pan"] == id_pan
    ]

    if pan.empty:
        return (
            "Nenhum PAN selecionado.",
            "",
            "",
            ""
        )

    registro = pan.iloc[0]

    nome = registro["nome"]

    nome_completo = registro["nome_completo"]

    status = registro["status"]

    taxonomia = registro["abrangencia_taxonomica"]

    geografia = registro["abrangencia_geografica"]

    ciclo = registro["ciclo"]

    ano_inicio = registro["ano_inicio"]

    ano_fim = registro["ano_fim"]

    especies = int(
        df_pan_especie[
            df_pan_especie["id_pan"] == id_pan
        ]["especie_id"].nunique()
    )

    biomas = (
        df_pan_bioma[
            df_pan_bioma["id_pan"] == id_pan
        ]["bioma"]
        .dropna()
        .astype(str)
        .tolist()
    )

    estados = (
        df_pan_estado[
            df_pan_estado["id_pan"] == id_pan
        ]["sigla_estado"]
        .dropna()
        .astype(str)
        .tolist()
    )

    if biomas:
        texto_biomas = ", ".join(biomas)
    else:
        texto_biomas = "Não informado"

    if estados:
        texto_estados = ", ".join(estados)
    else:
        texto_estados = "Não informado"

    periodo = ""

    if pd.notna(ano_inicio):

        periodo = str(int(ano_inicio))

        if pd.notna(ano_fim):
            periodo += f" – {int(ano_fim)}"

    return (
        nome,
        (
            f"{nome_completo}"
            if pd.notna(nome_completo)
            else ""
        ),
        (
            f"{especies} espécies · "
            f"{status} · "
            f"{taxonomia}"
        ),
        (
            f"Biomas: {texto_biomas} | "
            f"Estados: {texto_estados} | "
            f"Ciclo: {ciclo} | "
            f"Período: {periodo or 'Não informado'} | "
            f"Abrangência geográfica: "
            f"{geografia or 'Não informada'}"
        )
    )


# ============================================================
# LAYOUT
# ============================================================

layout = html.Div(
    className="app-container pagina6",
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
                            "Planos de Ação Nacional"
                        ),

                        html.P(
                            "Estratégias de conservação "
                            "voltadas à proteção da "
                            "biodiversidade brasileira."
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
                    className="nav-link active"
                ),

                dcc.Link(
                    "Espécies em destaque",
                    href="/destaques",
                    className="nav-link"
                )

            ]
        ),


        # ====================================================
        # CONTEÚDO
        # ====================================================

        html.Main(
            className="main-content",
            children=[


                # ====================================================
                # 01 — DIMENSÃO
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
                                            "A dimensão dos PANs"
                                        ),

                                        html.P(
                                            "Planos, espécies e "
                                            "territórios representados "
                                            "na base analisada",
                                            className="section-subtitle"
                                        )

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
                                            f"{total_pans:,}".replace(
                                                ",", "."
                                            ),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "PANs analisados",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Planos de Ação Nacional "
                                            "presentes na base",
                                            className="stat-description"
                                        )

                                    ]
                                ),


                                html.Div(
                                    className="stat-card",
                                    children=[

                                        html.Div(
                                            f"{total_especies:,}".replace(
                                                ",", "."
                                            ),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Espécies contempladas",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Espécies relacionadas "
                                            "aos PANs",
                                            className="stat-description"
                                        )

                                    ]
                                ),


                                html.Div(
                                    className="stat-card",
                                    children=[

                                        html.Div(
                                            str(total_biomas),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Biomas",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Biomas associados aos "
                                            "planos analisados",
                                            className="stat-description"
                                        )

                                    ]
                                ),


                                html.Div(
                                    className="stat-card",
                                    children=[

                                        html.Div(
                                            str(total_estados),
                                            className="stat-number"
                                        ),

                                        html.Div(
                                            "Estados e DF",
                                            className="stat-title"
                                        ),

                                        html.Div(
                                            "Unidades federativas "
                                            "envolvidas pelos PANs",
                                            className="stat-description"
                                        )

                                    ]
                                )

                            ]
                        )

                    ]
                ),


                # ====================================================
                # 02 — SITUAÇÃO
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
                                            "Qual é a situação dos PANs?"
                                        ),

                                        html.P(
                                            "Distribuição dos planos "
                                            "segundo seu status",
                                            className="section-subtitle"
                                        )

                                    ]
                                )

                            ]
                        ),


                        html.Div(
                            className="grafico-container",
                            children=[
                                dcc.Graph(
                                    figure=fig_status,
                                    config={
                                        "displayModeBar": False
                                    }
                                )
                            ]
                        ),

                        html.Div(
                            className="context-box",
                            children=[

                                html.P(
                                    [
                                        "Dos ",
                                        html.Strong("117 PANs"),
                                        " analisados, ",
                                        html.Strong("74 estão finalizados"),
                                        " e ",
                                        html.Strong("41 estão em execução"),
                                        ". Os dois registros restantes "
                                        "correspondem a um PAN elaborado "
                                        "e outro previsto."
                                    ]
                                )

                            ]
                        )

                    ]
                ),


                # ====================================================
                # 03 — MAIOR ABRANGÊNCIA
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
                                            "Quais PANs contemplam "
                                            "mais espécies?"
                                        ),

                                        html.P(
                                            "Os dez planos com maior "
                                            "número de espécies relacionadas",
                                            className="section-subtitle"
                                        )

                                    ]
                                )

                            ]
                        ),


                        html.Div(
                            className="grafico-container",
                            children=[
                                dcc.Graph(
                                    figure=fig_top_pans,
                                    config={
                                        "displayModeBar": False
                                    }
                                )
                            ]
                        ),

                        html.Div(
                            className="context-box",
                            children=[

                                html.P(
                                    [
                                        "A abrangência dos planos é "
                                        "heterogênea. Enquanto alguns PANs "
                                        "contemplam dezenas ou centenas "
                                        "de espécies, outros possuem "
                                        "escopo muito mais específico."
                                    ]
                                )

                            ]
                        )

                    ]
                ),


                # ====================================================
                # 04 — BIOMAS
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
                                            "Onde os PANs atuam?"
                                        ),

                                        html.P(
                                            "Distribuição dos planos "
                                            "entre os biomas registrados",
                                            className="section-subtitle"
                                        )

                                    ]
                                )

                            ]
                        ),


                        html.Div(
                            className="grafico-container",
                            children=[
                                dcc.Graph(
                                    figure=fig_biomas,
                                    config={
                                        "displayModeBar": False
                                    }
                                )
                            ]
                        ),

                        html.Div(
                            className="context-box",
                            children=[

                                html.P(
                                    [
                                        "A base reúne ",
                                        html.Strong(
                                            f"{total_biomas} biomas"
                                        ),
                                        " associados aos PANs. "
                                        "Um mesmo plano pode atuar em "
                                        "mais de um bioma, portanto os "
                                        "valores representam associações "
                                        "entre planos e biomas e não "
                                        "categorias mutuamente exclusivas."
                                    ]
                                )

                            ]
                        )

                    ]
                ),


                # ====================================================
                # 05 — ESTADOS
                # ====================================================

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
                                            "Em quais estados os PANs estão presentes?"
                                        ),

                                        html.P(
                                            "Número de planos associados "
                                            "a cada unidade federativa",
                                            className="section-subtitle"
                                        )

                                    ]
                                )

                            ]
                        ),


                        html.Div(
                            className="grafico-container",
                            children=[
                                dcc.Graph(
                                    figure=fig_estados,
                                    config={
                                        "displayModeBar": False
                                    }
                                )
                            ]
                        )

                    ]
                ),


                # ====================================================
                # 06 — EXPLORAÇÃO
                # ====================================================

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
                                            "Explore um Plano de Ação Nacional"
                                        ),

                                        html.P(
                                            "Selecione um PAN para "
                                            "ver sua abrangência",
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
                                    "Plano de Ação Nacional",
                                    className="label-filtro"
                                ),

                                dcc.Dropdown(
                                    id="dropdown-pan",
                                    options=[
                                        {
                                            "label": row["nome"],
                                            "value": row["id_pan"]
                                        }
                                        for _, row in df_pan.iterrows()
                                    ],
                                    placeholder=(
                                        "Selecione um PAN..."
                                    ),
                                    clearable=False
                                )

                            ]
                        ),


                        html.Div(
                            className="pan-detalhes",
                            children=[

                                html.Div(
                                    id="pan-nome",
                                    className="pan-detalhes-nome"
                                ),

                                html.Div(
                                    id="pan-nome-completo",
                                    className="pan-detalhes-completo"
                                ),

                                html.Div(
                                    id="pan-resumo",
                                    className="pan-detalhes-resumo"
                                ),

                                html.Div(
                                    id="pan-contexto",
                                    className="pan-detalhes-contexto"
                                )

                            ]
                        )

                    ]
                ),


                # ====================================================
                # 07 — CONCLUSÃO
                # ====================================================

                html.Section(
                    className="section",
                    children=[

                        html.Div(
                            className="section-heading",
                            children=[

                                html.Div(
                                    "07",
                                    className="section-number"
                                ),

                                html.Div(
                                    children=[

                                        html.H2(
                                            "O que os dados revelam?"
                                        ),

                                        html.P(
                                            "A dimensão territorial "
                                            "e taxonômica dos PANs",
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
                                        "Os PANs apresentam diferentes "
                                        "escalas de atuação. Alguns são "
                                        "direcionados a uma espécie "
                                        "específica, enquanto outros "
                                        "abrangem grupos maiores e "
                                        "diferentes territórios."
                                    ]
                                ),

                                html.P(
                                    [
                                        "Ao relacionar ",
                                        html.Strong(
                                            "espécies, biomas e estados"
                                        ),
                                        ", a base permite enxergar "
                                        "como os esforços de conservação "
                                        "estão distribuídos pelo território "
                                        "brasileiro."
                                    ]
                                ),

                                html.P(
                                    [
                                        "Assim, os PANs funcionam como "
                                        "uma camada de planejamento "
                                        "que conecta a biodiversidade "
                                        "identificada na base às "
                                        "estratégias de conservação."
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
                    "BIODATA · Projeto de integração e análise "
                    "de dados sobre biodiversidade"
                )

            ]
        )

    ]
)


# ============================================================
# CALLBACK — DETALHES DO PAN
# ============================================================

@dash.callback(
    Output(
        "pan-nome",
        "children"
    ),

    Output(
        "pan-nome-completo",
        "children"
    ),

    Output(
        "pan-resumo",
        "children"
    ),

    Output(
        "pan-contexto",
        "children"
    ),

    Input(
        "dropdown-pan",
        "value"
    )
)
def atualizar_pan(id_pan):

    if id_pan is None:
        return (
            "Selecione um PAN acima.",
            "",
            "",
            ""
        )

    return obter_detalhes_pan(id_pan)