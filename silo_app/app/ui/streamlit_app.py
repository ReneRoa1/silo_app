# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.storage.sqlite_db import init_db
from app.ui.home_page import render_home_page
from app.ui.dimensionamento_page import render_dimensionamento_page
from app.ui.projetos_page import render_projetos_page
from app.ui.historico_page import render_historico_page
from app.ui.sobre_page import render_sobre_page


ASSETS_DIR = Path("app/assets")
LOGO_PATH = ASSETS_DIR / "logo.png"

def carregar_css_global() -> None:
    css_path = Path("app/assets/styles.css")
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def run_streamlit_app() -> None:
    init_db()

    st.set_page_config(
        page_title="Dimensionamento de Silo",
        layout="wide",
    )
    carregar_css_global()
    if "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = "Início"

    paginas = ["Início", "Dimensionamento", "Projetos", "Histórico", "Sobre"]

    with st.sidebar:
        if LOGO_PATH.exists():
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(str(LOGO_PATH), width=90)

        st.markdown(
            """
            <div style="text-align: center; margin-top: 6px; margin-bottom: 12px;">
                <h3 style="margin-bottom: 4px;">SiloApp</h3>
                <p style="font-size: 13px; margin-top: 0;">
                    Dimensionamento de silo para silagem
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        pagina = st.radio(
            "Ir para",
            paginas,
            index=paginas.index(st.session_state["pagina_atual"]),
            label_visibility="collapsed",
        )
        st.session_state["pagina_atual"] = pagina

        st.markdown("---")
        st.caption("Protótipo funcional")
        st.caption("Versão 0.1")

    if pagina == "Início":
        render_home_page()
    elif pagina == "Dimensionamento":
        render_dimensionamento_page()
    elif pagina == "Projetos":
        render_projetos_page()
    elif pagina == "Histórico":
        render_historico_page()
    elif pagina == "Sobre":
        render_sobre_page()