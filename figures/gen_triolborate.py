#!/usr/bin/env python3
"""Genere triolborate.png : transmetallation (etape 3) PhB(OH)2 vs triolborate.

Version simplifiee : molecules REELLES dessinees par RDKit, avec PALLADIUM
explicite dans l'equation de transmetallation (en haut).

  HAUT   : equation de la transmetallation, Pd explicite (texte) :
           Ar-Pd(II)-OH + [Ph-B]- -> Ar-Pd(II)-Ph + B(residu).
  GAUCHE : acide phenylboronique PhB(OH)2 (RDKit). B sp2 trigonal NEUTRE.
  DROITE : triolborate cyclique de phenyle (RDKit), cage bicyclique reelle
           4-methyl-1-phenyl-2,6,7-trioxa-1-borabicyclo[2.2.2]octane.
           B sp3 tetraedrique, charge negative -> annotation ⊖ DEPORTEE
           a cote de la molecule pour bien la voir (pas sur le cycle).

Distinction a garder en tete (cf. slide 18) : ici le Pd est le CENTRE ACTIF
Pd(II) du cycle, PAS la nanoparticule Pd(0) stabilisee par le PVP.
"""

from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output"

C_TITLE = "#3D6B4A"
C_TEXT  = "#333333"
C_SLOW  = "#CC79A7"
C_FAST  = "#009E73"
C_BG_SLOW = "#F5E5EE"
C_BG_FAST = "#E5F0EA"

SMI_PHB  = "OB(O)c1ccccc1"                    # acide phenylboronique (sp2)
SMI_TRIOL = "[B-]12(OCC(C)(CO1)CO2)c3ccccc3"  # triolborate cyclique (sp3, -)


def mol_png(smiles, size=(420, 360), highlight_borate=False):
    mol = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(mol)
    hl, hlc = [], {}
    if highlight_borate:
        orange = (0.835, 0.369, 0.0)
        green = (0.0, 0.62, 0.45)
        for a in mol.GetAtoms():
            if a.GetSymbol() == "B":
                hl.append(a.GetIdx()); hlc[a.GetIdx()] = green
            if a.GetSymbol() == "O":
                hl.append(a.GetIdx()); hlc[a.GetIdx()] = orange
    d = rdMolDraw2D.MolDraw2DCairo(size[0], size[1])
    opts = d.drawOptions()
    opts.clearBackground = False
    opts.bondLineWidth = 2
    if hl:
        rdMolDraw2D.PrepareAndDrawMolecule(d, mol, highlightAtoms=hl,
                                           highlightAtomColors=hlc)
    else:
        rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
    d.FinishDrawing()
    return mpimg.imread(io.BytesIO(d.GetDrawingText()), format="png")


def draw_header(ax):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                 facecolor="#E8F0EA", edgecolor=C_TITLE, lw=1.6, zorder=0))
    ax.text(0.5, 0.74, "Transmétallation (étape 3) : le bore cède son Ph au Pd",
            color=C_TITLE, fontsize=13.5, fontweight="bold",
            ha="center", va="center", transform=ax.transAxes)
    ax.text(0.5, 0.30,
            "Ar–Pd(II)–OH   +   [Ph–B]⁻    →    Ar–Pd(II)–Ph   +   B(résidu)",
            color=C_TEXT, fontsize=13, fontweight="bold",
            ha="center", va="center", transform=ax.transAxes)


def draw_panel(ax, img, bg, edge, title, sub, *, charge_pos=None,
               charge_color=None):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                 facecolor=bg, edgecolor=edge, lw=1.8, zorder=0))
    ax.text(0.5, 0.93, title, color=edge, fontsize=12.5, fontweight="bold",
            ha="center", va="center", transform=ax.transAxes)
    ax.text(0.5, 0.84, sub, color=C_TEXT, fontsize=10.5, fontweight="bold",
            ha="center", va="center", transform=ax.transAxes)
    axin = ax.inset_axes([0.08, 0.06, 0.84, 0.72])
    axin.imshow(img); axin.axis("off")
    # charge ⊖ deportee a cote de la molecule (en coords panel, pas axin)
    if charge_pos is not None:
        x, y = charge_pos
        ax.text(x, y, r"$\ominus$", color=charge_color or edge, fontsize=24,
                fontweight="bold", ha="center", va="center",
                transform=ax.transAxes, zorder=20)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    phb = mol_png(SMI_PHB)
    triol = mol_png(SMI_TRIOL, highlight_borate=True)

    fig = plt.figure(figsize=(12.4, 5.2), dpi=200)
    fig.patch.set_facecolor("white")

    ax_top = fig.add_axes([0.02, 0.80, 0.96, 0.18]); draw_header(ax_top)
    ax_L = fig.add_axes([0.02, 0.02, 0.47, 0.74])
    ax_R = fig.add_axes([0.51, 0.02, 0.47, 0.74])

    draw_panel(ax_L, phb, C_BG_SLOW, C_SLOW,
               "Acide phénylboronique",
               "Ph–B(OH)₂  —  B sp², trigonal, NEUTRE")

    draw_panel(ax_R, triol, C_BG_FAST, C_FAST,
               "Triolborate cyclique de phényle",
               "B sp³, tétraédrique, boronate⁻ (K⁺)",
               charge_pos=(0.47, 0.47), charge_color=C_FAST)

    out = OUT_DIR / "triolborate.png"
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight",
                pad_inches=0.04)
    plt.close(fig)
    print(f"[OK] -> {out}")


if __name__ == "__main__":
    main()
