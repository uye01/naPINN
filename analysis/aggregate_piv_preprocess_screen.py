#!/usr/bin/env python3
"""Aggregate the real-PIV pre-processing-screen campaign.

Complete three-seed groups only. The like-for-like contrast is screen+MSE-PINN
against the same MSE-PINN with no screen, since that pair differs in exactly one
thing. naPINN is shown alongside as context, taken from the completed campaigns
in this repository.
"""

from __future__ import annotations

import argparse
import glob
import json
import statistics
from collections import defaultdict
from pathlib import Path


REQUIRED_SEEDS = {40, 41, 42}
SCREENS = ["global_z", "global_mad", "local_median"]

# Where the unscreened reference runs live for each condition.
REFERENCE = {
    "legacy4g_r15": {
        "aggregation": "analysis/results/runs/rebuttal_realpde_legacy_4g/aggregation.json",
        "group_filter": "ratio=0.15|b=1|o=1",
    },
    "ar1": {"glob": "outputs/rebuttal/realpde_recovery_20260726/cylinder_real_piv/{m}_ar1"},
    "spatial_burst": {
        "glob": "outputs/rebuttal/realpde_recovery_20260726/cylinder_real_piv/{m}_spatial_burst"
    },
    "sensor_drift10": {
        "glob": "outputs/rebuttal/realpde_recovery_20260726/cylinder_real_piv/{m}_sensor_drift10"
    },
    "sensor_drift30": {
        "glob": "outputs/rebuttal/realpde_recovery_20260726/cylinder_real_piv/{m}_sensor_drift30"
    },
}
REFERENCE_METHODS = {"mse": "mse", "naPINN": "napinn_rejection_01"}


def summarise(values: list[float]) -> str:
    if len(values) < 2:
        return f"{statistics.fmean(values):.4f} (n={len(values)})"
    return f"{statistics.fmean(values):.4f} +- {statistics.stdev(values):.4f}"


def load_screen_runs(root: Path) -> dict[tuple[str, str], list[dict]]:
    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for path in glob.glob(str(root / "**" / "metrics.json"), recursive=True):
        payload = json.loads(Path(path).read_text())
        if payload.get("status") != "complete":
            continue
        screen = payload.get("preprocess_screen")
        if not screen:
            continue
        # The run name carries the condition; the tag alone does not, because
        # legacy-4G encodes its corruption seed in the tag.
        run_name = Path(path).parent.name
        condition = run_name.rsplit(f"_{screen['screen']}_", 1)[0]
        cells[(condition, screen["screen"])].append(payload)
    return cells


def reference_means(condition: str) -> dict[str, list[float]]:
    spec = REFERENCE[condition]
    out: dict[str, list[float]] = {}
    if "aggregation" in spec:
        payload = json.loads(Path(spec["aggregation"]).read_text())
        for group in payload["groups"]:
            if spec["group_filter"] not in group["group_id"]:
                continue
            for label, method in REFERENCE_METHODS.items():
                canonical = "napinn" if method.startswith("napinn") else method
                if group["method"] == canonical and label not in out:
                    out[label] = list(group["metrics"]["rMAE"]["per_seed"].values())
        return out
    for label, method in REFERENCE_METHODS.items():
        values = []
        for path in glob.glob(spec["glob"].format(m=method) + "/heldout_seed_4*/metrics.json"):
            payload = json.loads(Path(path).read_text())
            if payload.get("status") == "complete":
                values.append(payload["rMAE"])
        if values:
            out[label] = values
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path("outputs/rebuttal/preprocess_screen_piv_20260730")
    )
    args = parser.parse_args()

    manifest = json.loads((args.root / "manifest_frozen.json").read_text())
    cells = load_screen_runs(args.root)

    print(
        f"\n{'condition':<16}{'screen':<14}{'k':>5}{'rMAE (screen+MSE)':>24}"
        f"{'corrupt cut':>13}{'clean cut':>11}"
    )
    for condition, spec in manifest["conditions"].items():
        reference = reference_means(condition)
        for label, values in reference.items():
            if len(values) == len(REQUIRED_SEEDS):
                print(f"{condition:<16}{'[no screen] ' + label:<19}{summarise(values):>37}")
        for screen in spec["screens"]:
            runs = cells.get((condition, screen), [])
            seeds = {r["seed"] for r in runs}
            if not REQUIRED_SEEDS.issubset(seeds):
                missing = sorted(REQUIRED_SEEDS - seeds)
                print(f"{condition:<16}{screen:<14}{spec['selected_k'][screen]:>5}"
                      f"{'  incomplete, missing seeds ' + str(missing)}")
                continue
            runs = [r for r in runs if r["seed"] in REQUIRED_SEEDS]
            rmae = [r["rMAE"] for r in runs]
            cut = [r["preprocess_screen"]["known_outlier_removed_fraction"] for r in runs]
            clean = [r["preprocess_screen"]["known_clean_removed_fraction"] for r in runs]
            print(
                f"{condition:<16}{screen:<14}{spec['selected_k'][screen]:>5}"
                f"{summarise(rmae):>24}"
                f"{100 * statistics.fmean(cut):>12.1f}%{100 * statistics.fmean(clean):>10.2f}%"
            )
        print()

    print(
        "Reading rule: the screen row and the [no screen] mse row differ in exactly one\n"
        "thing, so their gap is the effect of pre-processing. The two removal columns,\n"
        "not the error alone, explain why the gap goes the way it does."
    )


if __name__ == "__main__":
    main()
