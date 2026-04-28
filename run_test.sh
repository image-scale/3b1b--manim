#!/bin/bash
set -eo pipefail

export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export CI=true
export PYGLET_HEADLESS=1
export MPLBACKEND=Agg

cd /workspace/manim

rm -rf .pytest_cache
pytest -v --tb=short -p no:cacheprovider tests/

