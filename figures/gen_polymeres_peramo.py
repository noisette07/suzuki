#!/usr/bin/env python3
"""Genere polymeres_peramo.png : les 2 supports polymeres de Peramo.

Version simplifiee : on dessine les VRAIES molecules (monomeres) que le lecteur
reconnait, SANS la notation * (atomes-liens RDKit, peu lisible).
Le caractere "polymere" est porte par une fleche + le type de polymerisation
(polyaddition / polycondensation), notions du programme PC.

  GAUCHE  : PVP (polyvinylpyrrolidone) — support RETENU (PVP-Pd).
            Monomere reel = N-vinylpyrrolidone (C=C + cycle pyrrolidone N-C=O).
            -> polyaddition (ouverture de la double liaison C=C).
  DROITE  : PLGA-PEG — copolymere abandonne (instable).
            Monomeres reels = ethylene glycol (PEG) + acide lactique +
            acide glycolique (PLGA). -> polycondensation (esters).
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

C_PVP   = "#785028"
C_PLGA  = "#0072B2"
C_OK    = "#009E73"
C_KO    = "#D55E00"
C_TEXT  = "#4A4A4A"


def mol_png(smiles, size=(330, 230)):
    """Rend un SMILES de molecule REELLE (sans *) en image RGBA."""
    mol = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(mol)
    d = rdMolDraw2D.MolDraw2DCairo(size[0], size[1])
    opts = d.drawOptions()
    opts.clearBackground = False
    opts.bondLineWidth = 2
    rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
    d.FinishDrawing()
    png = d.GetDrawingText()
    return mpimg.imread(io.BytesIO(png), format="png")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Monomeres REELS (molecules entieres, aucune notation *) ----
    nvp  = mol_png("C=CN1CCCC1=O", size=(340, 300))   # N-vinylpyrrolidone (PVP)
    eg   = mol_png("OCCO",          size=(300, 150))   # ethylene glycol (PEG)
    lact = mol_png("CC(O)C(=O)O",   size=(300, 200))   # acide lactique (PLGA)
    glyc = mol_png("OCC(=O)O",      size=(300, 200))   # acide glycolique (PLGA)

    fig = plt.figure(figsize=(10.0, 3.52), dpi=200)  # reduit de 1/5e vs 12.5x4.4
    fig.patch.set_facecolor("white")

    # ================= PANNEAU GAUCHE : PVP =================
    axL = fig.add_axes([0.005, 0.005, 0.493, 0.99])
    axL.axis("off")
    axL.add_patch(plt.Rectangle((0, 0), 1, 1, transform=axL.transAxes,
                  facecolor="#E5F0EA", edgecolor=C_OK, lw=2.0, zorder=0))
    axL.text(0.5, 0.93, "PVP-Pd  —  support RETENU", color=C_OK,
             fontsize=14, fontweight="bold", ha="center", va="center",
             transform=axL.transAxes)
    axL.text(0.5, 0.86, "monomère : la N-vinylpyrrolidone",
             color=C_TEXT, fontsize=9, fontstyle="italic", ha="center",
             va="center", transform=axL.transAxes)
    axin = axL.inset_axes([0.20, 0.40, 0.60, 0.42])
    axin.imshow(nvp)
    axin.axis("off")
    # fleche polymerisation, centree
    axL.annotate("", xy=(0.5, 0.28), xytext=(0.5, 0.38),
                 xycoords=axL.transAxes,
                 arrowprops=dict(arrowstyle="-|>", color=C_PVP, lw=2.0))
    axL.text(0.50, 0.21, "→ PVP, polymère qui enrobe le Pd⁰", color=C_PVP,
             fontsize=9.5, fontweight="bold", ha="center", va="center",
             transform=axL.transAxes)
    axL.text(0.50, 0.14, "polyaddition (ouverture C=C)", color=C_PVP,
             fontsize=8, fontstyle="italic", ha="center", va="center",
             transform=axL.transAxes)
    # motif PVP
    axL.text(0.50, 0.06, r"motif : $-[-\mathrm{CH}_2-\mathrm{CH}(\mathrm{Npyrrolidone})-]_n-$",
             color=C_PVP, fontsize=9, ha="center", va="center",
             transform=axL.transAxes)

    # ================= PANNEAU DROITE : PLGA-PEG =================
    axR = fig.add_axes([0.502, 0.005, 0.493, 0.99])
    axR.axis("off")
    axR.add_patch(plt.Rectangle((0, 0), 1, 1, transform=axR.transAxes,
                  facecolor="#EAF1F7", edgecolor=C_PLGA, lw=2.0, zorder=0))
    axR.text(0.5, 0.93, "PLGA-PEG  —  abandonné (instable)", color=C_PLGA,
             fontsize=14, fontweight="bold", ha="center", va="center",
             transform=axR.transAxes)
    axR.text(0.5, 0.86, "copolymère à 2 blocs",
             color=C_TEXT, fontsize=9, fontstyle="italic", ha="center",
             va="center", transform=axR.transAxes)

    # separateur vertical entre les 2 sous-blocs
    axR.plot([0.585, 0.585], [0.08, 0.81], color=C_PLGA, lw=0.8,
             linestyle="--", transform=axR.transAxes, alpha=0.5)

    # ---- Sous-bloc PLGA (gauche du panneau droit) ----
    axR.text(0.29, 0.79, "bloc PLGA  —  polyester", color=C_PLGA,
             fontsize=10, fontweight="bold", ha="center", va="center",
             transform=axR.transAxes)
    ax_lac = axR.inset_axes([0.02, 0.55, 0.27, 0.21]); ax_lac.imshow(lact); ax_lac.axis("off")
    ax_gly = axR.inset_axes([0.30, 0.55, 0.27, 0.21]); ax_gly.imshow(glyc); ax_gly.axis("off")
    axR.text(0.155, 0.51, "ac. lactique", color=C_TEXT, fontsize=7.5,
             ha="center", va="center", transform=axR.transAxes)
    axR.text(0.435, 0.51, "ac. glycolique", color=C_TEXT, fontsize=7.5,
             ha="center", va="center", transform=axR.transAxes)
    axR.annotate("", xy=(0.29, 0.36), xytext=(0.29, 0.46),
                 xycoords=axR.transAxes,
                 arrowprops=dict(arrowstyle="-|>", color=C_PLGA, lw=1.8))
    axR.text(0.29, 0.41, "polycondensation", color=C_PLGA,
             fontsize=7.5, fontstyle="italic", ha="center", va="center",
             transform=axR.transAxes)
    axR.text(0.29, 0.30,
             r"$-[-\mathrm{O}-\mathrm{CHR}-\mathrm{CO}-]_n-$  avec R = H ou CH$_3$",
             color=C_PLGA, fontsize=8, ha="center", va="center",
             transform=axR.transAxes)

    # ---- Sous-bloc PEG (droite du panneau droit) ----
    axR.text(0.79, 0.79, "bloc PEG  —  polyéther", color=C_PLGA,
             fontsize=10, fontweight="bold", ha="center", va="center",
             transform=axR.transAxes)
    ax_eg = axR.inset_axes([0.65, 0.55, 0.28, 0.21]); ax_eg.imshow(eg); ax_eg.axis("off")
    axR.text(0.79, 0.51, "éthylène glycol", color=C_TEXT, fontsize=7.5,
             ha="center", va="center", transform=axR.transAxes)
    axR.annotate("", xy=(0.79, 0.36), xytext=(0.79, 0.46),
                 xycoords=axR.transAxes,
                 arrowprops=dict(arrowstyle="-|>", color=C_PLGA, lw=1.8))
    axR.text(0.79, 0.41, "polymérisation", color=C_PLGA,
             fontsize=7.5, fontstyle="italic", ha="center", va="center",
             transform=axR.transAxes)
    axR.text(0.79, 0.30,
             r"$-[-\mathrm{O}-\mathrm{CH}_2-\mathrm{CH}_2-]_m-$",
             color=C_PLGA, fontsize=8, ha="center", va="center",
             transform=axR.transAxes)
    axR.text(0.79, 0.235, "(liaisons éther)", color=C_TEXT,
             fontsize=7, fontstyle="italic", ha="center", va="center",
             transform=axR.transAxes)

    # ---- jonction des 2 blocs ----
    axR.text(0.50, 0.13, "← liaison ester →", color=C_PLGA,
             fontsize=9, fontweight="bold", ha="center", va="center",
             transform=axR.transAxes)
    axR.text(0.50, 0.07, "(jonction PEG–PLGA, 1 seul pont ester)",
             color=C_TEXT, fontsize=7.5, fontstyle="italic",
             ha="center", va="center", transform=axR.transAxes)

    out = OUT_DIR / "polymeres_peramo.png"
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight",
                pad_inches=0)
    plt.close(fig)
    print(f"[OK] -> {out}")


if __name__ == "__main__":
    main()
