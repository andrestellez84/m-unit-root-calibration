#!/usr/bin/env bash
# Auditoria A15 tras las enmiendas 1 y 2: inventario, B15.0, T3, B15.0b, tabulares, B15.2, B15.5, Paso 0 de B15.1 y B15.3,
# sondas (solo tiempos), suite y reporte. No lanza las corridas de B15.1 ni de B15.3 (esperan la confirmacion del autor).
set -u
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 PYTHONWARNINGS=ignore
L=experiments/results/logs_audit15
LOG=$L/chain2_audit15.log
mkdir -p $L
echo "[cadena A15-2] inicio $(date -u +%FT%TZ) commit $(git rev-parse --short HEAD)" >> $LOG
python experiments/audit15_inventory.py > $L/inventory_audit15.log 2>&1; echo "[B15.I] codigo $?" >> $LOG
python experiments/audit15_b0_iidasy.py > $L/b0_iidasy_audit15.log 2>&1; echo "[B15.0] codigo $?" >> $LOG
python experiments/audit15_b0_t3.py > $L/b0_t3_audit15.log 2>&1; echo "[B15.0 T3] codigo $?" >> $LOG
python experiments/audit15_b0b_lag.py > $L/b0b_lag_audit15.log 2>&1; echo "[B15.0b] codigo $?" >> $LOG
python experiments/audit15_tables.py > $L/tables_audit15.log 2>&1; echo "[tabulares] codigo $?" >> $LOG
python experiments/audit15_b2_slope.py > $L/e4_slope_audit15.log 2>&1; echo "[B15.2] codigo $?" >> $LOG
python experiments/audit15_b5_anon.py > $L/b5_anon_audit15.log 2>&1; echo "[B15.5] codigo $?" >> $LOG
python experiments/audit15_b1_paso0.py > $L/b1_paso0_audit15.log 2>&1; echo "[B15.1 Paso 0] codigo $?" >> $LOG
python experiments/audit15_b3_paso0.py > $L/b3_paso0_audit15.log 2>&1; echo "[B15.3 Paso 0] codigo $?" >> $LOG
python experiments/audit15_probes.py > $L/probes_audit15.log 2>&1; echo "[sondas] codigo $?" >> $LOG
python -m pytest tests -v -p no:cacheprovider > experiments/results/pytest_audit15.log 2>&1; echo "[suite] codigo $?" >> $LOG
python experiments/audit15_generate_report.py > $L/report_audit15.log 2>&1; echo "[reporte] codigo $?" >> $LOG
echo "[cadena A15-2] fin $(date -u +%FT%TZ)" >> $LOG
