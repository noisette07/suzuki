#!/usr/bin/env python3
"""Génère schema_produit_2D.png : 4-hydroxybiphényle avec H labels colorés.

Dessin matplotlib from scratch :
- 2 cycles aromatiques (biphényle) avec liaisons alternées
- OH sur position para du cycle de droite
- 9 H aromatiques + 1 OH, chacun avec une couleur assortie au tableau RMN du slide

Couleurs (RGB) :
  rouge   = H ortho (2e cycle)    -> 7.52-7.58 ppm
  orange  = H méta (2e cycle)     -> 7.46-7.50 ppm
  bleu    = H méta à OH           -> 7.38-7.48 ppm
  violet  = H para (2e cycle)     -> 7.27-7.33 ppm
  vert    = H ortho à OH          -> 6.88-6.94 ppm
  marron  = O-H phénol            -> 4.89 ppm
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "_TEST"

# Palette daltonian-safe (Wong, Nature Methods 2011)
# Distinguables pour deutéranopes/protanopes (~8% des hommes)
C_HO_PHENYL = "#D55E00"   # vermillon    - H ortho (2e cycle, jonction)
C_HM_PHENYL = "#E69F00"   # orange-jaune - H méta (2e cycle)
C_HM_OH     = "#0072B2"   # bleu         - H méta à OH (= ortho jonction côté OH)
C_HP_PHENYL = "#CC79A7"   # rose-violet  - H para (2e cycle)
C_HO_OH     = "#009E73"   # vert-bleu    - H ortho à OH
C_OH        = "#785028"   # marron       - O-H phénol


def hexagon_vertices(center, radius=1.0, pointy_top=False):
    """Retourne les 6 sommets d'un hexagone régulier.

    pointy_top=False -> hexagone avec sommets gauche/droite (flat top/bottom).
    Ordre des sommets : commence à droite (3h) et tourne dans le sens trigo.
    """
    cx, cy = center
    offset = np.pi / 6 if pointy_top else 0
    angles = np.linspace(0, 2 * np.pi, 7)[:-1] + offset
    return [(cx + radius * np.cos(a), cy + radius * np.sin(a)) for a in angles]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 3.2))
    R = 1.0  # rayon hexagone

    # Cycle droit (avec OH) : centre à (2.5, 0)
    # Sommets numérotés 0-5 dans le sens trigonométrique en partant de la droite (3h)
    ring_R = hexagon_vertices((2.5, 0), R, pointy_top=False)
    # Cycle gauche (phényle) : centre à (0, 0)
    ring_L = hexagon_vertices((0, 0), R, pointy_top=False)

    # Liaisons du cycle droit (alternance simple/double)
    # Ring_R sommets : 0=droite, 1=haut-droite, 2=haut-gauche, 3=gauche, 4=bas-gauche, 5=bas-droite
    # OH attaché au sommet 0 (droite = position para vs jonction)
    # Jonction sommet 3 (gauche)
    # Liaisons doubles : (0-1), (2-3), (4-5)  [convention Kekule]
    double_bonds_R = [(0, 1), (2, 3), (4, 5)]
    single_bonds_R = [(1, 2), (3, 4), (5, 0)]

    # Cycle gauche : OHv-aucun, jonction sommet 0 (droite = jonction vers cycle droit)
    # Liaisons doubles : (1-2), (3-4), (5-0)
    double_bonds_L = [(1, 2), (3, 4), (5, 0)]
    single_bonds_L = [(0, 1), (2, 3), (4, 5)]

    def draw_bond(p1, p2, double=False, lw=2.0):
        x1, y1 = p1
        x2, y2 = p2
        if not double:
            ax.plot([x1, x2], [y1, y2], color="black", lw=lw, solid_capstyle="round")
        else:
            # Liaison double : deux lignes parallèles
            dx, dy = x2 - x1, y2 - y1
            length = np.hypot(dx, dy)
            # Vecteur perpendiculaire normalisé
            px, py = -dy / length, dx / length
            offset = 0.08
            # Ligne 1 : centrale (un peu plus courte)
            shrink = 0.05
            ux, uy = dx / length, dy / length
            ax.plot([x1 + shrink * dx, x2 - shrink * dx],
                    [y1 + shrink * dy, y2 - shrink * dy],
                    color="black", lw=lw, solid_capstyle="round")
            # Ligne 2 : décalée
            ax.plot([x1 + offset * px + shrink * dx, x2 + offset * px - shrink * dx],
                    [y1 + offset * py + shrink * dy, y2 + offset * py - shrink * dy],
                    color="black", lw=lw, solid_capstyle="round")

    # Dessine cycle droit
    for i, j in single_bonds_R:
        draw_bond(ring_R[i], ring_R[j], double=False)
    for i, j in double_bonds_R:
        draw_bond(ring_R[i], ring_R[j], double=True)

    # Dessine cycle gauche
    for i, j in single_bonds_L:
        draw_bond(ring_L[i], ring_L[j], double=False)
    for i, j in double_bonds_L:
        draw_bond(ring_L[i], ring_L[j], double=True)

    # Liaison inter-cycles : sommet 3 (gauche) du cycle droit -- sommet 0 (droite) du cycle gauche
    draw_bond(ring_R[3], ring_L[0], double=False)

    # OH attaché au sommet 0 (droite) du cycle droit
    oh_anchor = ring_R[0]
    oh_dx, oh_dy = 0.85, 0
    oh_pos = (oh_anchor[0] + oh_dx, oh_anchor[1] + oh_dy)
    draw_bond(oh_anchor, oh_pos, double=False)
    ax.text(oh_pos[0] + 0.15, oh_pos[1], "OH",
            color=C_OH, fontsize=18, fontweight="bold",
            ha="left", va="center")

    # H labels colorés sur cycle droit
    # Cycle droit, sommets sans substituant : 1 (haut-droite), 2 (haut-gauche), 4 (bas-gauche), 5 (bas-droite)
    # 1 et 5 = ortho à OH (proches du sommet 0=OH)  -> vert
    # 2 et 4 = méta à OH (loin de OH, proches de jonction sommet 3) -> bleu
    H_RIGHT = [
        (1, C_HO_OH),    # haut-droite, ortho OH
        (2, C_HM_OH),    # haut-gauche, méta OH (= ortho jonction)
        (4, C_HM_OH),    # bas-gauche, méta OH (= ortho jonction)
        (5, C_HO_OH),    # bas-droite, ortho OH
    ]
    for vertex_idx, color in H_RIGHT:
        v = ring_R[vertex_idx]
        # Direction du label : vers l'extérieur de l'hexagone
        cx, cy = 2.5, 0
        dx, dy = v[0] - cx, v[1] - cy
        norm = np.hypot(dx, dy)
        label_pos = (v[0] + 0.5 * dx / norm, v[1] + 0.5 * dy / norm)
        ax.text(label_pos[0], label_pos[1], "H",
                color=color, fontsize=18, fontweight="bold",
                ha="center", va="center")

    # H labels colorés sur cycle gauche
    # Cycle gauche, sommets sans substituant : 1, 2, 3, 4, 5
    # Sommet 0 = jonction
    # Sommet 3 = para (loin de jonction)        -> violet
    # Sommets 1, 5 = ortho jonction              -> rouge
    # Sommets 2, 4 = méta jonction               -> orange
    H_LEFT = [
        (1, C_HO_PHENYL),  # haut-droite, ortho jonction (haut)
        (2, C_HM_PHENYL),  # haut-gauche, méta jonction
        (3, C_HP_PHENYL),  # gauche, para
        (4, C_HM_PHENYL),  # bas-gauche, méta jonction
        (5, C_HO_PHENYL),  # bas-droite, ortho jonction (bas)
    ]
    for vertex_idx, color in H_LEFT:
        v = ring_L[vertex_idx]
        cx, cy = 0, 0
        dx, dy = v[0] - cx, v[1] - cy
        norm = np.hypot(dx, dy)
        label_pos = (v[0] + 0.5 * dx / norm, v[1] + 0.5 * dy / norm)
        ax.text(label_pos[0], label_pos[1], "H",
                color=color, fontsize=18, fontweight="bold",
                ha="center", va="center")

    # Mise en page
    ax.set_xlim(-2.2, 5.0)
    ax.set_ylim(-1.8, 1.8)
    ax.set_aspect("equal")
    ax.axis("off")

    out_path = OUT_DIR / "schema_produit_2D.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[OK] -> {out_path}")


if __name__ == "__main__":
    main()
