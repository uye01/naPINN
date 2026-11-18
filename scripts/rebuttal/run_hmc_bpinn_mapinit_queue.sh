#!/usr/bin/env bash
# Corrected HMC B-PINN campaign (Reviewer 6XZg, W1).
#
# Supersedes run_hmc_bpinn_queue.sh, whose chains never left their random
# initialisation. See the frozen manifest in the output root for why that
# campaign is void and what changed here.
#
# One config per GPU; the caller passes the GPU index and the config index.
set -u
GPU="${1:?usage: run_hmc_bpinn_mapinit_queue.sh <gpu> <sigma_data> <seed>}"
SD="${2:?}"
SEED="${3:?}"
ROOT=outputs/rebuttal/hmc_bpinn_mapinit_20260731

python -m scripts.rebuttal.run_synthetic_hmc_bpinn \
  --seed "${SEED}" --device "cuda:${GPU}" \
  --sigma-data "${SD}" --sigma-pde 1.0 \
  --n-chains 2 --burn-in 1000 --n-samples 1000 --n-leapfrog 30 --thin 10 \
  --map-init-steps 30000 --map-lr 1e-3 --precondition \
  --output-root "${ROOT}/sigma_data_${SD}"
