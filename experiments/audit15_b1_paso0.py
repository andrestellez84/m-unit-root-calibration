"""
Auditoria A15 - B15.1, Paso 0 contra bootUR 1.0.5 (protocol_audit15.md, lectura 1.7; enmienda 1,
E1.3; enmienda 2, B1 y seccion 3). Familia 154.

200 series de n = 200 (celdas 0-3: iid c, iid ct, MA(-0.5) c, MA(-0.5) ct; 50 cada una). La
replica en Python (audit15_boot_engine: estadistico ADF-QD con la MAIC de Perron-Qu, DGP de
bootUR y generadores SB y SWB) se compara con boot_adf(detrend = "QD", criterion = "MAIC",
criterion_scale = FALSE, max_lag = floor(12 (T/100)^{1/4}), B = 399) ejecutado en R:
estadistico |D| <= 1e-10, retardo |D| = 0, media de |Dp| <= 0.02. Tamano de la replica sobre
2000 caminos iid de n = 200 por caso (celdas 4 y 5) dentro de la region exacta de 2000.
Control adicional: MZ_t-GLS de numba frente a audit8_unitroot.np_statistics en las 200 series.
Compuerta: SB -> brazo (iii); SWB -> brazo (v') «SWB (bootUR)».

Salida: experiments/results/b1_paso0_audit15.json.
"""
import os
import subprocess
import sys
import tempfile
import time

import numpy as np
from joblib import Parallel, delayed
from scipy.stats import binom

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit15_boot_engine as B                                    # noqa: E402
import audit12_unitroot as P12                                     # noqa: E402
import audit8_unitroot as U                                        # noqa: E402

OUT = os.path.join(C.RESULTS, "b1_paso0_audit15.json")
FAM = C.FAMILY["PASO0_BOOTUR"]
N = 200
PER_CELL = 50
SIZE_PATHS = 2000
RB = 399
CELLS = ((("ma", 0.0), "c"), (("ma", 0.0), "ct"), (("ma", -0.5), "c"), (("ma", -0.5), "ct"))
SIZE_CELLS = {4: "c", 5: "ct"}
ARM = {"SB": 6, "SWB": 7}
TOL_STAT = 10 ** -10
TOL_P = 0.02
TOL_MZT = 10 ** -12
RSCRIPT = r"C:\Program Files\R\R-4.6.1\bin\Rscript.exe"
DC = {"c": 1, "ct": 2}


def path(cell, i, err):
    return P12.null_path(err, N, C.rep_rng(FAM, cell, i))


def arm_rng(cell, i, a):
    return np.random.default_rng(np.random.SeedSequence(FAM, spawn_key=(cell, i, a)))


def replica(y, case, cell, i):
    T = len(y)
    pmax = B.kmax_rule(T)
    l = B.bootur_block_length(T)
    dc = DC[case]
    cqd = B.CQD_BOOTUR[dc - 1]
    out = {}
    for m, a in ARM.items():
        g = arm_rng(cell, i, a)
        if m == "SB":
            di = g.integers(0, T - l + 1, size=(RB, T))
            dz = np.zeros((1, 1))
            p, t, k = B.bootur_pvalue(y, pmax, dc, cqd, False, di, dz)
        else:
            dz = g.standard_normal((RB, T))
            di = np.zeros((1, 1), dtype=np.int64)
            p, t, k = B.bootur_pvalue(y, pmax, dc, cqd, True, di, dz)
        out[m] = {"p": p, "stat": t, "lag": int(k)}
    return out


def noise_benchmark(rows, m):
    """Diagnostico (no cambia la compuerta): E|p_py - p_r| si los dos lados fueran replicas exactas con
    remuestreos independientes: E|X - Y|/B con X, Y ~ Bin(B, p) independientes, p = media de los dos
    p-valores de la serie; y la media con signo de p_py - p_r con su EE."""
    k = np.arange(RB + 1)
    diff = np.arange(-RB, RB + 1)
    exp = []
    for r in rows:
        p = (r[m]["p_py"] + r[m]["p_r"]) / 2
        f = binom.pmf(k, RB, p)
        exp.append(float(np.sum(np.abs(diff) * np.convolve(f, f[::-1])) / RB))
    d = np.array([r[m]["p_py"] - r[m]["p_r"] for r in rows])
    return {"expected_mean_abs_p_if_exact": float(np.mean(exp)), "observed_mean_abs_p": float(np.mean(np.abs(d))),
            "signed_mean_p_py_minus_r": float(np.mean(d)), "signed_mean_se": float(np.std(d, ddof=1) / np.sqrt(len(d)))}


def size_job(cell, case, idx):
    rows = []
    for i in idx:
        y = path(cell, i, ("ma", 0.0))
        r = replica(y, case, cell, i)
        rows.append([r["SB"]["p"], r["SWB"]["p"]])
    return rows


def main():
    t0 = time.time()
    series, meta = [], []
    for c, (err, case) in enumerate(CELLS):
        for i in range(PER_CELL):
            series.append((c, i, err, case, path(c, i, err)))
    T = N + 1
    pmax = B.kmax_rule(T)
    tmp = tempfile.mkdtemp(prefix="a15_p0_")
    Y = np.column_stack([s[4] for s in series])
    np.savetxt(os.path.join(tmp, "series.csv"), Y, delimiter=",", fmt="%.17g")
    with open(os.path.join(tmp, "meta.csv"), "w") as f:
        f.write("j,case,max_lag\n")
        for j, s in enumerate(series):
            f.write("%d,%s,%d\n" % (j, s[3], pmax))
    rs = subprocess.run([RSCRIPT, os.path.join(HERE, "audit15_bootur_paso0.R"), os.path.join(tmp, "series.csv"),
                         os.path.join(tmp, "meta.csv"), os.path.join(tmp, "r_out.csv")], capture_output=True, text=True)
    if rs.returncode != 0:
        print(rs.stdout, rs.stderr)
        return 2
    rv = np.genfromtxt(os.path.join(tmp, "r_out.csv"), delimiter=",", names=True, dtype=None, encoding="utf-8")
    t_r = time.time() - t0
    rows, mzt_d = [], []
    for j, (c, i, err, case, y) in enumerate(series):
        mine = replica(y, case, c, i)
        npk = U.np_statistics(y, case)
        nb = B.mzt_gls(y, case == "ct", B.CBAR_NP[case], U.kmax_rule(len(y)))
        mzt_d.append(max(abs(npk["MZt"] - nb[0]), abs(npk["MSB"] - nb[1])) if npk["k"] == nb[2] else float("inf"))
        rec = {"j": j, "cell": c, "i": i, "err": list(err), "case": case}
        for m in ARM:
            rec[m] = {"stat_py": mine[m]["stat"], "stat_r": float(rv["stat_" + m][j]), "lag_py": mine[m]["lag"],
                      "lag_r": int(rv["lag_" + m][j]), "p_py": mine[m]["p"], "p_r": float(rv["p_" + m][j])}
        rows.append(rec)
    crit = {}
    for m in ARM:
        ds = [abs(r[m]["stat_py"] - r[m]["stat_r"]) for r in rows]
        dl = [abs(r[m]["lag_py"] - r[m]["lag_r"]) for r in rows]
        dp = [abs(r[m]["p_py"] - r[m]["p_r"]) for r in rows]
        crit[m] = {"max_abs_stat": max(ds), "max_abs_lag": max(dl), "mean_abs_p": float(np.mean(dp)), "max_abs_p": max(dp),
                   "stat_ok": max(ds) <= TOL_STAT, "lag_ok": max(dl) == 0, "p_ok": float(np.mean(dp)) <= TOL_P}
    cores = min(os.cpu_count() or 1, 16)
    t1 = time.time()
    size = {}
    region = C.exact_region(SIZE_PATHS)
    for cell, case in SIZE_CELLS.items():
        split = [list(range(SIZE_PATHS))[k::cores] for k in range(cores)]
        res = Parallel(n_jobs=cores, backend="loky")(delayed(size_job)(cell, case, s) for s in split)
        pv = np.full((SIZE_PATHS, 2), np.nan)
        for s, r in zip(split, res):
            pv[np.array(s)] = r
        size[case] = {}
        for k, m in enumerate(ARM):
            rej = int(np.sum(pv[:, k] < C.ALPHA))
            size[case][m] = {"rejections": rej, "n": SIZE_PATHS, "rate": rej / SIZE_PATHS, "region": list(region),
                             "in_region": region[0] <= rej / SIZE_PATHS <= region[1]}
    gate = {m: bool(crit[m]["stat_ok"] and crit[m]["lag_ok"] and crit[m]["p_ok"]
                    and all(size[c][m]["in_region"] for c in size)) for m in ARM}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "reading": "protocol_audit15.md, lectura 1.7; enmienda 1, E1.3; enmienda 2, B1 y seccion 3",
           "config": {"n": N, "T": T, "pmax": pmax, "B": RB, "per_cell": PER_CELL, "cells": [[list(e), c] for e, c in CELLS],
                      "size_paths_per_case": SIZE_PATHS, "r_seeds": "set.seed(154000 + j) SB, set.seed(154500 + j) SWB",
                      "python_streams": "SeedSequence(154, spawn_key=(celda, i, 6 SB | 7 SWB))",
                      "bootur_version": rs.stdout.strip(), "tolerances": {"stat": TOL_STAT, "lag": 0, "mean_abs_p": TOL_P}},
           "series": rows, "criteria": crit, "size_replica": size,
           "noise_benchmark": {m: noise_benchmark(rows, m) for m in ARM},
           "mzt_numba_vs_np_statistics": {"max_abs": max(mzt_d), "ok": max(mzt_d) <= TOL_MZT},
           "gate": {"iii_sieve_SB": gate["SB"], "v_prime_SWB_bootUR": gate["SWB"]},
           "elapsed_sec": {"r": t_r, "size": time.time() - t1, "total": time.time() - t0}}
    C.write_result(OUT, out, __file__)
    for m in ARM:
        print(m, crit[m], {c: (size[c][m]["rate"], size[c][m]["in_region"]) for c in size})
    print("MZ_t numba vs np_statistics:", out["mzt_numba_vs_np_statistics"])
    print("diagnostico de ruido:", out["noise_benchmark"])
    print("compuerta:", out["gate"], "tiempo %.0f s" % out["elapsed_sec"]["total"])
    return 0 if all(gate.values()) else 3


if __name__ == "__main__":
    sys.exit(main())
