# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services.projeto_service import ProjetoService


def render_historico_page() -> None:
    projeto_service = ProjetoService()

    st.title("Histórico de simulações")
    st.caption("Resumo geral das simulações registradas em todos os projetos.")

    projetos = projeto_service.listar_projetos()

    if not projetos:
        st.info("Ainda não há projetos cadastrados.")
        return

    linhas = []

    for projeto in projetos:
        simulacoes = projeto_service.listar_simulacoes_do_projeto(projeto["id"])
        for s in simulacoes:
            dados_resultado = projeto_service.carregar_resultado_da_simulacao(s["id"]) or {}
            melhor = dados_resultado.get("melhor_solucao", {})

            linhas.append({
                "Projeto": projeto["nome"],
                "ID Projeto": projeto["id"],
                "ID Simulação": s["id"],
                "Nome da simulação": s.get("nome_simulacao") or f"Simulação {s['id']}",
                "Data": s["created_at"],
                "Tipo": melhor.get("tipo", "-"),
                "Volume (m³)": round(float(melhor.get("volume_silo_m3", 0) or 0), 2),
                "Área plantio (ha)": round(float(dados_resultado.get("area_a_ser_plantada", 0) or 0), 2),
            })

    if not linhas:
        st.info("Ainda não há simulações salvas.")
        return

    df = pd.DataFrame(linhas)
    st.dataframe(df, use_container_width=True, hide_index=True)