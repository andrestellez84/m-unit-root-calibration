#!/usr/bin/env bash
# Auditoria A13 - B13.E(2): DGP 5, AWB (sonda, corrida, analisis) y aplicacion con theta = 0.
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
L=experiments/results/logs_audit13
LOG=$L/chain_e2_audit13.log
mkdir -p $L
echo "[cadena E2] inicio $(date -u +%FT%TZ) commit $(git rev-parse --short HEAD)" >> $LOG
python experiments/audit13_e_dgp5.py --cores 14 > $L/e_dgp5_audit13.log 2>&1; echo "[dgp5] codigo $?" >> $LOG
python experiments/audit13_e_awb.py --budget --cores 14 > $L/e_awb_budget_audit13.log 2>&1; rc=$?; echo "[awb budget] codigo $rc" >> $LOG
if [ "$rc" = "0" ]; then
  python experiments/audit13_e_awb.py --run --cores 14 > $L/e_awb_run_audit13.log 2>&1; echo "[awb run] codigo $?" >> $LOG
  python experiments/audit13_e_awb.py --analyze > $L/e_awb_analyze_audit13.log 2>&1; echo "[awb analyze] codigo $?" >> $LOG
fi
python experiments/audit13_e_application.py --cores 14 > $L/e_application_audit13.log 2>&1; echo "[aplicacion] codigo $?" >> $LOG
echo "[cadena E2] fin $(date -u +%FT%TZ)" >> $LOG
