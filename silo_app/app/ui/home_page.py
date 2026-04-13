# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"


def _ir_para(pagina: str) -> None:
    st.session_state["pagina_atual"] = pagina
    st.rerun()


def _render_card(
    titulo: str,
    descricao: str,
    botao: str,
    pagina_destino: str,
    imagem: str | None = None,
    key: str = "",
) -> None:
    with st.container(border=True):
        if imagem:
            caminho = ASSETS_DIR / imagem
            if caminho.exists():
                col_img1, col_img2, col_img3 = st.columns([2, 3, 2])
                with col_img2:
                    st.image(str(caminho), width=130)

        st.markdown(f"### {titulo}")
        st.write(descricao)

        if st.button(botao, use_container_width=True, key=key):
            _ir_para(pagina_destino)


def render_home_page() -> None:
    with st.container():
        col_texto, col_logo = st.columns([10, 1])

        with col_texto:
            st.markdown(
                """
                <div style="
                    padding: 24px 28px;
                    border-radius: 18px 0 0 18px;
                    background: linear-gradient(135deg, #0f172a, #1e3a8a);
                    min-height: 150px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                ">
                    <h1 style="margin-bottom: 10px; color: white;">
                        Sistema de Dimensionamento de Silo para Silagem
                    </h1>
                    <p style="font-size: 18px; margin-bottom: 0; color: white;">
                        Plataforma para cálculo, otimização geométrica, visualização 3D,
                        gestão de projetos e emissão de relatório técnico.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_logo:
            if LOGO_PATH.exists():
                st.markdown(
                    """
                    <div style="
                        padding: 24px 12px;
                        border-radius: 0 18px 18px 0;
                        background: linear-gradient(135deg, #0f172a, #1e3a8a);
                        min-height: 0px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                    """,
                    unsafe_allow_html=True,
                )
                st.image(str(LOGO_PATH), width=120)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    """
                    <div style="
                        padding: 24px 12px;
                        border-radius: 0 18px 18px 0;
                        background: linear-gradient(135deg, #0f172a, #1e3a8a);
                        min-height: 150px;
                    ">
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        _render_card(
            titulo="Novo dimensionamento",
            descricao=(
                "Inicie uma nova simulação, informe os dados do rebanho, "
                "da forragem, da operação e obtenha a melhor solução."
            ),
            botao="Abrir dimensionamento",
            pagina_destino="Dimensionamento",
            imagem="dimensionamento.png",
            key="home_dim",
        )

    with col2:
        _render_card(
            titulo="Projetos salvos",
            descricao=(
                "Consulte os projetos já cadastrados, abra simulações anteriores "
                "e continue o trabalho a partir de dados já registrados."
            ),
            botao="Abrir projetos",
            pagina_destino="Projetos",
            imagem="projetos.png",
            key="home_proj",
        )

    with col3:
        _render_card(
            titulo="Histórico",
            descricao=(
                "Visualize simulações registradas, organize cenários "
                "e apresente a evolução dos estudos realizados."
            ),
            botao="Abrir histórico",
            pagina_destino="Histórico",
            imagem="historico.png",
            key="home_hist",
        )

    st.markdown("---")

    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Fluxo recomendado de uso")
        st.markdown(
            """
            1. Criar ou abrir um projeto  
            2. Informar os dados técnicos  
            3. Executar o dimensionamento  
            4. Avaliar resultado, alternativas e visualização 3D  
            5. Salvar a simulação e gerar o relatório em PDF
            """
        )

    with c2:
        st.subheader("Acesso rápido")
        if st.button("Sobre o sistema", use_container_width=True, key="home_sobre"):
            _ir_para("Sobre")