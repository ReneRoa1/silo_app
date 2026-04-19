# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import streamlit as st
from streamlit_option_menu import option_menu

from app.storage.sqlite_db import init_db
from app.ui.home_page import render_home_page
from app.ui.dimensionamento_page import render_dimensionamento_page
from app.ui.projetos_page import render_projetos_page
from app.ui.historico_page import render_historico_page
from app.ui.sobre_page import render_sobre_page


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"
CSS_PATH = ASSETS_DIR / "styles.css"


def carregar_css_global() -> None:
    if CSS_PATH.exists():
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def run_streamlit_app() -> None:
    init_db()

    st.set_page_config(
        page_title="SiloApp - Dimensionamento de Silo",
        page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None,
        layout="wide",
    )
    carregar_css_global()
    st.markdown(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">',
        unsafe_allow_html=True,
    )
    if "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = "Início"

    paginas = ["Início", "Dimensionamento", "Projetos", "Histórico", "Sobre"]

    # Navegação por query param (?goto=...) — usada pelos cards da home
    try:
        goto = st.query_params.get("goto")
        if goto and goto in paginas:
            st.session_state["pagina_atual"] = goto
            st.query_params.clear()
    except Exception:
        pass
    icones = ["house-fill", "rulers", "folder2-open", "clock-history", "info-circle"]

    with st.sidebar:
        if LOGO_PATH.exists():
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(str(LOGO_PATH), width=90)

        st.markdown(
            """
            <div style="text-align: center; margin-top: 4px; margin-bottom: 18px;">
                <h3 style="margin-bottom: 2px; font-size: 1.3rem;">SiloApp</h3>
                <p style="font-size: 12px; margin-top: 0; opacity: 0.8;">
                    Dimensionamento de silo para silagem
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        idx_atual = paginas.index(st.session_state["pagina_atual"]) if st.session_state["pagina_atual"] in paginas else 0

        pagina = option_menu(
            menu_title="",
            options=paginas,
            icons=icones,
            default_index=idx_atual,
            styles={
                "container": {"padding": "6px 8px", "background-color": "transparent"},
                "icon": {"font-size": "17px"},
                "nav-link": {"text-align": "left"},
            },
        )
        st.session_state["pagina_atual"] = pagina

        st.markdown(
            """
            <div style="text-align: center; margin-top: 28px; opacity: 0.5; font-size: 11px;">
                <p>Versao 0.1</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
