"""
Auditoria A8 - B1: validaciones (todas DURA).

V1  Regresion pre/post con defaults: el paquete del commit anterior a B1 (extraido
    con git archive) y el actual, en procesos hijos, sobre las 100 series de la
    celda "regression" (familia 91): max|delta| = 0 en estadistico y p-valor
    (defaults, configuracion publicada con N_cal = 50000 y seed = 42, caso "ct")
    y muestra nula ordenada identica. La suite completa se corre aparte
    (pytest_audit8.log).
V2  R = 0 admisible: compute_statistic con R = 0 devuelve |g1_std|.
V3  RM con tau = 0 frente a MSB-HAC directo, n^{-2} sum_{t=0}^{n} (Y_t - Ybar)^2 / s2
    (sum sobre n + 1 puntos; el divisor n^2 sale de Var_k con ddof = 1 sobre n + 1
    valores por n de la estandarizacion), a 1e-12 relativo.
V4  RM-GLS: invariancia a Y -> aY + b (constante) y Y -> aY + b + ct (tendencia),
    peor diferencia relativa <= 1e-10; no dependencia de la deriva (tendencia) con
    numeros aleatorios comunes sobre mu in {0, 0.05, 0.2}, <= 1e-12 relativo.
V5  Ng-Perron: n = 2000 (T = 2001 puntos), paseo aleatorio gaussiano, N = 20000,
    retardo fijo 0; cuantiles empiricos al 5% a +-3% relativo de la Tabla 1 de
    Ng y Perron (2001).

Salida: experiments/results/b1_validation_audit8.json.
Uso: python experiments/audit8_b1_validate.py --cores 14
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_design as D                                          # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
import audit8_b1_regression_child as RC                            # noqa: E402

OUT = os.path.join(C.RESULTS, "b1_validation_audit8.json")
FAM = C.FAMILY["B1"]
PRODUCTION_FILE = "src/stationarity_test/rm_core.py"
NP_N = 2000
NP_REPS = 20000
NP_TOL = 0.03
INV_TOL = 1e-10
DRIFT_TOL = 1e-12
TAU0_TOL = 1e-12
R0_TOL = 1e-15
INV_SERIES = 20
INV_N = (200, 500)
DRIFT_MU = (0.0, 0.05, 0.2)
SCALES = (0.1, 10.0)
SHIFTS_C = (3.7, -150.0)
SHIFTS_CT = ((3.7, -0.25), (-150.0, 2.5))
THETA = (0.1, 0.1)


def pre_b1_commit():
    added = C.git("log", "--diff-filter=A", "--format=%H", "--", PRODUCTION_FILE).splitlines()
    if not added:
        raise RuntimeError("%s no esta commiteado: commitea B1 antes de validar" % PRODUCTION_FILE)
    return C.git("rev-parse", added[-1] + "^")


def run_child(src_root, out):
    env = dict(os.environ)
    env["PYTHONPATH"] = src_root
    cell = D.cell_index(FAM, "regression")
    r = subprocess.run([sys.executable, os.path.join(HERE, "audit8_b1_regression_child.py"), "--out", out,
                        "--family", str(FAM), "--cell", str(cell)], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    with open(out, encoding="utf-8") as f:
        return json.load(f)


def v1_regression():
    base = pre_b1_commit()
    with tempfile.TemporaryDirectory() as tmp:
        arch = os.path.join(tmp, "src.tar")
        subprocess.run(["git", "archive", "-o", arch, base, "src"], cwd=C.REPO, check=True)
        subprocess.run(["tar", "-xf", arch, "-C", tmp], check=True)
        old = run_child(os.path.join(tmp, "src"), os.path.join(tmp, "old.json"))
        new = run_child(os.path.join(C.REPO, "src"), os.path.join(tmp, "new.json"))
    keys = sorted(k for k in old["rows"][0] if k not in ("i", "n"))
    diffs = {k: float(max(abs(a[k] - b[k]) for a, b in zip(old["rows"], new["rows"]))) for k in keys}
    stat_keys = [k for k in keys if k.startswith("stat")]
    p_keys = [k for k in keys if k.startswith("p_")]
    return {"pre_b1_commit": base, "series": len(new["rows"]), "old_module": old["module_file"],
            "new_module": new["module_file"], "max_abs_diff_by_field": diffs,
            "max_abs_diff_statistic": max(diffs[k] for k in stat_keys),
            "max_abs_diff_p_value": max(diffs[k] for k in p_keys),
            "null_sample_identical": old["null_R0.5_n200_sha256"] == new["null_R0.5_n200_sha256"],
            "golden_rows": old["rows"],
            "passed": all(v == 0.0 for v in diffs.values()) and old["null_R0.5_n200_sha256"] == new["null_R0.5_n200_sha256"]}


def v2_v3_tau0():
    from stationarity_test.statistic import compute_statistic
    from stationarity_test.hac_estimator import hac_newey_west
    cell = D.cell_index(FAM, "regression")
    worst_tau0, worst_r0 = 0.0, 0.0
    for i in range(RC.N_SERIES):
        Y = RC.series(i, cell, FAM)
        n = len(Y) - 1
        s2 = hac_newey_west(np.diff(Y))
        direct = np.sqrt(np.sum((Y - Y.mean()) ** 2) / n ** 2 / s2)
        r = compute_statistic(Y, THETA, 0.0, tau_mode="zero", cal_sigma="hac")
        worst_tau0 = max(worst_tau0, abs(r["statistic"] - direct) / direct)
        r0 = compute_statistic(Y, THETA, 0.0)
        worst_r0 = max(worst_r0, abs(r0["statistic"] - abs(r0["g1_std"])) / abs(r0["g1_std"]))
    return ({"series": RC.N_SERIES, "worst_rel_diff_statistic_vs_abs_g1_std": worst_r0, "tolerance": R0_TOL,
             "passed": worst_r0 <= R0_TOL},
            {"series": RC.N_SERIES, "formula": "sqrt(n^-2 sum_{t=0}^{n} (Y_t - Ybar)^2 / s2_HAC)",
             "worst_rel_diff": worst_tau0, "tolerance": TAU0_TOL, "passed": worst_tau0 <= TAU0_TOL})


def _gls_stat(Y, case):
    from stationarity_test.statistic import compute_statistic
    return compute_statistic(Y, THETA, 0.0, anchor="gls", cal_sigma="hac", deterministics=case)["statistic"]


def _rm_ct_stat(Y):
    from stationarity_test.statistic import compute_statistic
    return compute_statistic(Y, THETA, 0.0, cal_sigma="hac", deterministics="ct")["statistic"]


def v4_gls():
    out = {}
    worst = {"c": 0.0, "ct": 0.0}
    for case in ("c", "ct"):
        cell = D.cell_index(FAM, "invariance_dm" if case == "c" else "invariance_ct")
        for i in range(INV_SERIES):
            n = INV_N[i % len(INV_N)]
            rng = C.rep_rng(FAM, cell, i)
            Y = np.concatenate([[0.0], np.cumsum(rng.standard_normal(n))])
            if i % 2:
                Y = Y + 0.3 * np.arange(n + 1) if case == "ct" else Y
            ref = _gls_stat(Y, case)
            t = np.arange(n + 1, dtype=np.float64)
            for a in SCALES:
                shifts = SHIFTS_C if case == "c" else SHIFTS_CT
                for sh in shifts:
                    Z = a * Y + sh if case == "c" else a * Y + sh[0] + sh[1] * t
                    worst[case] = max(worst[case], abs(_gls_stat(Z, case) - ref) / ref)
    out["invariance"] = {"series_per_case": INV_SERIES, "n": list(INV_N), "scales": list(SCALES),
                         "shifts_c": list(SHIFTS_C), "shifts_ct": [list(s) for s in SHIFTS_CT],
                         "worst_rel_diff": worst, "tolerance": INV_TOL,
                         "passed": all(v <= INV_TOL for v in worst.values())}
    cell = D.cell_index(FAM, "drift_ct")
    wg, wr = 0.0, 0.0
    for i in range(INV_SERIES):
        n = INV_N[i % len(INV_N)]
        eps = C.rep_rng(FAM, cell, i).standard_normal(n)
        stats_g, stats_r = [], []
        for mu in DRIFT_MU:
            Y = np.concatenate([[0.0], np.cumsum(eps + mu)])
            stats_g.append(_gls_stat(Y, "ct"))
            stats_r.append(_rm_ct_stat(Y))
        wg = max(wg, (max(stats_g) - min(stats_g)) / min(stats_g))
        wr = max(wr, (max(stats_r) - min(stats_r)) / min(stats_r))
    out["drift"] = {"series": INV_SERIES, "mu": list(DRIFT_MU), "worst_rel_diff_rm_gls_ct": wg,
                    "worst_rel_diff_rm_ct": wr, "tolerance": DRIFT_TOL,
                    "passed": wg <= DRIFT_TOL and wr <= DRIFT_TOL}
    return out


def _np_rows(case, cell, idx):
    out = []
    for i in idx:
        y = D.gauss_rw(NP_N, C.rep_rng(FAM, cell, i))
        r = U.np_statistics(y, case, k=0)
        out.append([r[s] for s in U.NP_STATS])
    return out


def v5_np(cores):
    res = {}
    for case, cname in (("c", "np_validation_dm"), ("ct", "np_validation_ct")):
        cell = D.cell_index(FAM, cname)
        parts = [list(range(NP_REPS))[j::cores] for j in range(cores)]
        rows = np.array(sum(Parallel(n_jobs=cores)(delayed(_np_rows)(case, cell, p) for p in parts), []))
        q = np.quantile(rows, 0.05, axis=0)
        # error estandar del cuantil por bootstrap (200 remuestreos, semilla derivada de la celda)
        brng = np.random.default_rng(C.rep_seedseq(FAM, cell, NP_REPS))
        boots = np.array([np.quantile(rows[brng.integers(0, len(rows), len(rows))], 0.05, axis=0) for _ in range(200)])
        stats = {}
        for j, s in enumerate(U.NP_STATS):
            cv = U.NP_CV5[case][s]
            rel = abs(q[j] - cv) / abs(cv)
            stats[s] = {"empirical_q05": float(q[j]), "bootstrap_se": float(boots[:, j].std(ddof=1)),
                        "ng_perron_2001": cv, "rel_diff": float(rel), "passed": bool(rel <= NP_TOL)}
        res[case] = {"cell": cname, "n": NP_N, "T_points": NP_N + 1, "reps": NP_REPS, "lag": 0,
                     "cbar": U.NP_CBAR[case], "stats": stats}
    return {"tolerance_rel": NP_TOL, "cases": res,
            "passed": all(s["passed"] for c in res.values() for s in c["stats"].values()),
            "failing": ["%s/%s" % (c, s) for c, r in res.items() for s, v in r["stats"].items() if not v["passed"]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    print("V1 regresion pre/post ...", flush=True)
    v1 = v1_regression()
    print("  statistic %r  p %r  nula %s" % (v1["max_abs_diff_statistic"], v1["max_abs_diff_p_value"], v1["null_sample_identical"]), flush=True)
    print("V2/V3 R = 0 y tau = 0 ...", flush=True)
    v2, v3 = v2_v3_tau0()
    print("  R0 %r  tau0 %r" % (float(v2["worst_rel_diff_statistic_vs_abs_g1_std"]), float(v3["worst_rel_diff"])), flush=True)
    print("V4 RM-GLS ...", flush=True)
    v4 = v4_gls()
    print("  %s" % json.dumps({k: {kk: vv for kk, vv in v.items() if kk.startswith("worst")} for k, v in v4.items()}), flush=True)
    print("V5 Ng-Perron ...", flush=True)
    v5 = v5_np(a.cores)
    for case, r in v5["cases"].items():
        print("  %s %s" % (case, {s: (round(v["empirical_q05"], 4), v["ng_perron_2001"], round(v["rel_diff"], 4), v["passed"])
                                 for s, v in r["stats"].items()}), flush=True)
    gates = {"V1_regression": v1["passed"], "V2_R0_admissible": v2["passed"], "V3_tau0_vs_msb_hac": v3["passed"],
             "V4_gls_invariance": v4["invariance"]["passed"], "V4_gls_drift": v4["drift"]["passed"],
             "V5_ng_perron": v5["passed"]}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "V1_regression": v1, "V2_R0": v2, "V3_tau0": v3, "V4_gls": v4, "V5_ng_perron": v5,
           "gates": gates, "all_passed": all(gates.values()), "elapsed_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print(json.dumps(C.plain(gates)), "-> TODAS PASAN" if out["all_passed"] else "-> FALLA")
    print(OUT)
    return 0 if out["all_passed"] else 4


if __name__ == "__main__":
    sys.exit(main())
