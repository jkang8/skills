#!/bin/sh
# Prove the examples work: Python pairs behave the same before and after; TS pairs type-check.
#   skills/architecture/references/examples/check.sh   (needs uv and pnpm; fetches deps on first run)
set -eu
cd "$(dirname "$0")"
(cd py && uv run -q --no-project --python 3.11 --with fastapi --with sqlalchemy --with pydantic --with httpx \
  python -m unittest test_examples)
(cd ts && pnpm install --silent --ignore-workspace && pnpm exec tsc --noEmit && echo "ts: type-check clean")
