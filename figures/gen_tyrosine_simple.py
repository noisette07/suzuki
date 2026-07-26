#!/usr/bin/env python3
"""Genere tyrosine_simple.png : formule de la tyrosine LIBRE (sans Boc, sans I).

Pour la slide S15 "Suzuki en conditions physiologiques" : aider a
comprendre tout de suite ce qu'est une tyrosine (AA porteur d'un phenol).
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

C_OK = "#009E73"
C_TEXT = "#4A4A4A"
C_LABEL = "#3D6B4A"


def mol_png(smiles, size=(360, 260)):
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

    # 3-iodotyrosine : H2N-CH(COOH)-CH2-C6H3(I)(OH) — iode en ortho du OH
    tyr = mol_png("NC(Cc1cc(I)c(O)cc1)C(=O)O", size=(360, 260))

    fig = plt.figure(figsize=(4.0, 3.2), dpi=200)
    fig.patch.set_facecolor("white")

    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                 facecolor="#EAF5EE", edgecolor=C_OK, lw=1.8, zorder=0))

    ax.text(0.5, 0.93, "Tyrosine  (Tyr, Y)", color=C_LABEL,
            fontsize=12, fontweight="bold", ha="center", va="center",
            transform=ax.transAxes)
    ax.text(0.5, 0.85, "acide aminé porteur d'un phénol",
            color=C_TEXT, fontsize=8, fontstyle="italic", ha="center",
            va="center", transform=ax.transAxes)

    axin = ax.inset_axes([0.10, 0.20, 0.80, 0.62])
    axin.imshow(tyr)
    axin.axis("off")

    ax.text(0.5, 0.10,
            "iodée naturellement en ortho du OH → Ar–I",
            color=C_LABEL, fontsize=8, fontweight="bold", ha="center",
            va="center", transform=ax.transAxes)

    out = OUT_DIR / "tyrosine_simple.png"
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight",
                pad_inches=0.03)
    plt.close(fig)
    print(f"[OK] -> {out}")


if __name__ == "__main__":
    main()
