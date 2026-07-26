#!/usr/bin/env python3
"""Génère les 4 étapes du cycle catalytique Suzuki via LaTeX + tikz.

Style "papier scientifique" inspiré des images originales :
- Header : encadré avec l'équation chimique de l'étape
- Cycle au centre : étape active en couleur (rouge/orange/bleu/vert), reste en gris pâle
- Footer : 3 faits clés séparés par `|`
"""

import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "_PYTHON" / "_BUILD"
OUT_DIR = ROOT / "output" / "_TEST"

# Couleurs RGB pour chaque étape (1 couleur dédiée par étape)
STEPS = [
    {
        "n": 1, "abbr": "AO", "name": "Addition oxydante",
        "color_rgb": "215,40,40",     # rouge
        "equation": r"\mathrm{Ar\text{-}I} + \mathrm{Pd(0)} \longrightarrow \mathrm{Ar\text{-}Pd(II)\text{-}I}",
        "facts": "Liaison C--I rompue (234 kJ/mol) $|$ Pd passe de n.o.~0 \\`a +II $|$ \\'Etape limitante du cycle",
        "active_nodes": [1, 2],      # Pd(0), Ar-Pd-I
        "active_arc": 1,
    },
    {
        "n": 2, "abbr": "LE", "name": "\\'Echange de ligands",
        "color_rgb": "230,130,30",    # orange
        "equation": r"\mathrm{Ar\text{-}Pd(II)\text{-}I} + \mathrm{KCO_3^-} \longrightarrow \mathrm{Ar\text{-}Pd(II)\text{-}OCO_2^-} + \mathrm{KI}",
        "facts": "I$^-$ remplac\\'e par OCO$_2^-$ sur Pd $|$ Pd plus \\'electrophile pour la TM $|$ Sans K$_2$CO$_3$ $\\to$ pas d'\\'echange",
        "active_nodes": [2, 3],      # Ar-Pd-I, Ar-Pd-OCO2
        "active_arc": 2,
    },
    {
        "n": 3, "abbr": "TM", "name": "Transm\\'etallation",
        "color_rgb": "30,90,200",     # bleu
        "equation": r"\mathrm{Ar\text{-}Pd(II)\text{-}OCO_2^-} + \mathrm{Ar'B(OH)_3^-} \longrightarrow \mathrm{Ar\text{-}Pd(II)\text{-}Ar'} + \mathrm{B(OH)_3} + \mathrm{HCO_3^-}",
        "facts": "Le bore est activ\\'e par K$_2$CO$_3$ (sp$^2 \\to$ sp$^3$) $|$ Ar$'$ transf\\'er\\'e de B vers Pd $|$ Sans base $\\to$ pas de couplage",
        "active_nodes": [3, 4],      # Ar-Pd-OCO2, Ar-Pd-Ar'
        "active_arc": 3,
    },
    {
        "n": 4, "abbr": "ER", "name": "\\'Elimination r\\'eductrice",
        "color_rgb": "30,150,60",     # vert
        "equation": r"\mathrm{Ar\text{-}Pd(II)\text{-}Ar'} \longrightarrow \mathrm{Ar\text{-}Ar'} + \mathrm{Pd(0)}",
        "facts": "Liaison C--C form\\'ee (350 kJ/mol) $|$ Irr\\'eversible $|$ Pd(0) r\\'eg\\'en\\'er\\'e $\\to$ recyclage du catalyseur",
        "active_nodes": [4, 1],      # Ar-Pd-Ar', Pd(0)
        "active_arc": 4,
    },
]

LATEX_TEMPLATE = r"""
\documentclass[border=12pt]{standalone}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage{lmodern}
\usepackage{amsmath}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc,positioning,shapes.geometric}
\usepackage{xcolor}

% Couleurs paramétrées par Python
\definecolor{active}{RGB}{__COLOR__}
\definecolor{faded}{RGB}{180,180,180}
\definecolor{footerc}{RGB}{60,60,60}

% Style des nœuds (paramétré : actif = couleur étape, sinon = faded)
\tikzset{
  node1color/.style={draw=__C1__, text=__C1__, line width=__W1__, font=\sffamily\__NF1__\bfseries},
  node2color/.style={draw=__C2__, text=__C2__, line width=__W2__, font=\sffamily\__NF2__\bfseries},
  node3color/.style={draw=__C3__, text=__C3__, line width=__W3__, font=\sffamily\__NF3__\bfseries},
  node4color/.style={draw=__C4__, text=__C4__, line width=__W4__, font=\sffamily\__NF4__\bfseries},
  arc1color/.style={draw=__A1__, line width=__AW1__},
  arc2color/.style={draw=__A2__, line width=__AW2__},
  arc3color/.style={draw=__A3__, line width=__AW3__},
  arc4color/.style={draw=__A4__, line width=__AW4__},
  label1color/.style={text=__A1__, font=\sffamily\__LSZ1__\__LB1__},
  label2color/.style={text=__A2__, font=\sffamily\__LSZ2__\__LB2__},
  label3color/.style={text=__A3__, font=\sffamily\__LSZ3__\__LB3__},
  label4color/.style={text=__A4__, font=\sffamily\__LSZ4__\__LB4__},
}

\begin{document}
\begin{tikzpicture}[
  every node/.style={font=\sffamily\bfseries},
  cycarrow/.style={->, >={Stealth[length=18pt,width=14pt]}},
  pdnode/.style={circle, minimum size=2.4cm, inner sep=2pt, align=center},
  side/.style={font=\sffamily\bfseries\small, text=footerc, inner sep=2pt},
]

% Bounding box explicite : force toutes les images à avoir EXACTEMENT
% les mêmes dimensions (indépendamment de la longueur des labels actifs)
\useasboundingbox (-8.4, -5.5) rectangle (8.4, 6);

% ========== HEADER : équation encadrée ==========
\node[draw=black, line width=1.5pt, rounded corners=2pt, inner sep=10pt, font=\sffamily\bfseries\large]
  (header) at (0, 5.0) {$__EQUATION__$};

% ========== CYCLE : 4 nœuds (Pd(0), Ar-Pd-I, Ar-Pd-OCO2-, Ar-Pd-Ar') ==========
% Disposition : losange (4 sommets) compact
\node[pdnode, node1color] (pd0)    at ( 0, 2.4) {$\mathrm{Pd(0)}$};
\node[pdnode, node2color] (pdI)    at ( 2.6, 0) {$\mathrm{Ar\text{-}Pd(II)\text{-}I}$};
\node[pdnode, node3color] (pdOCO)  at ( 0,-2.4) {$\mathrm{Ar\text{-}Pd(II)\text{-}OCO_2^-}$};
\node[pdnode, node4color] (pdArAr) at (-2.6, 0) {$\mathrm{Ar\text{-}Pd(II)\text{-}Ar'}$};

% ========== 4 arcs (sens horaire) ==========
\draw[cycarrow, arc1color] (pd0)    to[bend left=25] (pdI);
\draw[cycarrow, arc2color] (pdI)    to[bend left=25] (pdOCO);
\draw[cycarrow, arc3color] (pdOCO)  to[bend left=25] (pdArAr);
\draw[cycarrow, arc4color] (pdArAr) to[bend left=25] (pd0);

% ========== Labels des étapes aux coins ; le label de l'etape ACTIVE est masque ==========
% (l'etape active est deja nommee par l'equation header + la couleur + la legende du slide ;
%  son coin reste libre pour les especes entrantes/sortantes).
\node[label1color, anchor=south west, align=left]  at ( 2.0, 1.8) {__LABEL1__};
\node[label2color, anchor=north west, align=left]  at ( 2.0,-1.8) {__LABEL2__};
\node[label3color, anchor=north east, align=right] at (-2.0,-1.8) {__LABEL3__};
\node[label4color, anchor=south east, align=right] at (-2.0, 1.8) {__LABEL4__};

% ========== Réactifs/produits du seul step actif ==========
__REACTANTS__

% ========== FOOTER : 3 faits cles (DESACTIVE dans l'image) ==========
% Les faits restent documentes dans STEPS[*]["facts"] cote Python pour reference
% mais ne sont plus imprimes sur l'image generee (decision utilisateur).
% \node[font=\sffamily\bfseries\normalsize, text=footerc] at (0, -4.5) {__FACTS__};

\end{tikzpicture}
\end{document}
"""

# Couleurs pour le composant "faded" (gris pâle)
GRAY = "180,180,180"
BLACK = "40,40,40"

# Réactifs/produits sur la flèche de l'étape active (style modèle ENS) :
# espèces entrantes (+) et sortantes (-) dessinées par de petites flèches
# le long de l'arc actif. Couleur = couleur de l'étape (style "active").
# Layout des arcs : 1=haut-droit, 2=bas-droit, 3=bas-gauche, 4=haut-gauche.
REACTANTS_BY_STEP = {
    # AO (arc pd0->pdI, haut-droit) : Ar-I rejoint l'arc en biais depuis l'exterieur
    1: r"""
\node[text=active, font=\sffamily\bfseries\normalsize, anchor=west] (r1in) at (4.2, 2.55) {$+\;\mathrm{Ar\text{-}I}$};
\draw[-{Stealth[length=8pt]}, active, line width=1.4pt] (r1in.west) to[bend right=16] (2.4, 1.95);
""",
    # LE (arc pdI->pdOCO, bas-droit) : entre KCO3- (concave, espace ouvert), sort KI (vers l'exterieur)
    2: r"""
\node[text=active, font=\sffamily\bfseries\normalsize, anchor=west] (r2in) at (4.2, -1.15) {$+\;\mathrm{KCO_3^-}$};
\draw[-{Stealth[length=8pt]}, active, line width=1.4pt] (r2in.west) to[bend left=16] (2.6, -1.5);
\node[text=active, font=\sffamily\bfseries\normalsize, anchor=west] (r2out) at (4.6, -2.95) {$-\;\mathrm{KI}$};
\draw[-{Stealth[length=8pt]}, active, line width=1.4pt] (2.7, -2.05) to[bend right=12] (r2out.west);
""",
    # TM (arc pdOCO->pdArAr, bas-gauche) : entre Ar'B(OH)3- (concave), sort B(OH)3 + HCO3- (exterieur)
    3: r"""
\node[text=active, font=\sffamily\bfseries\normalsize, anchor=east] (r3in) at (-4.2, -1.15) {$+\;\mathrm{Ar'B(OH)_3^-}$};
\draw[-{Stealth[length=8pt]}, active, line width=1.4pt] (r3in.east) to[bend right=16] (-2.6, -1.5);
\node[text=active, font=\sffamily\bfseries\normalsize, anchor=east, align=right] (r3out) at (-4.6, -2.95) {$-\;\mathrm{B(OH)_3},\ \mathrm{HCO_3^-}$};
\draw[-{Stealth[length=8pt]}, active, line width=1.4pt] (-2.7, -2.05) to[bend left=12] (r3out.east);
""",
    # ER (arc pdArAr->pd0, haut-gauche) : sort le produit Ar-Ar' (vers l'exterieur, depuis le milieu de l'arc)
    4: r"""
\node[text=active, font=\sffamily\bfseries\normalsize, anchor=east] (r4out) at (-4.2, 2.55) {$-\;\mathrm{Ar\text{-}Ar'}$ (produit)};
\draw[-{Stealth[length=8pt]}, active, line width=1.4pt] (-2.55, 2.15) to[bend right=12] (r4out.east);
""",
}


def generate_step(step_n: int) -> Path:
    """Génère le PNG pour l'étape `step_n` (1-4)."""
    step = STEPS[step_n - 1]
    active_color = step["color_rgb"]
    active_nodes = set(step["active_nodes"])
    active_arc = step["active_arc"]

    tex = LATEX_TEMPLATE.replace("__COLOR__", active_color)
    tex = tex.replace("__EQUATION__", step["equation"])
    tex = tex.replace("__FACTS__", step["facts"])
    tex = tex.replace("__REACTANTS__", REACTANTS_BY_STEP[step_n])

    # Labels des etapes : le coin de l'etape ACTIVE est masque (libere pour les especes)
    label_text = {
        1: r"1. Addition\\oxydante",
        2: r"2. \'Echange\\de ligands",
        3: r"3. Transm\'e-\\tallation",
        4: r"4. \'Elimination\\r\'eductrice",
    }
    for i in range(1, 5):
        tex = tex.replace(f"__LABEL{i}__", "" if i == active_arc else label_text[i])

    # Nœuds : taille uniforme (pas de scaling). Active = bordure épaisse + couleur. Faded = normal + gris.
    for i in range(1, 5):
        if i in active_nodes:
            tex = tex.replace(f"__C{i}__", "active")
            tex = tex.replace(f"__W{i}__", "3.5pt")
            tex = tex.replace(f"__NF{i}__", "normalsize")
        else:
            tex = tex.replace(f"__C{i}__", "faded")
            tex = tex.replace(f"__W{i}__", "1.2pt")
            tex = tex.replace(f"__NF{i}__", "normalsize")

    # Arcs et labels d'étape : actif (flèche très épaisse + label LARGE), faded normal
    for i in range(1, 5):
        if i == active_arc:
            tex = tex.replace(f"__A{i}__", "active")
            tex = tex.replace(f"__AW{i}__", "4.0pt")
            tex = tex.replace(f"__LSZ{i}__", "normalsize")
            tex = tex.replace(f"__LB{i}__", "bfseries")
        else:
            tex = tex.replace(f"__A{i}__", "faded")
            tex = tex.replace(f"__AW{i}__", "1.4pt")
            tex = tex.replace(f"__LSZ{i}__", "normalsize")
            tex = tex.replace(f"__LB{i}__", "bfseries")

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    job = f"cycle_etape{step['n']}_{step['abbr']}"
    tex_path = BUILD_DIR / f"{job}.tex"
    pdf_path = BUILD_DIR / f"{job}.pdf"
    png_path = OUT_DIR / f"{job}.png"

    tex_path.write_text(tex, encoding="utf-8")

    # Compile LaTeX -> PDF
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{job}.tex"],
        cwd=str(BUILD_DIR), capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[ERREUR pdflatex pour étape {step_n}]", file=sys.stderr)
        print(result.stdout[-2500:], file=sys.stderr)
        raise RuntimeError(f"pdflatex failed for step {step_n}")

    # Convertit PDF -> PNG (200 dpi, fond blanc opaque)
    result = subprocess.run(
        ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER",
         "-sDEVICE=png16m", "-r200",
         "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
         f"-sOutputFile={png_path.name}", f"{job}.pdf"],
        cwd=str(BUILD_DIR), capture_output=True, text=True
    )
    built_png = BUILD_DIR / png_path.name
    if built_png.exists():
        built_png.replace(png_path)

    print(f"[OK] étape {step_n} ({step['name']}) -> {png_path}")
    return png_path


def main():
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        generate_step(n)
    else:
        for n in range(1, 5):
            generate_step(n)


if __name__ == "__main__":
    main()
