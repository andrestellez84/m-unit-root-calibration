#!/usr/bin/env bash
# Auditoria A10 - cadena tras el analisis de B10.1: B10.3 (condicional), B10.4, B10.5, suite.
# El reporte se genera aparte (audit10_generate_report.py).
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1
L=experiments/results/logs_audit10
LOG=$L/chain_audit10.log
echo "[cadena] inicio $(date -u +%FT%TZ)" >> $LOG
stop=$(python -c "
import json
b = json.load(open('experiments/results/b101_theta_audit10.json'))
print(1 if b['gate_stop'] else 0)")
if [ "$stop" = "1" ]; then
  echo "[cadena] compuerta B10.1 detiene" >> $LOG
  exit 0
fi
need=$(python -c "
import json
print(1 if json.load(open('experiments/results/b101_theta_audit10.json'))['primary_theta'] != 0.1 else 0)")
echo "[b103] necesario: $need" >> $LOG
if [ "$need" = "1" ]; then
  python experiments/audit10_b103_equalized.py >> $L/b103_equalized_audit10.log 2>&1; echo "[b103.1] codigo $?" >> $LOG
  python experiments/audit10_b103_lown.py --run --cores 14 >> $L/b103_lown_run_audit10.log 2>&1; echo "[b103.7 run] codigo $?" >> $LOG
  python experiments/audit10_b103_lown.py --analyze >> $L/b103_lown_analyze_audit10.log 2>&1; echo "[b103.7 analyze] codigo $?" >> $LOG
  python experiments/audit10_b103_finite.py >> $L/b103_finite_audit10.log 2>&1; echo "[b103.3] codigo $?" >> $LOG
  python experiments/audit10_b103_dgp5.py --cores 14 >> $L/b103_dgp5_audit10.log 2>&1; echo "[b103.2] codigo $?" >> $LOG
  python experiments/audit10_b103_cv.py --cores 14 >> $L/b103_cv_audit10.log 2>&1; echo "[b103.6] codigo $?" >> $LOG
  python experiments/audit10_b103_awb.py --budget --cores 14 >> $L/b103_awb_budget_audit10.log 2>&1; rc=$?; echo "[b103.4 budget] codigo $rc" >> $LOG
  if [ "$rc" = "0" ]; then
    python experiments/audit10_b103_awb.py --run --cores 14 >> $L/b103_awb_run_audit10.log 2>&1; echo "[b103.4 run] codigo $?" >> $LOG
    python experiments/audit10_b103_awb.py --analyze >> $L/b103_awb_analyze_audit10.log 2>&1; echo "[b103.4 analyze] codigo $?" >> $LOG
  fi
  python experiments/audit10_b103_application.py --cores 14 >> $L/b103_application_audit10.log 2>&1; echo "[b103.5] codigo $?" >> $LOG
fi
python experiments/audit10_b104_cv5000.py --cores 14 >> $L/b104_audit10.log 2>&1; echo "[b104] codigo $?" >> $LOG
python experiments/make_figures_audit10.py >> $L/figures_audit10.log 2>&1; echo "[figuras] codigo $?" >> $LOG
python -m pytest tests -v -p no:cacheprovider > experiments/results/pytest_audit10.log 2>&1; echo "[suite] codigo $?" >> $LOG
echo "[cadena] fin $(date -u +%FT%TZ)" >> $LOG
