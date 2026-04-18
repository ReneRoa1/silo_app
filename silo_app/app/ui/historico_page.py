# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services.projeto_service import ProjetoService


def render_historico_page() -> None:
    projeto_service = ProjetoService()

    st.markdown(
        """
        <div class="page-header">
            <h1>Historico de simulacoes</h1>
            <p>Resumo geral das simulacoes registradas em todos os projetos.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    projetos = projeto_service.listar_projetos()

    if not projetos:
        st.info("Ainda nao ha projetos cadastrados.")
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
                "ID Simulacao": s["id"],
                "Nome da simulacao": s.get("nome_simulacao") or f"Simulacao {s['id']}",
                "Data": s["created_at"],
                "Tipo": melhor.get("tipo", "-"),
                "Volume (m3)": round(float(melhor.get("volume_silo_m3", 0) or 0), 2),
                "Area plantio (ha)": round(float(dados_resultado.get("area_a_ser_plantada", 0) or 0), 2),
            })

    if not linhas:
        st.info("Ainda nao ha simulacoes salvas.")
        return

    df = pd.DataFrame(linhas)
    st.dataframe(df, use_container_width=True, hide_index=True)
