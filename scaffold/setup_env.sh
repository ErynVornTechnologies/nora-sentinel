#!/usr/bin/env bash
# NORA Sentinel - portable training environment bootstrap (sudo-free).
# Stands up the same venv on any Linux/WSL box with an NVIDIA GPU.
set -euo pipefail

VENV="${LLM_VENV:-$HOME/llm_training/venv}"
TORCH_INDEX="${TORCH_INDEX:-https://download.pytorch.org/whl/cu128}"

echo "[setup] ensuring uv is installed..."
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "[setup] creating venv at $VENV ..."
uv venv "$VENV" --python 3.12
# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "[setup] installing torch from $TORCH_INDEX ..."
uv pip install torch --index-url "$TORCH_INDEX"

echo "[setup] installing training libraries..."
uv pip install transformers datasets accelerate peft trl bitsandbytes sentencepiece tensorboard pyyaml

echo "[setup] CUDA sanity check..."
python - <<'PY'
import torch
print("torch", torch.__version__, "cuda", torch.version.cuda)
print("cuda_available", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device", torch.cuda.get_device_name(0))
    x = torch.randn(1024, 1024, device="cuda") @ torch.randn(1024, 1024, device="cuda")
    print("matmul_ok", float(x.sum()) == float(x.sum()))
PY
echo "[setup] done."
