# -*- coding: utf-8 -*-
"""
Gera diagrama 2D do silo (seção transversal + vista lateral) com matplotlib.
Usado para embutir no PDF sem dependência do kaleido/Chromium.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


AZUL_PREENCH = "#AED6F1"
AZUL_BORDA = "#16324F"
CINZA_BG = "white"


def _desenhar_secao(ax, tipo: str, base: float, topo: float, altura: float) -> None:
    tipo_l = tipo.lower()

    if "oval" in tipo_l:
        from matplotlib.patches import Ellipse
        elipse = Ellipse(
            (0, altura / 2),
            width=base,
            height=altura,
            linewidth=2,
            edgecolor=AZUL_BORDA,
            facecolor=AZUL_PREENCH,
            alpha=0.55,
        )
        ax.add_patch(elipse)
        lim_x = base * 0.75
        lim_y_min = -altura * 0.35
        lim_y_max = altura * 1.35

    elif "trapez" in tipo_l:
        xs = [-base / 2, base / 2, topo / 2, -topo / 2, -base / 2]
        ys = [0, 0, altura, altura, 0]
        ax.fill(xs, ys, color=AZUL_PREENCH, alpha=0.55)
        ax.plot(xs, ys, color=AZUL_BORDA, linewidth=2)
        lim_x = max(base, topo) * 0.75
        lim_y_min = -altura * 0.35
        lim_y_max = altura * 1.6

    else:  # retangular
        rect = patches.Rectangle(
            (-base / 2, 0), base, altura,
            linewidth=2, edgecolor=AZUL_BORDA, facecolor=AZUL_PREENCH, alpha=0.55,
        )
        ax.add_patch(rect)
        lim_x = base * 0.75
        lim_y_min = -altura * 0.35
        lim_y_max = altura * 1.35

    # Cota horizontal (base)
    y_cota = -altura * 0.18
    ax.annotate(
        "", xy=(base / 2, y_cota), xytext=(-base / 2, y_cota),
        arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.2),
    )
    ax.text(0, y_cota - altura * 0.07, f"Base: {base:.2f} m",
            ha="center", va="top", fontsize=8.5, color="#333333")

    # Cota do topo (apenas para trapezoidal)
    if "trapez" in tipo_l and topo != base:
        y_cota_topo = altura + altura * 0.12
        ax.annotate(
            "", xy=(topo / 2, y_cota_topo), xytext=(-topo / 2, y_cota_topo),
            arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.2),
        )
        ax.text(0, y_cota_topo + altura * 0.05, f"Topo: {topo:.2f} m",
                ha="center", va="bottom", fontsize=8.5, color="#333333")

    # Cota vertical (altura)
    x_cota = base / 2 + base * 0.18
    ax.annotate(
        "", xy=(x_cota, altura), xytext=(x_cota, 0),
        arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.2),
    )
    ax.text(x_cota + base * 0.05, altura / 2, f"{altura:.2f} m",
            ha="left", va="center", fontsize=8.5, color="#333333")

    ax.set_xlim(-lim_x - base * 0.1, lim_x + base * 0.4)
    ax.set_ylim(lim_y_min, lim_y_max)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Seção Transversal", fontsize=10, fontweight="bold",
                 color=AZUL_BORDA, pad=8)


def _desenhar_lateral(ax, altura: float, comprimento: float) -> None:
    rect = patches.Rectangle(
        (0, 0), comprimento, altura,
        linewidth=2, edgecolor=AZUL_BORDA, facecolor="#D6EAF8", alpha=0.55,
    )
    ax.add_patch(rect)

    # Cota comprimento
    y_cota = -altura * 0.18
    ax.annotate(
        "", xy=(comprimento, y_cota), xytext=(0, y_cota),
        arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.2),
    )
    ax.text(comprimento / 2, y_cota - altura * 0.07, f"{comprimento:.2f} m",
            ha="center", va="top", fontsize=8.5, color="#333333")

    # Cota altura
    x_cota = comprimento + comprimento * 0.06
    ax.annotate(
        "", xy=(x_cota, altura), xytext=(x_cota, 0),
        arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.2),
    )
    ax.text(x_cota + comprimento * 0.02, altura / 2, f"{altura:.2f} m",
            ha="left", va="center", fontsize=8.5, color="#333333")

    ax.set_xlim(-comprimento * 0.08, comprimento * 1.22)
    ax.set_ylim(-altura * 0.35, altura * 1.35)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Vista Lateral", fontsize=10, fontweight="bold",
                 color=AZUL_BORDA, pad=8)


def gerar_diagrama_silo_bytes(
    tipo: str,
    largura_base_m: float,
    largura_topo_m: float,
    altura_m: float,
    comprimento_m: float,
) -> bytes:
    """Retorna bytes PNG do diagrama 2D do silo."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), facecolor=CINZA_BG)

    _desenhar_secao(ax1, tipo, largura_base_m, largura_topo_m, altura_m)
    _desenhar_lateral(ax2, altura_m, comprimento_m)

    fig.suptitle(
        f"Silo — {tipo}",
        fontsize=11, fontweight="bold", color=AZUL_BORDA, y=1.01,
    )
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=CINZA_BG)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def gerar_diagrama_silo_arquivo(
    tipo: str,
    largura_base_m: float,
    largura_topo_m: float,
    altura_m: float,
    comprimento_m: float,
    destino: Path,
) -> Path:
    """Salva o diagrama como PNG em `destino` e retorna o caminho."""
    dados = gerar_diagrama_silo_bytes(tipo, largura_base_m, largura_topo_m, altura_m, comprimento_m)
    destino.write_bytes(dados)
    return destino
