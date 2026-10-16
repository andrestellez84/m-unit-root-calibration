#!/usr/bin/env bash
# Auditoria A8 - continuacion de la cadena desde B5 (B3 y B4 ya completos).
# Misma mecanica que audit8_run_rest.sh: relanza mientras el bloque devuelva 2.
# Uso: bash experiments/audit8_run_tail.sh [CORES]
set -u
cd "$(dirname "$0")/.."
CORES="${1:-14}"
LOG=experiments/results/logs_audit8
MAX_BLOCKS=12

run_blocks() {
  local label="$1"; shift
  local i=1
  while [ "$i" -le "$MAX_BLOCKS" ]; do
    echo "[$label] bloque $i: $*"
    PYTHONUNBUFFERED=1 "$@" >> "$LOG/${label}_audit8.log" 2>&1
    local rc=$?
    echo "[$label] bloque $i termino con codigo $rc"
    if [ "$rc" -eq 0 ]; then return 0; fi
    if [ "$rc" -ne 2 ]; then return "$rc"; fi
    i=$((i + 1))
  done
  echo "[$label] agotados $MAX_BLOCKS bloques"
  return 3
}

step() {
  local label="$1"; shift
  echo "[$label] $*"
  PYTHONUNBUFFERED=1 "$@" >> "$LOG/${label}_audit8.log" 2>&1
  local rc=$?
  echo "[$label] codigo $rc"
  return "$rc"
}

mkdir -p "$LOG"
run_blocks b5_run python experiments/audit8_b5_power.py --run --cores "$CORES" || exit $?
step b5_analyze python experiments/audit8_b5_power.py --analyze --cores "$CORES" || exit $?
step b6 python experiments/audit8_b6_application.py --cores "$CORES" || exit $?
run_blocks b7 python experiments/audit8_b7_critical_values.py --cores "$CORES" || exit $?
step b8 python experiments/make_figures_audit8.py || exit $?
step suite python -m pytest tests -v -p no:cacheprovider || true
cp "$LOG/suite_audit8.log" experiments/results/pytest_audit8.log
step report python experiments/audit8_generate_report.py || exit $?
echo "cadena completa"
