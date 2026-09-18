#!/usr/bin/env bash
set -euo pipefail

npm install

cd slides && npm install && cd ..

curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv sync --group dev
uv run pre-commit install
