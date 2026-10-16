"""Genera las series pareadas para el benchmark y llama al bench de R."""
import os, subprocess, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from experiments.audit6_wild_bootstrap_sweep import generate_dgp3_series, RSCRIPT

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, "results", "checkpoints")
OUT = os.path.join(HERE, "results", "bench_bootur_audit6.json")
os.makedirs(TMP, exist_ok=True)

bins = []
for n in (200, 500, 1000):
    mat = generate_dgp3_series(n, 1.0, 20)          # DGP3 r=1.0, semillas reales
    p = os.path.join(TMP, f"bench_n{n}.bin")
    mat.T.tofile(p)
    bins.append(p)
    print(f"  series n={n}: {mat.shape} -> {p}")

cmd = [RSCRIPT, os.path.join(HERE, "audit6_bench_bootur.R"), *bins, OUT]
print("\nlanzando bench de R...\n", flush=True)
t0 = time.time()
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, bufsize=1)
for line in proc.stdout:
    print(line, end="", flush=True)
proc.wait()
print(f"\nbench total: {time.time() - t0:.1f} s  rc={proc.returncode}")
for p in bins:
    if os.path.exists(p):
        os.remove(p)
