#!/usr/bin/env bash
# Auditoria A15, cierre (enmienda 3): B15.3 y B15.1 regenerados desde sus checkpoints en el commit final, suite y reporte final.
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 PYTHONWARNINGS=ignore
L=experiments/results/logs_audit15
LOG=$L/chain_final_audit15.log
echo "[cierre A15] inicio $(date -u +%FT%TZ) commit $(git rev-parse --short HEAD)" >> $LOG
python experiments/audit15_b3_fixedb.py > $L/b3_fixedb_final_audit15.log 2>&1; echo "[B15.3] codigo $?" >> $LOG
python experiments/audit15_b1_boot.py > $L/b1_boot_final_audit15.log 2>&1; echo "[B15.1] codigo $?" >> $LOG
python -m pytest tests -v -p no:cacheprovider > experiments/results/pytest_audit15.log 2>&1; echo "[suite] codigo $?" >> $LOG
python experiments/audit15_generate_report.py > $L/report_audit15.log 2>&1; echo "[reporte] codigo $?" >> $LOG
echo "[cierre A15] fin $(date -u +%FT%TZ)" >> $LOG
