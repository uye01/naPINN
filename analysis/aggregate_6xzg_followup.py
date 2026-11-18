#!/usr/bin/env python3
"""Aggregate the three follow-up campaigns for reviewer 6XZg.

E1 pre-processing baseline (W4), E2 HMC B-PINN (W1) and E3 the EMA seed
extension (W5). Each section prints only complete groups and says plainly what
is still missing, so a partial campaign cannot be mistaken for a finished one.
"""

from __future__ import annotations

import argparse
import glob
import json
import statistics
from collections import defaultdict
from pathlib import Path


PDES = ["allencahn2d", "burgers2d", "lambdaomega2d"]
SCREENS = ["global_z", "global_mad", "local_median"]
REQUIRED_SEEDS = {40, 41, 42}


def load(pattern: str) -> list[dict]:
    """Load complete runs, keeping the path since some settings live only there.

    ``ema_momentum`` and ``sigma_data`` are encoded in the output directory by
    the runner and the queue script rather than written into metrics.json.
    """
    out = []
    for path in glob.glob(pattern, recursive=True):
        payload = json.loads(Path(path).read_text())
        if payload.get("status") == "complete":
            payload["_path"] = path
            out.append(payload)
    return out


def from_path(path: str, marker: str) -> float | None:
    # Deepest first: the output root can itself begin with the marker (for
    # example ema_seed_extension_...), which would otherwise shadow the
    # sensitivity label that actually carries the value.
    for part in reversed(Path(path).parts):
        if part.startswith(marker):
            token = part[len(marker):].split("_")[0]
            try:
                return float(token)
            except ValueError:
                return None
    return None


def summarise(values: list[float]) -> str:
    if len(values) < 2:
        return f"{statistics.fmean(values):.5f} (n={len(values)})"
    return f"{statistics.fmean(values):.5f} +- {statistics.stdev(values):.5f}"


def report_preprocess(root: Path) -> None:
    print("\n=== E1  pre-processing baseline (W4): screen, drop, train MSE-PINN ===")
    runs = load(str(root / "**" / "metrics.json"))
    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in runs:
        screen = (r.get("preprocess_screen") or {}).get("screen")
        if screen:
            cells[(r["experiment_name"], screen)].append(r)
    print(f"{'PDE':<15}{'screen':<15}{'rMAE':>22}{'outliers cut':>14}{'clean cut':>11}")
    for pde in PDES:
        for screen in SCREENS:
            got = cells.get((pde, screen), [])
            seeds = {r["seed"] for r in got}
            if not REQUIRED_SEEDS.issubset(seeds):
                missing = sorted(REQUIRED_SEEDS - seeds)
                print(f"{pde:<15}{screen:<15}{'incomplete, missing seeds ' + str(missing):>47}")
                continue
            got = [r for r in got if r["seed"] in REQUIRED_SEEDS]
            rmae = [r["field_rMAE"] for r in got]
            out = [r["preprocess_screen"]["known_outlier_removed_fraction"] for r in got]
            clean = [r["preprocess_screen"]["known_clean_removed_fraction"] for r in got]
            print(
                f"{pde:<15}{screen:<15}{summarise(rmae):>22}"
                f"{100 * statistics.fmean(out):>13.1f}%{100 * statistics.fmean(clean):>10.2f}%"
            )


def report_hmc(root: Path) -> None:
    print("\n=== E2  HMC B-PINN (W1) ===")
    runs = load(str(root / "**" / "metrics.json"))
    if not runs:
        print("  no completed runs yet")
        return
    by_sigma: dict[float, list[dict]] = defaultdict(list)
    for r in runs:
        by_sigma[from_path(r["_path"], "sigma_data_")].append(r)
    for sigma, group in sorted(by_sigma.items(), key=lambda kv: str(kv[0])):
        rmae = [r["field_rMAE_posterior_mean_of_draws"] for r in group]
        acc = [r["diagnostics"]["acceptance_rate"] for r in group]
        rhat = [r["diagnostics"]["split_r_hat_on_pde_parameter"] for r in group]
        passed = [r["diagnostics"]["passes_predeclared_thresholds"] for r in group]
        print(
            f"  sigma_data={sigma}: rMAE {summarise(rmae)}  "
            f"acceptance {statistics.fmean(acc):.3f}  "
            f"R-hat {statistics.fmean(rhat):.3f}  "
            f"diagnostics passed {sum(passed)}/{len(passed)}  (n={len(group)})"
        )
    print(
        "  Reporting rule: if the predeclared thresholds are not met, report the"
        " attempt as inconclusive and do not quote the error value."
    )


def report_ema(new_root: Path, base_root: Path) -> None:
    print("\n=== E3  EMA sweep, seeds 40-42 plus 43-47 (W5) ===")
    combined: dict[float, list[tuple[int, float]]] = defaultdict(list)
    for r in load(str(base_root / "**" / "metrics.json")):
        if (
            r.get("method") == "napinn"
            and r.get("experiment_name") == "allencahn2d"
            and r.get("outlier_ratio") == 0.15
            and "_reject_0.5_" in r["_path"]
            and "gcut" not in r["_path"]
            and "gsteep" not in r["_path"]
            and "warmup" not in r["_path"]
        ):
            m = from_path(r["_path"], "ema_")
            if m is not None:
                combined[m].append((r["seed"], r["field_rMAE"]))
    for r in load(str(new_root / "**" / "metrics.json")):
        m = from_path(r["_path"], "ema_")
        if m is not None:
            combined[m].append((r["seed"], r["field_rMAE"]))
    for m in sorted(combined):
        pairs = sorted(set(combined[m]))
        values = [v for _, v in pairs]
        print(f"  m={m:<5} {summarise(values):<26} n={len(values)}  seeds {[s for s, _ in pairs]}")
    print("  W5 asks whether the ordering is a trend or seed noise; read the s.d.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--preprocess-root",
        type=Path,
        default=Path("outputs/rebuttal/preprocess_screen_20260728"),
    )
    parser.add_argument(
        "--hmc-root", type=Path, default=Path("outputs/rebuttal/hmc_bpinn_20260728")
    )
    parser.add_argument(
        "--ema-root",
        type=Path,
        default=Path("outputs/rebuttal/ema_seed_extension_20260728"),
    )
    parser.add_argument(
        "--ema-base-root",
        type=Path,
        default=Path("outputs/rebuttal/synthetic_supplement_recovery_20260726"),
    )
    args = parser.parse_args()
    report_preprocess(args.preprocess_root)
    report_hmc(args.hmc_root)
    report_ema(args.ema_root, args.ema_base_root)
