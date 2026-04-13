# -*- coding: utf-8 -*-
import math
import plotly.graph_objects as go


def criar_solido_prismatico(largura_base: float, largura_topo: float, altura: float, comprimento: float):
    x = [
        0, largura_base, largura_base, 0,
        (largura_base - largura_topo) / 2.0,
        (largura_base + largura_topo) / 2.0,
        (largura_base + largura_topo) / 2.0,
        (largura_base - largura_topo) / 2.0,
    ]
    y = [0, 0, comprimento, comprimento, 0, 0, comprimento, comprimento]
    z = [0, 0, 0, 0, altura, altura, altura, altura]

    i = [0, 0, 0, 4, 4, 1, 2, 3, 0, 1, 6, 7]
    j = [1, 2, 3, 5, 6, 5, 6, 7, 4, 5, 2, 3]
    k = [2, 3, 1, 6, 7, 6, 7, 4, 5, 6, 7, 4]

    return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, opacity=0.6)


def criar_solido_superficie_oval(largura_base: float, altura: float, comprimento: float, n_pontos: int = 40):
    xs, ys, zs = [], [], []

    for y in [0.0, comprimento]:
        for i in range(n_pontos + 1):
            t = math.pi * i / n_pontos
            x = (largura_base / 2.0) * (1 + math.cos(t))
            z = altura * math.sin(t)
            xs.append(x)
            ys.append(y)
            zs.append(z)

    ii, jj, kk = [], [], []
    offset = n_pontos + 1
    for i in range(n_pontos):
        a = i
        b = i + 1
        c = offset + i
        d = offset + i + 1
        ii.extend([a, b])
        jj.extend([b, d])
        kk.extend([c, c])

    return go.Mesh3d(x=xs, y=ys, z=zs, i=ii, j=jj, k=kk, opacity=0.6)
