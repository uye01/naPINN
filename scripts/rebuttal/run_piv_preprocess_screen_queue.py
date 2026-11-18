#!/usr/bin/env python3
"""Run the pre-processing-screen baseline on real PIV, per the frozen manifest.

Reads outputs/rebuttal/preprocess_screen_piv_20260730/manifest_frozen.json and
launches exactly the runs it declares. Nothing about the screen, the threshold,
or the seed set is decided here; this script only dispatches.

Legacy-4G carries a per-seed corruption realization, so its variant config is
selected by seed. The structured corruptions were injected once, so all three
seeds share one artifact and vary only the model initialization.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path


MANIFEST = Path("outputs/rebuttal/preprocess_screen_piv_20260730/manifest_frozen.json")
LEGACY_VARIANT = (
    "configs/experiment/realpdebench_cylinder_legacy4g_seed{seed}_r15_b1_o1.yaml"
)


def build_jobs(manifest: dict) -> list[dict]:
    jobs = []
    for condition, spec in manifest["conditions"].items():
        for screen in spec["screens"]:
            k = spec["selected_k"][screen]
            for seed in manifest["seeds"]:
                variant = (
                    LEGACY_VARIANT.format(seed=seed)
                    if spec["per_seed_corruption_realization"]
                    else spec["variant_config"]
                )
                jobs.append(
                    {
                        "condition": condition,
                        "screen": screen,
                        "k": k,
                        "seed": seed,
                        "variant": variant,
                        "run_name": f"{condition}_{screen}_k{k}_seed_{seed}",
                    }
                )
    return jobs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--devices", default="cuda:0,cuda:1,cuda:2,cuda:3")
    parser.add_argument(
        "--per-device",
        type=int,
        default=2,
        help="Concurrent runs per GPU. Peak memory is under 500 MB per run.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    jobs = build_jobs(manifest)
    if len(jobs) != manifest["expected_runs"]:
        raise SystemExit(
            f"Built {len(jobs)} jobs but the manifest declares "
            f"{manifest['expected_runs']}"
        )

    devices = args.devices.split(",")
    slots = [device for device in devices for _ in range(args.per_device)]
    root = Path(manifest["output_root"])
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    pending = list(jobs)
    running: list[tuple[subprocess.Popen, dict, str]] = []
    completed, failed = 0, []
    while pending or running:
        while pending and len(running) < len(slots):
            busy = [device for _, _, device in running]
            free = next(d for d in slots if busy.count(d) < args.per_device)
            job = pending.pop(0)
            command = [
                "python",
                "scripts/rebuttal/run_realpdebench.py",
                "--exp-config",
                "configs/experiment/realpdebench_cylinder_mse.yaml",
                "--variant-config",
                job["variant"],
                "--seed",
                str(job["seed"]),
                "--device",
                free,
                "--output-root",
                str(root),
                "--run-name",
                job["run_name"],
                "--preprocess-screen",
                job["screen"],
                "--preprocess-k",
                str(job["k"]),
            ]
            if args.dry_run:
                print(" ".join(command))
                continue
            log = (log_dir / f"{job['run_name']}.log").open("w")
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            running.append((process, job, free))
            print(f"launch {job['run_name']} on {free}", flush=True)
        if args.dry_run:
            break
        time.sleep(10)
        for entry in list(running):
            process, job, _ = entry
            if process.poll() is None:
                continue
            running.remove(entry)
            if process.returncode == 0:
                completed += 1
                print(f"done   {job['run_name']}  ({completed}/{len(jobs)})", flush=True)
            else:
                failed.append(job["run_name"])
                print(f"FAILED {job['run_name']} rc={process.returncode}", flush=True)

    if failed:
        raise SystemExit(f"{len(failed)} runs failed: {failed}")
    print(f"all {completed} runs complete")


if __name__ == "__main__":
    main()
