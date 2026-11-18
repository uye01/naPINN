#!/usr/bin/env python3
"""Select the pre-processing screen threshold on real PIV, before any training.

Same rule as the synthetic campaign: for each screen, scan k, score detection
against the known corruption labels, and take the best F1. Selection looks at
detection quality only; no field error is inspected. The chosen thresholds are
frozen into a manifest before a single training run starts.

The legacy-4G condition has a seed-39 corruption realization that no reporting
run uses, so it is calibrated exactly like the synthetic benchmarks. The
structured conditions -- persistent drift and spatially clustered burst failure
-- were injected once, so there is no held-out realization to calibrate on and
the threshold is chosen on the same data that is later evaluated. That is more
generous to the baseline than the synthetic protocol, and it is disclosed
rather than hidden.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
from pathlib import Path

import torch
import yaml

from pinnlab.registry import get_experiment
from pinnlab.utils.seed import seed_everything
from scripts.rebuttal.preprocess_screen import SCREENS, compute_screen_mask


K_GRID = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
CALIBRATION_SEED = 39


def deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_experiment(
    common_config: Path,
    exp_config: Path,
    variant_config: Path,
    device: str,
    seed: int,
):
    # Same composition order as the runner: common, then method, then variant.
    config = deep_merge(
        yaml.safe_load(common_config.read_text()),
        yaml.safe_load(exp_config.read_text()),
    )
    config = deep_merge(config, yaml.safe_load(variant_config.read_text()))
    config["device"] = device
    seed_everything(seed)
    with contextlib.redirect_stdout(io.StringIO()):
        experiment = get_experiment(config["experiment_name"])(config, torch.device(device))
    return experiment


def score(flagged: torch.Tensor, corrupted: torch.Tensor) -> dict[str, float]:
    true_positive = int((flagged & corrupted).sum())
    false_positive = int((flagged & ~corrupted).sum())
    false_negative = int((~flagged & corrupted).sum())
    precision = true_positive / max(true_positive + false_positive, 1)
    recall = true_positive / max(true_positive + false_negative, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1.0e-12)
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "clean_removed_fraction": float(flagged[~corrupted].float().mean()),
        "removed_fraction": float(flagged.float().mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--common-config",
        type=Path,
        default=Path("configs/experiment/realpdebench_cylinder_common.yaml"),
    )
    parser.add_argument("--exp-config", type=Path, required=True)
    parser.add_argument("--variant-config", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--seed", type=int, default=CALIBRATION_SEED)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    experiment = load_experiment(
        args.common_config,
        args.exp_config,
        args.variant_config,
        args.device,
        args.seed,
    )
    corrupted = experiment.data_corruption_labels.any(dim=1)
    coordinates = experiment.X_data.detach()
    values = experiment.y_data.detach()

    print(
        f"{args.label}: {values.shape[0]} rows, "
        f"{int(corrupted.sum())} corrupted ({100 * float(corrupted.float().mean()):.1f}%)"
    )
    selected: dict[str, float] = {}
    detail: dict[str, dict] = {}
    for screen in SCREENS:
        best = None
        rows = []
        for k in K_GRID:
            flagged = compute_screen_mask(coordinates, values, screen, k)
            row = {"k": k, **score(flagged, corrupted)}
            rows.append(row)
            if best is None or row["f1"] > best["f1"]:
                best = row
        selected[screen] = best["k"]
        detail[screen] = {"grid": rows, "selected": best}
        print(f"  {screen:<14} k={best['k']:<4} F1={best['f1']:.3f} "
              f"recall={best['recall']:.3f} precision={best['precision']:.3f} "
              f"clean_cut={100 * best['clean_removed_fraction']:.2f}%")

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(
                {
                    "label": args.label,
                    "common_config": str(args.common_config),
                    "exp_config": str(args.exp_config),
                    "variant_config": str(args.variant_config),
                    "calibration_seed": args.seed,
                    "k_grid": K_GRID,
                    "n_rows": int(values.shape[0]),
                    "n_corrupted_rows": int(corrupted.sum()),
                    "selected_k": selected,
                    "detail": detail,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
