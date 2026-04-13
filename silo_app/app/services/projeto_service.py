# -*- coding: utf-8 -*-
from __future__ import annotations

import json

from app.domain.models import Projeto, EntradaDimensionamento, ResultadoDimensionamento
from app.storage.project_repository import ProjectRepository


class ProjetoService:
    def __init__(self, repository: ProjectRepository | None = None) -> None:
        self.repository = repository or ProjectRepository()

    def criar_projeto(
        self,
        nome: str,
        responsavel_tecnico: str = "",
        propriedade: str = "",
        observacoes: str = "",
    ) -> int:
        projeto = Projeto(
            nome=nome,
            responsavel_tecnico=responsavel_tecnico,
            propriedade=propriedade,
            observacoes=observacoes,
        )
        return self.repository.criar_projeto(projeto)

    def obter_ou_criar_projeto(
        self,
        nome: str,
        responsavel_tecnico: str = "",
        propriedade: str = "",
        observacoes: str = "",
    ) -> int:
        existente = self.repository.buscar_projeto_por_nome(nome)

        if existente:
            self.repository.atualizar_projeto(
                project_id=int(existente["id"]),
                nome=nome,
                responsavel_tecnico=responsavel_tecnico,
                propriedade=propriedade,
                observacoes=observacoes,
                updated_at=Projeto(nome=nome).updated_at,
            )
            return int(existente["id"])

        return self.criar_projeto(
            nome=nome,
            responsavel_tecnico=responsavel_tecnico,
            propriedade=propriedade,
            observacoes=observacoes,
        )

    def listar_projetos(self):
        return self.repository.listar_projetos()

    def buscar_projeto_por_id(self, project_id: int):
        return self.repository.buscar_projeto_por_id(project_id)

    def salvar_simulacao(
        self,
        project_id: int,
        entrada: EntradaDimensionamento,
        resultado: ResultadoDimensionamento,
        nome_simulacao: str | None = None,
    ) -> int:
        return self.repository.salvar_simulacao(
            project_id=project_id,
            entrada=entrada,
            resultado=resultado,
            nome_simulacao=nome_simulacao,
        )

    def listar_simulacoes_do_projeto(self, project_id: int):
        return self.repository.listar_simulacoes_do_projeto(project_id)

    def buscar_simulacao_por_id(self, simulation_id: int):
        return self.repository.buscar_simulacao_por_id(simulation_id)

    def carregar_entrada_da_simulacao(self, simulation_id: int) -> dict | None:
        simulacao = self.buscar_simulacao_por_id(simulation_id)
        if not simulacao:
            return None
        return json.loads(simulacao["dados_entrada_json"])

    def carregar_resultado_da_simulacao(self, simulation_id: int) -> dict | None:
        simulacao = self.buscar_simulacao_por_id(simulation_id)
        if not simulacao:
            return None
        return json.loads(simulacao["resultados_json"])

    def carregar_dados_do_projeto(self, project_id: int) -> dict | None:
        projeto = self.buscar_projeto_por_id(project_id)
        if not projeto:
            return None
        return projeto