"""Annotate IR spectra to highlight the C-I band (~500 cm^-1).

Reactif (4-iodophenol, SP_IR1.png from ChemicalBook): a clear band near ~500 cm^-1.
Produit (SPECTRE_IR.jpeg, full-range 4000-400 cm^-1): no band at ~500 cm^-1.

Output: SP_IR1_annote.png and SPECTRE_IR_annote.png.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMG = os.path.join(ROOT, "output")

# Color for the annotation (red, high visibility)
ANNOT_COLOR = "#D62828"
LABEL_BG = "#FFFFFF"


def _setup_ax(ax, img, title=None):
    ax.imshow(img)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    if title:
        ax.set_title(title, fontsize=11, color="#333", pad=6)


def annotate_reactif(out_path):
    """SP_IR1.png — bande C-I bien visible.

    Le tracé occupe environ x in [0.05, 0.97], y in [0.05, 0.92].
    500 cm^-1 sur axe 4000->450 (decroissant) est a x ~0.96.
    La bande descend a ~50%T (y ~0.5 du tracé).
    """
    src = os.path.join(IMG, "SP_IR1.png")
    img = Image.open(src)
    W, H = img.size

    fig, ax = plt.subplots(figsize=(W / 100, H / 100), dpi=150)
    _setup_ax(ax, img)

    # Position de la bande C-I sur ce spectre (estimation visuelle)
    # axe X de 4000 (gauche) à 450 (droite). 500 cm^-1 = pic juste a droite
    # de ma position precedente (Hoff T11). cx pousse vers ~0.94.
    cx = 0.94 * W
    cy = 0.50 * H
    rx = 0.022 * W
    ry = 0.30 * H

    ellipse = patches.Ellipse(
        (cx, cy),
        width=2 * rx,
        height=2 * ry,
        linewidth=3,
        edgecolor=ANNOT_COLOR,
        facecolor="none",
    )
    ax.add_patch(ellipse)

    # Label "C-I" avec fond blanc
    ax.text(
        cx,
        0.13 * H,
        "C–I",
        fontsize=18,
        fontweight="bold",
        color=ANNOT_COLOR,
        ha="center",
        va="center",
        bbox=dict(facecolor=LABEL_BG, edgecolor=ANNOT_COLOR, boxstyle="round,pad=0.3", linewidth=2),
    )

    # Petite fleche du label vers l'ellipse
    arrow = FancyArrowPatch(
        (cx, 0.18 * H),
        (cx, cy - ry),
        arrowstyle="->",
        color=ANNOT_COLOR,
        linewidth=2,
        mutation_scale=15,
    )
    ax.add_patch(arrow)

    fig.tight_layout(pad=0)
    fig.savefig(out_path, dpi=150, pad_inches=0)
    plt.close(fig)
    print(f"[OK] {out_path}")


def annotate_produit(out_path):
    """SPECTRE_IR.jpeg — pas de bande C-I (bruit de fond a 500 cm^-1).

    Tracé full-range 4000-400 cm^-1.
    Le tracé occupe environ x in [0.08, 0.94], y in [0.05, 0.88].
    500 cm^-1 est a x ~0.90.
    """
    src = os.path.join(IMG, "SPECTRE_IR.jpeg")
    img = Image.open(src)
    W, H = img.size

    fig, ax = plt.subplots(figsize=(W / 100, H / 100), dpi=150)
    _setup_ax(ax, img)

    # Position attendue de la C-I (absente)
    # Recalibre: avec cx=0.80 on tombait sur 1000 cm^-1 (test precedent).
    # Donc 500 cm^-1 est nettement plus a droite.
    cx = 0.93 * W
    cy = 0.50 * H
    rx = 0.03 * W
    ry = 0.32 * H

    ellipse = patches.Ellipse(
        (cx, cy),
        width=2 * rx,
        height=2 * ry,
        linewidth=3,
        edgecolor=ANNOT_COLOR,
        facecolor="none",
        linestyle="--",
    )
    ax.add_patch(ellipse)

    # Croix au centre pour indiquer absence
    ax.plot(
        [cx - 0.012 * W, cx + 0.012 * W],
        [cy - 0.04 * H, cy + 0.04 * H],
        color=ANNOT_COLOR,
        linewidth=3,
    )
    ax.plot(
        [cx - 0.012 * W, cx + 0.012 * W],
        [cy + 0.04 * H, cy - 0.04 * H],
        color=ANNOT_COLOR,
        linewidth=3,
    )

    # Label "C-I absente" avec fond blanc
    label_x = cx - 0.15 * W
    label_y = 0.18 * H
    ax.text(
        label_x,
        label_y,
        "C–I absente",
        fontsize=15,
        fontweight="bold",
        color=ANNOT_COLOR,
        ha="center",
        va="center",
        bbox=dict(facecolor=LABEL_BG, edgecolor=ANNOT_COLOR, boxstyle="round,pad=0.3", linewidth=2),
    )

    # Fleche du label vers la zone
    arrow = FancyArrowPatch(
        (label_x + 0.07 * W, label_y),
        (cx - rx, cy - 0.5 * ry),
        arrowstyle="->",
        color=ANNOT_COLOR,
        linewidth=2,
        mutation_scale=15,
    )
    ax.add_patch(arrow)

    fig.tight_layout(pad=0)
    fig.savefig(out_path, dpi=150, pad_inches=0)
    plt.close(fig)
    print(f"[OK] {out_path}")


def main():
    annotate_reactif(os.path.join(IMG, "SP_IR1_annote.png"))
    annotate_produit(os.path.join(IMG, "SPECTRE_IR_annote.png"))


if __name__ == "__main__":
    main()
