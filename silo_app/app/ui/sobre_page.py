# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st


def render_sobre_page() -> None:
    st.markdown(
        """
        <div class="page-header">
            <h1>Sobre o sistema</h1>
            <p>Informacoes sobre o SiloApp e seus recursos.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ### Sistema de Dimensionamento de Silo para Silagem

        Aplicativo desenvolvido para apoiar tecnicos, produtores e estudantes
        no planejamento de silos para silagem, com foco em organizacao,
        calculo tecnico, visualizacao e geracao de relatorios.
        """
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="result-card">
                <h4>Recursos atuais</h4>
                <ul style="line-height: 2;">
                    <li>Dimensionamento tecnico</li>
                    <li>Otimizacao geometrica</li>
                    <li>Visualizacao 3D</li>
                    <li>Relatorio em PDF</li>
                    <li>Cadastro de projetos</li>
                    <li>Historico de simulacoes</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="result-card">
                <h4>Informacoes do prototipo</h4>
                <ul style="line-height: 2;">
                    <li><strong>Versao:</strong> Prototipo 0.1</li>
                    <li><strong>Status:</strong> Em desenvolvimento</li>
                    <li><strong>Uso:</strong> Demonstracao tecnica e academica</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.info("Prototipo funcional em evolucao para versao profissional instalavel.")
