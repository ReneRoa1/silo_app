# -*- coding: utf-8 -*-
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services.projeto_service import ProjetoService


def render_projetos_page() -> None:
    projeto_service = ProjetoService()

    st.markdown(
        """
        <div class="page-header">
            <h1>Projetos salvos</h1>
            <p>Gerencie projetos salvos e abra simulacoes anteriores para continuar a analise.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    projetos = projeto_service.listar_projetos()

    if not projetos:
        st.info("Nenhum projeto salvo ainda.")
        return

    df = pd.DataFrame([
        {
            "ID": p["id"],
            "Nome": p["nome"],
            "Responsavel tecnico": p.get("responsavel_tecnico", ""),
            "Propriedade": p.get("propriedade", ""),
            "Ultima atualizacao": p.get("updated_at", ""),
        }
        for p in projetos
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)

    opcoes = {
        f"{p['id']} - {p['nome']}": p["id"]
        for p in projetos
    }

    projeto_label = st.selectbox("Selecionar projeto", list(opcoes.keys()))
    projeto_id = opcoes[projeto_label]

    simulacoes = projeto_service.listar_simulacoes_do_projeto(projeto_id)

    st.markdown("### Simulacoes do projeto")
    simulacao_id = None

    if simulacoes:
        linhas = []
        for s in simulacoes:
            linhas.append({
                "ID": s["id"],
                "Nome da simulacao": s.get("nome_simulacao") or f"Simulacao {s['id']}",
                "Data": s["created_at"],
            })
        st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)

        opcoes_sim = {
            f"{s.get('nome_simulacao') or 'Simulacao ' + str(s['id'])} - {s['created_at']}": s["id"]
            for s in simulacoes
        }

        simulacao_label = st.selectbox(
            "Selecionar simulacao (opcional)",
            options=["Somente projeto"] + list(opcoes_sim.keys())
        )

        if simulacao_label != "Somente projeto":
            simulacao_id = opcoes_sim[simulacao_label]
    else:
        st.info("Este projeto ainda nao possui simulacoes.")

    if st.button("Abrir no dimensionamento", use_container_width=True):
        st.session_state["projeto_id_selecionado"] = projeto_id
        st.session_state["pagina_atual"] = "Dimensionamento"
        st.session_state["carregar_projeto_automaticamente"] = True

        if simulacao_id is not None:
            st.session_state["simulacao_id_selecionada"] = simulacao_id
            st.session_state["carregar_simulacao_automaticamente"] = True
        else:
            st.session_state["simulacao_id_selecionada"] = None
            st.session_state["carregar_simulacao_automaticamente"] = False

        st.rerun()
