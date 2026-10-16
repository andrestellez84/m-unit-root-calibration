#!/usr/bin/env bash
# Auditoria A13 - B13.Q (enmienda 1): Q0-Q5 sobre paper_latex_v14.zip, suite y reporte regenerado. Sin simulaciones.
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
L=experiments/results/logs_audit13
LOG=$L/chain_q_audit13.log
mkdir -p $L
echo "[cadena Q] inicio $(date -u +%FT%TZ) commit $(git rev-parse --short HEAD)" >> $LOG
python experiments/audit13_q_inventory.py > $L/q_inventory_audit13.log 2>&1; echo "[Q0] codigo $?" >> $LOG
python experiments/audit13_q_attrib.py > $L/q_attrib_audit13.log 2>&1; echo "[Q1] codigo $?" >> $LOG
python experiments/make_figures_audit13q.py > $L/figures_audit13q.log 2>&1; echo "[Q2] codigo $?" >> $LOG
python experiments/audit13_q_claims.py > $L/q_claims_audit13.log 2>&1; echo "[Q3] codigo $?" >> $LOG
python experiments/audit13_q_phrases.py > $L/q_phrases_audit13.log 2>&1; echo "[Q4] codigo $?" >> $LOG
python experiments/audit13_q_supplement.py > $L/q_supplement_audit13.log 2>&1; echo "[Q5] codigo $?" >> $LOG
python -m pytest tests -v -p no:cacheprovider > experiments/results/pytest_audit13q.log 2>&1; echo "[suite] codigo $?" >> $LOG
python experiments/audit13_generate_report.py > $L/report_audit13q.log 2>&1; echo "[reporte] codigo $?" >> $LOG
echo "[cadena Q] fin $(date -u +%FT%TZ)" >> $LOG
