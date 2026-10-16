#!/usr/bin/env bash
# Auditoria A9 - cola de la cadena: B9.6 (condicional), figuras, suite y reporte.
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1
LOG=experiments/results/logs_audit9/chain_audit9.log
L=experiments/results/logs_audit9
need=$(python -c "
import json, os
b92 = json.load(open('experiments/results/b92_theta_audit9.json'))
awb = False
p = 'experiments/results/b95_awb_audit9.json'
if os.path.exists(p):
    awb = json.load(open(p))['rule']['recommend_awb']
print(1 if (b92['primary_theta'] != 0.1 or awb) else 0)")
echo "[b96] necesario: $need" >> $LOG
if [ "$need" = "1" ]; then
  python experiments/audit9_b96_application.py --cores 14 >> $L/b96_audit9.log 2>&1; echo "[b96] codigo $?" >> $LOG
fi
python experiments/make_figures_audit9.py >> $L/figures_audit9.log 2>&1; echo "[figuras] codigo $?" >> $LOG
python -m pytest tests -v -p no:cacheprovider > experiments/results/pytest_audit9.log 2>&1; echo "[suite] codigo $?" >> $LOG
python experiments/audit9_generate_report.py >> $L/report_audit9.log 2>&1; echo "[reporte] codigo $?" >> $LOG
echo "[cola] fin $(date -u +%FT%TZ)" >> $LOG
