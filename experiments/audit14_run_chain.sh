#!/usr/bin/env bash
# Auditoria A14 (protocol_audit14.md, lectura 12): B14.0, B14.1, tablas, B14.2, B14.3, suite y reporte. Sin simulaciones.
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
L=experiments/results/logs_audit14
LOG=$L/chain_audit14.log
mkdir -p $L
echo "[cadena A14] inicio $(date -u +%FT%TZ) commit $(git rev-parse --short HEAD)" >> $LOG
python experiments/audit14_b0_inventory.py > $L/b0_inventory_audit14.log 2>&1; echo "[B14.0] codigo $?" >> $LOG
python experiments/audit14_b1_critical.py > $L/b1_critical_audit14.log 2>&1; echo "[B14.1] codigo $?" >> $LOG
python experiments/audit14_tables.py > $L/tables_audit14.log 2>&1; echo "[tablas] codigo $?" >> $LOG
python experiments/audit14_b2_sources.py > $L/b2_sources_audit14.log 2>&1; echo "[B14.2] codigo $?" >> $LOG
python experiments/audit14_b3_verify.py > $L/b3_verify_audit14.log 2>&1; echo "[B14.3] codigo $?" >> $LOG
python -m pytest tests -v -p no:cacheprovider > experiments/results/pytest_audit14.log 2>&1; echo "[suite] codigo $?" >> $LOG
python experiments/audit14_generate_report.py > $L/report_audit14.log 2>&1; echo "[reporte] codigo $?" >> $LOG
echo "[cadena A14] fin $(date -u +%FT%TZ)" >> $LOG
