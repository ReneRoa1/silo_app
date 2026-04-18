# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.domain.models import EntradaDimensionamento, Projeto
from app.services.dimensionamento_service import executar_dimensionamento
from app.services.projeto_service import ProjetoService
from app.services.relatorio_service import gerar_pdf_projeto
from app.visualization.plotly_3d import (
    criar_solido_prismatico,
    criar_solido_superficie_oval,
)


ETAPAS = [
    {"num": 1, "nome": "Rebanho",   "icon": ":material/pets:"},
    {"num": 2, "nome": "Forragem",  "icon": ":material/grass:"},
    {"num": 3, "nome": "Operacao",  "icon": ":material/engineering:"},
    {"num": 4, "nome": "Silo",      "icon": ":material/warehouse:"},
]


def _valor_inicial(chave: str, padrao):
    return st.session_state.get(chave, padrao)


def _carregar_entrada_na_sessao(entrada_dict: dict) -> None:
    campos = [
        "numero_animais", "peso_medio_kg", "consumo_percent_pv", "volumoso_percent",
        "teor_ms_percent", "perdas_percent", "produtividade_mn_t_ha",
        "periodo_dias", "desabastecimento_m_dia", "compactacao_t_m3",
        "tipo_estrutura", "tipo_secao", "largura_trator_m",
        "folga_lateral_m", "passadas_min", "passadas_max",
        "altura_min_m", "altura_max_m", "passo_altura_m",
        "talude_h_por_v", "largura_topo_min_m",
    ]
    for campo in campos:
        if campo in entrada_dict:
            st.session_state[campo] = entrada_dict[campo]


def _carregar_projeto_na_sessao(projeto_dict: dict) -> None:
    mapa = {
        "nome_projeto": "nome",
        "propriedade": "propriedade",
        "responsavel_tecnico": "responsavel_tecnico",
        "observacoes": "observacoes",
    }
    for campo_sessao, campo_projeto in mapa.items():
        if campo_projeto in projeto_dict and projeto_dict[campo_projeto] is not None:
            st.session_state[campo_sessao] = projeto_dict[campo_projeto]


def render_dimensionamento_page() -> None:
    projeto_service = ProjetoService()

    # --- Carregar projeto/simulação da sessão ---
    if st.session_state.get("carregar_projeto_automaticamente"):
        projeto_id = st.session_state.get("projeto_id_selecionado")
        if projeto_id:
            projeto = projeto_service.carregar_dados_do_projeto(projeto_id)
            if projeto:
                _carregar_projeto_na_sessao(projeto)
        st.session_state["carregar_projeto_automaticamente"] = False

    if st.session_state.get("carregar_simulacao_automaticamente"):
        simulacao_id = st.session_state.get("simulacao_id_selecionada")
        if simulacao_id:
            entrada_dict = projeto_service.carregar_entrada_da_simulacao(simulacao_id)
            simulacao = projeto_service.buscar_simulacao_por_id(simulacao_id)
            if entrada_dict:
                _carregar_entrada_na_sessao(entrada_dict)
                st.session_state["etapa_entrada"] = 4
            if simulacao and simulacao.get("nome_simulacao"):
                st.session_state["nome_simulacao"] = simulacao["nome_simulacao"]
        st.session_state["carregar_simulacao_automaticamente"] = False

    # --- Page header ---
    st.markdown(
        """
        <div class="page-header">
            <h1>Dimensionamento de Silo</h1>
            <p>Informe os dados tecnicos, execute o calculo e registre a simulacao do projeto.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Abas principais ---
    tab_entrada, tab_resultados = st.tabs(["Entrada de Dados", "Resultados"])

    with tab_entrada:
        _render_entrada_dados()

    with tab_resultados:
        _render_resultados(projeto_service)


# =============================================
# FORMULÁRIO POR ETAPAS
# =============================================

def _render_stepper_bar(etapa_atual: int) -> None:
    """Barra visual de progresso das etapas."""
    parts = []
    for i, etapa in enumerate(ETAPAS):
        num = etapa["num"]
        if num < etapa_atual:
            estado = "done"
            icone = "&#10003;"
        elif num == etapa_atual:
            estado = "active"
            icone = str(num)
        else:
            estado = "pending"
            icone = str(num)

        parts.append(
            f'<div class="stepper-step">'
            f'  <div class="stepper-circle {estado}">{icone}</div>'
            f'  <span class="stepper-label {estado}">{etapa["nome"]}</span>'
            f'</div>'
        )
        if i < len(ETAPAS) - 1:
            line_estado = "done" if num < etapa_atual else "pending"
            parts.append(f'<div class="stepper-line {line_estado}"></div>')

    st.markdown(f'<div class="stepper-bar">{"".join(parts)}</div>', unsafe_allow_html=True)


def _render_entrada_dados() -> None:
    if "etapa_entrada" not in st.session_state:
        st.session_state["etapa_entrada"] = 1

    etapa = st.session_state["etapa_entrada"]

    # --- Projeto (sempre acessível, colapsado) ---
    with st.expander("Projeto (opcional)", expanded=False, icon=":material/description:"):
        cp1, cp2 = st.columns(2)
        with cp1:
            st.text_input("Nome do projeto", value=_valor_inicial("nome_projeto", ""), key="nome_projeto", placeholder="Ex: Fazenda São João")
            st.text_input("Propriedade", value=_valor_inicial("propriedade", ""), key="propriedade", placeholder="Nome da propriedade")
        with cp2:
            st.text_input("Responsavel tecnico", value=_valor_inicial("responsavel_tecnico", ""), key="responsavel_tecnico", placeholder="Nome do responsavel")
            st.text_area("Observacoes", value=_valor_inicial("observacoes", ""), key="observacoes", height=100, placeholder="Observacoes gerais...")

    st.write("")

    # --- Stepper visual ---
    _render_stepper_bar(etapa)

    # --- Etapa 1: Rebanho ---
    _visivel = etapa == 1
    with st.expander("1. Rebanho", expanded=_visivel, icon=":material/pets:"):
        cr1, cr2 = st.columns(2)
        with cr1:
            st.number_input("Quantidade de animais", min_value=0, value=int(_valor_inicial("numero_animais", 0)), key="numero_animais", help="Numero total de animais do rebanho")
            st.number_input("Peso medio (kg)", min_value=0.0, value=float(_valor_inicial("peso_medio_kg", 0.0)), key="peso_medio_kg", step=10.0, help="Peso medio por animal em kg")
        with cr2:
            st.number_input("Consumo (% PV)", min_value=0.0, value=float(_valor_inicial("consumo_percent_pv", 0.0)), key="consumo_percent_pv", step=0.1, help="Consumo diario em % do peso vivo")
            st.number_input("Volumoso (%)", min_value=0, max_value=100, value=int(_valor_inicial("volumoso_percent", 0)), key="volumoso_percent", help="Percentual de volumoso na dieta")

        if etapa == 1:
            # Validação: todos os campos devem ser > 0
            rebanho_ok = all([
                st.session_state.get("numero_animais", 0) > 0,
                st.session_state.get("peso_medio_kg", 0) > 0,
                st.session_state.get("consumo_percent_pv", 0) > 0,
                st.session_state.get("volumoso_percent", 0) > 0,
            ])
            st.write("")
            if not rebanho_ok:
                st.info("Preencha todos os campos acima para continuar.")
            if st.button("Continuar para Forragem  >>>", use_container_width=True, type="primary", key="btn_etapa1", disabled=not rebanho_ok):
                st.session_state["etapa_entrada"] = 2
                st.rerun()

    # --- Etapa 2: Forragem ---
    if etapa >= 2:
        _visivel = etapa == 2
        with st.expander("2. Forragem", expanded=_visivel, icon=":material/grass:"):
            cf1, cf2, cf3 = st.columns(3)
            with cf1:
                st.number_input("MS (%)", min_value=0.0, value=float(_valor_inicial("teor_ms_percent", 0.0)), key="teor_ms_percent", step=1.0, help="Teor de materia seca da forragem (%)")
            with cf2:
                st.number_input("Perdas (%)", min_value=0.0, value=float(_valor_inicial("perdas_percent", 0.0)), key="perdas_percent", step=1.0, help="Percentual estimado de perdas")
            with cf3:
                st.number_input("Produtividade (t MN/ha)", min_value=0.0, value=float(_valor_inicial("produtividade_mn_t_ha", 0.0)), key="produtividade_mn_t_ha", step=5.0, help="Produtividade em toneladas de materia natural por hectare")

            if etapa == 2:
                forragem_ok = all([
                    st.session_state.get("teor_ms_percent", 0) > 0,
                    st.session_state.get("produtividade_mn_t_ha", 0) > 0,
                ])
                st.write("")
                if not forragem_ok:
                    st.info("Preencha MS e Produtividade para continuar.")
                c_voltar, c_avancar = st.columns(2)
                with c_voltar:
                    if st.button("<<< Voltar", use_container_width=True, key="btn_voltar2"):
                        st.session_state["etapa_entrada"] = 1
                        st.rerun()
                with c_avancar:
                    if st.button("Continuar para Operacao  >>>", use_container_width=True, type="primary", key="btn_etapa2", disabled=not forragem_ok):
                        st.session_state["etapa_entrada"] = 3
                        st.rerun()

    # --- Etapa 3: Operação ---
    if etapa >= 3:
        _visivel = etapa == 3
        with st.expander("3. Operacao", expanded=_visivel, icon=":material/engineering:"):
            co1, co2, co3 = st.columns(3)
            with co1:
                st.number_input("Periodo (dias)", min_value=0, value=int(_valor_inicial("periodo_dias", 0)), key="periodo_dias", step=30, help="Periodo total de alimentacao em dias")
            with co2:
                st.number_input("Desabastecimento (m/dia)", min_value=0.0, value=float(_valor_inicial("desabastecimento_m_dia", 0.0)), key="desabastecimento_m_dia", step=0.05, help="Avanco diario na face do silo (m/dia)")
            with co3:
                st.number_input("Compactacao (t/m3)", min_value=0.0, value=float(_valor_inicial("compactacao_t_m3", 0.0)), key="compactacao_t_m3", step=0.05, help="Densidade de compactacao da silagem (t/m3)")

            if etapa == 3:
                operacao_ok = all([
                    st.session_state.get("periodo_dias", 0) > 0,
                    st.session_state.get("desabastecimento_m_dia", 0) > 0,
                    st.session_state.get("compactacao_t_m3", 0) > 0,
                ])
                st.write("")
                if not operacao_ok:
                    st.info("Preencha todos os campos acima para continuar.")
                c_voltar, c_avancar = st.columns(2)
                with c_voltar:
                    if st.button("<<< Voltar", use_container_width=True, key="btn_voltar3"):
                        st.session_state["etapa_entrada"] = 2
                        st.rerun()
                with c_avancar:
                    if st.button("Continuar para Silo  >>>", use_container_width=True, type="primary", key="btn_etapa3", disabled=not operacao_ok):
                        st.session_state["etapa_entrada"] = 4
                        st.rerun()

    # --- Etapa 4: Silo + Avançadas + Executar ---
    if etapa >= 4:
        with st.expander("4. Silo", expanded=True, icon=":material/warehouse:"):
            cs1, cs2, cs3 = st.columns(3)
            opcoes_tipo_estrutura = ["Trincheira", "Superfície"]
            tipo_estrutura_inicial = _valor_inicial("tipo_estrutura", "Trincheira")

            with cs1:
                st.selectbox(
                    "Tipo de estrutura",
                    options=opcoes_tipo_estrutura,
                    index=opcoes_tipo_estrutura.index(tipo_estrutura_inicial) if tipo_estrutura_inicial in opcoes_tipo_estrutura else 0,
                    key="tipo_estrutura",
                )

            tipo_estrutura = st.session_state.get("tipo_estrutura", "Trincheira")
            if tipo_estrutura == "Superfície":
                opcoes_secao = ["Retangular", "Trapezoidal", "Ovalada"]
            else:
                opcoes_secao = ["Retangular", "Trapezoidal"]

            tipo_secao_inicial = _valor_inicial("tipo_secao", opcoes_secao[0])
            if tipo_secao_inicial not in opcoes_secao:
                tipo_secao_inicial = opcoes_secao[0]

            with cs2:
                st.selectbox("Secao transversal", opcoes_secao, index=opcoes_secao.index(tipo_secao_inicial), key="tipo_secao")
            with cs3:
                st.number_input("Largura do trator (m)", min_value=0.0, value=float(_valor_inicial("largura_trator_m", 2.4)), key="largura_trator_m", step=0.1)

        with st.expander("Opcoes avancadas", expanded=False, icon=":material/tune:"):
            ca1, ca2, ca3 = st.columns(3)
            with ca1:
                st.number_input("Altura minima (m)", value=float(_valor_inicial("altura_min_m", 2.0)), key="altura_min_m")
            with ca2:
                st.number_input("Altura maxima (m)", value=float(_valor_inicial("altura_max_m", 4.0)), key="altura_max_m")
            with ca3:
                st.number_input(
                    "Passo de variacao da altura (m)",
                    value=float(_valor_inicial("passo_altura_m", 0.50)),
                    key="passo_altura_m",
                    help="Quanto menor o passo, mais refinada sera a busca pela melhor altura.",
                )

        st.write("")

        c_voltar_final, c_executar = st.columns([1, 2])
        with c_voltar_final:
            if st.button("<<< Voltar", use_container_width=True, key="btn_voltar4"):
                st.session_state["etapa_entrada"] = 3
                st.rerun()
        with c_executar:
            if st.button("Executar dimensionamento", type="primary", use_container_width=True):
                entrada = _montar_entrada()
                with st.spinner("Calculando o dimensionamento..."):
                    try:
                        resultado = executar_dimensionamento(entrada)
                        st.session_state["resultado"] = resultado
                        st.session_state["entrada"] = entrada
                        st.session_state["indice_solucao_ativa"] = 0
                        st.success("Calculo concluido! Veja a aba **Resultados**.")
                    except Exception as e:
                        st.error(f"Erro: {e}")


def _montar_entrada() -> EntradaDimensionamento:
    return EntradaDimensionamento(
        numero_animais=int(st.session_state.get("numero_animais", 100)),
        peso_medio_kg=float(st.session_state.get("peso_medio_kg", 450.0)),
        consumo_percent_pv=float(st.session_state.get("consumo_percent_pv", 2.5)),
        volumoso_percent=float(st.session_state.get("volumoso_percent", 60)),
        teor_ms_percent=float(st.session_state.get("teor_ms_percent", 32.0)),
        perdas_percent=float(st.session_state.get("perdas_percent", 10.0)),
        produtividade_mn_t_ha=float(st.session_state.get("produtividade_mn_t_ha", 40.0)),
        periodo_dias=int(st.session_state.get("periodo_dias", 180)),
        desabastecimento_m_dia=float(st.session_state.get("desabastecimento_m_dia", 0.15)),
        compactacao_t_m3=float(st.session_state.get("compactacao_t_m3", 0.65)),
        tipo_estrutura=st.session_state.get("tipo_estrutura", "Trincheira"),
        tipo_secao=st.session_state.get("tipo_secao", "Retangular"),
        largura_trator_m=float(st.session_state.get("largura_trator_m", 2.4)),
        folga_lateral_m=0.0,
        passadas_min=1,
        passadas_max=1,
        altura_min_m=float(st.session_state.get("altura_min_m", 2.0)),
        altura_max_m=float(st.session_state.get("altura_max_m", 4.0)),
        passo_altura_m=float(st.session_state.get("passo_altura_m", 0.50)),
        talude_h_por_v=0.0,
        largura_topo_min_m=0.0,
    )


# =============================================
# ABA RESULTADOS
# =============================================

def _render_resultados(projeto_service: ProjetoService) -> None:
    resultado = st.session_state.get("resultado")
    entrada_salva = st.session_state.get("entrada")

    if not resultado or not entrada_salva:
        st.markdown(
            """
            <div class="result-card" style="text-align: center; padding: 48px 24px;">
                <p style="font-size: 1.2rem; color: #6b7280 !important; margin-bottom: 8px;">
                    <i class="bi bi-clipboard-data" style="font-size: 2.4rem; color: #1c93c6;"></i>
                </p>
                <h3 style="color: #1f2937 !important;">Nenhum resultado disponivel</h3>
                <p style="color: #6b7280 !important;">
                    Preencha os dados na aba <strong>Entrada de Dados</strong> e execute o dimensionamento.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    melhor_padrao = resultado.melhor_solucao
    indice_solucao_ativa = st.session_state.get("indice_solucao_ativa", 0)
    if indice_solucao_ativa >= len(resultado.solucoes):
        indice_solucao_ativa = 0
    melhor = resultado.solucoes[indice_solucao_ativa]

    # --- KPI Cards ---
    st.markdown(
        f"""
        <div style="display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap;">
            <div class="kpi-card" style="flex: 1; min-width: 180px;">
                <div class="kpi-label">Volume do silo</div>
                <div class="kpi-value">{resultado.volume_total_necessario:.2f} m3</div>
            </div>
            <div class="kpi-card" style="flex: 1; min-width: 180px;">
                <div class="kpi-label">Area de plantio</div>
                <div class="kpi-value">{resultado.area_a_ser_plantada:.2f} ha</div>
            </div>
            <div class="kpi-card" style="flex: 1; min-width: 180px;">
                <div class="kpi-label">Comprimento operacional</div>
                <div class="kpi-value">{resultado.comprimento_operacional:.2f} m</div>
            </div>
            <div class="kpi-card" style="flex: 1; min-width: 180px;">
                <div class="kpi-label">Area minima da face</div>
                <div class="kpi-value">{resultado.area_minima_da_face:.2f} m2</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sub1, sub2, sub3 = st.tabs(["Solucao", "Alternativas", "3D e Exportacao"])

    with sub1:
        _render_solucao(melhor, resultado)

    with sub2:
        _render_alternativas(resultado)

    with sub3:
        _render_3d_exportacao(melhor, resultado, entrada_salva, projeto_service)


def _render_solucao(melhor, resultado) -> None:
    st.subheader("Melhor solucao encontrada")

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Tipo", melhor.tipo)
    s2.metric("Base menor", f"{melhor.largura_base_m:.2f} m")
    s3.metric("Base maior/topo", f"{melhor.largura_topo_m:.2f} m")
    s4.metric("Altura", f"{melhor.altura_m:.2f} m")
    s5.metric("Comprimento", f"{melhor.comprimento_m:.2f} m")

    s6, s7, s8, s9, s10 = st.columns(5)
    s6.metric("Area da secao", f"{melhor.area_secao_m2:.2f} m2")
    s7.metric("Area da face", f"{melhor.face_m2:.2f} m2")
    s8.metric("Volume", f"{melhor.volume_silo_m3:.2f} m3")
    s9.metric("Excedente", f"{melhor.excedente_m3:.2f} m3")
    s10.metric("Passadas", str(melhor.passadas))

    st.markdown("---")
    st.markdown("### Resumo tecnico")

    resumo_df = pd.DataFrame([
        {"Parametro": "Tipo de solucao", "Valor": melhor.tipo},
        {"Parametro": "Largura da base", "Valor": f"{melhor.largura_base_m:.2f} m"},
        {"Parametro": "Largura do topo/base maior", "Valor": f"{melhor.largura_topo_m:.2f} m"},
        {"Parametro": "Altura", "Valor": f"{melhor.altura_m:.2f} m"},
        {"Parametro": "Comprimento", "Valor": f"{melhor.comprimento_m:.2f} m"},
        {"Parametro": "Area da secao transversal", "Valor": f"{melhor.area_secao_m2:.2f} m2"},
        {"Parametro": "Area da face", "Valor": f"{melhor.face_m2:.2f} m2"},
        {"Parametro": "Volume do silo", "Valor": f"{melhor.volume_silo_m3:.2f} m3"},
        {"Parametro": "Excedente de volume", "Valor": f"{melhor.excedente_m3:.2f} m3"},
        {"Parametro": "Numero de passadas", "Valor": str(melhor.passadas)},
        {"Parametro": "Pontuacao da otimizacao", "Valor": f"{melhor.penalidade:.2f}"},
    ])
    st.dataframe(resumo_df, use_container_width=True, hide_index=True)

    st.markdown("### Alertas e observacoes")
    if resultado.alertas:
        for a in resultado.alertas:
            st.warning(a)
    else:
        st.success("Nenhum alerta tecnico automatico foi identificado para esta simulacao.")


def _render_alternativas(resultado) -> None:
    st.subheader("Alternativas avaliadas")

    df = pd.DataFrame([
        {
            "Indice": i,
            "Tipo": s.tipo,
            "Base menor (m)": round(s.largura_base_m, 2),
            "Base maior/topo (m)": round(s.largura_topo_m, 2),
            "Altura (m)": round(s.altura_m, 2),
            "Comprimento (m)": round(s.comprimento_m, 2),
            "Area da secao (m2)": round(s.area_secao_m2, 2),
            "Area da face (m2)": round(s.face_m2, 2),
            "Volume (m3)": round(s.volume_silo_m3, 2),
            "Excedente (m3)": round(s.excedente_m3, 2),
            "Passadas": s.passadas,
            "Pontuacao": round(s.penalidade, 2),
        }
        for i, s in enumerate(resultado.solucoes)
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    opcoes_alternativas = {
        f"Alternativa {i + 1} - {s.tipo} - Altura {s.altura_m:.2f} m - Comprimento {s.comprimento_m:.2f} m": i
        for i, s in enumerate(resultado.solucoes)
    }

    alternativa_escolhida = st.selectbox(
        "Escolher alternativa para usar no resultado, PDF e salvamento",
        options=list(opcoes_alternativas.keys()),
        index=st.session_state.get("indice_solucao_ativa", 0),
    )

    if st.button("Usar alternativa selecionada", use_container_width=True):
        st.session_state["indice_solucao_ativa"] = opcoes_alternativas[alternativa_escolhida]
        st.success("Alternativa selecionada aplicada ao resultado atual.")
        st.rerun()


def _render_3d_exportacao(melhor, resultado, entrada_salva, projeto_service) -> None:
    st.subheader("Visualizacao tridimensional do silo")
    st.caption("Representacao geometrica da melhor solucao encontrada pelo modelo.")

    if "Ovalada" in melhor.tipo:
        fig = go.Figure(
            data=[criar_solido_superficie_oval(
                melhor.largura_base_m, melhor.altura_m, melhor.comprimento_m
            )]
        )
    else:
        fig = go.Figure(
            data=[criar_solido_prismatico(
                melhor.largura_base_m, melhor.largura_topo_m,
                melhor.altura_m, melhor.comprimento_m
            )]
        )

    fig.update_layout(
        scene=dict(
            xaxis_title="Largura (m)",
            yaxis_title="Comprimento (m)",
            zaxis_title="Altura (m)",
            aspectmode="manual",
            aspectratio=dict(x=1.2, y=2.2, z=0.9),
            camera=dict(
                eye=dict(x=1.7, y=1.7, z=1.1),
                projection=dict(type="orthographic"),
            ),
        ),
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    from app.config import get_temp_dir
    from app.visualization.silo_diagram import gerar_diagrama_silo_arquivo

    caminho = get_temp_dir() / "silo.png"
    try:
        gerar_diagrama_silo_arquivo(
            tipo=melhor.tipo,
            largura_base_m=melhor.largura_base_m,
            largura_topo_m=melhor.largura_topo_m,
            altura_m=melhor.altura_m,
            comprimento_m=melhor.comprimento_m,
            destino=caminho,
        )
    except Exception:
        caminho = None

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.subheader("Projeto e exportacao")

    nome_projeto = st.session_state.get("nome_projeto", "") or "Projeto sem nome"
    responsavel_tecnico = st.session_state.get("responsavel_tecnico", "")
    propriedade = st.session_state.get("propriedade", "")
    observacoes = st.session_state.get("observacoes", "")

    nome_simulacao = st.text_input(
        "Nome da simulacao",
        value=st.session_state.get("nome_simulacao", "Cenario base"),
        key="nome_simulacao",
        help="Use nomes descritivos para facilitar a comparacao de cenarios.",
    )

    col_salvar, col_pdf = st.columns(2)

    with col_salvar:
        if st.button("Salvar projeto", use_container_width=True):
            with st.spinner("Salvando..."):
                try:
                    project_id = projeto_service.obter_ou_criar_projeto(
                        nome=nome_projeto,
                        responsavel_tecnico=responsavel_tecnico,
                        propriedade=propriedade,
                        observacoes=observacoes,
                    )
                    simulation_id = projeto_service.salvar_simulacao(
                        project_id, entrada_salva, resultado,
                        nome_simulacao=nome_simulacao.strip() if nome_simulacao.strip() else None,
                    )
                    st.success(
                        f"Simulacao salva com sucesso no projeto ID {project_id}. "
                        f"Simulacao ID {simulation_id}."
                    )
                except Exception as e:
                    st.error(f"Erro ao salvar projeto: {e}")

    with col_pdf:
        projeto = Projeto(
            nome=nome_projeto,
            responsavel_tecnico=responsavel_tecnico,
            propriedade=propriedade,
            observacoes=observacoes,
        )
        try:
            resultado_pdf = resultado
            resultado_pdf.melhor_solucao = melhor
            pdf = gerar_pdf_projeto(
                projeto, entrada_salva, resultado_pdf,
                caminho_imagem_silo=str(caminho) if caminho else None
            )
            st.download_button(
                "Baixar PDF", pdf, "relatorio.pdf",
                mime="application/pdf", use_container_width=True,
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

    st.markdown("---")
    st.subheader("Historico resumido do projeto")

    projeto_existente = projeto_service.repository.buscar_projeto_por_nome(nome_projeto)
    if projeto_existente:
        simulacoes_projeto = projeto_service.listar_simulacoes_do_projeto(int(projeto_existente["id"]))
        if simulacoes_projeto:
            linhas_historico = []
            for sim in simulacoes_projeto:
                dados_resultado = projeto_service.carregar_resultado_da_simulacao(sim["id"]) or {}
                melhor_hist = dados_resultado.get("melhor_solucao", {})
                linhas_historico.append({
                    "ID Simulacao": sim["id"],
                    "Nome": sim.get("nome_simulacao") or f"Simulacao {sim['id']}",
                    "Data": sim["created_at"],
                    "Tipo": melhor_hist.get("tipo", "-"),
                    "Volume (m3)": round(float(melhor_hist.get("volume_silo_m3", 0) or 0), 2),
                    "Area plantio (ha)": round(float(dados_resultado.get("area_a_ser_plantada", 0) or 0), 2),
                })
            st.dataframe(pd.DataFrame(linhas_historico), use_container_width=True, hide_index=True)
        else:
            st.info("Este projeto ainda nao possui simulacoes registradas.")
    else:
        st.info("Salve este projeto para comecar a formar o historico.")
