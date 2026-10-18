#!/bin/sh
# Prove the boundary templates work: each must pass its good fixture and fail its bad one.
#   skills/architecture/scripts/check_templates.sh   (needs uv and pnpm; fetches import-linter and dependency-cruiser)
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
fail=0
CRUISER_VERSION=18.4.0 TS_VERSION=5.6.3  # tested together; dependency-cruiser 16.x crashes on Node 26

# Each runner prints the tool's verdict line, so a crash can't pass for a caught violation.
py() { # $1 fixture dir with src/shop
  d="$(mktemp -d "$WORK/run.XXXXXX")"; cp -R "$1/." "$d/"
  sed 's/<pkg>/shop/g' "$HERE/templates/importlinter.toml" > "$d/.importlinter.toml"
  (cd "$d" && PYTHONPATH=src uv run -q --no-project --with import-linter --with fastapi \
    lint-imports --config .importlinter.toml > out.txt 2>&1) || true
  grep -oE 'Contracts: [0-9]+ kept, [0-9]+ broken' "$d/out.txt" || echo "crashed: $(tail -1 "$d/out.txt")"
}
ts() { # $1 fixture dir with src/
  d="$(mktemp -d "$WORK/run.XXXXXX")"; cp -R "$1/." "$d/"
  cp "$HERE/templates/dependency-cruiser.cjs" "$d/.dependency-cruiser.cjs"
  (cd "$d" && pnpm dlx -s --package "dependency-cruiser@$CRUISER_VERSION" --package "typescript@$TS_VERSION" depcruise --config .dependency-cruiser.cjs src > out.txt 2>&1) || true
  if grep -q "no dependency violations found" "$d/out.txt"; then echo clean
  else v="$(grep -oE 'error (no-circular|components-not-to-api)' "$d/out.txt" | sort -u | tr '\n' ' ')"; echo "${v:-crashed: $(tail -1 "$d/out.txt")}"; fi
}
expect() { # $1 label, $2 expected verdict, $3 actual verdict
  if [ "$2" = "$3" ]; then echo "ok   $1: $3"; else echo "FAIL $1: got '$3', wanted '$2'"; fail=1; fi
}
expect "import-linter, good layers" "Contracts: 2 kept, 0 broken" "$(py "$HERE/fixtures/good")"
expect "import-linter, domain imports fastapi and routes" "Contracts: 0 kept, 2 broken" "$(py "$HERE/fixtures/layers-bad")"
expect "dependency-cruiser, good web" "clean" "$(ts "$HERE/fixtures/good/web")"
expect "dependency-cruiser, component imports api" "error components-not-to-api " "$(ts "$HERE/fixtures/web-bad")"
expect "dependency-cruiser, cycle" "error no-circular " "$(ts "$HERE/fixtures/bad/web")"
exit $fail
