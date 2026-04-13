# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import Any

from app.domain.models import Projeto, EntradaDimensionamento, ResultadoDimensionamento
from app.storage.sqlite_db import get_connection
from app.config import get_db_path


class ProjectRepository:
    def __init__(self) -> None:
        self.db_path = str(get_db_path())

    def criar_projeto(self, projeto: Projeto) -> int:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO projects (
                nome, responsavel_tecnico, propriedade, observacoes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                projeto.nome,
                projeto.responsavel_tecnico,
                projeto.propriedade,
                projeto.observacoes,
                projeto.created_at,
                projeto.updated_at,
            ),
        )

        conn.commit()
        project_id = cursor.lastrowid
        conn.close()
        return int(project_id)

    def atualizar_projeto(
        self,
        project_id: int,
        nome: str,
        responsavel_tecnico: str,
        propriedade: str,
        observacoes: str,
        updated_at: str,
    ) -> None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE projects
            SET nome = ?, responsavel_tecnico = ?, propriedade = ?, observacoes = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                nome,
                responsavel_tecnico,
                propriedade,
                observacoes,
                updated_at,
                project_id,
            ),
        )

        conn.commit()
        conn.close()

    def listar_projetos(self) -> list[dict[str, Any]]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
        rows = cursor.fetchall()

        conn.close()
        return [dict(row) for row in rows]

    def buscar_projeto_por_id(self, project_id: int) -> dict[str, Any] | None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()

        conn.close()
        return dict(row) if row else None

    def buscar_projeto_por_nome(self, nome: str) -> dict[str, Any] | None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM projects WHERE nome = ? ORDER BY id DESC LIMIT 1",
            (nome,),
        )
        row = cursor.fetchone()

        conn.close()
        return dict(row) if row else None

    def salvar_simulacao(
        self,
        project_id: int,
        entrada: EntradaDimensionamento,
        resultado: ResultadoDimensionamento,
        nome_simulacao: str | None = None,
    ) -> int:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO simulations (
                project_id, nome_simulacao, dados_entrada_json, resultados_json, alertas_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                nome_simulacao,
                json.dumps(entrada.to_dict(), ensure_ascii=False),
                json.dumps(resultado.to_dict(), ensure_ascii=False),
                json.dumps(resultado.alertas, ensure_ascii=False),
                resultado.data_hora_simulacao,
            ),
        )

        cursor.execute(
            "UPDATE projects SET updated_at = ? WHERE id = ?",
            (resultado.data_hora_simulacao, project_id),
        )

        conn.commit()
        simulation_id = cursor.lastrowid
        conn.close()
        return int(simulation_id)

    def listar_simulacoes_do_projeto(self, project_id: int) -> list[dict[str, Any]]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, project_id, nome_simulacao, dados_entrada_json, resultados_json, alertas_json, created_at
            FROM simulations
            WHERE project_id = ?
            ORDER BY id DESC
            """,
            (project_id,),
        )
        rows = cursor.fetchall()

        conn.close()
        return [dict(row) for row in rows]

    def buscar_simulacao_por_id(self, simulation_id: int) -> dict[str, Any] | None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, project_id, nome_simulacao, dados_entrada_json, resultados_json, alertas_json, created_at
            FROM simulations
            WHERE id = ?
            """,
            (simulation_id,),
        )
        row = cursor.fetchone()

        conn.close()
        return dict(row) if row else None