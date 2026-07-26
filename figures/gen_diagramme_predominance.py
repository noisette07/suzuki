#!/usr/bin/env python3
"""Genere diagramme_predominance.png : axe pH avec molecules topologiques.

Diagramme :
- Axe pH 0 -> 14
- pKa = 9,5 (4-hydroxybiphenyle)
- Gauche (pH < 9,5) : ArOH forme moleculaire (precipite en milieu acide)
- Droite (pH > 9,5) : ArO- forme ionique (soluble en milieu basique)

Molecules dessinees from scratch en topologique (sans heteroatomes implicites)
pour rester coherent avec gen_schema_produit.py.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output"

# Palette Wong (daltonian-safe)
C_ACID = "#FDE8DC"   # fond rose pale (domaine acide)
C_BASE = "#E6F0F5"   # fond bleu pale (domaine basique)
C_PKA  = "#4A7C59"   # vert primaire pour la ligne pKa
C_OH   = "#785028"   # marron pour le OH (coherent avec schema produit)
C_O    = "#0072B2"   # bleu pour le O- (forme ionique)
C_BOND = "#333333"   # liaisons noir-gris


def hexagon_vertices(center, radius=1.0):
    """6 sommets d'un hexagone regulier flat-top. Sens trigo a partir de 3h."""
    cx, cy = center
    angles = np.linspace(0, 2 * np.pi, 7)[:-1]
    return [(cx + radius * np.cos(a), cy + radius * np.sin(a)) for a in angles]


def draw_bond(ax, p1, p2, double=False, lw=1.5):
    x1, y1 = p1
    x2, y2 = p2
    if not double:
        ax.plot([x1, x2], [y1, y2], color=C_BOND, lw=lw, solid_capstyle="round")
    else:
        dx, dy = x2 - x1, y2 - y1
        length = np.hypot(dx, dy)
        px, py = -dy / length, dx / length
        offset = 0.06
        shrink = 0.05
        ax.plot([x1 + shrink * dx, x2 - shrink * dx],
                [y1 + shrink * dy, y2 - shrink * dy],
                color=C_BOND, lw=lw, solid_capstyle="round")
        ax.plot([x1 + offset * px + shrink * dx, x2 + offset * px - shrink * dx],
                [y1 + offset * py + shrink * dy, y2 + offset * py - shrink * dy],
                color=C_BOND, lw=lw, solid_capstyle="round")


def draw_biphenyl(ax, center_x, center_y, scale=0.55, charged=False):
    """Dessine 4-hydroxybiphenyle (charged=False) ou phenolate (charged=True).

    Structure : cycle gauche (phenyle) + cycle droit (avec OH ou O-).
    Le OH/O- est porte par le sommet droite du cycle droit.
    """
    R = scale
    # Cycle gauche : centre (cx - 1.7*R, cy)
    ring_L = hexagon_vertices((center_x - 1.7 * R, center_y), R)
    # Cycle droit : centre (cx + 0.5*R, cy)
    ring_R = hexagon_vertices((center_x + 0.5 * R, center_y), R)

    # Liaisons cycle gauche (Kekule)
    double_bonds_L = [(1, 2), (3, 4), (5, 0)]
    single_bonds_L = [(0, 1), (2, 3), (4, 5)]
    for i, j in single_bonds_L:
        draw_bond(ax, ring_L[i], ring_L[j], double=False)
    for i, j in double_bonds_L:
        draw_bond(ax, ring_L[i], ring_L[j], double=True)

    # Liaisons cycle droit (Kekule)
    double_bonds_R = [(0, 1), (2, 3), (4, 5)]
    single_bonds_R = [(1, 2), (3, 4), (5, 0)]
    for i, j in single_bonds_R:
        draw_bond(ax, ring_R[i], ring_R[j], double=False)
    for i, j in double_bonds_R:
        draw_bond(ax, ring_R[i], ring_R[j], double=True)

    # Liaison inter-cycles : sommet 3 (gauche) du cycle droit -- sommet 0 (droite) du cycle gauche
    draw_bond(ax, ring_R[3], ring_L[0], double=False)

    # Groupement OH ou O- sur le sommet 0 (droite) du cycle droit
    oh_anchor = ring_R[0]
    oh_dx, oh_dy = 0.45 * R, 0
    oh_pos = (oh_anchor[0] + oh_dx, oh_anchor[1] + oh_dy)
    draw_bond(ax, oh_anchor, oh_pos, double=False)
    if charged:
        ax.text(oh_pos[0] + 0.18 * R, oh_pos[1], "O⁻",
                color=C_O, fontsize=20, fontweight="bold",
                ha="left", va="center")
    else:
        ax.text(oh_pos[0] + 0.18 * R, oh_pos[1], "OH",
                color=C_OH, fontsize=20, fontweight="bold",
                ha="left", va="center")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 3.2))

    # Bandes de fond : domaines acide / basique
    ax.axvspan(0, 9.5, color=C_ACID, alpha=0.7, zorder=0)
    ax.axvspan(9.5, 14, color=C_BASE, alpha=0.7, zorder=0)

    # Ligne pKa
    ax.axvline(9.5, color=C_PKA, lw=2.5, zorder=2)
    # pKa libelle SOUS l'echelle (sous l'axe pH), pas au-dessus
    ax.text(9.5, -0.18, "pKₐ = 9,5", color=C_PKA, fontsize=13, fontweight="bold",
            ha="center", va="top", transform=ax.get_xaxis_transform())

    # Axe pH (graduations)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 1)
    ax.set_xticks(range(0, 15, 1))
    ax.set_xticklabels([str(i) for i in range(0, 15)], fontsize=10)
    ax.set_yticks([])
    ax.set_xlabel("pH", fontsize=13, fontweight="bold")

    # Bordures (style propre)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_linewidth(1.5)
    ax.tick_params(axis="x", length=6, width=1.2)

    # Etiquettes des domaines (au-dessus des molecules)
    ax.text(4.75, 0.78, "Forme moléculaire (ArOH)",
            fontsize=11, fontweight="bold", color=C_OH,
            ha="center", va="center")
    ax.text(11.75, 0.78, "Forme ionique (ArO⁻)",
            fontsize=11, fontweight="bold", color=C_O,
            ha="center", va="center")

    # Molecules topologiques dans chaque domaine
    # Coordonnees des centres en unites de l'axe (pH, y_normalise)
    # On utilise des inset ax pour des molecules avec un aspect ratio correct
    inset_left = ax.inset_axes([0.15, 0.12, 0.38, 0.62])
    inset_left.set_xlim(-3, 3)
    inset_left.set_ylim(-1, 1)
    inset_left.set_aspect("equal")
    inset_left.axis("off")
    draw_biphenyl(inset_left, center_x=0, center_y=0, scale=0.80, charged=False)

    inset_right = ax.inset_axes([0.66, 0.12, 0.32, 0.62])
    inset_right.set_xlim(-3, 3)
    inset_right.set_ylim(-1, 1)
    inset_right.set_aspect("equal")
    inset_right.axis("off")
    draw_biphenyl(inset_right, center_x=0, center_y=0, scale=0.80, charged=True)

    # Annotations sous les molecules
    ax.text(4.75, 0.05, "précipite en milieu acide",
            fontsize=9, fontstyle="italic", color="#555",
            ha="center", va="center")
    ax.text(11.75, 0.05, "soluble en milieu basique",
            fontsize=9, fontstyle="italic", color="#555",
            ha="center", va="center")

    out_path = OUT_DIR / "diagramme_predominance.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white", pad_inches=0.15)
    plt.close(fig)
    print(f"[OK] -> {out_path}")


if __name__ == "__main__":
    main()
