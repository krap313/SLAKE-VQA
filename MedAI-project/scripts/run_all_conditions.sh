#!/usr/bin/env bash
set -euo pipefail

SLAKE_ROOT="${1:-/workspace/datasets/SLAKE_raw/Slake1.0}"
SPLIT="${2:-test}"
MAX_SAMPLES="${3:-2094}"
BASE_OUT="${4:-outputs_full}"

CONDITIONS=(
  original
  black
  lpf
  hpf
  patch_shuffle
)

echo "SLAKE_ROOT: ${SLAKE_ROOT}"
echo "SPLIT: ${SPLIT}"
echo "MAX_SAMPLES: ${MAX_SAMPLES}"
echo "BASE_OUT: ${BASE_OUT}"

mkdir -p "${BASE_OUT}"

for CONDITION in "${CONDITIONS[@]}"; do
  OUT_DIR="${BASE_OUT}/${CONDITION}"
  SUMMARY_PATH="${OUT_DIR}/summary.json"

  if [ -f "${SUMMARY_PATH}" ]; then
    echo "========================================"
    echo "Skipping condition: ${CONDITION} (summary.json exists)"
    echo "========================================"
    continue
  fi

  echo "========================================"
  echo "Running condition: ${CONDITION}"
  echo "========================================"

  python -m src.run_eval \
    --use_hf \
    --slake_root "${SLAKE_ROOT}" \
    --split "${SPLIT}" \
    --condition "${CONDITION}" \
    --output_dir "${OUT_DIR}" \
    --max_samples "${MAX_SAMPLES}"
done

echo "All conditions finished."