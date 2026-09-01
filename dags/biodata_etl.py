from datetime import datetime
import os
import subprocess
from pathlib import Path

import psycopg2

from airflow.sdk import dag, task


# ============================================================
# CAMINHOS DENTRO DO CONTAINER AIRFLOW
# ============================================================

BASE_DIR = Path("/opt/airflow")

EXTRACT_DIR = BASE_DIR / "extract"
TRANSFORM_DIR = BASE_DIR / "transform"
LOAD_DIR = BASE_DIR / "load"
SQL_DIR = BASE_DIR / "sql"


# ============================================================
# FUNÇÃO AUXILIAR — EXECUTAR SCRIPT PYTHON
# ============================================================

def executar_script(caminho_script):
    """
    Executa um script Python dentro do container Airflow.
    """

    print(f"\nExecutando: {caminho_script}")

    ambiente = os.environ.copy()

    # Dentro do Docker, localhost aponta para o próprio container.
    # Como o PostgreSQL do Biodata está rodando no Windows,
    # usamos host.docker.internal para acessá-lo.
    ambiente["DB_HOST"] = "host.docker.internal"

    resultado = subprocess.run(
        ["python", str(caminho_script)],
        cwd=str(BASE_DIR),
        env=ambiente,
        capture_output=True,
        text=True
    )

    print(resultado.stdout)

    if resultado.stderr:
        print(resultado.stderr)

    if resultado.returncode != 0:
        raise RuntimeError(
            f"Erro ao executar {caminho_script}"
        )

    print(f"Concluído: {caminho_script}")


# ============================================================
# DAG
# ============================================================

@dag(
    dag_id="biodata_etl",
    start_date=datetime(2026, 8, 30),
    schedule=None,
    catchup=False,
    tags=["biodata", "etl"],
)
def biodata_etl():

    # ========================================================
    # EXTRACT
    # ========================================================

    @task
    def extract_gbif():
        executar_script(
            EXTRACT_DIR / "extract_gbif.py"
        )

    @task
    def extract_iucn():
        executar_script(
            EXTRACT_DIR / "extract_iucn.py"
        )

    @task
    def extract_icmbio():
        executar_script(
            EXTRACT_DIR / "extract_icmbio.py"
        )

    @task
    def extract_pan():
        executar_script(
            EXTRACT_DIR / "extract_pan.py"
        )

    # ========================================================
    # TRANSFORM
    # ========================================================

    @task
    def transform_gbif():
        executar_script(
            TRANSFORM_DIR / "transform_gbif.py"
        )

    @task
    def enrich_nome_popular_gbif():
        executar_script(
            TRANSFORM_DIR / "enrich_nome_popular_gbif.py"
        )

    @task
    def transform_iucn():
        executar_script(
            TRANSFORM_DIR / "transform_iucn.py"
        )

    @task
    def transform_icmbio():
        executar_script(
            TRANSFORM_DIR / "transform_icmbio.py"
        )

    @task
    def transform_pan():
        executar_script(
            TRANSFORM_DIR / "transform_pan.py"
        )

    @task
    def transform_final():
        executar_script(
            TRANSFORM_DIR / "transform_final.py"
        )

    # ========================================================
    # LOAD
    # ========================================================

    @task
    def load_postgresql():
        executar_script(
            LOAD_DIR / "postgresload.py"
        )

    # ========================================================
    # ESPÉCIES EM DESTAQUE
    # ========================================================

    @task
    def carregar_especies_destaque():

        print("\nCarregando espécies em destaque...")

        caminho_sql = SQL_DIR / "especie_destaque.sql"

        if not caminho_sql.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {caminho_sql}"
            )

        with open(
            caminho_sql,
            "r",
            encoding="utf-8"
        ) as arquivo:
            sql = arquivo.read()

        conexao = None
        cursor = None

        try:

            conexao = psycopg2.connect(
                host="host.docker.internal",
                port=os.getenv("DB_PORT"),
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )

            cursor = conexao.cursor()

            cursor.execute(sql)

            conexao.commit()

            print(
                "Espécies em destaque carregadas com sucesso."
            )

        except Exception:

            if conexao:
                conexao.rollback()

            raise

        finally:

            if cursor:
                cursor.close()

            if conexao:
                conexao.close()

    # ========================================================
    # INSTANCIAR TAREFAS
    # ========================================================

    gbif = extract_gbif()
    iucn = extract_iucn()
    icmbio = extract_icmbio()
    pan = extract_pan()

    trans_gbif = transform_gbif()
    enriquecer_gbif = enrich_nome_popular_gbif()

    trans_iucn = transform_iucn()
    trans_icmbio = transform_icmbio()
    trans_pan = transform_pan()

    final = transform_final()

    load = load_postgresql()

    destaque = carregar_especies_destaque()

    # ========================================================
    # DEPENDÊNCIAS
    # ========================================================

    # GBIF
    gbif >> trans_gbif
    trans_gbif >> enriquecer_gbif

    # IUCN
    iucn >> trans_iucn

    # ICMBio
    icmbio >> trans_icmbio

    # PAN
    pan >> trans_pan

    # Todos os transforms precisam terminar
    # antes da transformação final.
    [
        enriquecer_gbif,
        trans_iucn,
        trans_icmbio,
        trans_pan
    ] >> final

    # Transformação final → Load
    final >> load

    # Load → espécies em destaque
    load >> destaque


# ============================================================
# REGISTRO DA DAG
# ============================================================

biodata_etl()