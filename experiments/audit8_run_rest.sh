#!/usr/bin/env bash
# Auditoria A8 - cadena de ejecucion de B3 a B8 y del reporte.
#
# Cada bloque de computo se relanza mientras devuelva 2 (tope de 4 h alcanzado:
# para limpio entre lotes y reanuda desde los checkpoints). Se detiene si una
# compuerta dura no pasa (B4) o si la regla de presupuesto se excede (B5).
#
# Uso: bash experiments/audit8_run_rest.sh [CORES]
set -u
cd "$(dirname "$0")/.."
CORES="${1:-14}"
LOG=experiments/results/logs_audit8
MAX_BLOCKS=12

run_blocks() {         # run_blocks <etiqueta> <comando...>
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

step() {               # step <etiqueta> <comando...>
  local label="$1"; shift
  echo "[$label] $*"
  PYTHONUNBUFFERED=1 "$@" >> "$LOG/${label}_audit8.log" 2>&1
  local rc=$?
  echo "[$label] codigo $rc"
  return "$rc"
}

gate() {               # gate <archivo json> <expresion python sobre d>
  python -c "
import json, sys
d = json.load(open(r'experiments/results/$1'))
ok = bool($2)
print('compuerta', r'$1', ok)
sys.exit(0 if ok else 1)
"
}

mkdir -p "$LOG"

run_blocks b3_run python experiments/audit8_b3_comparators.py --run --cores "$CORES" || exit $?
step b3_analyze python experiments/audit8_b3_comparators.py --analyze --cores "$CORES" || exit $?

run_blocks b4_run python experiments/audit8_b4_local_power.py --cores "$CORES" || exit $?
step b4_analyze python experiments/audit8_b4_local_power.py --analyze --cores "$CORES" || exit $?
gate b4_local_power_audit8.json "d['prior_gate']['passed']" || { echo "compuerta previa de B4 no pasa: se detiene"; exit 7; }

step b5_budget python experiments/audit8_b5_power.py --budget --cores "$CORES" || exit $?
run_blocks b5_run python experiments/audit8_b5_power.py --run --cores "$CORES" || exit $?
step b5_analyze python experiments/audit8_b5_power.py --analyze --cores "$CORES" || exit $?

step b6 python experiments/audit8_b6_application.py --cores "$CORES" || exit $?
run_blocks b7 python experiments/audit8_b7_critical_values.py --cores "$CORES" || exit $?
step b8 python experiments/make_figures_audit8.py || exit $?
step suite python -m pytest tests -v -p no:cacheprovider || true
cp "$LOG/suite_audit8.log" experiments/results/pytest_audit8.log
step report python experiments/audit8_generate_report.py || exit $?
echo "cadena completa"
