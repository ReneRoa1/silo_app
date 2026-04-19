# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import Any

import streamlit as st

from app.domain.models import EntradaDimensionamento, ResultadoDimensionamento
from app.services.dimensionamento_service import executar_dimensionamento
from app.services.projeto_service import ProjetoService

_TTL_QUERY = 60
_TTL_CALC = 60 * 60


def _hash_entrada(entrada: EntradaDimensionamento) -> str:
    return json.dumps(entrada.to_dict(), sort_keys=True, ensure_ascii=False)


@st.cache_data(
    show_spinner=False,
    ttl=_TTL_CALC,
    hash_funcs={EntradaDimensionamento: _hash_entrada},
)
def executar_dimensionamento_cached(entrada: EntradaDimensionamento) -> ResultadoDimensionamento:
    return executar_dimensionamento(entrada)


@st.cache_data(show_spinner=False, ttl=_TTL_QUERY)
def listar_projetos_cached() -> list[dict[str, Any]]:
    return ProjetoService().listar_projetos()


@st.cache_data(show_spinner=False, ttl=_TTL_QUERY)
def listar_simulacoes_cached(project_id: int) -> list[dict[str, Any]]:
    return ProjetoService().listar_simulacoes_do_projeto(project_id)


@st.cache_data(show_spinner=False, ttl=_TTL_QUERY)
def carregar_resultado_simulacao_cached(simulation_id: int) -> dict | None:
    return ProjetoService().carregar_resultado_da_simulacao(simulation_id)


@st.cache_data(show_spinner=False, ttl=_TTL_QUERY)
def buscar_projeto_por_nome_cached(nome: str) -> dict[str, Any] | None:
    return ProjetoService().repository.buscar_projeto_por_nome(nome)


def invalidar_cache_projetos() -> None:
    listar_projetos_cached.clear()
    listar_simulacoes_cached.clear()
    carregar_resultado_simulacao_cached.clear()
    buscar_projeto_por_nome_cached.clear()
