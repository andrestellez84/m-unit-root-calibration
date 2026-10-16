"""
Auditoria A12 - B12.B: atribucion con Perron-Qu (familia 131 sin trayectorias nuevas).

Trayectorias (protocolo_audit12, lectura 13): DGP 1 de B5/A8 (familia 95) de B9.1
(dgp1_rho*_n{200,500,1000} en c; ct_power_rho*_n{200,500} en ct) y potencia local de
B9.2 (lp_{dm,ct}_c{5,10,15}, n = 2000). Paso 0: 50 primeras trayectorias recalculadas
frente a las filas de B9.1/B9.2 (las que leyo B9.3), max |Delta| = 0. Se calculan las
columnas PQ (audit12_unitroot.row_pq) en todas las trayectorias.

Variantes (tau = 0, anclaje GLS): (a) gls_t0 (sigma_hat HAC), (b) glsb_t0 (s2_AR
MAIC-GLS), (b') glsbp_t0 (s2_AR MAIC-MCO), todas con cv simulado; (c) MSB-GLS NP con
cv asintotico. (a) y (b): calibracion de A10 (N_cal = 500 000) en n <= 1000 y de A9
(50 000) en n = 2000; (b'): familia 136. Diferencias pareadas (a)-(b'), (b')-(b),
(b')-(c) (y (a)-(b), (b)-(c) de referencia), por celda y en media por n. Clasifica C
y contrasta la direccion registrada (b') > (b).

Uso: python experiments/audit12_bB_attrib.py --run --cores 14 ; --analyze
Salida: experiments/results/bB_attrib_audit12.json (checkpoints en checkpoints/audit12_bB).
"""
import argparse
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit12_common as C                                         # noqa: E402
import audit12_unitroot as P                                       # noqa: E402
import audit12_runner as R                                         # noqa: E402
import audit12_cal as CAL                                          # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b91_equalized as B91                                 # noqa: E402
import audit9_b92_theta as B92                                     # noqa: E402

FAM = C.FAMILY["B"]
CKPT = os.path.join(C.CKPT_ROOT, "audit12_bB")
OUT = os.path.join(C.RESULTS, "bB_attrib_audit12.json")
DGP1_N = (200, 500, 1000)
CT_N = (200, 500)
LP_C = (5.0, 10.0, 15.0)
LP_N = D9.N_LP
PASO0 = 50
PASO0_COLS = ("s2", "gls_t0", "gls_t0.02", "glsb_t0", "dfgls", "mzt", "msb", "k", "s2ar")
PQJ = {c: i for i, c in enumerate(P.COLS_PQ)}
C_TOL, C_SE = 0.010, 0.002
DIAG_N = 200


def power_cells():
    out = {}
    for k, spec in B91.cells().items():
        if k.startswith("dgp1_") and spec["n"] in DGP1_N:
            out[k] = {"n": spec["n"], "case": "c", "rho": spec["rho"], "reps": D9.N_SIM, "source": "b91"}
        elif k.startswith("ct_power_") and spec["n"] in CT_N:
            out[k] = {"n": spec["n"], "case": "ct", "rho": spec["rho"], "reps": D9.N_SIM, "source": "b91"}
    for case in D9.LP_CASES:
        for c in LP_C:
            out["lp_%s_c%s" % (case, D9.cname(c))] = {"n": LP_N, "case": D9.CASE_DET[case], "lp_case": case, "c": c,
                                                      "reps": D9.N_POWER, "source": "b92"}
    return out


def path(name, spec, i):
    if spec["source"] == "b91":
        return D9.b5_path(name, i)
    return D9.lp_path(spec["lp_case"], spec["c"], i)


def ref_rows(name, spec):
    if spec["source"] == "b91":
        rows, _ = C.load_rows(B91.CKPT, name, spec["reps"])
        return rows, E.columns(**B91.flags_for(name))
    rows, _ = C.load_rows(B92.CKPT, name, spec["reps"])
    return rows, E.columns(cases=(spec["case"],), **B92.LP_FLAGS)


def row_fn(name, spec):
    def f(i):
        return P.row_pq(path(name, spec, i), spec["n"], cases=(spec["case"],))
    return f


def run(cores, max_seconds):
    t_block = time.time()
    resume = "python experiments/audit12_bB_attrib.py --run --cores %d" % cores
    R.warm(cores)
    try:
        for name, spec in power_cells().items():
            print("[CELDA] %s" % name, flush=True)
            R.run_cell(name, spec["reps"], row_fn(name, spec), len(P.COLS_PQ), CKPT, cores, t_block, max_seconds, resume,
                       per_core=200, log=lambda s: print(s, flush=True))
    except C.BudgetExhausted as exc:
        print("[TOPE] %s" % exc, flush=True)
        return 2
    print("bloque B: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def paso0(name, spec, rows, cols):
    J = E.index(cols)
    case = spec["case"]
    worst = {}
    new = [P.np_part(path(name, spec, i), spec["n"], case) for i in range(PASO0)]
    for c in PASO0_COLS:
        key = "s2" if c == "s2" else "%s|%s" % (case, c)
        if key not in J:
            continue
        a, b = np.array([d[c] for d in new]), rows[:PASO0, J[key]]
        d = np.where(np.isnan(a) & np.isnan(b), 0.0, np.abs(a - b))
        worst[c] = float(np.max(np.where(np.isnan(d), np.inf, d)))
    return {"reps": PASO0, "by_column": worst, "max_abs_diff": max(worst.values())}


def pq_rule(n, case):
    from stationarity_test.empirical_eigenvalues import cdf_from_null_stats
    pq, pqc, _ = CAL.load_pq(n)
    col = pq[:, list(pqc).index("%s|glsbp_t0" % case)]
    cdf = cdf_from_null_stats(col)
    return (lambda x: np.clip(cdf(x), 0.0, 1.0) < C.ALPHA), int(np.sum(np.isfinite(col)))


def ab_rules(n, case):
    if n == LP_N:
        rej, _ = B91.rejectors_for([n], (case,))[0][(n, case)]
        return rej, "A9 N_cal = 50 000 (semilla 42)"
    rows, cols = CAL.load_a10(n)
    rej, _ = E.rejector(rows, cols, case)
    return rej, "A10 N_cal = 500 000 (semilla 42)"


def analyze():
    t0 = time.time()
    cells = power_cells()
    rules, pq_rules = {}, {}
    for n, case in sorted({(s["n"], s["case"]) for s in cells.values()}):
        rules[(n, case)] = ab_rules(n, case)
        pq_rules[(n, case)] = pq_rule(n, case)
    res, p0 = {}, {}
    for name, spec in cells.items():
        n, case = spec["n"], spec["case"]
        rows, cols = ref_rows(name, spec)
        p0[name] = paso0(name, spec, rows, cols)
        pq, el = R.load_cell(CKPT, name, spec["reps"])
        rej, src = rules[(n, case)]
        v = {"a": rej(rows, cols, "gls_t0"), "b": rej(rows, cols, "glsb_t0"),
             "bp": pq_rules[(n, case)][0](pq[:, PQJ["glsbp_t0"]]), "c": E.reject_asy(rows, cols, case, "msb")}
        J = E.index(cols)
        rec = {"n": n, "case": case, "rates": {k: C.rate_record(x) for k, x in v.items()},
               "diffs": {"a_minus_bp": C.paired_diff(v["a"], v["bp"]), "bp_minus_b": C.paired_diff(v["bp"], v["b"]),
                         "bp_minus_c": C.paired_diff(v["bp"], v["c"]), "a_minus_b": C.paired_diff(v["a"], v["b"]),
                         "b_minus_c": C.paired_diff(v["b"], v["c"])},
               "ab_calibration": src, "bp_N_cal": pq_rules[(n, case)][1], "pq_elapsed_sec": el,
               "diagnostics": {"k_gls": float(np.nanmedian(rows[:, J["%s|k" % case]])), "k_ols": float(np.nanmedian(pq[:, PQJ["kpq"]])),
                               "s2ar_gls": float(np.nanmedian(rows[:, J["%s|s2ar" % case]])),
                               "s2ar_ols": float(np.nanmedian(pq[:, PQJ["s2ar_pq"]])),
                               "s2_hac": float(np.nanmedian(rows[:, J["s2"]]))},
               "nan_pq": {c: int(np.sum(~np.isfinite(pq[:, i]))) for c, i in PQJ.items()}}
        if spec["source"] == "b91":
            rec["rho"] = spec["rho"]
        else:
            rec.update({"c": spec["c"], "lp_case": spec["lp_case"]})
        res[name] = rec
    by_n = {}
    for case in ("c", "ct"):
        for n in sorted({r["n"] for r in res.values() if r["case"] == case and "rho" in r}):
            ks = [k for k, r in res.items() if r["case"] == case and r["n"] == n and "rho" in r]
            by_n["%s|%d" % (case, n)] = {"cells": ks, **{d: C.mean_with_se([res[k]["diffs"][d] for k in ks])
                                                         for d in res[ks[0]]["diffs"]}}
    m = by_n["c|%d" % DIAG_N]
    C_rule = {"rule": "DGP 1, c, n = 200: media (a)-(b') <= %g con EE <= %g" % (C_TOL, C_SE), "mean": m["a_minus_bp"]["mean"],
              "se": m["a_minus_bp"]["se"], "k": m["a_minus_bp"]["k"],
              "holds": m["a_minus_bp"]["mean"] <= C_TOL and m["a_minus_bp"]["se"] <= C_SE}
    direction = {"rule": "(b') > (b) en DGP 1, c, n = 200 (media sobre los 7 rho)", "mean": m["bp_minus_b"]["mean"],
                 "se": m["bp_minus_b"]["se"], "holds": m["bp_minus_b"]["mean"] > 0}
    diag = {k: dict(rho=r["rho"], case=r["case"], **r["diagnostics"]) for k, r in res.items() if "rho" in r and r["n"] == DIAG_N}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"variants": {"a": "gls_t0 (sigma_hat HAC), cv simulado", "b": "glsb_t0 (s2_AR MAIC-GLS), cv simulado",
                                   "bp": "glsbp_t0 (s2_AR MAIC-MCO, Perron-Qu), cv simulado (familia 136)",
                                   "c": "MSB-GLS NP (MAIC-GLS), cv asintotico de NP 2001"},
                      "trajectories": "B5 de A8 (familia 95) via B9.1; potencia local de B9.2 (familia 102)",
                      "se": "pareado sd(d_i)/sqrt(N); medias por n con sqrt(sum se^2)/k (B9.3)",
                      "dgp1_n": list(DGP1_N), "ct_n": list(CT_N), "lp_c": list(LP_C), "lp_n": LP_N},
           "paso0": p0, "paso0_worst": max(v["max_abs_diff"] for v in p0.values()), "cells": res, "by_n": by_n,
           "C": C_rule, "prediction_direction": direction, "diagnostics_n200": diag,
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("Paso 0", out["paso0_worst"])
    for k, v in by_n.items():
        print(k, {d: (round(x["mean"] * 100, 2), round(x["se"] * 100, 2)) for d, x in v.items() if d != "cells"})
    print("C", C_rule, "\ndireccion", direction)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    a = ap.parse_args()
    if a.run:
        rc = run(a.cores, a.max_seconds)
        if rc:
            return rc
    if a.analyze:
        return analyze()
    return 0


if __name__ == "__main__":
    sys.exit(main())
