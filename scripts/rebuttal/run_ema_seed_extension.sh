#!/usr/bin/env bash
# EMA seed extension for reviewer 6XZg's W5.
#
# The three-seed sweep could not distinguish a trend from seed noise: at
# m = 0.01 the sample s.d. was 0.03716, which spans the whole range of means.
# This adds seeds 43-47 so the sweep has eight seeds per value. Seeds 40-42
# already exist in outputs/rebuttal/synthetic_supplement_recovery_20260726 and
# are not re-run; the aggregation combines both roots.
set -u
GPU="${1:?usage: run_ema_seed_extension.sh <gpu>}"
ROOT=outputs/rebuttal/ema_seed_extension_20260728

for M in 0.01 0.05 0.10; do
  for SEED in 43 44 45 46 47; do
    echo "=== m=${M} seed=${SEED} ==="
    python -m scripts.rebuttal.run_synthetic \
      --experiment-name allencahn2d \
      --method napinn \
      --seed "${SEED}" \
      --device "cuda:${GPU}" \
      --noise-kind 4G \
      --outlier-ratio 0.15 \
      --ema-momentum "${M}" \
      --rejection-cost 0.5 \
      --experiment-config configs/rebuttal/allencahn2d.yaml \
      --output-root "${ROOT}"
  done
done
