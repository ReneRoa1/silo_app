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


def _valor_inicial(chave: str, padrao):
    return st.session_state.get(chave, padrao)


def _carregar_entrada_na_sessao(entrada_dict: dict) -> None:
    campos = [
        "numero_animais",
        "peso_medio_kg",
        "consumo_percent_pv",
        "volumoso_percent",
        "teor_ms_percent",
        "perdas_percent",
        "produtividade_mn_t_ha",
        "periodo_dias",
        "desabastecimento_m_dia",
        "compactacao_t_m3",
        "tipo_estrutura",
        "tipo_secao",
        "largura_trator_m",
        "folga_lateral_m",
        "passadas_min",
        "passadas_max",
        "altura_min_m",
        "altura_max_m",
        "passo_altura_m",
        "talude_h_por_v",
        "largura_topo_min_m",
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
            if simulacao and simulacao.get("nome_simulacao"):
                st.session_state["nome_simulacao"] = simulacao["nome_simulacao"]
        st.session_state["carregar_simulacao_automaticamente"] = False

        st.title("Novo dimensionamento")
        st.caption("Informe os dados técnicos, execute o cálculo e registre a simulação do projeto.")

    with st.sidebar:
        st.header("Projeto")

        nome_projeto = st.text_input("Nome do projeto", value=_valor_inicial("nome_projeto", "Projeto de dimensionamento"), key="nome_projeto")
        propriedade = st.text_input("Propriedade", value=_valor_inicial("propriedade", ""), key="propriedade")
        responsavel_tecnico = st.text_input("Responsável técnico", value=_valor_inicial("responsavel_tecnico", ""), key="responsavel_tecnico")
        observacoes = st.text_area("Observações", value=_valor_inicial("observacoes", ""), key="observacoes")

        st.header("Animais")
        numero_animais = st.number_input("Quantidade de animais", min_value=1, value=int(_valor_inicial("numero_animais", 100)), key="numero_animais")
        peso_medio_kg = st.number_input("Peso médio (kg)", value=float(_valor_inicial("peso_medio_kg", 450.0)), key="peso_medio_kg")
        consumo_percent_pv = st.number_input("Consumo (% PV)", value=float(_valor_inicial("consumo_percent_pv", 2.5)), key="consumo_percent_pv")
        volumoso_percent = st.slider("Volumoso (%)", 0, 100, int(_valor_inicial("volumoso_percent", 60)), key="volumoso_percent")

        st.header("Forragem")
        teor_ms_percent = st.number_input("MS (%)", value=float(_valor_inicial("teor_ms_percent", 32.0)), key="teor_ms_percent")
        perdas_percent = st.number_input("Perdas (%)", value=float(_valor_inicial("perdas_percent", 10.0)), key="perdas_percent")
        produtividade_mn_t_ha = st.number_input("Produtividade (t/ha)", value=float(_valor_inicial("produtividade_mn_t_ha", 40.0)), key="produtividade_mn_t_ha")

        st.header("Operação")
        periodo_dias = st.number_input("Período (dias)", value=int(_valor_inicial("periodo_dias", 180)), key="periodo_dias")
        desabastecimento_m_dia = st.number_input("Desabastecimento (m/dia)", value=float(_valor_inicial("desabastecimento_m_dia", 0.15)), key="desabastecimento_m_dia")
        compactacao_t_m3 = st.number_input("Compactação", value=float(_valor_inicial("compactacao_t_m3", 0.65)), key="compactacao_t_m3")

        st.header("Silo")
        opcoes_tipo_estrutura = ["Trincheira", "Superfície"]
        tipo_estrutura_inicial = _valor_inicial("tipo_estrutura", "Trincheira")
        tipo_estrutura = st.selectbox(
            "Tipo",
            options=opcoes_tipo_estrutura,
            index=opcoes_tipo_estrutura.index(tipo_estrutura_inicial) if tipo_estrutura_inicial in opcoes_tipo_estrutura else 0,
            key="tipo_estrutura",
        )

        if tipo_estrutura == "Superfície":
            opcoes_secao = ["Retangular", "Trapezoidal", "Ovalada"]
        else:
            opcoes_secao = ["Retangular", "Trapezoidal"]

        tipo_secao_inicial = _valor_inicial("tipo_secao", opcoes_secao[0])
        if tipo_secao_inicial not in opcoes_secao:
            tipo_secao_inicial = opcoes_secao[0]

        tipo_secao = st.selectbox("Seção", opcoes_secao, index=opcoes_secao.index(tipo_secao_inicial), key="tipo_secao")
        largura_trator_m = st.number_input("Largura trator", value=float(_valor_inicial("largura_trator_m", 2.4)), key="largura_trator_m")

        with st.expander("Opções avançadas"):
            altura_min_m = st.number_input(
                "Altura mínima (m)",
                value=float(_valor_inicial("altura_min_m", 2.0)),
                key="altura_min_m",
            )
            altura_max_m = st.number_input(
                "Altura máxima (m)",
                value=float(_valor_inicial("altura_max_m", 4.0)),
                key="altura_max_m",
            )
            passo_altura_m = st.number_input(
                "Passo de variação da altura (m)",
                value=float(_valor_inicial("passo_altura_m", 0.50)),
                key="passo_altura_m",
                help="Quanto menor o passo, mais refinada será a busca pela melhor altura.",
            )

        folga_lateral_m = 0.0
        passadas_min = 1
        passadas_max = 1
        talude_h_por_v = 0.0
        largura_topo_min_m = 0.0

    entrada = EntradaDimensionamento(
        numero_animais=int(numero_animais),
        peso_medio_kg=float(peso_medio_kg),
        consumo_percent_pv=float(consumo_percent_pv),
        volumoso_percent=float(volumoso_percent),
        teor_ms_percent=float(teor_ms_percent),
        perdas_percent=float(perdas_percent),
        produtividade_mn_t_ha=float(produtividade_mn_t_ha),
        periodo_dias=int(periodo_dias),
        desabastecimento_m_dia=float(desabastecimento_m_dia),
        compactacao_t_m3=float(compactacao_t_m3),
        tipo_estrutura=tipo_estrutura,
        tipo_secao=tipo_secao,
        largura_trator_m=float(largura_trator_m),
        folga_lateral_m=float(folga_lateral_m),
        passadas_min=int(passadas_min),
        passadas_max=int(passadas_max),
        altura_min_m=float(altura_min_m),
        altura_max_m=float(altura_max_m),
        passo_altura_m=float(passo_altura_m),
        talude_h_por_v=float(talude_h_por_v),
        largura_topo_min_m=float(largura_topo_min_m),
    )

    if st.button("Executar dimensionamento", type="primary"):
        try:
            resultado = executar_dimensionamento(entrada)
            st.session_state["resultado"] = resultado
            st.session_state["entrada"] = entrada
            st.session_state["indice_solucao_ativa"] = 0
            st.success("Cálculo concluído.")
        except Exception as e:
            st.error(f"Erro: {e}")

    resultado = st.session_state.get("resultado")
    entrada_salva = st.session_state.get("entrada")

    if resultado and entrada_salva:
        melhor_padrao = resultado.melhor_solucao

        indice_solucao_ativa = st.session_state.get("indice_solucao_ativa", 0)
        if indice_solucao_ativa >= len(resultado.solucoes):
            indice_solucao_ativa = 0

        melhor = resultado.solucoes[indice_solucao_ativa]

        tab1, tab2, tab3, tab4 = st.tabs(["Resultado", "Alternativas", "3D", "Projeto"])

        with tab1:
            st.subheader("Indicadores principais")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Volume do silo", f"{resultado.volume_total_necessario:.2f} m³")
            c2.metric("Área de plantio", f"{resultado.area_a_ser_plantada:.2f} ha")
            c3.metric("Comprimento operacional", f"{resultado.comprimento_operacional:.2f} m")
            c4.metric("Área mínima da face", f"{resultado.area_minima_da_face:.2f} m²")

            st.markdown("---")
            st.subheader("Melhor solução encontrada")

            s1, s2, s3, s4, s5 = st.columns(5)
            s1.metric("Tipo", melhor.tipo)
            s2.metric("Base menor", f"{melhor.largura_base_m:.2f} m")
            s3.metric("Base maior/topo", f"{melhor.largura_topo_m:.2f} m")
            s4.metric("Altura", f"{melhor.altura_m:.2f} m")
            s5.metric("Comprimento", f"{melhor.comprimento_m:.2f} m")

            s6, s7, s8, s9, s10 = st.columns(5)
            s6.metric("Área da seção", f"{melhor.area_secao_m2:.2f} m²")
            s7.metric("Área da face", f"{melhor.face_m2:.2f} m²")
            s8.metric("Volume", f"{melhor.volume_silo_m3:.2f} m³")
            s9.metric("Excedente", f"{melhor.excedente_m3:.2f} m³")
            s10.metric("Passadas", str(melhor.passadas))

            st.markdown("### Resumo técnico")
            resumo_df = pd.DataFrame(
                [
                    {"Parâmetro": "Tipo de solução", "Valor": melhor.tipo},
                    {"Parâmetro": "Largura da base", "Valor": f"{melhor.largura_base_m:.2f} m"},
                    {"Parâmetro": "Largura do topo/base maior", "Valor": f"{melhor.largura_topo_m:.2f} m"},
                    {"Parâmetro": "Altura", "Valor": f"{melhor.altura_m:.2f} m"},
                    {"Parâmetro": "Comprimento", "Valor": f"{melhor.comprimento_m:.2f} m"},
                    {"Parâmetro": "Área da seção transversal", "Valor": f"{melhor.area_secao_m2:.2f} m²"},
                    {"Parâmetro": "Área da face", "Valor": f"{melhor.face_m2:.2f} m²"},
                    {"Parâmetro": "Volume do silo", "Valor": f"{melhor.volume_silo_m3:.2f} m³"},
                    {"Parâmetro": "Excedente de volume", "Valor": f"{melhor.excedente_m3:.2f} m³"},
                    {"Parâmetro": "Número de passadas", "Valor": str(melhor.passadas)},
                    {"Parâmetro": "Pontuação da otimização", "Valor": f"{melhor.penalidade:.2f}"},
                ]
            )
            st.dataframe(resumo_df, use_container_width=True, hide_index=True)

            st.markdown("### Alertas e observações")
            if resultado.alertas:
                for a in resultado.alertas:
                    st.warning(a)
            else:
                st.success("Nenhum alerta técnico automático foi identificado para esta simulação.")

        with tab2:
            st.subheader("Alternativas avaliadas")

            df = pd.DataFrame([
                {
                    "Índice": i,
                    "Tipo": s.tipo,
                    "Base menor (m)": round(s.largura_base_m, 2),
                    "Base maior/topo (m)": round(s.largura_topo_m, 2),
                    "Altura (m)": round(s.altura_m, 2),
                    "Comprimento (m)": round(s.comprimento_m, 2),
                    "Área da seção (m²)": round(s.area_secao_m2, 2),
                    "Área da face (m²)": round(s.face_m2, 2),
                    "Volume (m³)": round(s.volume_silo_m3, 2),
                    "Excedente (m³)": round(s.excedente_m3, 2),
                    "Passadas": s.passadas,
                    "Pontuação": round(s.penalidade, 2),
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

        with tab3:
            st.subheader("Visualização tridimensional do silo")
            st.caption("Representação geométrica da melhor solução encontrada pelo modelo.")

            if "Ovalada" in melhor.tipo:
                fig = go.Figure(
                    data=[criar_solido_superficie_oval(
                        melhor.largura_base_m,
                        melhor.altura_m,
                        melhor.comprimento_m
                    )]
                )
            else:
                fig = go.Figure(
                    data=[criar_solido_prismatico(
                        melhor.largura_base_m,
                        melhor.largura_topo_m,
                        melhor.altura_m,
                        melhor.comprimento_m
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
            caminho = get_temp_dir() / "silo.png"

            try:
                fig.write_image(str(caminho))
            except Exception:
                caminho = None

        with tab4:
            st.subheader("Projeto e exportação")

            nome_simulacao = st.text_input(
                "Nome da simulação",
                value=st.session_state.get("nome_simulacao", "Cenário base"),
                key="nome_simulacao",
                help="Use nomes descritivos para facilitar a comparação de cenários.",
            )

            col_salvar, col_pdf = st.columns(2)

            with col_salvar:
                if st.button("Salvar projeto", use_container_width=True):
                    try:
                        project_id = projeto_service.obter_ou_criar_projeto(
                            nome=nome_projeto,
                            responsavel_tecnico=responsavel_tecnico,
                            propriedade=propriedade,
                            observacoes=observacoes,
                        )

                        simulation_id = projeto_service.salvar_simulacao(
                            project_id,
                            entrada_salva,
                            resultado,
                            nome_simulacao=nome_simulacao.strip() if nome_simulacao.strip() else None,
                        )

                        st.success(
                            f"Simulação salva com sucesso no projeto ID {project_id}. "
                            f"Simulação ID {simulation_id}."
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
                        projeto,
                        entrada_salva,
                        resultado_pdf,
                        caminho_imagem_silo=str(caminho) if caminho else None
                    )
                    st.download_button(
                        "Baixar PDF",
                        pdf,
                        "relatorio.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")

            st.markdown("---")
            st.subheader("Histórico resumido do projeto")

            projeto_existente = projeto_service.repository.buscar_projeto_por_nome(nome_projeto)

            if projeto_existente:
                simulacoes_projeto = projeto_service.listar_simulacoes_do_projeto(int(projeto_existente["id"]))

                if simulacoes_projeto:
                    linhas_historico = []
                    for sim in simulacoes_projeto:
                        dados_resultado = projeto_service.carregar_resultado_da_simulacao(sim["id"]) or {}
                        melhor_hist = dados_resultado.get("melhor_solucao", {})

                        linhas_historico.append({
                            "ID Simulação": sim["id"],
                            "Nome": sim.get("nome_simulacao") or f"Simulação {sim['id']}",
                            "Data": sim["created_at"],
                            "Tipo": melhor_hist.get("tipo", "-"),
                            "Volume (m³)": round(float(melhor_hist.get("volume_silo_m3", 0) or 0), 2),
                            "Área plantio (ha)": round(float(dados_resultado.get("area_a_ser_plantada", 0) or 0), 2),
                        })

                    st.dataframe(
                        pd.DataFrame(linhas_historico),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("Este projeto ainda não possui simulações registradas.")
            else:
                st.info("Salve este projeto para começar a formar o histórico.")