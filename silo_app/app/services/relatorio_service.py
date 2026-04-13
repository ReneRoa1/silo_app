# -*- coding: utf-8 -*-
from __future__ import annotations

from app.domain.models import Projeto, EntradaDimensionamento, ResultadoDimensionamento
from app.reports.pdf_report import gerar_relatorio_pdf


def gerar_pdf_projeto(
    projeto: Projeto,
    entrada: EntradaDimensionamento,
    resultado: ResultadoDimensionamento,
    caminho_imagem_silo: str | None = None,
    caminho_logo: str | None = None,
) -> bytes:
    dados_entrada = {
        "Quantidade de animais": str(entrada.numero_animais),
        "Peso médio": f"{entrada.peso_medio_kg:.2f} kg",
        "Consumo de matéria seca": f"{entrada.consumo_percent_pv:.2f} % PV",
        "Participação do volumoso na dieta": f"{entrada.volumoso_percent:.2f} %",
        "Teor de matéria seca da forragem": f"{entrada.teor_ms_percent:.2f} %",
        "Perdas previstas": f"{entrada.perdas_percent:.2f} %",
        "Produtividade da forragem": f"{entrada.produtividade_mn_t_ha:.2f} t MN/ha",
        "Período de fornecimento": f"{entrada.periodo_dias} dias",
        "Taxa de desabastecimento": f"{entrada.desabastecimento_m_dia:.2f} m/dia",
        "Compactação da silagem": f"{entrada.compactacao_t_m3:.2f} t MN/m³",
        "Tipo estrutural do silo": entrada.tipo_estrutura,
        "Forma da seção transversal": entrada.tipo_secao,
        "Largura do trator": f"{entrada.largura_trator_m:.2f} m",
    }

    melhor = resultado.melhor_solucao
    resultados = {
        "Volume a ensilar": f"{resultado.volume_a_ser_ensilado:.2f} t MN",
        "Volume do silo": f"{resultado.volume_total_necessario:.2f} m³",
        "Área de plantio": f"{resultado.area_a_ser_plantada:.2f} ha",
        "Comprimento do silo": f"{resultado.comprimento_operacional:.2f} m",
        "Melhor tipo de silo": melhor.tipo,
        "Base menor": f"{melhor.largura_base_m:.2f} m",
        "Base maior ou topo": f"{melhor.largura_topo_m:.2f} m",
        "Altura": f"{melhor.altura_m:.2f} m",
        "Comprimento": f"{melhor.comprimento_m:.2f} m",
        "Número de passadas": str(melhor.passadas),
    }

    return gerar_relatorio_pdf(
        dados_entrada=dados_entrada,
        resultados=resultados,
        alertas=resultado.alertas,
        nome_projeto=projeto.nome,
        data_hora_simulacao=resultado.data_hora_simulacao,
        imagem_silo_path=caminho_imagem_silo,
        logo_path=caminho_logo,
        responsavel_tecnico=projeto.responsavel_tecnico or None,
    )