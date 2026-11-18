#!/usr/bin/env bash
# Pre-processing baseline for reviewer 6XZg's W4.
#
# Screen the raw measurements, drop the flagged rows, then train an ordinary
# MSE-PINN. Thresholds were selected on calibration seed 39 by detection F1 and
# frozen in outputs/rebuttal/preprocess_screen_20260728/manifest_frozen.json
# before these runs started.
#
# Shard 0 takes allencahn2d, shard 1 takes burgers2d and lambdaomega2d.
set -u
GPU="${1:?usage: run_preprocess_screen_queue.sh <gpu> <shard>}"
SHARD="${2:?usage: run_preprocess_screen_queue.sh <gpu> <shard>}"
ROOT=outputs/rebuttal/preprocess_screen_20260728

if [ "${SHARD}" = "0" ]; then
  PDES="allencahn2d"
else
  PDES="burgers2d lambdaomega2d"
fi

for PDE in ${PDES}; do
  for SCREEN in global_z global_mad local_median; do
    case "${PDE}_${SCREEN}" in
      allencahn2d_global_z)      K=1.5 ;;
      allencahn2d_global_mad)    K=2.0 ;;
      allencahn2d_local_median)  K=2.0 ;;
      burgers2d_global_z)        K=1.5 ;;
      burgers2d_global_mad)      K=2.0 ;;
      burgers2d_local_median)    K=2.5 ;;
      lambdaomega2d_global_z)    K=2.0 ;;
      lambdaomega2d_global_mad)  K=2.0 ;;
      lambdaomega2d_local_median) K=2.5 ;;
      *) echo "no frozen threshold for ${PDE}_${SCREEN}" >&2; exit 1 ;;
    esac
    for SEED in 40 41 42; do
      echo "=== ${PDE} ${SCREEN} k=${K} seed=${SEED} ==="
      python -m scripts.rebuttal.run_synthetic \
        --experiment-name "${PDE}" \
        --method mse \
        --seed "${SEED}" \
        --device "cuda:${GPU}" \
        --noise-kind 4G \
        --outlier-ratio 0.15 \
        --preprocess-screen "${SCREEN}" \
        --preprocess-k "${K}" \
        --experiment-config "configs/rebuttal/${PDE}.yaml" \
        --output-root "${ROOT}"
    done
  done
done
