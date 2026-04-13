# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime

from app.domain.models import EntradaDimensionamento, ResultadoDimensionamento, SolucaoSilo
from app.domain.validacoes import validar_entrada

from calculos import (
    Rebanho,
    Dieta,
    Forragem,
    Operacao,
    calcular_ap_ha,
    calcular_cmi,
    calcular_cmn,
    calcular_comprimento_operacional,
    calcular_cr,
    calcular_ct,
    calcular_cvo,
    calcular_face_minima,
    calcular_ve_t,
    calcular_volume_total_silo,
)

from otimizacao import (
    otimizar_secao_ovalada,
    otimizar_secao_retangular,
    otimizar_secao_trapezoidal,
)


def _gerar_alertas(dados: EntradaDimensionamento, melhor: SolucaoSilo, area_minima_da_face: float) -> list[str]:
    alertas = []

    if dados.teor_ms_percent < 28:
        alertas.append("O teor de matéria seca está baixo. Vale revisar o ponto de ensilagem.")
    if dados.teor_ms_percent > 40:
        alertas.append("O teor de matéria seca está elevado. Isso pode dificultar a compactação e a fermentação.")
    if melhor.face_m2 < area_minima_da_face:
        alertas.append("A melhor solução apresenta área da face abaixo da área mínima calculada.")
    if melhor.comprimento_m > 100:
        alertas.append("O comprimento do silo ficou elevado. Considere dividir o silo em duas partes.")
    if dados.compactacao_t_m3 < 0.30:
        alertas.append("A compactação informada está baixa para muitas situações práticas.")
    if dados.tipo_secao == "Trapezoidal" and melhor.largura_topo_m < dados.largura_topo_min_m:
        alertas.append("A base maior ou topo ficaram abaixo do mínimo desejado.")

    return alertas


def executar_dimensionamento(dados: EntradaDimensionamento) -> ResultadoDimensionamento:
    validar_entrada(dados)

    rebanho = Rebanho(
        numero_animais=int(dados.numero_animais),
        peso_medio_kg=float(dados.peso_medio_kg),
        consumo_percent_pv=float(dados.consumo_percent_pv),
    )

    dieta = Dieta(volumoso_percent=float(dados.volumoso_percent))

    forragem = Forragem(
        teor_ms_percent=float(dados.teor_ms_percent),
        perdas_percent=float(dados.perdas_percent),
        produtividade_mn_t_ha=float(dados.produtividade_mn_t_ha),
    )

    operacao = Operacao(
        periodo_dias=int(dados.periodo_dias),
        desabastecimento_m_dia=float(dados.desabastecimento_m_dia),
        compactacao_t_m3=float(dados.compactacao_t_m3),
        largura_trator_m=float(dados.largura_trator_m),
    )

    consumo_medio_individual = calcular_cmi(rebanho.peso_medio_kg, rebanho.consumo_percent_pv)
    consumo_volumoso = calcular_cvo(consumo_medio_individual, dieta.volumoso_percent)
    consumo_materia_natural = calcular_cmn(consumo_volumoso, forragem.teor_ms_percent)
    consumo_rebanho = calcular_cr(consumo_materia_natural, rebanho.numero_animais)
    consumo_total = calcular_ct(consumo_rebanho, operacao.periodo_dias)
    volume_a_ser_ensilado = calcular_ve_t(consumo_total, forragem.perdas_percent)
    area_a_ser_plantada = calcular_ap_ha(volume_a_ser_ensilado, forragem.produtividade_mn_t_ha)
    comprimento_operacional = calcular_comprimento_operacional(
        operacao.desabastecimento_m_dia,
        operacao.periodo_dias,
    )
    volume_total_necessario = calcular_volume_total_silo(volume_a_ser_ensilado, operacao.compactacao_t_m3)
    area_minima_da_face = calcular_face_minima(
        cr_kg_dia=consumo_rebanho,
        compactacao_t_m3=operacao.compactacao_t_m3,
        desabastecimento_m_dia=operacao.desabastecimento_m_dia,
    )

    if dados.tipo_secao == "Retangular":
        solucoes_brutas = otimizar_secao_retangular(
            volume_necessario_m3=volume_total_necessario,
            comprimento_operacional_m=comprimento_operacional,
            face_minima_m2=area_minima_da_face,
            largura_trator_m=operacao.largura_trator_m,
            altura_min_m=float(dados.altura_min_m),
            altura_max_m=float(dados.altura_max_m),
            passo_altura_m=float(dados.passo_altura_m),
            passadas_min=int(dados.passadas_min),
            passadas_max=int(dados.passadas_max),
            folga_lateral_m=float(dados.folga_lateral_m),
            tipo_estrutura=dados.tipo_estrutura,
        )
    elif dados.tipo_secao == "Trapezoidal":
        solucoes_brutas = otimizar_secao_trapezoidal(
            volume_necessario_m3=volume_total_necessario,
            comprimento_operacional_m=comprimento_operacional,
            face_minima_m2=area_minima_da_face,
            largura_trator_m=operacao.largura_trator_m,
            altura_min_m=float(dados.altura_min_m),
            altura_max_m=float(dados.altura_max_m),
            passo_altura_m=float(dados.passo_altura_m),
            passadas_min=int(dados.passadas_min),
            passadas_max=int(dados.passadas_max),
            folga_lateral_m=float(dados.folga_lateral_m),
            talude_h_por_v=float(dados.talude_h_por_v),
            largura_topo_min_m=float(dados.largura_topo_min_m),
            tipo_estrutura=dados.tipo_estrutura,
        )
    else:
        solucoes_brutas = otimizar_secao_ovalada(
            volume_necessario_m3=volume_total_necessario,
            comprimento_operacional_m=comprimento_operacional,
            face_minima_m2=area_minima_da_face,
            largura_trator_m=operacao.largura_trator_m,
            altura_min_m=float(dados.altura_min_m),
            altura_max_m=float(dados.altura_max_m),
            passo_altura_m=float(dados.passo_altura_m),
            passadas_min=int(dados.passadas_min),
            passadas_max=int(dados.passadas_max),
            folga_lateral_m=float(dados.folga_lateral_m),
            largura_base_min_m=float(dados.largura_topo_min_m),
            tipo_estrutura=dados.tipo_estrutura,
        )

    if not solucoes_brutas:
        raise ValueError("Nenhuma solução foi encontrada com os limites informados.")

    solucoes = [
        SolucaoSilo(
            tipo=s.tipo,
            largura_base_m=s.largura_base_m,
            largura_topo_m=s.largura_topo_m,
            altura_m=s.altura_m,
            comprimento_m=s.comprimento_m,
            area_secao_m2=s.area_secao_m2,
            face_m2=s.face_m2,
            volume_silo_m3=s.volume_silo_m3,
            excedente_m3=s.excedente_m3,
            passadas=s.passadas,
            penalidade=s.penalidade,
        )
        for s in solucoes_brutas
    ]

    melhor = solucoes[0]
    alertas = _gerar_alertas(dados, melhor, area_minima_da_face)

    return ResultadoDimensionamento(
        consumo_medio_individual=consumo_medio_individual,
        consumo_volumoso=consumo_volumoso,
        consumo_materia_natural=consumo_materia_natural,
        consumo_rebanho=consumo_rebanho,
        consumo_total=consumo_total,
        volume_a_ser_ensilado=volume_a_ser_ensilado,
        area_a_ser_plantada=area_a_ser_plantada,
        comprimento_operacional=comprimento_operacional,
        volume_total_necessario=volume_total_necessario,
        area_minima_da_face=area_minima_da_face,
        melhor_solucao=melhor,
        solucoes=solucoes,
        alertas=alertas,
        data_hora_simulacao=datetime.now().strftime("%d/%m/%Y %H:%M"),
    )