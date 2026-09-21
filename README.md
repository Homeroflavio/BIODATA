# 🌿 BIODATA — Engenharia de Dados aplicada à Biodiversidade

> Pipeline de dados para integração, tratamento, armazenamento e visualização de informações sobre biodiversidade, espécies, conservação, ocorrências geográficas e Planos de Ação Nacional.

**Criador:** Homero Flávio  
**Área:** Engenharia e Análise de Dados  
**Ano:** 2026  
**Status:** Em desenvolvimento / implantação em nuvem

---

## <img width="1344" height="600" alt="image" src="https://github.com/user-attachments/assets/a9587f67-4826-4fe8-ba2a-cca04e7da1c3" />

  


<img width="1347" height="601" alt="image" src="https://github.com/user-attachments/assets/e9cd32a3-9979-4ce9-b032-b296117373e6" />


### 🔗 Dashboard

**Link do dashboard:** https://biodata-wlc4.onrender.com/


---

## 🛫 Apache Airflow

<img width="1366" height="603" alt="image" src="https://github.com/user-attachments/assets/db098869-256b-45c3-a123-d1bd5e1110d8" />


---

# 1. Sobre o projeto

O **Biodata** é um projeto de Engenharia de Dados desenvolvido para integrar diferentes fontes de dados relacionadas à biodiversidade e transformá-las em uma estrutura organizada para análise.

A solução combina **ETL, APIs REST, Python, Pandas, PostgreSQL, Docker, Apache Airflow e Plotly Dash**, criando um fluxo completo desde a coleta de dados brutos até o armazenamento analítico e a visualização.

O projeto demonstra:

- extração de fontes externas;
- armazenamento de dados brutos;
- limpeza e padronização;
- transformação para estruturas analíticas;
- modelagem relacional;
- carga no PostgreSQL;
- orquestração com Airflow;
- containerização com Docker;
- banco PostgreSQL em nuvem;
- dashboard interativo.

# 2. Fontes de dados

### GBIF — Global Biodiversity Information Facility
Fornece registros de ocorrência de espécies e informações geográficas, utilizados em análises de localização, distribuição e evolução temporal.

### IUCN — International Union for Conservation of Nature
Fornece avaliações e categorias relacionadas ao estado de conservação das espécies.

### ICMBio
Fornece informações relacionadas à avaliação e conservação de espécies no Brasil.

### PAN — Planos de Ação Nacional
Representa planos e ações voltados à conservação de espécies e grupos prioritários.

# 3. Arquitetura

```text
GBIF ─────┐
IUCN ─────┤
ICMBio ───┼──> EXTRACT / BRONZE
PAN ──────┘          │
                     ▼
               TRANSFORM / PRATA
                     │
                     ▼
                 LOAD / OURO
                     │
                     ▼
              PostgreSQL / Neon
                     │
                     ▼
                SQL / Queries
                     │
                     ▼
                Plotly Dash
                     │
                     ▼
                 Dashboard
```

O **Apache Airflow** atua como camada de orquestração, controlando a ordem e execução das tarefas.

# 4. Camadas Bronze, Prata e Ouro

**Bronze:** dados coletados das fontes externas, preservados em formato bruto.

**Prata:** limpeza, padronização, conversão de tipos, tratamento de valores ausentes, normalização e preparação para integração.

**Ouro:** dados preparados para consumo analítico, organizados em dimensões e fatos no PostgreSQL.

# 5. Processo ETL

## Extract
Scripts independentes realizam a coleta:

```text
extract/
├── extract_gbif.py
├── extract_iucn.py
├── extract_icmbio.py
└── extract_pan.py
```

## Transform
Os dados são tratados e padronizados com Python/Pandas. O processo contempla limpeza, conversão de tipos, tratamento de ausências, organização das dimensões e fatos e uma transformação final de integração.

## Load
Os dados transformados são carregados no PostgreSQL para consumo analítico pelo dashboard.

# 6. Banco de dados

O banco final utiliza **PostgreSQL** e possui estrutura dimensional/relacional, incluindo:

```text
dim_categoria_risco
dim_especie
dim_local
dim_pan
especie_destaque

fato_avaliacao_icmbio
fato_avaliacao_iucn
fato_ocorrencia_gbif

pan_bioma
pan_especie
pan_estado
```

A tabela `especie_destaque` foi adicionada posteriormente para controlar uma seleção curada de espécies apresentadas na aplicação.

A tabela `fato_ocorrencia_gbif` inclui dados como latitude, longitude, data de observação, categoria IUCN e `ano_observacao`.

# 7. Dashboard

O dashboard utiliza **Plotly Dash** e possui páginas para:

- Sobre o projeto;
- Cenário de conservação;
- Brasil;
- Distribuição;
- Evolução;
- PANs;
- Espécies em destaque.

A aplicação utiliza consultas SQL para gerar indicadores, análises temporais, análises geográficas e detalhes de espécies.

# 8. Apache Airflow

A DAG principal chama-se:

```text
biodata_etl
```

O fluxo organiza:

```text
EXTRACT
 ├── GBIF
 ├── IUCN
 ├── ICMBio
 └── PAN

TRANSFORM
 ├── GBIF
 ├── enriquecimento GBIF
 ├── IUCN
 ├── ICMBio
 ├── PAN
 └── transformação final

LOAD
 └── PostgreSQL

PÓS-LOAD
 └── espécies em destaque
```

As dependências garantem que as transformações necessárias sejam concluídas antes da transformação final e da carga.

# 9. Docker

O ambiente do Airflow é executado com **Docker e Docker Compose**.

A composição possui serviços para Airflow, Scheduler, DAG Processor e o banco de metadados do Airflow.

O Docker fornece um ambiente reproduzível e reduz problemas de configuração e dependências.

# 10. Migração para a nuvem

Durante o desenvolvimento, o PostgreSQL foi executado localmente. Após a validação, o banco foi migrado para **Neon PostgreSQL**.

A escolha manteve PostgreSQL como tecnologia principal e permitiu separar o banco da máquina de desenvolvimento.

Arquitetura de implantação:

```text
GitHub
   │
   ▼
Render
   │
   ▼
Dash / Plotly
   │
   ▼
Neon PostgreSQL
```

As credenciais são fornecidas por variáveis de ambiente.

# 11. Desafios e soluções

### Diferenças entre fontes
Cada fonte possui estrutura, nomenclatura e formato próprios. A solução foi separar a extração por fonte e realizar a padronização na etapa de transformação.

### Qualidade dos dados
Foram necessários tratamentos para valores ausentes, tipos, nomenclaturas, datas, coordenadas e possíveis duplicidades.

### Datas
A manipulação de datas apresentou dificuldades nos gráficos. Como a análise temporal era predominantemente anual, foi utilizado o campo `ano_observacao`, simplificando as consultas e visualizações.

### Ambiente Oracle
Durante o desenvolvimento foram encontrados desafios relacionados ao ambiente Oracle, incluindo diferenças de configuração/conexão e compatibilidade em relação ao PostgreSQL. A consolidação do banco analítico em PostgreSQL simplificou a aplicação e manteve o projeto alinhado ao modelo relacional utilizado.

### APIs
As fontes possuem comportamentos e limitações diferentes. A separação dos extratores permite tratar cada API individualmente.

### Dados sensíveis
Alguns registros de biodiversidade podem ter restrições relacionadas à localização. Portanto, ausência de uma localização não deve ser interpretada automaticamente como ausência da espécie.

# 12. Stack tecnológica

| Tecnologia | Uso |
|---|---|
| Python | Linguagem principal |
| Pandas | Tratamento e transformação |
| SQL | Consultas e análise |
| PostgreSQL | Banco relacional |
| Neon | PostgreSQL em nuvem |
| Apache Airflow | Orquestração |
| Docker | Containerização |
| Docker Compose | Ambiente dos containers |
| Plotly Dash | Dashboard |
| Plotly | Visualizações |
| Psycopg2 | Conexão PostgreSQL |
| Git / GitHub | Versionamento |

# 13. Estrutura

```text
Biodata/
├── dags/
├── extract/
├── transform/
├── load/
├── sql/
├── dash/
│   ├── app.py
│   ├── database.py
│   ├── queries.py
│   ├── pagina2.py
│   ├── pagina3.py
│   ├── pagina4.py
│   ├── pagina5.py
│   ├── pagina6.py
│   ├── pagina7.py
│   └── assets/
├── dados_brutos/
├── dados_transformados/
├── dados_finais/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

# 14. Segurança

O `.env` **não deve ser enviado ao GitHub**.

Variáveis como:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
DB_SSLMODE
IUCN_API_KEY
```

devem permanecer protegidas.

Em produção, as variáveis devem ser configuradas na plataforma de hospedagem.

# 15. Execução local

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Dashboard:

```bash
cd dash
python app.py
```

Airflow:

```bash
docker compose up -d
docker compose ps
```

# 16. Estado atual

O banco PostgreSQL já foi migrado para o **Neon** e o dashboard foi validado localmente utilizando a conexão com o banco em nuvem.

A próxima etapa de infraestrutura é publicar o Dash no **Render**.

O Airflow continua sendo utilizado no ambiente atual para orquestração da pipeline. Uma evolução futura poderá hospedar também o Airflow para permitir atualizações automáticas sem depender do computador local.

# 17. Melhorias futuras

- Hospedagem remota do Airflow;
- atualização automática;
- testes automatizados;
- validações de qualidade dos dados;
- monitoramento;
- logs estruturados;
- alertas de falha;
- observabilidade;
- novas fontes de biodiversidade;
- evolução para Data Lake/Lakehouse quando houver justificativa técnica.

# 18. Autor

**Homero Flávio**  
Estudante de Análise e Desenvolvimento de Sistemas, com foco em Engenharia e Análise de Dados.

**GitHub:** `COLE AQUI O LINK`  
**Dashboard:** `COLE AQUI O LINK DO RENDER`

---

⭐ Se este projeto for útil, considere deixar uma estrela no repositório.
