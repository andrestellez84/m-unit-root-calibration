"""
Auditoria A7 - diagnostico del costo y de la reproducibilidad del bootstrap.

Motivo: el presupuesto por sondas del Bloque 1 midio el bootstrap DF-GLS
(bootUR boot_adf, AWB, QD, B=399, 14 nucleos) de 5 a 7 veces mas lento que A6
para la misma llamada. Antes de atribuirlo a nada se miden, sobre las mismas 14
series de calibracion de la sonda:

  1. el worker de R en un proceso sin ningun pool de Python;
  2. el worker de R con el pool de 14 procesos de loky ya calentado y residente,
     que es la condicion en que corrio la sonda del presupuesto;
  3. la reproducibilidad: el mismo lote dos veces seguidas. El worker heredado
     de A6 no fija la semilla del generador de R, de modo que el remuestreo
     puede variar de una corrida a otra.

Registra la memoria fisica disponible antes y despues de cada llamada.

Uso: python experiments/audit7_bootstrap_cost_diag.py
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                  # noqa: E402
import audit7_design as D                                  # noqa: E402
import audit7_dgp5_runner as RUN                           # noqa: E402

OUT = os.path.join(C.RESULTS, "bootstrap_cost_diagnostic_audit7.json")
BUDGET = os.path.join(C.RESULTS, "block1_budget_audit7.json")
K = C.PROBE_SERIES
CORES = 14
B = D.DGP5_B


def memory():
    try:
        import psutil
        vm = psutil.virtual_memory()
        return {"total_gb": vm.total / 2 ** 30, "available_gb": vm.available / 2 ** 30,
                "source": "psutil"}
    except ImportError:
        cmd = ["powershell", "-NoProfile", "-Command",
               "Get-CimInstance Win32_OperatingSystem | "
               "Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"]
        d = json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)
        return {"total_gb": d["TotalVisibleMemorySize"] / 2 ** 20,
                "available_gb": d["FreePhysicalMemory"] / 2 ** 20,
                "source": "Win32_OperatingSystem (FreePhysicalMemory)"}


def boot(n):
    m0 = memory()
    p, t = RUN.run_bootstrap("cal", n, None, None, D.cal_seed_base(n), list(range(K)), CORES, B)
    t["memory_before"] = m0
    t["memory_after"] = memory()
    return p, t


def main():
    t0 = time.time()
    res = {"clean_no_python_pool": {}, "with_warm_python_pool": {}}

    print("[1] worker de R sin pool de Python")
    p_a, t = boot(200)
    res["clean_no_python_pool"]["200"] = t
    print("    n=200   %.3f s/serie interno  (pared %.1f s)" % (t["r_internal_sec_per_series"], t["r_wall_sec"]))
    p_b, _ = boot(200)
    pa, pb = np.array(p_a), np.array(p_b)
    both = ~(np.isnan(pa) | np.isnan(pb))
    determinism = {"n": 200, "series": K, "max_abs_diff_pvalue": float(np.max(np.abs(pa[both] - pb[both]))),
                   "identical": bool(np.array_equal(pa, pb, equal_nan=True)),
                   "p_first_run": p_a, "p_second_run": p_b}
    print("[3] mismo lote dos veces: identico=%s  max|diff p|=%.4f"
          % (determinism["identical"], determinism["max_abs_diff_pvalue"]))
    for n in (500, 1000):
        _, t = boot(n)
        res["clean_no_python_pool"][str(n)] = t
        print("    n=%-5d %.3f s/serie interno  (pared %.1f s)" % (n, t["r_internal_sec_per_series"], t["r_wall_sec"]))

    print("[2] worker de R con el pool de loky caliente y residente")
    m_pre = memory()
    RUN.warm_pool(CORES, D.CAL_N_GRID)
    m_post = memory()
    print("    memoria disponible: %.2f GB antes del pool, %.2f GB con el pool"
          % (m_pre["available_gb"], m_post["available_gb"]))
    for n in D.CAL_N_GRID:
        _, t = boot(n)
        res["with_warm_python_pool"][str(n)] = t
        print("    n=%-5d %.3f s/serie interno  (pared %.1f s)" % (n, t["r_internal_sec_per_series"], t["r_wall_sec"]))

    with open(BUDGET, encoding="utf-8") as f:
        budget = json.load(f)
    comparison = {}
    for n in D.CAL_N_GRID:
        clean = res["clean_no_python_pool"][str(n)]["r_internal_sec_per_series"]
        pool = res["with_warm_python_pool"][str(n)]["r_internal_sec_per_series"]
        probe = budget["per_n"][str(n)]["bootstrap_steady_sec_per_series"]
        comparison[str(n)] = {"clean": clean, "with_pool": pool, "budget_probe": probe,
                              "pool_over_clean": pool / clean, "budget_over_clean": probe / clean}
    C.atomic_write_json(OUT, {
        "provenance": C.provenance(dgp="bootstrap_cost_diagnostic", n_sim=K,
                                   seed_formula="series de calibracion 70*10^8+n_idx*10^5, i=0..13",
                                   extra_code_files=[RUN.WORKER_R]),
        "memory_python_pool": {"before_pool": m_pre, "with_pool": m_post},
        "timings": res, "comparison_sec_per_series": comparison,
        "determinism": determinism,
        "elapsed_sec": round(time.time() - t0, 1),
    })
    print("\n%-6s %10s %10s %13s %10s %12s" % ("n", "limpio", "con pool", "sonda presup", "pool/limp", "sonda/limp"))
    for n, c in comparison.items():
        print("%-6s %10.3f %10.3f %13.3f %9.2fx %11.2fx" % (n, c["clean"], c["with_pool"], c["budget_probe"],
                                                         c["pool_over_clean"], c["budget_over_clean"]))
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
