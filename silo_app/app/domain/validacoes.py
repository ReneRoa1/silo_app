# -*- coding: utf-8 -*-
from app.domain.models import EntradaDimensionamento


def validar_entrada(dados: EntradaDimensionamento) -> None:
    if dados.numero_animais < 1:
        raise ValueError("A quantidade de animais deve ser maior que zero.")

    if dados.altura_max_m < dados.altura_min_m:
        raise ValueError("A altura máxima não pode ser menor que a altura mínima.")

    if dados.passo_altura_m <= 0:
        raise ValueError("O passo de altura deve ser maior que zero.")

    if dados.compactacao_t_m3 <= 0:
        raise ValueError("A compactação deve ser maior que zero.")

    if dados.teor_ms_percent <= 0:
        raise ValueError("O teor de matéria seca deve ser maior que zero.")