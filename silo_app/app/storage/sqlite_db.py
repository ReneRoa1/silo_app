# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path


from app.config import get_db_path

def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    db_file = str(get_db_path()) if db_path is None else db_path

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            responsavel_tecnico TEXT,
            propriedade TEXT,
            observacoes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            nome_simulacao TEXT,
            dados_entrada_json TEXT NOT NULL,
            resultados_json TEXT NOT NULL,
            alertas_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
    """)

    cursor.execute("PRAGMA table_info(simulations)")
    colunas = [linha[1] for linha in cursor.fetchall()]
    if "nome_simulacao" not in colunas:
        cursor.execute("ALTER TABLE simulations ADD COLUMN nome_simulacao TEXT")

    conn.commit()
    conn.close()