#!/usr/bin/env python3
"""Propagation d'incertitudes par méthode de Monte Carlo — projet Suzuki.

Contexte : couplage de Suzuki-Miyaura (4-iodophénol + acide phénylboronique,
catalyseur Pd/C recyclé sur 2 cycles). Les seules incertitudes propagées sont
celles des pesées :
  - balance classique  : ±10 mg  (4-iodophénol)
  - balance de précision : ±0,1 mg (produit purifié, Pd/C)

Pour chaque tirage, les masses sont perturbées par un bruit gaussien centré
sur la valeur mesurée, puis on recalcule rendement isolé et taux de
récupération du Pd/C. La pesée initiale de 4-iodophénol est commune aux deux
cycles : son tirage est partagé (variables corrélées).

Usage :
    python3 monte_carlo.py            # résumé + export CSV
    python3 monte_carlo.py -n 50000   # plus de tirages
    python3 monte_carlo.py --no-csv   # résumé seul
"""

import argparse
import csv
import math
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# Données expérimentales (mg, lues sur les balances)
# ---------------------------------------------------------------------------

MESURES = {
    "iodophenol": 900.0,     # 4-iodophénol engagé (balance classique)
    "produit_c1": 434.9,     # produit purifié, cycle 1
    "produit_c2": 399.7,     # produit purifié, cycle 2
    "pdc_avant": 49.2,       # Pd/C engagé au cycle 1
    "pdc_apres_c1": 33.5,    # Pd/C récupéré après le cycle 1
    "pdc_apres_c2": 23.7,    # Pd/C récupéré après le cycle 2
}

# Masses molaires (g/mol) et incertitudes-types des balances (mg)
M_IODOPHENOL = 220.01        # 4-iodophénol
M_PRODUIT = 170.21           # 4-hydroxybiphényle
M_PD = 106.42                # palladium
TENEUR_PD = 0.05             # Pd/C à 5 % massique
U_BALANCE_CLASSIQUE = 10.0   # ±0,01 g
U_BALANCE_PRECISION = 0.1    # ±0,1 mg


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def masse_max_theorique(m_iodophenol: float) -> float:
    """Masse maximale de produit (mg) si conversion totale du 4-iodophénol."""
    return m_iodophenol / M_IODOPHENOL * M_PRODUIT


def simuler(n: int, seed: int = 42) -> dict[str, list[float]]:
    """Tire n jeux de masses bruitées et calcule les grandeurs d'intérêt.

    Retourne un dictionnaire de séries : rendements isolés (%) et taux de
    récupération du Pd/C (%) pour chaque cycle.
    """
    rng = random.Random(seed)

    def tirage(cle: str, sigma: float) -> float:
        return rng.gauss(MESURES[cle], sigma)

    series = {"r_c1": [], "r_c2": [], "recup_c1": [], "recup_c2": []}
    for _ in range(n):
        # Tirage UNIQUE du 4-iodophénol : la même pesée sert aux 2 cycles
        m_iodo = tirage("iodophenol", U_BALANCE_CLASSIQUE)
        m_max = masse_max_theorique(m_iodo)

        m_prod_c1 = tirage("produit_c1", U_BALANCE_PRECISION)
        m_prod_c2 = tirage("produit_c2", U_BALANCE_PRECISION)
        m_pdc_avant = tirage("pdc_avant", U_BALANCE_PRECISION)
        m_pdc_c1 = tirage("pdc_apres_c1", U_BALANCE_PRECISION)
        m_pdc_c2 = tirage("pdc_apres_c2", U_BALANCE_PRECISION)

        series["r_c1"].append(m_prod_c1 / m_max * 100)
        series["r_c2"].append(m_prod_c2 / m_max * 100)
        # Récupération : C2 est rapporté au Pd/C réengagé (celui récupéré en C1)
        series["recup_c1"].append(m_pdc_c1 / m_pdc_avant * 100)
        series["recup_c2"].append(m_pdc_c2 / m_pdc_c1 * 100)

    return series


# ---------------------------------------------------------------------------
# Statistiques
# ---------------------------------------------------------------------------

def moyenne(valeurs: list[float]) -> float:
    return sum(valeurs) / len(valeurs)


def ecart_type(valeurs: list[float]) -> float:
    """Écart-type d'échantillon (dénominateur n-1)."""
    m = moyenne(valeurs)
    return math.sqrt(sum((x - m) ** 2 for x in valeurs) / (len(valeurs) - 1))


def percentile(valeurs: list[float], p: float) -> float:
    """Percentile par interpolation linéaire (0 <= p <= 100)."""
    tri = sorted(valeurs)
    k = (len(tri) - 1) * p / 100
    i = int(k)
    j = min(i + 1, len(tri) - 1)
    return tri[i] + (k - i) * (tri[j] - tri[i])


def resume(nom: str, valeurs: list[float]) -> str:
    """Ligne de synthèse : moyenne ± 2 sigma et intervalle de confiance à 95 %."""
    return (
        f"  {nom} : {moyenne(valeurs):.1f} +/- {2 * ecart_type(valeurs):.1f} %"
        f"   IC 95 % : [{percentile(valeurs, 2.5):.1f} ; {percentile(valeurs, 97.5):.1f}]"
    )


# ---------------------------------------------------------------------------
# Programme principal
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-n", type=int, default=10_000, help="nombre de tirages")
    parser.add_argument("--seed", type=int, default=42, help="graine aléatoire")
    parser.add_argument("--no-csv", action="store_true", help="ne pas exporter le CSV")
    parser.add_argument(
        "-o", "--output", default="output/monte_carlo_data.csv",
        help="chemin du CSV exporté",
    )
    args = parser.parse_args()

    series = simuler(args.n, args.seed)

    mol_pct_pd = (
        MESURES["pdc_avant"] * TENEUR_PD / M_PD
        / (MESURES["iodophenol"] / M_IODOPHENOL) * 100
    )
    print(f"Monte Carlo, {args.n} tirages (seed {args.seed})")
    print(f"Masse maximale théorique : {masse_max_theorique(MESURES['iodophenol']):.0f} mg")
    print(f"Charge catalytique : {mol_pct_pd:.2f} mol% Pd")
    print()
    print("Rendement isolé (masse brute)")
    print(resume("C1", series["r_c1"]))
    print(resume("C2", series["r_c2"]))
    print()
    print("Récupération Pd/C")
    print(resume("C1", series["recup_c1"]))
    print(resume("C2", series["recup_c2"]))

    if not args.no_csv:
        chemin = Path(__file__).resolve().parent / args.output
        chemin.parent.mkdir(parents=True, exist_ok=True)
        with open(chemin, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tirage", "r_c1", "r_c2", "recup_pdc_c1", "recup_pdc_c2"])
            for i in range(args.n):
                writer.writerow([
                    i + 1,
                    f"{series['r_c1'][i]:.4f}",
                    f"{series['r_c2'][i]:.4f}",
                    f"{series['recup_c1'][i]:.4f}",
                    f"{series['recup_c2'][i]:.4f}",
                ])
        print(f"\nExport : {chemin}")


if __name__ == "__main__":
    main()
