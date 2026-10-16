import os
import sys
import subprocess
import json
import time
import numpy as np

RSCRIPT = r"C:\Program Files\R\R-4.6.1\bin\x64\Rscript.exe"
WORKER_R = os.path.join("experiments", "audit6_wild_bootstrap_worker.R")
RESULTS_DIR = os.path.join("experiments", "results")

n = 200
r = 1.0
N_sim = 100
B = 999
cores = 12

seed_base = 300000 + n * 100 + int(r * 10)
print(f"Generating {N_sim} series for smoke test (n={n}, r={r}, seed_base={seed_base})...")

series_list = []
for i in range(N_sim):
    rng = np.random.default_rng(seed_base + i)
    t_break = n // 2
    eps = np.empty(n)
    eps[:t_break] = rng.standard_normal(t_break)
    eps[t_break:] = rng.standard_normal(n - t_break) * r
    y = np.empty(n + 1, dtype=np.float64)
    y[0] = 0.0
    np.cumsum(eps, out=y[1:])
    series_list.append(y)

mat = np.column_stack(series_list)  # shape: (n+1, N_sim)
bin_path = os.path.join(RESULTS_DIR, "smoke_series.bin")
mat.T.tofile(bin_path)
print(f"Saved binary data to {bin_path} ({mat.nbytes} bytes)")

expected_first_5 = ",".join(f"{v:.6f}" for v in mat[:5, 0])
out_json = os.path.join(RESULTS_DIR, "smoke_result.json")
cmd = [RSCRIPT, WORKER_R, bin_path, str(n), str(N_sim), str(B), str(cores), out_json, expected_first_5]

print(f"Calling R bootUR worker with {cores} cores, B={B}, guard={expected_first_5}...")
t0 = time.time()
p = subprocess.run(cmd, capture_output=True, text=True)
elapsed = time.time() - t0

if os.path.exists(bin_path):
    os.remove(bin_path)

print(f"STDOUT: {p.stdout}")
if p.stderr:
    print(f"STDERR: {p.stderr}")

if p.returncode != 0:
    print(f"ERROR: Rscript failed with code {p.returncode}")
    sys.exit(1)

with open(out_json, "r", encoding="utf-8") as f:
    res = json.load(f)

print("=" * 60)
print(f"SMOKE TEST RESULTS (Dual comparators):")
print(f"  boot_adf (QD):  rate = {res['adf']['rate']:.4f} [{res['adf']['ci_lower']:.4f}, {res['adf']['ci_upper']:.4f}] ({res['adf']['rejections']}/{res['N_sim']})")
print(f"  boot_union:     rate = {res['union']['rate']:.4f} [{res['union']['ci_lower']:.4f}, {res['union']['ci_upper']:.4f}] ({res['union']['rejections']}/{res['N_sim']})")
print(f"Total time: {elapsed:.1f}s")
print("=" * 60)
