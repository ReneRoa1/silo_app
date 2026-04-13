# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


AZUL_ESCURO = colors.HexColor("#16324F")
AZUL_CLARO = colors.HexColor("#EAF1F8")
CINZA_CLARO = colors.HexColor("#F4F4F5")
VERMELHO_CLARO = colors.HexColor("#FDECEC")
VERMELHO_TEXTO = colors.HexColor("#B42318")


def _linhas_de_campo(campos: Dict[str, str]) -> list[list[str]]:
    return [[chave, str(valor)] for chave, valor in campos.items()]


def _tabela_campos(campos: Dict[str, str], larguras=(6.0 * cm, 11.8 * cm)) -> Table:
    dados = _linhas_de_campo(campos)
    tabela = Table(dados, colWidths=list(larguras), hAlign="LEFT")
    estilo = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, CINZA_CLARO]),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#BBBBBB")),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D0D0D0")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )
    tabela.setStyle(estilo)
    return tabela


def _titulo_secao(texto: str) -> Table:
    tabela = Table([[texto]], colWidths=[17.8 * cm], hAlign="LEFT")
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), AZUL_CLARO),
                ("TEXTCOLOR", (0, 0), (-1, -1), AZUL_ESCURO),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("BOX", (0, 0), (-1, -1), 0, colors.white),
            ]
        )
    )
    return tabela


def _tabela_alertas(alertas: Iterable[str]) -> Table:
    lista_alertas = list(alertas)
    if not lista_alertas:
        lista_alertas = ["Nenhum alerta automático foi identificado."]
        fundo = CINZA_CLARO
        cor_texto = colors.black
    else:
        fundo = VERMELHO_CLARO
        cor_texto = VERMELHO_TEXTO

    dados = [[f"â¢ {item}"] for item in lista_alertas]
    tabela = Table(dados, colWidths=[17.8 * cm], hAlign="LEFT")
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), fundo),
                ("TEXTCOLOR", (0, 0), (-1, -1), cor_texto),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D5DD")),
            ]
        )
    )
    return tabela


def _bloco_cabecalho(
    nome_projeto: str,
    data_hora_simulacao: str,
    logo_path: Optional[str] = None,
) -> Table:
    styles = getSampleStyleSheet()
    estilo_titulo = styles["Heading2"]
    estilo_titulo.fontName = "Helvetica-Bold"
    estilo_titulo.fontSize = 13
    estilo_titulo.textColor = colors.white
    estilo_titulo.leading = 16
    estilo_normal = styles["BodyText"]
    estilo_normal.fontName = "Helvetica"
    estilo_normal.fontSize = 9
    estilo_normal.textColor = colors.white
    estilo_normal.leading = 12

    if logo_path is not None and Path(logo_path).exists():
        logo = Image(logo_path, width=2.2 * cm, height=2.2 * cm)
    else:
        logo = Paragraph("<b>UFMS</b>", estilo_normal)

    titulo = Paragraph("Relatório de Dimensionamento de Silo para Silagem", estilo_titulo)
    info = Paragraph(f"<b>Projeto:</b> {nome_projeto}<br/><b>Simulação:</b> {data_hora_simulacao}", estilo_normal,)

    tabela = Table(
        [[logo, titulo, info]],
        colWidths=[2.8 * cm, 9.2 * cm, 5.8 * cm],
        hAlign="LEFT",
    )
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), AZUL_ESCURO),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0, colors.white),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return tabela


def _quadro_resumo(resultados: Dict[str, str]) -> Table:
    chaves = list(resultados.keys())
    valores = list(resultados.values())

    pares = []
    for i in range(0, len(chaves), 2):
        esquerda_titulo = chaves[i]
        esquerda_valor = valores[i]
        if i + 1 < len(chaves):
            direita_titulo = chaves[i + 1]
            direita_valor = valores[i + 1]
        else:
            direita_titulo = ""
            direita_valor = ""
        pares.append([esquerda_titulo, esquerda_valor, direita_titulo, direita_valor])

    tabela = Table(
        pares,
        colWidths=[4.0 * cm, 4.9 * cm, 4.0 * cm, 4.9 * cm],
        hAlign="LEFT",
    )
    tabela.setStyle(
        TableStyle(
            [
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, CINZA_CLARO]),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#BBBBBB")),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D0D0D0")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return tabela


def gerar_relatorio_pdf(
    dados_entrada: Dict[str, str],
    resultados: Dict[str, str],
    alertas: Iterable[str],
    nome_projeto: str,
    data_hora_simulacao: Optional[str] = None,
    imagem_silo_path: Optional[str] = None,
    logo_path: Optional[str] = None,
    responsavel_tecnico: Optional[str] = None,
) -> bytes:
    if not data_hora_simulacao:
        data_hora_simulacao = datetime.now().strftime("%d/%m/%Y %H:%M")

    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    elementos = []
    elementos.append(_bloco_cabecalho(nome_projeto, data_hora_simulacao, logo_path=logo_path))
    elementos.append(Spacer(1, 0.35 * cm))

    identificacao = {
        "Projeto": nome_projeto,
        "Data/Hora": data_hora_simulacao,
        "Responsável técnico": responsavel_tecnico or "Não informado",
    }
    elementos.append(_titulo_secao("Identificação"))
    elementos.append(_tabela_campos(identificacao, larguras=(6.0 * cm, 11.8 * cm)))
    elementos.append(Spacer(1, 0.3 * cm))

    elementos.append(_titulo_secao("Resumo do dimensionamento"))
    elementos.append(_quadro_resumo(resultados))
    elementos.append(Spacer(1, 0.3 * cm))

    elementos.append(_titulo_secao("Dados de entrada"))
    elementos.append(_tabela_campos(dados_entrada, larguras=(6.0 * cm, 11.8 * cm)))
    elementos.append(Spacer(1, 0.3 * cm))

    elementos.append(_titulo_secao("Alertas e observações"))
    elementos.append(_tabela_alertas(alertas))
    elementos.append(Spacer(1, 0.3 * cm))

    if imagem_silo_path is not None and Path(imagem_silo_path).exists():
        elementos.append(_titulo_secao("Visualização do silo"))
        elementos.append(Image(imagem_silo_path, width=15.5 * cm, height=8.0 * cm))
        elementos.append(Spacer(1, 0.25 * cm))

    rodape = Table(
        [["Relatório gerado automaticamente pelo sistema"]],
        colWidths=[17.8 * cm],
        hAlign="LEFT",
    )
    rodape.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#667085")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Oblique"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elementos.append(rodape)

    documento.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()
