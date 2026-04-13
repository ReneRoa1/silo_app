# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List, Tuple

from geometrias import (
    area_secao_retangular,
    area_secao_trapezio,
    area_secao_superficie_oval,
    base_maior_trapezio,
)


@dataclass
class SolucaoSilo:
    tipo: str
    largura_base_m: float
    largura_topo_m: float
    altura_m: float
    comprimento_m: float
    area_secao_m2: float
    volume_silo_m3: float
    face_m2: float
    excedente_m3: float
    penalidade: float
    passadas: int


def gerar_larguras_candidatas(
    largura_trator_m: float,
    passadas_min: int = 2,
    passadas_max: int = 5,
    folga_lateral_m: float = 0.0,
) -> List[Tuple[float, int]]:
    candidatas = []
    for passadas in range(passadas_min, passadas_max + 1):
        largura = largura_trator_m * passadas + folga_lateral_m
        candidatas.append((round(largura, 2), passadas))
    return candidatas


def otimizar_secao_retangular(
    volume_necessario_m3: float,
    comprimento_operacional_m: float,
    face_minima_m2: float,
    largura_trator_m: float,
    altura_min_m: float,
    altura_max_m: float,
    passo_altura_m: float,
    passadas_min: int,
    passadas_max: int,
    folga_lateral_m: float,
    tipo_estrutura: str,
) -> List[SolucaoSilo]:
    solucoes = []

    # Area da secao = volume / comprimento
    area_secao_necessaria = volume_necessario_m3 / comprimento_operacional_m

    altura = altura_min_m
    while altura <= altura_max_m + 1e-9:
        # Largura do retangulo calculada pela area conhecida
        largura = area_secao_necessaria / altura

        if largura <= 0:
            altura += passo_altura_m
            continue

        face = area_secao_necessaria

        if face < face_minima_m2:
            altura += passo_altura_m
            continue

        comprimento_final = comprimento_operacional_m
        volume_silo = area_secao_necessaria * comprimento_final
        excedente = volume_silo - volume_necessario_m3

        if excedente < 0:
            altura += passo_altura_m
            continue

        penalidade = 0.0
        penalidade += excedente * 2.0
        penalidade += comprimento_final * 0.5

        if altura > 3.5:
            penalidade += (altura - 3.5) * 25.0

        if comprimento_final > 40:
            penalidade += (comprimento_final - 40) * 10.0

        solucoes.append(
            SolucaoSilo(
                tipo=f"{tipo_estrutura} - Retangular",
                largura_base_m=round(largura, 2),
                largura_topo_m=round(largura, 2),
                altura_m=round(altura, 2),
                comprimento_m=round(comprimento_final, 2),
                area_secao_m2=round(area_secao_necessaria, 2),
                volume_silo_m3=round(volume_silo, 2),
                face_m2=round(face, 2),
                excedente_m3=round(excedente, 2),
                penalidade=round(penalidade, 2),
                passadas=1,
            )
        )

        altura += passo_altura_m

    solucoes.sort(key=lambda s: s.penalidade)
    return solucoes


def otimizar_secao_trapezoidal(
    volume_necessario_m3: float,
    comprimento_operacional_m: float,
    face_minima_m2: float,
    largura_trator_m: float,
    altura_min_m: float,
    altura_max_m: float,
    passo_altura_m: float,
    passadas_min: int,
    passadas_max: int,
    folga_lateral_m: float,
    talude_h_por_v: float,
    largura_topo_min_m: float,
    tipo_estrutura: str,
) -> List[SolucaoSilo]:
    solucoes = []

    # Area da secao = volume / comprimento
    area_secao_necessaria = volume_necessario_m3 / comprimento_operacional_m

    # Para silo trincheira, limitar altura maxima em 3,0 m
    if tipo_estrutura.strip().lower() == "trincheira":
        altura_max_util = min(altura_max_m, 3.0)
    else:
        altura_max_util = altura_max_m

    altura = altura_min_m
    while altura <= altura_max_util + 1e-9:
        # Nova regra:
        # B = b + 0.5 * h
        # A = ((B + b) * h) / 2
        # A = ((b + 0.5h + b) * h) / 2
        # A = ((2b + 0.5h) * h) / 2
        # A = b*h + 0.25*h^2
        # b = (A - 0.25*h^2) / h

        base_menor = (area_secao_necessaria - 0.25 * altura * altura) / altura
        base_maior = base_menor + 0.5 * altura

        # Descarta geometrias impossiveis
        if base_menor <= 0 or base_maior <= 0:
            altura += passo_altura_m
            continue

        # Recalcula a area para conferir
        area_secao = ((base_maior + base_menor) * altura) / 2
        face = area_secao

        if face < face_minima_m2:
            altura += passo_altura_m
            continue

        comprimento_final = comprimento_operacional_m
        volume_silo = area_secao * comprimento_final
        excedente = volume_silo - volume_necessario_m3

        if excedente < 0:
            altura += passo_altura_m
            continue

        penalidade = 0.0
        penalidade += excedente * 2.0
        penalidade += comprimento_final * 0.5
        penalidade += abs(base_maior - base_menor) * 0.7

        if altura > 3.0:
            penalidade += (altura - 3.0) * 25.0

        if comprimento_final > 40:
            penalidade += (comprimento_final - 40) * 10.0

        solucoes.append(
            SolucaoSilo(
                tipo=f"{tipo_estrutura} - Trapezoidal",
                largura_base_m=round(base_menor, 2),
                largura_topo_m=round(base_maior, 2),
                altura_m=round(altura, 2),
                comprimento_m=round(comprimento_final, 2),
                area_secao_m2=round(area_secao, 2),
                volume_silo_m3=round(volume_silo, 2),
                face_m2=round(face, 2),
                excedente_m3=round(excedente, 2),
                penalidade=round(penalidade, 2),
                passadas=1,
            )
        )

        altura += passo_altura_m

    solucoes.sort(key=lambda s: s.penalidade)
    return solucoes


def otimizar_secao_ovalada(
    volume_necessario_m3: float,
    comprimento_operacional_m: float,
    face_minima_m2: float,
    largura_trator_m: float,
    altura_min_m: float,
    altura_max_m: float,
    passo_altura_m: float,
    passadas_min: int,
    passadas_max: int,
    folga_lateral_m: float,
    largura_base_min_m: float,
    tipo_estrutura: str,
) -> List[SolucaoSilo]:
    solucoes = []
    larguras = gerar_larguras_candidatas(
        largura_trator_m, passadas_min, passadas_max, folga_lateral_m
    )

    altura = altura_min_m
    while altura <= altura_max_m + 1e-9:
        for largura_base, passadas in larguras:
            if largura_base < largura_base_min_m:
                continue

            area_secao = area_secao_superficie_oval(largura_base, altura)
            face = area_secao
            comprimento_por_volume = volume_necessario_m3 / area_secao
            comprimento_final = max(comprimento_por_volume, comprimento_operacional_m)
            volume_silo = area_secao * comprimento_final
            excedente = volume_silo - volume_necessario_m3

            penalidade = 0.0
            penalidade += excedente * 2.0
            penalidade += comprimento_final * 0.5
            penalidade += altura * 0.8
            if face < face_minima_m2:
                penalidade += 10000.0
            if altura > 3.0:
                penalidade += (altura - 3.0) * 35.0
            if comprimento_final > 50:
                penalidade += (comprimento_final - 50) * 8.0

            solucoes.append(
                SolucaoSilo(
                    tipo=f"{tipo_estrutura} - Ovalada",
                    largura_base_m=round(largura_base, 2),
                    largura_topo_m=0.0,
                    altura_m=round(altura, 2),
                    comprimento_m=round(comprimento_final, 2),
                    area_secao_m2=round(area_secao, 2),
                    volume_silo_m3=round(volume_silo, 2),
                    face_m2=round(face, 2),
                    excedente_m3=round(excedente, 2),
                    penalidade=round(penalidade, 2),
                    passadas=passadas,
                )
            )
        altura += passo_altura_m

    solucoes.sort(key=lambda s: s.penalidade)
    return solucoes
