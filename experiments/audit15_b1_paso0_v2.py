"""
Auditoria A15 - B15.1, Paso 0 con B = 999 (enmienda 3, E3.1 y E3.2). Familia 159.

E3.1: 200 series de n = 200 (celdas 0-3; 50 cada una). Replica en Python (audit15_boot_engine)
frente a boot_adf(detrend = "QD", criterion = "MAIC", criterion_scale = FALSE, max_lag =
floor(12 (T/100)^{1/4}), B = 999), por metodo (SB, SWB):
  (a) max |D estadistico| <= 1e-10 y max |D retardo| = 0;
  (b) |media(p_py - p_R)| <= 2.58 EE, EE = sd(p_py - p_R; ddof = 1)/sqrt(200);
  (c) media |p_py - p_R| <= 1.15 x media de E|X - Y|/B, X, Y ~ Bin(B, p) independientes,
      p = (p_py + p_R)/2 de cada serie (formula de audit15_b1_paso0.noise_benchmark, commit 6c938d8).
E3.2: bootUR y la replica sobre los MISMOS 2000 caminos iid de n = 200 por caso (celdas 4 y 5),
B = 999; rechazo con p < 0.05; diferencia pareada (b - c)/N con EE [b + c - (b - c)^2/N]^{1/2}/N;
pasa si |D| <= 2.58 EE. El tamano de bootUR se reporta con Wilson (no es compuerta).
Semillas R: set.seed(159000 + j) SB y set.seed(159500 + j) SWB en las 200 series; set.seed(1590000
+ 10000 c + i) SB y set.seed(1595000 + 10000 c + i) SWB en los caminos de tamano.

Salida: experiments/results/b1_paso0_v2_audit15.json.
"""
import math
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
import audit15_design as D                                         # noqa: E402
import audit15_boot_engine as B                                    # noqa: E402
import audit12_unitroot as P12                                     # noqa: E402

OUT = os.path.join(C.RESULTS, "b1_paso0_v2_audit15.json")
FAM = C.FAMILY["PASO0_V2"]
N = 200
RB = D.B_PASO0_V2
SERIES_CELLS = ((("ma", 0.0), "c"), (("ma", 0.0), "ct"), (("ma", -0.5), "c"), (("ma", -0.5), "ct"))
SIZE_CELLS = {4: "c", 5: "ct"}
ARM = D.PASO0_ARMS
TOL_STAT = 10 ** -10
Z = 2.58                                       # enmienda 3, E3.1(b) y E3.2
NOISE_FACTOR = 1.15                            # enmienda 3, E3.1(c)
RSCRIPT = r"C:\Program Files\R\R-4.6.1\bin\Rscript.exe"
DC = {"c": 1, "ct": 2}
R_CHUNKS = 8


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
            p, t, k = B.bootur_pvalue(y, pmax, dc, cqd, False, di, np.zeros((1, 1)))
        else:
            dz = g.standard_normal((RB, T))
            p, t, k = B.bootur_pvalue(y, pmax, dc, cqd, True, np.zeros((1, 1), dtype=np.int64), dz)
        out[m] = {"p": p, "stat": t, "lag": int(k)}
    return out


def replica_job(items):
    return [replica(y, case, c, i) for c, i, case, y in items]


def noise_expected(p_mid, Bn):
    """E|X - Y|/B con X, Y ~ Bin(B, p) independientes (formula registrada en la enmienda 3)."""
    k = np.arange(Bn + 1)
    diff = np.arange(-Bn, Bn + 1)
    f = binom.pmf(k, Bn, p_mid)
    return float(np.sum(np.abs(diff) * np.convolve(f, f[::-1])) / Bn)


def run_r(series, seeds, tmp, tag):
    """Ejecuta el script de R en R_CHUNKS procesos paralelos; devuelve filas en el orden de 'series'."""
    T = N + 1
    pmax = B.kmax_rule(T)
    chunks = [list(range(len(series)))[k::R_CHUNKS] for k in range(R_CHUNKS)]
    procs = []
    for k, idx in enumerate(chunks):
        if not idx:
            continue
        sp = os.path.join(tmp, "%s_s%d.csv" % (tag, k))
        mp = os.path.join(tmp, "%s_m%d.csv" % (tag, k))
        op = os.path.join(tmp, "%s_o%d.csv" % (tag, k))
        np.savetxt(sp, np.column_stack([series[j][3] for j in idx]), delimiter=",", fmt="%.17g")
        with open(mp, "w") as f:
            f.write("j,case,max_lag,seed_sb,seed_swb,B\n")
            for j in idx:
                f.write("%d,%s,%d,%d,%d,%d\n" % (j, series[j][2], pmax, seeds[j][0], seeds[j][1], RB))
        procs.append((idx, op, subprocess.Popen([RSCRIPT, os.path.join(HERE, "audit15_bootur_paso0_v2.R"), sp, mp, op],
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)))
    rows = [None] * len(series)
    version = None
    for idx, op, pr in procs:
        so, se = pr.communicate()
        if pr.returncode != 0:
            raise RuntimeError(se)
        version = so.strip()
        rv = np.genfromtxt(op, delimiter=",", names=True, dtype=None, encoding="utf-8")
        rv = np.atleast_1d(rv)
        for r in rv:
            rows[int(r["j"])] = {m: {"stat": float(r["stat_" + m]), "p": float(r["p_" + m]), "lag": int(r["lag_" + m])} for m in ARM}
    return rows, version


def main():
    t0 = time.time()
    cores = min(os.cpu_count() or 1, 16)
    series = []
    for c, (err, case) in enumerate(SERIES_CELLS):
        for i in range(D.PASO0_REPS[c]):
            series.append((c, i, case, path(c, i, err)))
    seeds = [(159000 + j, 159500 + j) for j in range(len(series))]
    size_paths = []
    for c, case in SIZE_CELLS.items():
        for i in range(D.PASO0_REPS[c]):
            size_paths.append((c, i, case, path(c, i, ("ma", 0.0))))
    size_seeds = [(1590000 + 10000 * c + i, 1595000 + 10000 * c + i) for c, i, _, _ in size_paths]
    tmp = tempfile.mkdtemp(prefix="a15_p0v2_")
    split = [series[k::cores] for k in range(cores)]
    py = Parallel(n_jobs=cores, backend="loky")(delayed(replica_job)(s) for s in split)
    mine = {}
    for s, r in zip(split, py):
        for (c, i, _, _), x in zip(s, r):
            mine[(c, i)] = x
    rrows, version = run_r(series, seeds, tmp, "ser")
    rows = []
    for j, (c, i, case, y) in enumerate(series):
        rec = {"j": j, "cell": c, "i": i, "case": case}
        for m in ARM:
            rec[m] = {"stat_py": mine[(c, i)][m]["stat"], "stat_r": rrows[j][m]["stat"], "lag_py": mine[(c, i)][m]["lag"],
                      "lag_r": rrows[j][m]["lag"], "p_py": mine[(c, i)][m]["p"], "p_r": rrows[j][m]["p"]}
        rows.append(rec)
    crit = {}
    for m in ARM:
        ds = max(abs(r[m]["stat_py"] - r[m]["stat_r"]) for r in rows)
        dl = max(abs(r[m]["lag_py"] - r[m]["lag_r"]) for r in rows)
        d = np.array([r[m]["p_py"] - r[m]["p_r"] for r in rows])
        se = float(np.std(d, ddof=1) / math.sqrt(d.size))
        exp = float(np.mean([noise_expected((r[m]["p_py"] + r[m]["p_r"]) / 2, RB) for r in rows]))
        crit[m] = {"a_max_abs_stat": ds, "a_max_abs_lag": dl, "a_ok": ds <= TOL_STAT and dl == 0,
                   "b_mean_signed": float(d.mean()), "b_se": se, "b_ok": abs(float(d.mean())) <= Z * se,
                   "c_mean_abs": float(np.mean(np.abs(d))), "c_expected_exact": exp, "c_bound": NOISE_FACTOR * exp,
                   "c_ok": float(np.mean(np.abs(d))) <= NOISE_FACTOR * exp}
    t1 = time.time()
    split = [size_paths[k::cores] for k in range(cores)]
    py = Parallel(n_jobs=cores, backend="loky")(delayed(replica_job)(s) for s in split)
    pys = {}
    for s, r in zip(split, py):
        for (c, i, _, _), x in zip(s, r):
            pys[(c, i)] = x
    rsz, _ = run_r(size_paths, size_seeds, tmp, "sz")
    size = {}
    for c, case in SIZE_CELLS.items():
        idx = [k for k, sp in enumerate(size_paths) if sp[0] == c]
        size[case] = {}
        for m in ARM:
            a = np.array([pys[(c, size_paths[k][1])][m]["p"] < C.ALPHA for k in idx])
            r = np.array([rsz[k][m]["p"] < C.ALPHA for k in idx])
            n = len(idx)
            b_ = int(np.sum(a & ~r))
            c_ = int(np.sum(~a & r))
            diff = (b_ - c_) / n
            se = math.sqrt(max(b_ + c_ - (b_ - c_) ** 2 / n, 0.0)) / n
            wl, wu = C.wilson(int(r.sum()), n)
            size[case][m] = {"n": n, "rejections_py": int(a.sum()), "rejections_bootur": int(r.sum()), "size_py": float(a.mean()),
                             "size_bootur": float(r.mean()), "bootur_wilson": [wl, wu], "discordant_b": b_, "discordant_c": c_,
                             "diff": diff, "se_paired": se, "ok": abs(diff) <= Z * se if se > 0 else diff == 0,
                             "bootur_in_region": C.exact_region(n)[0] <= float(r.mean()) <= C.exact_region(n)[1],
                             "region": C.exact_region(n)}
    gate = {m: bool(crit[m]["a_ok"] and crit[m]["b_ok"] and crit[m]["c_ok"] and all(size[cs][m]["ok"] for cs in size)) for m in ARM}
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "reading": "enmienda 3, E3.1 y E3.2",
           "config": {"n": N, "T": N + 1, "pmax": B.kmax_rule(N + 1), "B": RB, "series": len(series), "size_paths_per_case": D.PASO0_REPS[4],
                      "cells": [[list(e), c] for e, c in SERIES_CELLS], "bootur_version": version, "z": Z, "noise_factor": NOISE_FACTOR,
                      "r_seeds": {"series": "159000 + j (SB), 159500 + j (SWB)", "size": "1590000 + 10000 c + i (SB), 1595000 + 10000 c + i (SWB)"},
                      "python_streams": "SeedSequence(159, spawn_key=(celda, i, 6 SB | 7 SWB))", "rejection": "p < 0.05 en los dos lados"},
           "series": rows, "criteria": crit, "size_paired": size,
           "gate": {"iii_SB_bootUR": gate["SB"], "v_prime_SWB_bootUR": gate["SWB"]},
           "elapsed_sec": {"series": t1 - t0, "size": time.time() - t1, "total": time.time() - t0}}
    C.write_result(OUT, out, __file__)
    for m in ARM:
        print(m, {k: v for k, v in crit[m].items()})
        for cs in size:
            s = size[cs][m]
            print("   tamano %s: py %.4f bootUR %.4f D %.4f EE %.4f ok %s" % (cs, s["size_py"], s["size_bootur"], s["diff"], s["se_paired"], s["ok"]))
    print("compuerta:", out["gate"], "tiempo %.0f s" % out["elapsed_sec"]["total"])
    return 0 if gate["SB"] else 3


if __name__ == "__main__":
    sys.exit(main())
