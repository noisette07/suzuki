#!/usr/bin/env python3
"""Genere tyr_phe_mesomere.png : N-Boc-3-iodo-Phe vs N-Boc-3-iodo-Tyr.

Version simplifiee : molecules ENTIERES dessinees par RDKit (tous les groupes
visibles : carbamate Boc, COOH, CH2, C-alpha, cycle, I, et OH pour la Tyr),
au lieu d'un squelette schematique avec etiquettes texte.

  GAUCHE : N-Boc-3-iodo-Phenylalanine — cycle neutre, AO rapide (97 %).
  DROITE : N-Boc-3-iodo-Tyrosine — le OH du phenol (mis en evidence) enrichit
           le cycle par effet mesomere donneur (+M) et ralentit l'addition
           oxydante ; on compense avec le triolborate (70 % -> 90 %).
Bandeau superieur : equation generale du couplage de Suzuki.
"""

from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import io

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output"

C_MESO   = "#D55E00"   # vermillon (+M)
C_NEUTRE = "#888888"
C_TITLE  = "#3D6B4A"
C_TEXT   = "#333333"
C_BG_PHE = "#F0F0F0"
C_BG_TYR = "#FDE8DC"

# N-Boc-3-iodo-phenylalanine : I en meta de la chaine, cycle neutre
SMI_PHE = "OC(=O)C(Cc1cccc(I)c1)NC(=O)OC(C)(C)C"
# N-Boc-3-iodo-tyrosine : OH en para de la chaine, I en ortho du OH
SMI_TYR = "OC(=O)C(Cc1cc(I)c(O)cc1)NC(=O)OC(C)(C)C"


def mol_png(smiles, size=(560, 440), highlight_phenol=False):
    """Rend une molecule REELLE (sans *). Si highlight_phenol, surligne le
    cycle aromatique et l'oxygene du phenol en orange (+M)."""
    mol = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(mol)

    hl_atoms, hl_colors = [], {}
    if highlight_phenol:
        orange = (0.835, 0.369, 0.0)
        pale = (0.992, 0.910, 0.863)
        for a in mol.GetAtoms():
            if a.GetIsAromatic():
                hl_atoms.append(a.GetIdx()); hl_colors[a.GetIdx()] = pale
            # oxygene phenol : O lie a un C aromatique et portant un H
            if a.GetSymbol() == "O" and a.GetTotalNumHs() >= 1:
                if any(nb.GetIsAromatic() for nb in a.GetNeighbors()):
                    hl_atoms.append(a.GetIdx()); hl_colors[a.GetIdx()] = orange

    d = rdMolDraw2D.MolDraw2DCairo(size[0], size[1])
    opts = d.drawOptions()
    opts.clearBackground = False
    opts.bondLineWidth = 2
    if hl_atoms:
        rdMolDraw2D.PrepareAndDrawMolecule(
            d, mol, highlightAtoms=hl_atoms, highlightAtomColors=hl_colors)
    else:
        rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
    d.FinishDrawing()
    return mpimg.imread(io.BytesIO(d.GetDrawingText()), format="png")


def draw_header(ax):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                 facecolor="#E8F0EA", edgecolor=C_TITLE, lw=1.6, zorder=0))
    ax.text(0.5, 0.80, "Couplage de Suzuki — sur acide aminé iodé",
            color=C_TITLE, fontsize=14, fontweight="bold",
            ha="center", va="center", transform=ax.transAxes)
    # Equation
    ax.text(0.10, 0.34, r"$\mathrm{Ar\!-\!I}$", fontsize=13, color=C_TEXT,
            fontweight="bold", ha="center", va="center", transform=ax.transAxes)
    ax.text(0.235, 0.34, r"$+\;\;\mathrm{Ph\!-\!B(OR)_3^-}$", fontsize=13,
            color=C_TEXT, ha="center", va="center", transform=ax.transAxes)
    ax.annotate("", xy=(0.60, 0.34), xytext=(0.42, 0.34),
                xycoords=ax.transAxes,
                arrowprops=dict(arrowstyle="-|>", color=C_TITLE, lw=2.0))
    ax.text(0.51, 0.50, "nano-Pd", fontsize=10, color=C_TITLE,
            fontweight="bold", ha="center", va="center", transform=ax.transAxes)
    ax.text(0.51, 0.17, "37 °C, 2 h, H₂O", fontsize=9, color=C_TEXT,
            fontstyle="italic", ha="center", va="center", transform=ax.transAxes)
    ax.text(0.70, 0.34, r"$\mathrm{Ar\!-\!Ph}$", fontsize=13, color=C_TEXT,
            fontweight="bold", ha="center", va="center", transform=ax.transAxes)
    ax.text(0.82, 0.34, "(biaryl)", fontsize=11, color=C_NEUTRE,
            fontstyle="italic", ha="center", va="center", transform=ax.transAxes)


def draw_panel(ax, img, bg, title, badge_text, badge_color, conclusion):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                 facecolor=bg, edgecolor="none", zorder=0))
    ax.text(0.5, 0.96, title, color=C_TITLE, fontsize=13, fontweight="bold",
            ha="center", va="center", transform=ax.transAxes)
    axin = ax.inset_axes([0.04, 0.22, 0.92, 0.70])
    axin.imshow(img); axin.axis("off")
    # badge (cycle neutre / +M)
    ax.text(0.5, 0.16, badge_text, color=badge_color, fontsize=11,
            fontweight="bold", ha="center", va="center", transform=ax.transAxes)
    ax.text(0.5, 0.06, conclusion, color=C_TEXT, fontsize=10.5,
            fontweight="bold", ha="center", va="center",
            transform=ax.transAxes, linespacing=1.3)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    phe = mol_png(SMI_PHE)
    tyr = mol_png(SMI_TYR, highlight_phenol=True)

    fig = plt.figure(figsize=(9.2, 8.6), dpi=200)
    fig.patch.set_facecolor("white")

    ax_top = fig.add_axes([0.03, 0.855, 0.94, 0.135]); draw_header(ax_top)
    ax_L = fig.add_axes([0.025, 0.02, 0.46, 0.81])
    ax_R = fig.add_axes([0.515, 0.02, 0.46, 0.81])

    draw_panel(ax_L, phe, C_BG_PHE, "N-Boc-3-iodo-Phénylalanine",
               "cycle neutre", C_NEUTRE,
               "AO rapide → 97 %  (2 h, pH 7)")
    draw_panel(ax_R, tyr, C_BG_TYR, "N-Boc-3-iodo-Tyrosine",
               "OH = donneur +M → cycle enrichi → AO ralentie", C_MESO,
               "70 % (PhB(OH)₂) → 90 % (triolborate)\n[pH 8, 2 h]")

    out = OUT_DIR / "tyr_phe_mesomere.png"
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight",
                pad_inches=0.04)
    plt.close(fig)
    print(f"[OK] -> {out}")


if __name__ == "__main__":
    main()
