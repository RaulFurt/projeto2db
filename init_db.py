"""Cria (ou recria) as tabelas e os dados executando os scripts da pasta sql/.

Uso:
    python init_db.py

A conexão vem da variável de ambiente DATABASE_URL; o padrão é o banco do
docker-compose.yml (postgresql://patrimonio:patrimonio@localhost:5432/patrimonio).
"""
import os
from pathlib import Path

import psycopg

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://patrimonio:patrimonio@localhost:5432/patrimonio")
SCRIPTS = ["01_schema.sql", "02_povoamento.sql"]


def init_db() -> None:
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        for name in SCRIPTS:
            conn.execute((BASE_DIR / "sql" / name).read_text(encoding="utf-8"))
            print(f"  ok  sql/{name}")


if __name__ == "__main__":
    print(f"Criando o banco em {DATABASE_URL.rsplit('@', 1)[-1]} ...")
    init_db()
    with psycopg.connect(DATABASE_URL) as conn:
        for table in ["categoria", "setor", "fornecedor", "fornecedor_telefone",
                      "funcionario", "equipamento", "acautelamento", "manutencao"]:
            total = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table:<20} {total:>3} linhas")
