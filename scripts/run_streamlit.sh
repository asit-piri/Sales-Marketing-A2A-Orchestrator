#!/usr/bin/env bash
set -euo pipefail

# Locate repo root (one level up from scripts/)
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# Exec streamlit so it inherits signals and PID
exec streamlit run src/ui/app.py
