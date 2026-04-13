# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class Rebanho:
    numero_animais: int
    peso_medio_kg: float
    consumo_percent_pv: float


@dataclass
class Dieta:
    volumoso_percent: float


@dataclass
class Forragem:
    teor_ms_percent: float
    perdas_percent: float
    produtividade_mn_t_ha: float


@dataclass
class Operacao:
    periodo_dias: int
    desabastecimento_m_dia: float
    compactacao_t_m3: float
    largura_trator_m: float


def calcular_cmi(peso_medio_kg: float, consumo_percent_pv: float) -> float:
    return peso_medio_kg * (consumo_percent_pv / 100.0)


def calcular_cvo(cmi_kg_ms: float, volumoso_percent: float) -> float:
    return cmi_kg_ms * (volumoso_percent / 100.0)


def calcular_cmn(cvo_kg_ms: float, teor_ms_percent: float) -> float:
    return cvo_kg_ms / (teor_ms_percent / 100.0)


def calcular_cr(cmn_kg_mn: float, numero_animais: int) -> float:
    return cmn_kg_mn * numero_animais


def calcular_ct(cr_kg_dia: float, periodo_dias: int) -> float:
    return cr_kg_dia * periodo_dias


def calcular_ve_t(ct_kg: float, perdas_percent: float) -> float:
    ct_t = ct_kg / 1000.0
    return ct_t * 100.0 / (100.0 - perdas_percent)


def calcular_ap_ha(ve_t_mn: float, produtividade_t_ha: float) -> float:
    return ve_t_mn / produtividade_t_ha


def calcular_comprimento_operacional(desabastecimento_m_dia: float, periodo_dias: int) -> float:
    return desabastecimento_m_dia * periodo_dias


def calcular_volume_total_silo(ve_t_mn: float, compactacao_t_m3: float) -> float:
    return ve_t_mn / compactacao_t_m3


def calcular_face_minima(cr_kg_dia: float, compactacao_t_m3: float, desabastecimento_m_dia: float) -> float:
    densidade_kg_m3 = compactacao_t_m3 * 1000.0
    return cr_kg_dia / (densidade_kg_m3 * desabastecimento_m_dia)
