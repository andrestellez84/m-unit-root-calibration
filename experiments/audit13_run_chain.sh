#!/usr/bin/env bash
# Auditoria A13 - cadena limpia: B13.0, E(1), E(2), E(3), T, cifras del texto, suite y reporte.
# Los computos con checkpoint (familia 141, AWB, aplicacion, DGP 5) se reanudan desde sus checkpoints.
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
L=experiments/results/logs_audit13
LOG=$L/chain_audit13.log
mkdir -p $L
echo "[cadena] inicio $(date -u +%FT%TZ) commit $(git rev-parse --short HEAD)" >> $LOG
python experiments/audit13_b130_inventory.py > $L/b130_audit13.log 2>&1; echo "[B13.0] codigo $?" >> $LOG
python experiments/audit13_e_size.py --run --analyze --cores 14 > $L/e_size_audit13.log 2>&1; echo "[E1 size] codigo $?" >> $LOG
python experiments/audit13_e_equalized.py > $L/e_equalized_audit13.log 2>&1; echo "[E1 igualado] codigo $?" >> $LOG
python experiments/audit13_e_calib.py > $L/e_calib_audit13.log 2>&1; echo "[E1 calib] codigo $?" >> $LOG
python experiments/audit13_e_dgp5.py --cores 14 > $L/e_dgp5_audit13.log 2>&1; echo "[E2 dgp5] codigo $?" >> $LOG
python experiments/audit13_e_awb.py --budget --cores 14 > $L/e_awb_budget_audit13.log 2>&1; rc=$?; echo "[E2 awb budget] codigo $rc" >> $LOG
if [ "$rc" = "0" ]; then
  python experiments/audit13_e_awb.py --run --cores 14 > $L/e_awb_run_audit13.log 2>&1; echo "[E2 awb run] codigo $?" >> $LOG
  python experiments/audit13_e_awb.py --analyze > $L/e_awb_analyze_audit13.log 2>&1; echo "[E2 awb analyze] codigo $?" >> $LOG
fi
python experiments/audit13_e_application.py --cores 14 > $L/e_application_audit13.log 2>&1; echo "[E2 aplicacion] codigo $?" >> $LOG
python experiments/audit13_tables.py > $L/tables_audit13.log 2>&1; echo "[tablas] codigo $?" >> $LOG
python experiments/make_figures_audit13.py > $L/figures_audit13.log 2>&1; echo "[figuras] codigo $?" >> $LOG
python experiments/audit13_t_tables.py > $L/t_tables_audit13.log 2>&1; echo "[B13.T] codigo $?" >> $LOG
python experiments/audit13_claims.py > $L/claims_audit13.log 2>&1; echo "[frases] codigo $?" >> $LOG
python -m pytest tests -v -p no:cacheprovider > experiments/results/pytest_audit13.log 2>&1; echo "[suite] codigo $?" >> $LOG
python experiments/audit13_generate_report.py > $L/report_audit13.log 2>&1; echo "[reporte] codigo $?" >> $LOG
echo "[cadena] fin $(date -u +%FT%TZ)" >> $LOG
