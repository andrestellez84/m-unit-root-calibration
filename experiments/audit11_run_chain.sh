#!/usr/bin/env bash
# Auditoria A11 - cadena completa desde codigo commiteado: T0, T3/T4 (reanudan desde checkpoints), T1, T2, T5, suite, reporte.
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
L=experiments/results/logs_audit11
LOG=$L/chain_audit11.log
mkdir -p $L
echo "[cadena] inicio $(date -u +%FT%TZ) commit $(git rev-parse --short HEAD)" >> $LOG
python experiments/audit11_t0_protocol.py > $L/t0_audit11.log 2>&1; echo "[t0] codigo $?" >> $LOG
python experiments/audit11_t3_anchor.py --run --analyze --cores 14 > $L/t3_analyze_audit11.log 2>&1; echo "[t3] codigo $?" >> $LOG
python experiments/audit11_t4_trend.py --run --analyze --cores 14 > $L/t4_analyze_audit11.log 2>&1; echo "[t4] codigo $?" >> $LOG
python experiments/make_figures_audit11.py > $L/figures_audit11.log 2>&1; echo "[t1] codigo $?" >> $LOG
python experiments/audit11_t2_dgp2.py > $L/t2_audit11.log 2>&1; echo "[t2] codigo $?" >> $LOG
python experiments/audit11_t5_claims.py > $L/t5_audit11.log 2>&1; echo "[t5] codigo $?" >> $LOG
python -m pytest tests -v -p no:cacheprovider > experiments/results/pytest_audit11.log 2>&1; echo "[suite] codigo $?" >> $LOG
python experiments/audit11_generate_report.py > $L/report_audit11.log 2>&1; echo "[reporte] codigo $?" >> $LOG
echo "[cadena] fin $(date -u +%FT%TZ)" >> $LOG
