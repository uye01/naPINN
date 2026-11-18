"""Redraw the trained-gate figure with the paper's notation.

The original run outputs are not in this checkout, so the measurement
positions are read back from the original vector figure (extracted by
extract_vector_figures.py). Axis calibration comes from the tick marks of that
figure. Allen-Cahn, 10% gross outliers, trained gate tau = 2.18, a = 36.12.

Usage: python3 make_gate.py ORIGINAL_GATE_PDF OUT_PDF
"""

import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pymupdf

TAU, A = 2.18, 36.12
N_CLEAN, N_CORRUPT = 20250, 2250

# Calibration from the original tick marks (PDF points, y downward).
X_AT_MINUS7, X_PER_UNIT = 42.94, 61.245
Y_AT_0, Y_AT_1 = 213.12, 11.52
LEGEND_BOX = (45.0, 0.0, 85.0, 70.0)  # legend handles, excluded from data


def read_points(path):
    page = pymupdf.open(path)[0]
    clean, corrupt = [], []
    for d in page.get_drawings():
        f = d.get("fill")
        if not f or d["rect"].width > 5 or d["rect"].width < 3:
            continue
        cx, cy = (d["rect"].x0 + d["rect"].x1) / 2, (d["rect"].y0 + d["rect"].y1) / 2
        if LEGEND_BOX[0] < cx < LEGEND_BOX[2] and cy < LEGEND_BOX[3]:
            continue
        z = -7 + (cx - X_AT_MINUS7) / X_PER_UNIT
        g = (Y_AT_0 - cy) / (Y_AT_0 - Y_AT_1)
        if f[0] == 0 and abs(f[1] - 0.502) < 0.01:
            clean.append((z, g))
        elif f[0] == 1 and f[1] == 0:
            corrupt.append((z, g))
    return np.array(clean), np.array(corrupt)


def main(src, out):
    clean, corrupt = read_points(src)
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
        "mathtext.fontset": "cm",
        "pdf.fonttype": 42,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
    # Same size as the noise-density panel it sits next to in the paper.
    fig, ax = plt.subplots(figsize=(493 / 72, 276 / 72))
    z = np.linspace(-8, 2, 2000)
    ax.plot(z, 1 / (1 + np.exp(-A * (z + TAU))), "k--", lw=2.5, dashes=(3.7, 1.6),
            label=rf"Learned gate ($\tau = {TAU}$, $a = {A}$)")
    ax.scatter(clean[:, 0], clean[:, 1], c="green", alpha=0.4, s=15, linewidths=1.0,
               label=f"Clean ({N_CLEAN:,} measurements)")
    ax.scatter(corrupt[:, 0], corrupt[:, 1], c="red", alpha=0.4, s=15, linewidths=1.0,
               label=f"Corrupted ({N_CORRUPT:,} measurements)")
    ax.axvline(-TAU, color="gray", ls=":", lw=2, dashes=(1, 1.65), label=r"Cutoff $z_i = -\tau$")
    ax.set_xlim(-7, -7 + (545.14 - 42.94) / X_PER_UNIT)
    ax.set_ylim(-(223.2 - Y_AT_0) / (Y_AT_0 - Y_AT_1), (Y_AT_0 - 1.44) / (Y_AT_0 - Y_AT_1))
    ax.set_xlabel(r"Standardized log-density $z_i$", fontsize=13)
    ax.set_ylabel(r"Reliability weight $g_i$", fontsize=13)
    ax.tick_params(labelsize=11)
    ax.legend(loc="upper left", fontsize=11, frameon=False, borderaxespad=0.2)
    fig.tight_layout(pad=0.2)
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
    print(f"{len(clean)} clean and {len(corrupt)} corrupted markers redrawn -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
