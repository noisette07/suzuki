"""Vérifications de base du script Monte Carlo.

Lancer depuis la racine du dépôt :
    python3 tests/test_monte_carlo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from monte_carlo import (
    MESURES,
    masse_max_theorique,
    moyenne,
    ecart_type,
    percentile,
    simuler,
)


def test_masse_max():
    # 900 mg / 220.01 g/mol * 170.21 g/mol = 696.2 mg
    attendu = 900.0 / 220.01 * 170.21
    assert abs(masse_max_theorique(900.0) - attendu) < 1e-9


def test_stats():
    valeurs = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert moyenne(valeurs) == 3.0
    assert abs(ecart_type(valeurs) - 1.5811388) < 1e-6
    assert percentile(valeurs, 50) == 3.0
    assert percentile(valeurs, 0) == 1.0
    assert percentile(valeurs, 100) == 5.0


def test_simulation_reproductible():
    a = simuler(200, seed=1)
    b = simuler(200, seed=1)
    assert a == b, "même graine => mêmes tirages"


def test_ordres_de_grandeur():
    series = simuler(5000, seed=42)
    # Les moyennes simulées doivent retomber sur les valeurs nominales
    r_c1_nominal = MESURES["produit_c1"] / masse_max_theorique(MESURES["iodophenol"]) * 100
    assert abs(moyenne(series["r_c1"]) - r_c1_nominal) < 0.5
    # La dispersion vient surtout de la balance classique (~1-2 % à 2 sigma)
    assert 0.2 < 2 * ecart_type(series["r_c1"]) < 3.0


if __name__ == "__main__":
    for nom, fonction in sorted(globals().items()):
        if nom.startswith("test_"):
            fonction()
            print(f"OK  {nom}")
    print("Tous les tests passent.")
