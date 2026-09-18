import os

import psycopg2
from dotenv import load_dotenv


# Carrega o .env que está dentro da pasta dash
load_dotenv()


def get_connection():
    """
    Cria uma conexão com o banco BIODATA.
    """

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "require"),
    )
    
if __name__ == "__main__":
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM dim_especie;")
    resultado = cursor.fetchone()[0]

    print(f"Espécies no banco: {resultado}")

    cursor.close()
    conexao.close()