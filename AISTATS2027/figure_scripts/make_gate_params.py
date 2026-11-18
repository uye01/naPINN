"""Gate-parameter trajectories on lambda-omega, labeled with the paper's notation.

The logged values are the pre-softplus parameters (they start at 2.0 and 30.0),
so the axes read tilde-tau and tilde-a. Data and smoothing are those of
analysis/plots/plot_steepness_cutoff.py.

Usage: python3 make_gate_params.py OUT_PDF
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from analysis.plots.plot_steepness_cutoff import _plot_gate_param_on_ax, set_pub_style  # noqa: E402

DATA = REPO / "analysis" / "results" / "data"
NAMES = ["15%", "10%", "5%"]


def main(out):
    set_pub_style()
    plt.rcParams.update({"pdf.fonttype": 42})
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 5.0))
    common = dict(curve_names=NAMES, smooth=True, smooth_method="savgol",
                  smooth_window=31, smooth_poly=3)
    _plot_gate_param_on_ax(axes[0], DATA / "cutoff.csv", r"Cutoff $\tilde\tau$",
                           legend_position="True", legend_bbox=(1.02, 0.62), **common)
    _plot_gate_param_on_ax(axes[1], DATA / "steepness.csv", r"Steepness $\tilde a$",
                           legend_position="False", **common)
    for ax in axes:
        ax.grid(False)
        ax.set_ylabel(ax.get_ylabel(), fontsize=13)
    axes[1].set_xlabel("Update", fontsize=13)
    fig.tight_layout(h_pad=1.0)
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1])
