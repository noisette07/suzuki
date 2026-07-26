from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = (
    SCRIPT_DIR.parent / "output" / "schema_montecarlo.png"
)


def normal_pdf(x: np.ndarray, mean: float, sigma: float) -> np.ndarray:
    scale = sigma * np.sqrt(2.0 * np.pi)
    return np.exp(-0.5 * ((x - mean) / sigma) ** 2) / scale


def build_figure() -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "axes.unicode_minus": False,
        }
    )

    x = np.linspace(53.0, 67.0, 1600)

    # Rendements ISOLES (masse brute, sans correction purete)
    # Monte Carlo N=10000, propagation des pesees uniquement
    mu_c2, sigma_c2 = 57.4, 1.3 / 2.0   # 2σ → écart-type
    mu_c1, sigma_c1 = 62.5, 1.4 / 2.0
    ci_c2 = (56.2, 58.7)
    ci_c1 = (61.1, 63.9)

    y_c2 = normal_pdf(x, mu_c2, sigma_c2)
    y_c1 = normal_pdf(x, mu_c1, sigma_c1)
    y_max = max(y_c1.max(), y_c2.max())

    fig = plt.figure(figsize=(14.0, 9.92), dpi=100, facecolor="white")
    grid = fig.add_gridspec(2, 1, height_ratios=[5.8, 1.7], hspace=0.12)
    ax = fig.add_subplot(grid[0])
    note_ax = fig.add_subplot(grid[1])

    ax.fill_between(x, y_c2, color="#d9d9d9", alpha=0.85, zorder=1)
    ax.fill_between(x, y_c1, color="#efefef", alpha=0.9, zorder=1)
    ax.plot(x, y_c2, color="black", linewidth=2.0, zorder=3)
    ax.plot(x, y_c1, color="black", linewidth=2.0, zorder=3)
    ax.vlines(mu_c2, 0, normal_pdf(np.array([mu_c2]), mu_c2, sigma_c2)[0], color="black", linewidth=1.7, zorder=4)
    ax.vlines(mu_c1, 0, normal_pdf(np.array([mu_c1]), mu_c1, sigma_c1)[0], color="black", linewidth=1.7, zorder=4)

    ax.set_xlim(53, 67)
    ax.set_ylim(0, y_max * 1.16)
    ax.set_xlabel("Rendement isolé (%)", fontsize=22)
    ax.set_ylabel("Densité de probabilité (arbitraire)", fontsize=22, labelpad=18)
    ax.set_yticks([])

    ticks = list(range(53, 68))
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{tick}%" for tick in ticks], fontsize=10)
    ax.tick_params(axis="x", width=1.8, length=6)

    for spine in ax.spines.values():
        spine.set_linewidth(1.8)

    top_y = y_max * 1.04
    ax.text(mu_c2, top_y, "Moyenne C2 = 57,4 %", fontsize=18, fontweight="bold", ha="center", va="bottom")
    ax.text(mu_c1, top_y, "Moyenne C1 = 62,5 %", fontsize=18, fontweight="bold", ha="center", va="bottom")

    ax.text(54.0, y_max * 0.86, "Rendement isolé C2", fontsize=18)
    ax.text(65.5, y_max * 0.86, "Rendement isolé C1", fontsize=18, ha="center")

    ax.annotate(
        "Incertitude\n$\\sigma$ = 1,3 %\n(pesées)",
        xy=(mu_c2 + sigma_c2, normal_pdf(np.array([mu_c2 + sigma_c2]), mu_c2, sigma_c2)[0] * 0.72),
        xytext=(54.0, y_max * 0.50),
        fontsize=16,
        ha="left",
        va="center",
        arrowprops=dict(
            arrowstyle="-|>",
            linewidth=1.6,
            color="black",
            connectionstyle="arc3,rad=-0.25",
        ),
    )

    ax.annotate(
        "Incertitude\n$\\sigma$ = 1,4 %\n(pesées)",
        xy=(mu_c1 + sigma_c1, normal_pdf(np.array([mu_c1 + sigma_c1]), mu_c1, sigma_c1)[0] * 0.72),
        xytext=(66.0, y_max * 0.50),
        fontsize=16,
        ha="center",
        va="center",
        arrowprops=dict(
            arrowstyle="-|>",
            linewidth=1.6,
            color="black",
            connectionstyle="arc3,rad=0.25",
        ),
    )

    interval_y = y_max * 0.05
    ax.annotate("", xy=(ci_c2[0], interval_y), xytext=(ci_c2[1], interval_y), arrowprops=dict(arrowstyle="<->", linewidth=1.8, color="#c0392b"))
    ax.annotate("", xy=(ci_c1[0], interval_y), xytext=(ci_c1[1], interval_y), arrowprops=dict(arrowstyle="<->", linewidth=1.8, color="#27ae60"))

    ax.annotate(
        "[56,2 ; 58,7]\n(IC 95 %)",
        xy=((ci_c2[0] + ci_c2[1]) / 2.0, interval_y),
        xytext=(54.5, y_max * 0.18),
        fontsize=16,
        ha="center",
        va="center",
        color="#c0392b",
        arrowprops=dict(
            arrowstyle="-|>",
            linewidth=1.5,
            color="#c0392b",
            connectionstyle="arc3,rad=-0.2",
        ),
    )

    ax.annotate(
        "[61,1 ; 63,9]\n(IC 95 %)",
        xy=((ci_c1[0] + ci_c1[1]) / 2.0, interval_y),
        xytext=(66.0, y_max * 0.22),
        fontsize=16,
        ha="center",
        va="center",
        color="#27ae60",
        arrowprops=dict(
            arrowstyle="-|>",
            linewidth=1.5,
            color="#27ae60",
            connectionstyle="arc3,rad=0.2",
        ),
    )

    # Annotation IC disjoints — la zone critique entre 58,7 et 61,1
    ax.axvspan(ci_c2[1], ci_c1[0], color="#fdecec", alpha=0.6, zorder=0)
    ax.text((ci_c2[1] + ci_c1[0]) / 2.0, y_max * 0.38,
            "Zone\ndisjointe\n(2,4 pt)",
            fontsize=12, fontweight="bold", color="#555",
            ha="center", va="center")

    note_ax.set_axis_off()
    note_ax.set_xlim(0, 1)
    note_ax.set_ylim(0, 1)
    note_ax.add_patch(
        Rectangle(
            (0.01, 0.04),
            0.98,
            0.9,
            fill=False,
            linewidth=1.8,
            edgecolor="black",
            transform=note_ax.transAxes,
        )
    )
    note_ax.text(
        0.5,
        0.76,
        "Distributions des rendements isolés (masse brute, sans correction)",
        ha="center",
        va="center",
        fontsize=17,
    )
    note_ax.text(
        0.04,
        0.50,
        "- IC 95 % disjoints (zone rose) : baisse C1 → C2 statistiquement significative.",
        ha="left",
        va="center",
        fontsize=14,
    )
    note_ax.text(
        0.04,
        0.28,
        "- Propagation des incertitudes de pesées (balance classique ±10 mg, balance de précision ±0,1 mg).",
        ha="left",
        va="center",
        fontsize=14,
    )
    note_ax.text(
        0.5,
        0.10,
        "Récupération Pd/C C1 : 68,1 ± 0,5 % | C2 : 70,7 ± 0,7 %",
        ha="center",
        va="bottom",
        fontsize=16,
    )

    fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.06)
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recrée le graphique Monte Carlo visible sur le schéma source."
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Chemin du PNG généré.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Affiche aussi la figure après génération.",
    )
    args = parser.parse_args()

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig = build_figure()
    fig.savefig(output_path, dpi=100, facecolor="white")
    if args.show:
        plt.show()
    plt.close(fig)

    print(f"Image générée : {output_path}")


if __name__ == "__main__":
    main()
