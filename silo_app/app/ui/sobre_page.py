# -*- coding: utf-8 -*-
from __future__ import annotations

import streamlit as st


def render_sobre_page() -> None:
    st.title("Sobre o sistema")

    st.markdown(
        """
        ### Sistema de Dimensionamento de Silo para Silagem

        Aplicativo desenvolvido para apoiar técnicos, produtores e estudantes
        no planejamento de silos para silagem, com foco em organização,
        cálculo técnico, visualização e geração de relatórios.
        """
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Recursos atuais")
        st.markdown(
            """
            - Dimensionamento técnico  
            - Otimização geométrica  
            - Visualização 3D  
            - Relatório em PDF  
            - Cadastro de projetos  
            - Histórico de simulações
            """
        )

    with col2:
        st.subheader("Informações do protótipo")
        st.markdown(
            """
            - **Versão:** Protótipo 0.1  
            - **Status:** Em desenvolvimento  
            - **Uso:** Demonstração técnica e acadêmica
            """
        )

    st.markdown("---")
    st.info("Protótipo funcional em evolução para versão profissional instalável.")