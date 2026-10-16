"""
Auditoria A8 - B1: diagnostico de la validacion de Ng-Perron que no paso (V5).

No cambia la compuerta ni su tolerancia: registra lo que se descarto.

D1  Detrending GLS y regresion con retardo 0 frente a arch.unitroot.DFGLS
    (200 series por caso, n = 500): max|delta| del residuo detrendido y del
    estadistico t.
D2  Estabilidad en T: cuantiles al 5% de MZa, MZt, MSB y MPT con retardo 0 en
    T = 501 y T = 10001 puntos (N = 20000 por caso), junto a los de V5 (T = 2001).
D3  P_T de ERS con cbar = -7 / -13.5 y w2 = s2 con retardo 0, sobre los caminos
    de V5 (T = 2001): cuantil al 5% frente a Elliott, Rothenberg y Stock (1996,
    Tabla I), y frente al MPT del mismo camino.

Error estandar de cada cuantil por bootstrap (200 remuestreos).
Salida: experiments/results/b1_np_diagnostic_audit8.json.
Uso: python experiments/audit8_b1_np_diagnostic.py --cores 14
"""
import argparse
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_design as D                                          # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
import audit8_b1_validate as V                                     # noqa: E402

OUT = os.path.join(C.RESULTS, "b1_np_diagnostic_audit8.json")
FAM = C.FAMILY["B1"]
ARCH_N = 500
ARCH_SERIES = 200
T_GRID = (501, 10001)
BOOT = 200
Q = 0.05


def _arch_rows(case, cell, idx):
    from arch.unitroot import DFGLS
    out = []
    for i in idx:
        y = D.gauss_rw(ARCH_N, C.rep_rng(FAM, cell, i))
        yd = U.gls_detrend(y, case)
        t = DFGLS(y, trend=case, lags=0)
        stat = float(t.stat)
        exog = np.asarray(t.regression.model.exog)[:, 0]
        dy = np.diff(yd)
        x = yd[:-1]
        b = float(x @ dy / (x @ x))
        e = dy - b * x
        s2 = float(e @ e) / (len(dy) - 1)
        tmine = b / np.sqrt(s2 / float(x @ x))
        out.append([float(np.max(np.abs(exog - yd[:-1]))), abs(stat - tmine)])
    return out


def _np_rows(case, cell, n, with_pt, idx):
    out = []
    for i in idx:
        y = D.gauss_rw(n, C.rep_rng(FAM, cell, i))
        r = U.np_statistics(y, case, k=0)
        row = [r[s] for s in U.NP_STATS]
        if with_pt:
            row.append(U.ers_pt(y, case, U.NP_CBAR[case], r["s2_ar"]))
        out.append(row)
    return out


def quantiles(rows, seed_ss):
    q = np.quantile(rows, Q, axis=0)
    rng = np.random.default_rng(seed_ss)
    boots = np.array([np.quantile(rows[rng.integers(0, len(rows), len(rows))], Q, axis=0) for _ in range(BOOT)])
    return q, boots.std(axis=0, ddof=1)


def par(fn, cores, reps, *args):
    parts = [list(range(reps))[j::cores] for j in range(cores)]
    return np.array(sum(Parallel(n_jobs=cores)(delayed(fn)(*args, p) for p in parts), []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    out = {"D1_arch_identity": {}, "D2_T_stability": {}, "D3_ers_pt": {}}
    for case, tag in (("c", "dm"), ("ct", "ct")):
        cell = D.cell_index(FAM, "np_diag_arch_%s" % tag)
        rows = par(_arch_rows, a.cores, ARCH_SERIES, case, cell)
        out["D1_arch_identity"][case] = {"series": ARCH_SERIES, "n": ARCH_N,
                                         "max_abs_diff_detrended": float(rows[:, 0].max()),
                                         "max_abs_diff_t_stat_lag0": float(rows[:, 1].max())}
        by_T = {}
        for T in T_GRID:
            cell = D.cell_index(FAM, "np_diag_T%d_%s" % (T, tag))
            r = par(_np_rows, a.cores, V.NP_REPS, case, cell, T - 1, False)
            q, se = quantiles(r, C.rep_seedseq(FAM, cell, V.NP_REPS))
            by_T[str(T)] = {s: {"q05": float(q[j]), "bootstrap_se": float(se[j]),
                                "ng_perron_2001": U.NP_CV5[case][s],
                                "rel_diff": float(abs(q[j] - U.NP_CV5[case][s]) / abs(U.NP_CV5[case][s]))}
                            for j, s in enumerate(U.NP_STATS)}
            print(case, T, {s: round(v["q05"], 4) for s, v in by_T[str(T)].items()}, flush=True)
        out["D2_T_stability"][case] = {"reps": V.NP_REPS, "lag": 0, "by_T_points": by_T}
        cell = D.cell_index(FAM, "np_validation_%s" % tag)
        r = par(_np_rows, a.cores, V.NP_REPS, case, cell, V.NP_N, True)
        q, se = quantiles(r, C.rep_seedseq(FAM, cell, V.NP_REPS + 1))
        out["D3_ers_pt"][case] = {"T_points": V.NP_N + 1, "reps": V.NP_REPS, "same_paths_as_V5": True,
                                  "cbar": U.NP_CBAR[case],
                                  "pt_q05": float(q[-1]), "pt_bootstrap_se": float(se[-1]),
                                  "ers_1996": U.ERS_PT_CV5[case],
                                  "pt_rel_diff_vs_ers": float(abs(q[-1] - U.ERS_PT_CV5[case]) / U.ERS_PT_CV5[case]),
                                  "mpt_q05_same_paths": float(q[3]),
                                  "ng_perron_2001_mpt": U.NP_CV5[case]["MPT"],
                                  "ers_vs_ng_perron_rel_diff": float(abs(U.ERS_PT_CV5[case] - U.NP_CV5[case]["MPT"])
                                                                     / U.NP_CV5[case]["MPT"])}
        print(case, "PT", out["D3_ers_pt"][case], flush=True)
    out["provenance"] = C.provenance(__file__, seed_family=FAM)
    out["elapsed_sec"] = round(time.time() - t0, 1)
    C.write_result(OUT, out, __file__)
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
