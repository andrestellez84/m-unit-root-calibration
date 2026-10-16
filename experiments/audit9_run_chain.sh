#!/usr/bin/env bash
# Auditoria A9 - cadena reanudable de B9.1 a B9.5 y B9.7 (cada invocacion con tope de 4 h;
# el codigo 2 significa "tope alcanzado, reanudar"; 3 = presupuesto excedido: se detiene).
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1
LOG=experiments/results/logs_audit9/chain_audit9.log
mkdir -p experiments/results/logs_audit9
step() {   # step <nombre> <log> <comando...>: repite mientras devuelva 2
  local name=$1 log=$2; shift 2
  for k in 1 2 3 4 5 6 7 8; do
    echo "[$name] intento $k: $*" >> $LOG
    "$@" >> experiments/results/logs_audit9/$log 2>&1
    local rc=$?
    echo "[$name] codigo $rc" >> $LOG
    [ $rc -eq 2 ] || return $rc
  done
  return 2
}
step b91_run b91_run_audit9.log python experiments/audit9_b91_equalized.py --run --cores 14 || exit 1
step b91_analyze b91_analyze_audit9.log python experiments/audit9_b91_equalized.py --analyze || exit 1
if [ ! -f experiments/results/b92_budget_audit9.json ]; then
  step b92_budget b92_budget_audit9.log python experiments/audit9_b92_theta.py --budget --cores 14 || { echo "[b92] presupuesto excedido: se detiene" >> $LOG; exit 3; }
fi
step b92_run b92_run_audit9.log python experiments/audit9_b92_theta.py --run --cores 14 || exit 1
step b92_analyze b92_analyze_audit9.log python experiments/audit9_b92_theta.py --analyze || exit 1
step b93 b93_audit9.log python experiments/audit9_b93_attribution.py || exit 1
step b94_run b94_run_audit9.log python experiments/audit9_b94_finite_sample.py --run --cores 14 || exit 1
step b94_analyze b94_analyze_audit9.log python experiments/audit9_b94_finite_sample.py --analyze || exit 1
if [ ! -f experiments/results/b95_budget_audit9.json ]; then
  step b95_budget b95_budget_audit9.log python experiments/audit9_b95_awb.py --budget --cores 14 || { echo "[b95] presupuesto excedido: B9.5 no se lanza" >> $LOG; }
fi
if [ -f experiments/results/b95_budget_audit9.json ] && python -c "import json,sys; sys.exit(0 if json.load(open('experiments/results/b95_budget_audit9.json'))['within_budget'] else 1)"; then
  step b95_run b95_run_audit9.log python experiments/audit9_b95_awb.py --run --cores 14 || exit 1
  step b95_analyze b95_analyze_audit9.log python experiments/audit9_b95_awb.py --analyze || exit 1
fi
step b97 b97_audit9.log python experiments/audit9_b97_critical_values.py --cores 14 || exit 1
echo "[cadena] fin $(date -u +%FT%TZ)" >> $LOG
