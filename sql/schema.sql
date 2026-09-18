-- ============================================================
-- BIODATA — Schema do banco PostgreSQL
-- Projeto de portfólio: dados de conservação de espécies
-- Fontes: GBIF, IUCN Red List, ICMBio (IPT + PAN/dados.gov.br)
-- ============================================================


-- ============================================================
-- DIMENSÕES
-- ============================================================

-- A "ficha" central de cada espécie. Todas as outras tabelas
-- de fato apontam pra cá via especie_id.
CREATE TABLE dim_especie (
    id SERIAL PRIMARY KEY,
    nome_cientifico VARCHAR(200) UNIQUE NOT NULL,  -- usar "species" (GBIF) / "scientificNameAuthorship" (ICMBio)
    nome_popular VARCHAR(200),
	reino VARCHAR(50),
    filo VARCHAR(50),
    classe VARCHAR(100),
    ordem VARCHAR(100),
    familia VARCHAR(100),
    genero VARCHAR(100),
    grupo_taxonomico VARCHAR(50)   -- agrupamento simplificado p/ gráficos (ex: "aves", "anfíbios")
);


-- Localização geográfica das ocorrências (GBIF). País/estado
-- em vez de bioma, porque a GBIF não fornece bioma nativamente.
CREATE TABLE dim_local (
    id SERIAL PRIMARY KEY,
    pais VARCHAR(100),
    estado_provincia VARCHAR(100),
    continente VARCHAR(50)
);

-- Tabela de apoio pra tratar os dois sistemas de categoria de
-- risco da IUCN (legado pré-1994 vs moderno) numa escala comum.
CREATE TABLE dim_categoria_risco (
    codigo VARCHAR(5) PRIMARY KEY,     -- ex: 'VU', 'EN', 'V', 'E'
    nome VARCHAR(50),                  -- ex: 'Vulnerable'
    sistema VARCHAR(20),               -- 'legado' ou 'moderno'
    peso_numerico INT                  -- escala 0-6, permite calcular tendência ao longo do tempo
);

-- Um Plano de Ação Nacional (PAN) do ICMBio. Fonte: CSV/XLSX
-- do dados.gov.br (aba "tabelaPanDados").
CREATE TABLE dim_pan (
    id_pan VARCHAR(20) PRIMARY KEY,
    nome VARCHAR(200),
    nome_completo VARCHAR(300),
    abrangencia_taxonomica VARCHAR(20),   -- Monoespecífico / Intraclasse / Multiclasse
    abrangencia_geografica VARCHAR(50),   -- Bioma / Nacional / Bacia / Ecossistema / Específico
    ciclo VARCHAR(20),                    -- normalizar "3 ciclo" -> "3º ciclo" no ETL
    status VARCHAR(20),                   -- Finalizado / Em execução / Previsto / Elaborado
    data_inicio DATE,
    data_fim DATE,
    ano_inicio INT,
    ano_fim INT,
    status_legal VARCHAR(100),
    site VARCHAR(300)
);


-- ============================================================
-- FATOS (eventos que se acumulam / se repetem ao longo do tempo)
-- ============================================================

-- Uma avaliação de risco feita pela IUCN, em determinado ano,
-- pra determinada espécie. Uma espécie pode ter várias linhas
-- aqui (uma por avaliação histórica).
CREATE TABLE fato_avaliacao_iucn (
    id SERIAL PRIMARY KEY,
    assessment_id BIGINT UNIQUE NOT NULL,
    especie_id INT REFERENCES dim_especie(id),
    ano_publicacao INT NOT NULL,
    data_avaliacao DATE,
    categoria_risco_codigo VARCHAR(5) REFERENCES dim_categoria_risco(codigo),
    e_avaliacao_atual BOOLEAN,          -- campo "latest" da API
    possivelmente_extinta BOOLEAN,
    criterio VARCHAR(50),               -- pode ser NULL em avaliações antigas (pré-1994)
    escopo VARCHAR(50)                  -- "Global" na maioria dos casos
);

-- Se a espécie está (ou não) na Lista de Espécies Ameaçadas da
-- Fauna do ICMBio. Fonte: IPT (lista_vermelha). OBS: essa fonte
-- não traz o grau de ameaça (VU/EN/CR) — só o fato de constar
-- na lista. Grau detalhado fica como limitação conhecida /
-- trabalho futuro (exigiria fichas individuais do SALVE).
CREATE TABLE fato_avaliacao_icmbio (
    id SERIAL PRIMARY KEY,
    especie_id INT REFERENCES dim_especie(id),
    taxon_id_icmbio BIGINT,             -- id/taxonID original do IPT, p/ rastreabilidade
    consta_lista_ameacada BOOLEAN DEFAULT TRUE,
    dado_sensivel BOOLEAN               -- flag "in_sensivel" do vernacularName
);

-- Uma ocorrência (avistamento/registro) da GBIF.
CREATE TABLE fato_ocorrencia_gbif (
    id SERIAL PRIMARY KEY,
    gbif_id BIGINT UNIQUE,              -- evita duplicar se o ETL rodar de novo
    especie_id INT REFERENCES dim_especie(id),
    local_id INT REFERENCES dim_local(id),
    latitude NUMERIC,
    longitude NUMERIC,
    incerteza_metros NUMERIC,           -- fica alto de propósito p/ espécies muito ameaçadas
    categoria_iucn VARCHAR(5),          -- bônus: já vem embutido na resposta da GBIF
    data_observacao DATE,
    ano_observacao INT,
    tem_alerta_qualidade BOOLEAN DEFAULT FALSE   -- baseado no campo "issues"
);


-- ============================================================
-- TABELAS PONTE (relações muitos-para-muitos)
-- ============================================================

-- Liga espécies aos PANs que as cobrem. Fonte: ODS, aba
-- "tabelaPanEspecies". Uma espécie pode estar em mais de um
-- PAN (ex: ciclos diferentes do mesmo plano).
CREATE TABLE pan_especie (
    id_pan VARCHAR(20) REFERENCES dim_pan(id_pan),
    especie_id INT REFERENCES dim_especie(id),
    PRIMARY KEY (id_pan, especie_id)
);

-- Liga PANs aos biomas que abrangem. Fonte: ODS, aba
-- "tabelaPanBiomas".
CREATE TABLE pan_bioma (
    id_pan VARCHAR(20) REFERENCES dim_pan(id_pan),
    bioma VARCHAR(50),
    PRIMARY KEY (id_pan, bioma)
);

-- Liga PANs aos estados brasileiros que abrangem. Fonte: ODS,
-- aba "tabelaPanEstados".
CREATE TABLE pan_estado (
    id_pan VARCHAR(20) REFERENCES dim_pan(id_pan),
    sigla_estado VARCHAR(2),
    PRIMARY KEY (id_pan, sigla_estado)
);

CREATE TABLE especie_destaque (
    especie_id INTEGER PRIMARY KEY,
    CONSTRAINT fk_especie_destaque
        FOREIGN KEY (especie_id)
        REFERENCES dim_especie(id)
        ON DELETE CASCADE
);