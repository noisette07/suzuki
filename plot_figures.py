#!/usr/bin/env python3
"""Graphiques de résultats du projet Suzuki (slides + annexes).

Chaque figure a sa fonction ; le script les génère toutes dans output/.

Usage :
    python3 plot_figures.py                 # toutes les figures
    python3 plot_figures.py --only sakurai  # une seule
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

OUT_DIR = Path(__file__).resolve().parent / "output"

# ---------------------------------------------------------------------------
# Résultats expérimentaux (issus de monte_carlo.py, N = 10 000)
# ---------------------------------------------------------------------------

RENDEMENTS = {"C1": 62.5, "C2": 57.4}            # rendement isolé (%)
IC95 = {"C1": (61.1, 63.9), "C2": (56.2, 58.7)}  # intervalles de confiance
RECUPERATION_PDC = {"C1": (68.1, 0.5), "C2": (70.7, 0.7)}

# Référence bibliographique : Sakurai et al. 2002 (Pd/C, 5 cycles)
SAKURAI_CYCLES = np.array([1, 2, 3, 4, 5])
SAKURAI_RDT = np.array([99, 97, 95, 92, 89])


def _axes_sobres(ax):
    """Style commun : grille légère, pas de cadre superflu."""
    ax.grid(alpha=0.3, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _sauver(fig, nom: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    chemin = OUT_DIR / nom
    fig.savefig(chemin, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"OK  {chemin.name}")


# ---------------------------------------------------------------------------
# Figure 1 — rendements isolés par cycle, avec IC 95 %
# ---------------------------------------------------------------------------

def fig_rendements():
    fig, ax = plt.subplots(figsize=(5.5, 4))

    cycles = list(RENDEMENTS)
    valeurs = [RENDEMENTS[c] for c in cycles]
    bas = [RENDEMENTS[c] - IC95[c][0] for c in cycles]
    haut = [IC95[c][1] - RENDEMENTS[c] for c in cycles]

    ax.bar(cycles, valeurs, yerr=[bas, haut], capsize=8, width=0.5,
           color=["#4a86c8", "#e07b39"], edgecolor="#333", linewidth=0.8, zorder=3)

    for i, c in enumerate(cycles):
        ax.text(i, valeurs[i] + 4.5, f"{valeurs[i]:.1f} %".replace(".", ","),
                ha="center", fontweight="bold", fontsize=11)
        ax.text(i + 0.18, IC95[c][1], f"{IC95[c][1]:.1f}", fontsize=8, va="center", color="#333")
        ax.text(i + 0.18, IC95[c][0], f"{IC95[c][0]:.1f}", fontsize=8, va="center", color="#333")

    # Les IC 95 % ne se recouvrent pas : la baisse C1 -> C2 est significative
    ax.annotate("", xy=(0.5, IC95["C1"][0]), xytext=(0.5, IC95["C2"][1]),
                arrowprops=dict(arrowstyle="<->", color="#27ae60", lw=1.5))
    ax.text(0.55, 59.9, "IC disjoints\n(baisse significative)",
            fontsize=8, color="#27ae60", fontweight="bold", va="center")

    for cycle, rdt in zip(("C1", "C2"), (99, 97)):
        ax.axhline(y=rdt, color="#888", linestyle=":", linewidth=1, zorder=2)
    ax.text(-0.05, 99, "Sakurai C1 (99 %)", fontsize=7, color="#666", va="center", ha="right")
    ax.text(1.45, 97, "Sakurai C2 (97 %)", fontsize=7, color="#666", va="center", ha="left")

    ax.set_ylabel("Rendement isolé (%)", fontsize=11)
    ax.set_title("Rendement isolé par cycle (masse brute)", fontsize=12, fontweight="bold")
    ax.set_ylim(45, 105)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.text(0.5, -0.18,
            "Monte Carlo N = 10 000, propagation des incertitudes de pesées\n"
            "(balance classique ±10 mg pour le 4-iodophénol, balance de précision ±0,1 mg)",
            transform=ax.transAxes, fontsize=7.5, color="#555", ha="center", va="top")

    _sauver(fig, "graphique_rendements.png")


# ---------------------------------------------------------------------------
# Figure 2 — confrontation avec Sakurai 2002
# ---------------------------------------------------------------------------

def fig_sakurai():
    fig, ax = plt.subplots(figsize=(6, 4.5))

    ax.plot(SAKURAI_CYCLES, SAKURAI_RDT, "ko", markersize=7,
            label="Sakurai 2002 (données)", zorder=4)
    for c, r in zip(SAKURAI_CYCLES, SAKURAI_RDT):
        ax.text(c + 0.12, r + 0.8, f"{r}%", fontsize=8, va="bottom")

    pente, ordonnee = np.polyfit(SAKURAI_CYCLES, SAKURAI_RDT, 1)
    x = np.linspace(0.5, 5.5, 50)
    ax.plot(x, pente * x + ordonnee, "k--", linewidth=1.2, alpha=0.6,
            label=f"Modèle linéaire : {pente:+.1f} pts/cycle", zorder=3)

    mes_cycles = np.array([1, 2])
    mes_rdt = np.array([RENDEMENTS["C1"], RENDEMENTS["C2"]])
    ax.plot(mes_cycles, mes_rdt, "rs", markersize=10, label="Mon projet", zorder=5)
    ma_pente = mes_rdt[1] - mes_rdt[0]
    x_mes = np.linspace(0.7, 2.5, 20)
    ax.plot(x_mes, mes_rdt[0] + ma_pente * (x_mes - 1), "r--", linewidth=1.2, alpha=0.6,
            label=f"Ma tendance : {ma_pente:+.1f} pts/cycle", zorder=3)
    ax.text(0.95, mes_rdt[0] - 2.5, "62,5%", fontsize=9, color="#c0392b",
            fontweight="bold", ha="right")
    ax.text(2.15, mes_rdt[1] - 2.5, "57,4%", fontsize=9, color="#c0392b",
            fontweight="bold", ha="left")

    ax.annotate("Déclin 2x plus rapide\n(conditions différentes)",
                xy=(3.5, 54), fontsize=8, color="#c0392b", fontstyle="italic",
                ha="center",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#fde8dc",
                          edgecolor="#c0392b", alpha=0.8))

    ax.set_xlabel("Numéro de cycle", fontsize=11)
    ax.set_ylabel("Rendement (%)", fontsize=11)
    ax.set_title("Confrontation résultats Sakurai / résultats expérimentaux",
                 fontsize=11, fontweight="bold")
    ax.set_xlim(0.3, 5.7)
    ax.set_ylim(50, 105)
    ax.set_xticks(SAKURAI_CYCLES)
    ax.legend(loc="center right", fontsize=8)
    _axes_sobres(ax)

    _sauver(fig, "graphique_sakurai_cycles.png")


# ---------------------------------------------------------------------------
# Figure 3 — économie du palladium
# ---------------------------------------------------------------------------

def fig_economie_pd():
    fig, ax = plt.subplots(figsize=(6, 3.5))

    libelles = [
        "Pd(PPh$_3$)$_4$ (homo)",
        "Pd/C 5 % (hétéro)",
        "Pd/C recyclé (idéal)",
        "Mon projet\nPd/C recyclé (68 %)",
    ]
    couts = [100, 35, 17.5, 20.8]
    annotations = ["~100 €/g", "35 €/g", "~18 €/g\n(35/2 cycles)", "~21 €/g"]

    barres = ax.barh(libelles, couts, height=0.55, zorder=3,
                     color=["#c0392b", "#e07b39", "#27ae60", "#4a86c8"],
                     edgecolor="#333", linewidth=0.8)
    for barre, texte in zip(barres, annotations):
        ax.text(barre.get_width() + 1.5, barre.get_y() + barre.get_height() / 2,
                texte, va="center", fontsize=9, fontweight="bold")

    ax.set_xlabel("Coût effectif (€/g)", fontsize=11)
    ax.set_title("Économie du palladium selon le catalyseur", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 130)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(20))
    ax.grid(axis="x", alpha=0.3, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.invert_yaxis()
    ax.text(0.5, -0.28, "Once Pd pur > 1 500 € (31,1 g)",
            transform=ax.transAxes, fontsize=8, color="grey", ha="right")

    _sauver(fig, "graphique_economie_pd.png")


# ---------------------------------------------------------------------------
# Figure 4 — hiérarchie des halogènes (flèches I > Br >> Cl)
# ---------------------------------------------------------------------------

def fig_halogenes():
    fig, ax = plt.subplots(figsize=(6, 6))

    donnees = [
        # (x, hauteur, halogène, énergie C-X, rendement, couleur)
        (1, 5.5, "I", "234 kJ/mol", ">99 %, T$_{amb}$", "#27ae60"),
        (3, 4.0, "Br", "285 kJ/mol", "76 %, 50 °C", "#e07b39"),
        (5, 2.5, "Cl", "339 kJ/mol", "~0 %", "#c0392b"),
    ]
    largeur_corps, largeur_pointe, hauteur_pointe = 0.6, 1.2, 0.6

    for x, h, halogene, energie, rendement, couleur in donnees:
        corps = plt.Polygon(
            [(x - largeur_corps / 2, 0), (x + largeur_corps / 2, 0),
             (x + largeur_corps / 2, h - hauteur_pointe),
             (x - largeur_corps / 2, h - hauteur_pointe)],
            facecolor=couleur, edgecolor="#333", linewidth=1.5)
        pointe = plt.Polygon(
            [(x - largeur_pointe / 2, h - hauteur_pointe),
             (x + largeur_pointe / 2, h - hauteur_pointe), (x, h)],
            facecolor=couleur, edgecolor="#333", linewidth=1.5)
        ax.add_patch(corps)
        ax.add_patch(pointe)
        ax.text(x, (h - hauteur_pointe) / 2, energie, ha="center", va="center",
                fontsize=11, fontweight="bold", color="white", rotation=90)
        ax.text(x, h + 0.2, rendement, ha="center", va="bottom", fontsize=11)
        ax.text(x, -0.5, halogene, ha="center", va="top", fontsize=18, fontweight="bold")

    ax.annotate("", xy=(-0.4, -0.3), xytext=(-0.4, 6.2),
                arrowprops=dict(arrowstyle="->", color="black", lw=2))
    ax.text(-0.85, 3.0, "Réactivité\ndécroissante", ha="center", va="center",
            fontsize=10, rotation=90)
    ax.annotate("", xy=(6.4, 6.2), xytext=(6.4, -0.3),
                arrowprops=dict(arrowstyle="->", color="black", lw=2))
    ax.text(6.85, 3.0, "Énergie C–X\ncroissante", ha="center", va="center",
            fontsize=10, rotation=270)

    ax.set_title("Hiérarchie I > Br >> Cl (Sakurai 2002)", fontsize=14,
                 fontweight="bold", pad=15)
    ax.set_xlim(-1.5, 7.5)
    ax.set_ylim(-1.0, 7.0)
    ax.set_aspect("equal")
    ax.axis("off")

    _sauver(fig, "schema_halogenes.png")


# ---------------------------------------------------------------------------
# Figure 5 — corrélation ln(rendement) / énergie de liaison C-X
# ---------------------------------------------------------------------------

def fig_arrhenius_hammond():
    fig, ax = plt.subplots(figsize=(6, 4.5))

    d_cx = np.array([234, 285, 339])            # énergies de liaison (kJ/mol)
    r_sakurai = np.array([99, 76, 0.5])         # Cl : trace, estimé 0,5 %
    ln_sakurai = np.log(r_sakurai)

    ax.plot(d_cx, ln_sakurai, "ko", markersize=9, zorder=5, label="Sakurai 2002")
    for d, ln_r, halogene, dx in zip(d_cx, ln_sakurai, ("I", "Br", "Cl"), (0, 0, -10)):
        ax.text(d + dx, ln_r + 0.25, halogene, fontsize=10, fontweight="bold",
                ha="center", va="bottom")

    pente, ordonnee = np.polyfit(d_cx, ln_sakurai, 1)
    x = np.linspace(220, 350, 50)
    ax.plot(x, pente * x + ordonnee, "k--", linewidth=1.2, alpha=0.6,
            label=f"Modèle : pente = {pente:.3f} mol/kJ")

    # Peramo 2019 (2 h, 37 °C, 1 mol%) — Cl non mesurable, seuls I et Br
    d_peramo = np.array([234, 285])
    ln_peramo = np.log(np.array([98, 90]))
    ax.plot(d_peramo, ln_peramo, "rs", markersize=9, zorder=5, label="Peramo 2019")
    ax.text(229, ln_peramo[0] - 0.35, "I", fontsize=9, fontweight="bold",
            color="#c0392b", ha="right")
    ax.text(292, ln_peramo[1] - 0.35, "Br", fontsize=9, fontweight="bold",
            color="#c0392b", ha="left")

    ax.axhspan(-2, 0, color="#fde8dc", alpha=0.4, zorder=0)
    ax.text(280, -1.3, "Zone inaccessible : R = 0 %  (Ea trop élevée)",
            fontsize=8, ha="center", fontstyle="italic", color="#c0392b")
    ax.text(222, 1.0, "Hammond : Ea proportionnelle à D(C–X)\nArrhenius : ln(R) en -D/RT",
            fontsize=8, fontstyle="italic", color="#555",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#ccc"))

    ax.set_xlabel("D(C–X) (kJ/mol)", fontsize=11)
    ax.set_ylabel("ln(Rendement)", fontsize=11)
    ax.set_title("Corrélation énergie de liaison / réactivité", fontsize=12, fontweight="bold")
    ax.set_xlim(215, 355)
    ax.set_ylim(-2, 5.5)
    ax.legend(loc="upper right", fontsize=8)
    _axes_sobres(ax)

    _sauver(fig, "graphique_arrhenius_hammond.png")


# ---------------------------------------------------------------------------

FIGURES = {
    "rendements": fig_rendements,
    "sakurai": fig_sakurai,
    "economie": fig_economie_pd,
    "halogenes": fig_halogenes,
    "arrhenius": fig_arrhenius_hammond,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", choices=sorted(FIGURES), help="une seule figure")
    args = parser.parse_args()

    if args.only:
        FIGURES[args.only]()
    else:
        for fonction in FIGURES.values():
            fonction()


if __name__ == "__main__":
    main()
