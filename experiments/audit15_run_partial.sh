#!/usr/bin/env bash
# Auditoria A15, bloques sin simulacion (protocol_audit15.md): B15.0, T3, tabular, B15.0b, B15.2, B15.5, suite y reporte parcial.
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
L=experiments/results/logs_audit15
LOG=$L/chain_partial_audit15.log
mkdir -p $L
echo "[cadena A15 parcial] inicio $(date -u +%FT%TZ) commit $(git rev-parse --short HEAD)" >> $LOG
python experiments/audit15_b0_iidasy.py > $L/b0_iidasy_audit15.log 2>&1; echo "[B15.0] codigo $?" >> $LOG
python experiments/audit15_b0_t3.py > $L/b0_t3_audit15.log 2>&1; echo "[B15.0 T3] codigo $?" >> $LOG
python experiments/audit15_tables.py > $L/tables_audit15.log 2>&1; echo "[tabular] codigo $?" >> $LOG
python experiments/audit15_b0b_lag.py > $L/b0b_lag_audit15.log 2>&1; echo "[B15.0b] codigo $?" >> $LOG
python experiments/audit15_b2_slope.py > $L/e4_slope_audit15.log 2>&1; echo "[B15.2] codigo $?" >> $LOG
python experiments/audit15_b5_anon.py > $L/b5_anon_audit15.log 2>&1; echo "[B15.5] codigo $?" >> $LOG
python -m pytest tests -v -p no:cacheprovider > experiments/results/pytest_audit15_partial.log 2>&1; echo "[suite] codigo $?" >> $LOG
python experiments/audit15_generate_report.py > $L/report_audit15.log 2>&1; echo "[reporte] codigo $?" >> $LOG
echo "[cadena A15 parcial] fin $(date -u +%FT%TZ)" >> $LOG
