#!/usr/bin/env bash
# Auditoria A12 - cadena tras B12.A: compuerta G-A1, calibracion PQ n = 1000/2000, B12.B, B12.C, B12.F,
# frases del v12, suite y reporte. Orden del encargo: B12.0 -> A -> B -> C -> F.
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
L=experiments/results/logs_audit12
LOG=$L/chain_audit12.log
mkdir -p $L
echo "[cadena] inicio $(date -u +%FT%TZ) commit $(git rev-parse --short HEAD)" >> $LOG
stop=$(python -c "
import json
b = json.load(open('experiments/results/bA_ma_audit12.json'))
print(1 if b['gate_stop'] else 0)")
if [ "$stop" = "1" ]; then
  echo "[cadena] G-A1 falla: se detiene (protocolo)" >> $LOG
  exit 0
fi
python experiments/audit12_cal.py --run --cores 14 --n 1000 2000 > $L/cal_large_audit12.log 2>&1; echo "[cal 1000 2000] codigo $?" >> $LOG
python experiments/audit12_bB_attrib.py --run --analyze --cores 14 > $L/bB_audit12.log 2>&1; echo "[B] codigo $?" >> $LOG
python experiments/audit12_bC_initial.py --run --analyze --cores 14 > $L/bC_audit12.log 2>&1; echo "[C] codigo $?" >> $LOG
python experiments/audit12_bF_anchor.py > $L/bF_audit12.log 2>&1; echo "[F] codigo $?" >> $LOG
python experiments/audit12_claims.py > $L/claims_audit12.log 2>&1; echo "[frases] codigo $?" >> $LOG
python -m pytest tests -v -p no:cacheprovider > experiments/results/pytest_audit12.log 2>&1; echo "[suite] codigo $?" >> $LOG
python experiments/audit12_generate_report.py > $L/report_audit12.log 2>&1; echo "[reporte] codigo $?" >> $LOG
echo "[cadena] fin $(date -u +%FT%TZ)" >> $LOG
