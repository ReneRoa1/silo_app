# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class Projeto:
    nome: str
    responsavel_tecnico: str = ""
    propriedade: str = ""
    observacoes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EntradaDimensionamento:
    numero_animais: int
    peso_medio_kg: float
    consumo_percent_pv: float
    volumoso_percent: float
    teor_ms_percent: float
    perdas_percent: float
    produtividade_mn_t_ha: float
    periodo_dias: int
    desabastecimento_m_dia: float
    compactacao_t_m3: float
    tipo_estrutura: str
    tipo_secao: str
    largura_trator_m: float
    folga_lateral_m: float = 0.0
    passadas_min: int = 2
    passadas_max: int = 5
    altura_min_m: float = 2.0
    altura_max_m: float = 4.0
    passo_altura_m: float = 0.25
    talude_h_por_v: float = 0.0
    largura_topo_min_m: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SolucaoSilo:
    tipo: str
    largura_base_m: float
    largura_topo_m: float
    altura_m: float
    comprimento_m: float
    area_secao_m2: float
    face_m2: float
    volume_silo_m3: float
    excedente_m3: float
    passadas: int
    penalidade: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResultadoDimensionamento:
    consumo_medio_individual: float
    consumo_volumoso: float
    consumo_materia_natural: float
    consumo_rebanho: float
    consumo_total: float
    volume_a_ser_ensilado: float
    area_a_ser_plantada: float
    comprimento_operacional: float
    volume_total_necessario: float
    area_minima_da_face: float
    melhor_solucao: SolucaoSilo
    solucoes: List[SolucaoSilo]
    alertas: List[str]
    data_hora_simulacao: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)