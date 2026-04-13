# -*- coding: utf-8 -*-
import math


def area_secao_retangular(largura_m: float, altura_m: float) -> float:
    return largura_m * altura_m


def area_secao_trapezio(base_menor_m: float, base_maior_m: float, altura_m: float) -> float:
    return (base_menor_m + base_maior_m) * altura_m / 2.0


def base_maior_trapezio(base_menor_m: float, altura_m: float, talude_h_por_v: float) -> float:
    return base_menor_m + 2.0 * talude_h_por_v * altura_m


def area_secao_superficie_oval(largura_base_m: float, altura_m: float) -> float:
    semi_eixo_horizontal = largura_base_m / 2.0
    semi_eixo_vertical = altura_m
    return 0.5 * math.pi * semi_eixo_horizontal * semi_eixo_vertical
