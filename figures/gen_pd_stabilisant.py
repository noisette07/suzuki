#!/usr/bin/env python3
"""Genere pd_stabilisant.png : pourquoi le stabilisant du Pd compte (vraie chimie).

Schema chimique en deux panneaux cote a cote, base sur la these de Peramo
(catalyseur RETENU = PVP-Pd, non PLGA-PEG) :

  GAUCHE  : Pd0 nu en milieu biologique. Deux problemes documentes :
            (1) sequestration non specifique par les briques biologiques
                porteuses de N / S / O (Peramo) ; le soufre est le pire
                ligand (chimie generale : HSAB mou-mou, liaison Pd-S forte).
            (2) agregation des NP non stabilisees (Peramo : ilots de Pd).
            -> sites satures, l'addition oxydante Pd0 + Ar-I n'a plus lieu.

  DROITE  : Pd0 enrobe dans la matrice PVP ("embedded in the polymer",
            Peramo). La matrice polymere limite le binding non specifique
            des biomolecules et empeche l'agregation, tout en laissant le
            petit substrat Ar-I atteindre le Pd -> AO -> cycle Suzuki a
            37 C, pH 7. PVP = excipient non cytotoxique (IC50 > 1 mM).

Sourcing (etiquete dans la legende du slide / speech) :
  - Faits Peramo : enrobage dans le polymere, agregation, IC50, AO.
  - Chimie generale ajoutee : HSAB / Pd-S ~250 kJ/mol, encombrement sterique.

Cible : ~1400 x 700 px (figsize 10.5 x 5 a 200 dpi).
Palette Wong (daltonian-safe).
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output"

# Palette Wong + couleurs metier
C_BOND     = "#333333"
C_PD       = "#2B2B2B"
C_PD_LABEL = "#FFFFFF"
C_S        = "#E69F00"   # soufre (mou, le pire)
C_N        = "#0072B2"   # azote
C_O        = "#D55E00"   # oxygene
C_I        = "#CC79A7"
C_PVP      = "#785028"   # matrice PVP
C_OK       = "#009E73"
C_KO       = "#D55E00"
C_TEXT     = "#4A4A4A"

C_BG_KO    = "#FDEDE5"
C_BG_OK    = "#E5F0EA"


def draw_pd_atom(ax, center, radius=0.30, label="Pd⁰"):
    cx, cy = center
    circle = Circle((cx, cy), radius, facecolor=C_PD, edgecolor=C_BOND,
                    lw=1.5, zorder=6)
    ax.add_patch(circle)
    ax.text(cx, cy, label, color=C_PD_LABEL, fontsize=11, fontweight="bold",
            ha="center", va="center", zorder=7)


def draw_donor(ax, anchor, atom, color, direction=(1, 0)):
    """Petite brique biologique : R-X (X = S, N ou O) orientee vers le Pd."""
    dx, dy = direction
    sx, sy = anchor
    r_x, r_y = sx - 0.32 * dx, sy - 0.32 * dy
    ax.plot([r_x, sx], [r_y, sy], color=C_BOND, lw=1.4,
            solid_capstyle="round", zorder=3)
    ax.text(r_x - 0.04 * dx, r_y - 0.04 * dy, "R", color=C_BOND, fontsize=9,
            fontweight="bold", ha="center", va="center", zorder=4)
    circ = Circle((sx, sy), 0.11, facecolor=color, edgecolor=C_BOND,
                  lw=1.0, zorder=5)
    ax.add_patch(circ)
    ax.text(sx, sy, atom, color="white", fontsize=8, fontweight="bold",
            ha="center", va="center", zorder=6)


def draw_dashed_bond(ax, p1, p2, color=C_KO, lw=2.0):
    x1, y1 = p1
    x2, y2 = p2
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, ls="--",
            solid_capstyle="round", zorder=4)


def draw_arrow(ax, start, end, color, rad=0.0, lw=1.8):
    arrow = FancyArrowPatch(
        start, end, connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>", mutation_scale=14, color=color, lw=lw, zorder=6)
    ax.add_patch(arrow)


def draw_pyrrolidone(ax, center, scale=0.30):
    """Motif pyrrolidone (unite de repetition de la PVP) : cycle a 5 atomes
    (N + 4 C) portant un C=O. Schematique, pour la 'vraie chimie'."""
    cx, cy = center
    # pentagone
    angles = np.linspace(90, 90 + 360, 6)[:-1]
    pts = [(cx + scale * np.cos(np.radians(a)),
            cy + scale * np.sin(np.radians(a))) for a in angles]
    xs = [p[0] for p in pts] + [pts[0][0]]
    ys = [p[1] for p in pts] + [pts[0][1]]
    ax.plot(xs, ys, color=C_PVP, lw=1.4, zorder=5)
    # N (sommet du haut)
    ax.text(pts[0][0], pts[0][1] + 0.02, "N", color=C_PVP, fontsize=7.5,
            fontweight="bold", ha="center", va="center", zorder=6)
    # C=O sur un carbone adjacent (pts[1], a droite)
    co_base = pts[1]
    co_tip = (co_base[0] + 0.26, co_base[1])
    ax.plot([co_base[0], co_tip[0]], [co_base[1], co_tip[1]],
            color=C_PVP, lw=1.4, zorder=5)
    ax.plot([co_base[0], co_tip[0]], [co_base[1] + 0.04, co_tip[1] + 0.04],
            color=C_PVP, lw=1.4, zorder=5)
    ax.text(co_tip[0] + 0.10, co_tip[1], "O", color=C_O, fontsize=7.5,
            fontweight="bold", ha="center", va="center", zorder=6)


def draw_panel_poisoned(ax, center=(-2.5, 0.0)):
    """GAUCHE : Pd0 nu -> sequestration non specifique + agregation."""
    cx, cy = center
    bg = mpatches.FancyBboxPatch(
        (cx - 2.15, cy - 1.90), 4.30, 3.85, boxstyle="round,pad=0.05",
        facecolor=C_BG_KO, edgecolor=C_KO, lw=1.8, zorder=0)
    ax.add_patch(bg)

    ax.text(cx, cy + 1.72, "Pd⁰ nu en milieu biologique",
            color=C_KO, fontsize=12, fontweight="bold",
            ha="center", va="center", zorder=5)

    pd_center = (cx, cy + 0.05)
    draw_pd_atom(ax, pd_center, radius=0.30)

    # Trois briques biologiques (S, N, O) sequestrent le Pd
    donors = [
        ((cx,         cy + 0.90), "S", C_S, (0.0, 1.0)),    # haut, soufre
        ((cx - 0.88,  cy + 0.10), "N", C_N, (-1.0, 0.0)),   # gauche, azote
        ((cx + 0.88,  cy - 0.10), "O", C_O, (1.0, -0.2)),   # droite, oxygene
    ]
    for pos, atom, color, dir_vec in donors:
        n = np.hypot(*dir_vec)
        unit = (dir_vec[0] / n, dir_vec[1] / n)
        draw_donor(ax, pos, atom, color, direction=unit)
        draw_dashed_bond(ax, pd_center, pos, color=C_KO, lw=1.8)

    ax.text(cx, cy - 0.78,
            "Séquestration non spécifique par les\n"
            "biomolécules (N, S, O). Le S est le pire :\n"
            "HSAB mou–mou, liaison Pd–S ~250 kJ/mol*",
            color=C_TEXT, fontsize=8, fontstyle="italic",
            ha="center", va="center", zorder=5, linespacing=1.3)

    # Ar-I bloque (AO impossible)
    start = (cx + 1.55, cy + 0.70)
    end = (cx + 0.42, cy + 0.20)
    ax.text(start[0] - 0.03, start[1], "Ar–I", color=C_I, fontsize=10,
            fontweight="bold", ha="right", va="center", zorder=6)
    draw_arrow(ax, start, end, color=C_I, rad=0.2, lw=1.5)
    ax.text(cx + 0.95, cy + 0.42, "✗", color=C_KO, fontsize=15,
            fontweight="bold", ha="center", va="center", zorder=7,
            bbox=dict(boxstyle="circle,pad=0.10", facecolor="white",
                      edgecolor=C_KO, lw=1.4))

    ax.text(cx, cy - 1.52, "Sites saturés → AO impossible",
            color=C_KO, fontsize=10, fontweight="bold",
            ha="center", va="center", zorder=5)
    ax.text(cx, cy - 1.74, "(+ agrégation des NP non stabilisées)",
            color=C_KO, fontsize=7.5, fontstyle="italic",
            ha="center", va="center", zorder=5)


def draw_panel_protected(ax, center=(2.5, 0.0)):
    """DROITE : Pd0 enrobe dans la matrice PVP -> protege mais actif."""
    cx, cy = center
    bg = mpatches.FancyBboxPatch(
        (cx - 2.15, cy - 1.90), 4.30, 3.85, boxstyle="round,pad=0.05",
        facecolor=C_BG_OK, edgecolor=C_OK, lw=1.8, zorder=0)
    ax.add_patch(bg)

    ax.text(cx, cy + 1.72, "Pd⁰ enrobé dans la matrice PVP",
            color=C_OK, fontsize=12, fontweight="bold",
            ha="center", va="center", zorder=5)

    pd_center = (cx, cy + 0.05)

    # Matrice PVP : ellipse en pointilles + chaines ondulantes autour du Pd
    shell = mpatches.Ellipse(pd_center, 1.85, 1.55, facecolor="none",
                             edgecolor=C_PVP, lw=1.6, ls="--", zorder=2)
    ax.add_patch(shell)
    # chaines polymere ondulantes (arcs autour)
    for ang0 in np.linspace(0, 360, 9)[:-1]:
        th = np.radians(ang0) + np.linspace(0, 0.7, 12)
        rr = 0.78 + 0.06 * np.sin(np.linspace(0, 3 * np.pi, 12))
        xs = pd_center[0] + rr * 0.95 * np.cos(th)
        ys = pd_center[1] + rr * 0.80 * np.sin(th)
        ax.plot(xs, ys, color=C_PVP, lw=1.1, alpha=0.55, zorder=2,
                solid_capstyle="round")

    draw_pd_atom(ax, pd_center, radius=0.28)

    # Motif pyrrolidone (la vraie unite de repetition de la PVP)
    draw_pyrrolidone(ax, (cx - 1.15, cy + 1.02), scale=0.22)
    ax.text(cx - 1.15, cy + 1.42, "motif pyrrolidone", color=C_PVP,
            fontsize=7, fontstyle="italic", ha="center", va="center",
            zorder=5)

    # Thiols / biomolecules repousses par la matrice (en haut, hors shell)
    for sx_t in [cx + 0.35, cx + 1.05]:
        sy_t = cy + 1.30
        ax.text(sx_t - 0.06, sy_t, "R–S–H", color=C_S, fontsize=8,
                fontweight="bold", ha="left", va="center", zorder=4)
        ax.text(sx_t + 0.42, sy_t, "✗", color=C_KO, fontsize=11,
                fontweight="bold", ha="center", va="center", zorder=5)

    # Ar-I (petit) penetre la matrice -> AO
    start = (cx + 1.65, cy - 0.05)
    end = (cx + 0.32, cy + 0.02)
    ax.text(start[0] - 0.03, start[1], "Ar–I", color=C_I, fontsize=10,
            fontweight="bold", ha="right", va="center", zorder=6)
    draw_arrow(ax, start, end, color=C_OK, rad=-0.15, lw=1.8)

    # Produit AO
    draw_arrow(ax, (cx - 0.32, cy + 0.02), (cx - 0.80, cy + 0.02),
               color=C_OK, rad=0.0, lw=1.5)
    ax.text(cx - 0.56, cy + 0.22, "AO", color=C_OK, fontsize=9,
            fontweight="bold", ha="center", va="center", zorder=6)
    ax.text(cx - 1.55, cy + 0.02, "Ar–Pd(II)–I\n(actif)", color=C_OK,
            fontsize=8, fontweight="bold", ha="left", va="center",
            zorder=5, linespacing=1.2)

    ax.text(cx, cy - 1.05,
            "Matrice : limite le binding non spécifique\n"
            "et l'agrégation ; le petit Ar–I passe encore",
            color=C_TEXT, fontsize=8, fontstyle="italic",
            ha="center", va="center", zorder=5, linespacing=1.3)

    ax.text(cx, cy - 1.52, "Pd⁰ accessible → Suzuki tourne (37 °C, pH 7)",
            color=C_OK, fontsize=8.5, fontweight="bold",
            ha="center", va="center", zorder=5)
    ax.text(cx, cy - 1.74, "PVP : excipient non cytotoxique (IC50 > 1 mM)",
            color=C_PVP, fontsize=7.5, fontstyle="italic",
            ha="center", va="center", zorder=5)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=200)
    ax.set_xlim(-5.2, 5.2)
    ax.set_ylim(-2.22, 2.02)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    draw_panel_poisoned(ax, center=(-2.5, -0.05))
    draw_panel_protected(ax, center=(2.5, -0.05))

    ax.plot([0, 0], [-1.92, 1.90], color="#CCCCCC", lw=1.0, ls="--", zorder=1)

    # Note de sourcing (bas de figure)
    ax.text(0, -2.08,
            "* HSAB / Pd–S ~250 kJ/mol et encombrement stérique = chimie générale ; "
            "enrobage PVP, agrégation et IC50 = données Peramo (2019).",
            color="#888888", fontsize=6.0, fontstyle="italic",
            ha="center", va="center", zorder=5)

    out_path = OUT_DIR / "pd_stabilisant.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight",
                facecolor="white", pad_inches=0.02)
    plt.close(fig)
    print(f"[OK] -> {out_path}")


if __name__ == "__main__":
    main()
