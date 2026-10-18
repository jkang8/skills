#!/bin/sh
# Fixture test for sec_check.sh: a clean repo passes, a vulnerable one fails all four tools.
#   skills/security/scripts/test_sec_check.sh   (needs uv and pnpm, and the network on first run)
# The fake token is generated at run time so no secret-shaped string is ever committed.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
fail=0
expect() { # $1 label, $2 pattern that must appear in $3 output file
  if grep -qE "$2" "$3"; then echo "ok   $1"; else echo "FAIL $1"; sed 's/^/     /' "$3"; fail=1; fi
}

mkdir -p "$W/clean" && cat > "$W/clean/app.py" <<'EOF'
import subprocess


def list_dir(path: str) -> str:
    return subprocess.run(["ls", path], capture_output=True, text=True, check=True).stdout
EOF
"$HERE/sec_check.sh" "$W/clean" > "$W/clean.out" 2>&1
expect "clean repo passes" '^sec check: clean' "$W/clean.out"

mkdir -p "$W/bad/web" && cat > "$W/bad/app.py" <<'EOF'
import subprocess


def run(cmd: str, expr: str):
    subprocess.call(cmd, shell=True)
    return eval(expr)
EOF
printf 'GH_PAT = "ghp_%s"\n' "$(python3 -c 'import random,string; print("".join(random.choices(string.ascii_letters + string.digits, k=36)))')" > "$W/bad/config.py"
printf 'requests==2.19.0\n' > "$W/bad/requirements.txt"
printf '{"name": "web", "private": true, "dependencies": {"lodash": "4.17.15"}}\n' > "$W/bad/web/package.json"
(cd "$W/bad/web" && pnpm install --lockfile-only --silent --ignore-workspace >/dev/null 2>&1)
"$HERE/sec_check.sh" "$W/bad" > "$W/bad.out" 2>&1; rc=$?
expect "ruff S flags shell=True and eval" '^FAIL  ruff S' "$W/bad.out"
expect "gitleaks flags the token" '^FAIL  gitleaks' "$W/bad.out"
expect "pip-audit flags requests 2.19.0" '^FAIL  pip-audit' "$W/bad.out"
expect "pnpm audit flags lodash 4.17.15" '^FAIL  pnpm audit' "$W/bad.out"
[ $rc = 1 ] && echo "ok   vulnerable repo exits 1" || { echo "FAIL vulnerable repo exit $rc"; fail=1; }
exit $fail
