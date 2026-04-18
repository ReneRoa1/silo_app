# -*- coding: utf-8 -*-
from __future__ import annotations

from urllib.parse import quote

import streamlit as st


def _ir_para(pagina: str) -> None:
    st.session_state["pagina_atual"] = pagina
    st.rerun()


def _card_link(icone: str, titulo: str, descricao: str, destino: str, badge: str = "") -> None:
    """Card totalmente clicável: o próprio <a> é o card, href muda a query e dispara rerun."""
    badge_html = f'<span class="nav-card-badge">{badge}</span>' if badge else ""
    href = f"?goto={quote(destino)}"
    st.markdown(
        f"""
        <a class="nav-card" href="{href}" target="_self">
            {badge_html}
            <div class="nav-card-icon">
                <i class="bi bi-{icone}"></i>
            </div>
            <h3 class="nav-card-title">{titulo}</h3>
            <p class="nav-card-desc">{descricao}</p>
            <span class="nav-card-link">Acessar <i class="bi bi-arrow-right"></i></span>
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_home_page() -> None:
    # --- Hero Banner ---
    st.markdown(
        """
        <div class="hero-banner">
            <h1>Sistema de Dimensionamento de Silo para Silagem</h1>
            <p>
                Plataforma para calculo, otimizacao geometrica, visualizacao 3D,
                gestao de projetos e emissao de relatorio tecnico.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    # --- Cards clicáveis ---
    col1, col2, col3 = st.columns(3)

    with col1:
        _card_link(
            icone="rulers",
            titulo="Novo dimensionamento",
            descricao="Inicie uma nova simulacao, informe os dados do rebanho, da forragem, da operacao e obtenha a melhor solucao.",
            destino="Dimensionamento",
            badge="Cálculo",
        )

    with col2:
        _card_link(
            icone="folder2-open",
            titulo="Projetos salvos",
            descricao="Consulte os projetos ja cadastrados, abra simulacoes anteriores e continue o trabalho.",
            destino="Projetos",
            badge="Gestão",
        )

    with col3:
        _card_link(
            icone="clock-history",
            titulo="Histórico",
            descricao="Visualize simulacoes registradas, organize cenarios e apresente a evolucao dos estudos.",
            destino="Histórico",
            badge="Análise",
        )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # --- Fluxo de uso + Ação rápida ---
    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown("### Fluxo recomendado de uso")

        steps = [
            "Criar ou abrir um projeto",
            "Informar os dados tecnicos",
            "Executar o dimensionamento",
            "Avaliar resultado, alternativas e visualizacao 3D",
            "Salvar a simulacao e gerar o relatorio em PDF",
        ]

        for i, step in enumerate(steps, 1):
            st.markdown(
                f"""
                <div class="step-item">
                    <div class="step-number">{i}</div>
                    <div class="step-text">{step}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with c2:
        st.markdown("### Acesso rapido")

        st.markdown(
            """
            <div class="quick-action">
                <h3><i class="bi bi-lightning-fill"></i> Acao rapida</h3>
                <p>Comece um novo dimensionamento agora</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("Novo dimensionamento", use_container_width=True, key="home_quick_dim", type="primary"):
            _ir_para("Dimensionamento")

        st.write("")
        if st.button("Sobre o sistema", use_container_width=True, key="home_sobre"):
            _ir_para("Sobre")
