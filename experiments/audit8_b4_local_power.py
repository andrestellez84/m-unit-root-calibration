"""
Auditoria A8 - B4: potencia local asintotica y regla de adopcion GLS.

DGP: AR(1) Y_t = rho Y_{t-1} + e_t, Y_0 = 0, e_t iid N(0, 1), rho = 1 - c/n,
n = 2000, c in {0, 1, ..., 30} y c = 13.5, N = 20000 por c; familia 94. Caso
demeaned y con tendencia; todos los estadisticos del caso con tendencia son
invariantes a una tendencia lineal, de modo que se usan los mismos DGP sin
tendencia (con caminos independientes por caso).

Procedimientos: RM y RM-GLS (R = 0, theta in {0.05, 0.1, 0.2}), MSB-HAC
(tau = 0), con calibracion "hac"; DF-GLS, MSB-GLS y MZt-GLS (MAIC); envolvente
gaussiana: para cada c, P_T de ERS con cbar = -c (w2 = s2_AR con el retardo
MAIC del caso), calibrado por simulacion en c = 0 con N = 20000.

Umbrales bajo c = 0 con N_cal = 50000 (celda lap_<caso>_cal): RM, RM-GLS y
MSB-HAC con p = F_null(stat) < 0.05 (build_null_cdf); DF-GLS, MSB-GLS y MZt-GLS
con stat < cuantil 5%. Envolvente: cuantil 5% de P_T(cbar) sobre
lap_<caso>_envcal (N = 20000).

Compuerta previa (DURA): en c = 0 todos los procedimientos rechazan dentro de la
region exacta con un conjunto independiente de N = 5000 (lap_<caso>_test0). La
envolvente en c = 0 es degenerada (cbar = 0) y no entra en la compuerta; los
tamanos de los 30 P_T(cbar) sobre ese conjunto se reportan como informacion.

Regla de adopcion GLS (protocolo, seccion 2): G1 de este bloque, G2 y G3 de
b3_comparators_audit8.json.

Salida: experiments/results/b4_local_power_audit8.json.
Uso:
  python experiments/audit8_b4_local_power.py --cores 14 --max-seconds 14400
  python experiments/audit8_b4_local_power.py --analyze
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
import audit8_b2_size as B2                                        # noqa: E402
from power_comparison import generate_ar1                          # noqa: E402
from stationarity_test.rm_core import path_statistic, hac_sigma_sq  # noqa: E402
from stationarity_test.empirical_eigenvalues import cdf_from_null_stats  # noqa: E402

FAM = C.FAMILY["B4"]
CKPT = os.path.join(C.CKPT_ROOT, "audit8_b4")
OUT = os.path.join(C.RESULTS, "b4_local_power_audit8.json")
N = 2000
N_POWER = 20000
N_CAL = 50000
N_ENV = 20000
N_TEST = 5000
CASES = {"dm": "c", "ct": "ct"}
THETAS = (0.05, 0.1, 0.2)
C_GRID = tuple(float(c) for c in D.B4_C) + D.B4_C_EXTRA
CBARS = tuple(-c for c in C_GRID if c > 0)
REPORT_C = (0.0, 2.0, 5.0, 7.0, 10.0, 13.5, 15.0, 20.0, 25.0, 30.0)
GAP_C = (5.0, 10.0, 20.0)
G1_C = 10.0
G1_PP = 10.0
G3_PP = 0.30
RM_PROCS = tuple(["rm_t%g" % t for t in THETAS] + ["gls_t%g" % t for t in THETAS] + ["msbhac"])
Q_PROCS = ("dfgls", "msb", "mzt")
PROCS = RM_PROCS + Q_PROCS
COLS = PROCS + ("k",) + tuple("pt_%g" % -cb for cb in CBARS)
IDX = {c: i for i, c in enumerate(COLS)}


def cname(case, c):
    return "lap_%s_c%s" % (case, ("%d" % c) if float(c).is_integer() else ("%g" % c))


def row(case, cell, rho, i):
    y = generate_ar1(n=N, rho=rho, rng=C.rep_rng(FAM, cell, i))
    det = CASES[case]
    s2 = hac_sigma_sq(y)
    out = []
    for t in THETAS:
        t1, t2 = B2.taus(t, N, "theta")
        out.append(path_statistic(y, N, t1, t2, 0.0, s2, B2.C1, B2.C2, deterministics=det, anchor="mean", need_g2=False)[0])
    for t in THETAS:
        t1, t2 = B2.taus(t, N, "theta")
        out.append(path_statistic(y, N, t1, t2, 0.0, s2, B2.C1, B2.C2, deterministics=det, anchor="gls", need_g2=False)[0])
    t1, t2 = B2.taus(0.1, N, "zero")
    out.append(path_statistic(y, N, t1, t2, 0.0, s2, B2.C1, B2.C2, deterministics=det, anchor="mean", need_g2=False)[0])
    r = U.np_statistics(y, det)
    out.append(U.dfgls_maic(y, det, r["k"])[0])
    out += [r["MSB"], r["MZt"], r["k"]]
    out += [U.ers_pt(y, det, cb, r["s2_ar"]) for cb in CBARS]
    return [float(v) for v in out]


def _rows(case, cell, rho, idx):
    return [row(case, cell, rho, i) for i in idx]


def batch_fn(case, cell, rho, cores):
    def fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(delayed(_rows)(case, cell, rho, p) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return fn


def jobs():
    out = []
    for case in CASES:
        for role, reps in (("cal", N_CAL), ("envcal", N_ENV), ("test0", N_TEST)):
            name = "lap_%s_%s" % (case, role)
            out.append((case, name, 1.0, reps))
        for c in C_GRID:
            name = cname(case, c)
            out.append((case, name, 1.0 - c / N, N_POWER))
    return out


def run(a):
    resume = "python experiments/audit8_b4_local_power.py --cores %d --max-seconds %.0f" % (a.cores, a.max_seconds)
    t_block = time.time()
    for case, name, rho, reps in jobs():
        cell = D.cell_index(FAM, name)
        print("\n[CELDA] %s rho=%.5f" % (name, rho), flush=True)
        try:
            C.run_cell(name, reps, batch_fn(case, cell, rho, a.cores), CKPT, a.cores, t_block, a.max_seconds, resume)
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc, flush=True)
            return 2
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def load(name, reps):
    saved = B2.CKPT
    try:
        B2.CKPT = CKPT
        return B2.load_rows(name, reps)[0]
    finally:
        B2.CKPT = saved


def rejector(cal, env):
    cdfs = {p: cdf_from_null_stats(cal[:, IDX[p]]) for p in RM_PROCS}
    qs = {p: np.nanquantile(cal[:, IDX[p]], C.ALPHA) for p in Q_PROCS}
    qenv = {-cb: np.nanquantile(env[:, IDX["pt_%g" % -cb]], C.ALPHA) for cb in CBARS}

    def rej(rows):
        out = {}
        for p in RM_PROCS:
            out[p] = np.clip(cdfs[p](rows[:, IDX[p]]), 0.0, 1.0) < C.ALPHA
        for p in Q_PROCS:
            out[p] = np.nan_to_num(rows[:, IDX[p]], nan=np.inf) < qs[p]
        return out

    def env_rej(rows, c):
        return rows[:, IDX["pt_%g" % c]] < qenv[c]
    return rej, env_rej, {p: float(v) for p, v in qs.items()}, {str(k): float(v) for k, v in qenv.items()}


def c50(cs, pw):
    for (c0, p0), (c1, p1) in zip(zip(cs, pw), zip(cs[1:], pw[1:])):
        if p0 < 0.5 <= p1:
            return c0 + (0.5 - p0) * (c1 - c0) / (p1 - p0)
    return None


def analyze(a):
    t0 = time.time()
    region = C.exact_region(N_TEST)
    res = {}
    for case in CASES:
        cal = load("lap_%s_cal" % case, N_CAL)
        env = load("lap_%s_envcal" % case, N_ENV)
        test0 = load("lap_%s_test0" % case, N_TEST)
        rej, env_rej, qs, qenv = rejector(cal, env)
        r0 = rej(test0)
        gate = {p: C.rate_record(r0[p], region) for p in PROCS}
        pt_sizes = {str(-cb): C.rate_record(env_rej(test0, -cb), region) for cb in CBARS}
        power = {}
        for c in sorted(C_GRID):
            rows = load(cname(case, c), N_POWER)
            rr = rej(rows)
            power[str(c)] = {p: float(rr[p].mean()) for p in PROCS}
            power[str(c)]["envelope"] = C.ALPHA if c == 0 else float(env_rej(rows, c).mean())
            power[str(c)]["nan"] = {p: int(np.isnan(rows[:, IDX[p]]).sum()) for p in PROCS}
        cs = sorted(C_GRID)
        gaps = {p: {str(c): power[str(c)]["envelope"] - power[str(c)][p] for c in GAP_C} for p in PROCS}
        maxgap = {}
        for p in PROCS:
            g = [(power[str(c)]["envelope"] - power[str(c)][p], c) for c in cs]
            m = max(g)
            maxgap[p] = {"gap": m[0], "c": m[1]}
        half = {p: c50(cs, [power[str(c)][p] for c in cs]) for p in PROCS + ("envelope",)}
        res[case] = {"gate_c0": gate, "gate_passed": all(v["in_region"] for v in gate.values()),
                     "pt_sizes_c0_informative": pt_sizes, "sim_thresholds": qs, "envelope_thresholds": qenv,
                     "power": power, "gap_to_envelope": gaps, "max_gap": maxgap, "c_at_50pct": half}
    b3 = C.read_json("b3_comparators_audit8.json")
    g1_gap_gls = res["dm"]["gap_to_envelope"]["gls_t0.1"][str(G1_C)]
    g1_gap_rm = res["dm"]["gap_to_envelope"]["rm_t0.1"][str(G1_C)]
    g1 = {"gap_rmgls_pp": g1_gap_gls * 100, "gap_rm_pp": g1_gap_rm * 100,
          "reduction_pp": (g1_gap_rm - g1_gap_gls) * 100, "threshold_pp": G1_PP,
          "holds": bool((g1_gap_rm - g1_gap_gls) * 100 >= G1_PP)}
    g2src = b3["G2_rmgls_gaussian_size"]
    g2 = {"sizes": g2src, "region": b3["exact_region_5000"], "holds": all(v["in_region"] for v in g2src.values())}
    g3src = b3["G3_input"]
    g3 = {"excess_pp": g3src["excess_pp"], "mean_delta_rmgls": g3src["mean_delta_rmgls"],
          "mean_delta_rm": g3src["mean_delta_rm"], "threshold_pp": G3_PP, "holds": bool(g3src["excess_pp"] <= G3_PP)}
    adopt = g1["holds"] and g2["holds"] and g3["holds"]
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"n": N, "N_power": N_POWER, "N_cal": N_CAL, "N_envelope_cal": N_ENV, "N_test0": N_TEST,
                      "c_grid": list(C_GRID), "thetas": list(THETAS), "report_c": list(REPORT_C),
                      "rule_rm": "p = F_null(stat) < 0.05, calibracion hac bajo c = 0",
                      "rule_quantile": "stat < cuantil 5% bajo c = 0",
                      "envelope": "P_T de ERS con cbar = -c, umbral simulado en c = 0 con N = 20000; en c = 0 vale alpha"},
           "exact_region_test0": region, "cases": res,
           "prior_gate": {"passed": all(r["gate_passed"] for r in res.values())},
           "gls_rule": {"G1": g1, "G2": g2, "G3": g3, "adopt_gls": adopt,
                        "primary_final": "RM-GLS (anclada por GLS)" if adopt else "RM (demeaned)"},
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("compuerta previa", out["prior_gate"], {k: [p for p, v in r["gate_c0"].items() if not v["in_region"]] for k, r in res.items()})
    print("G1", g1, "\nG2", g2["holds"], "\nG3", g3["holds"], g3["excess_pp"], "\nprimaria", out["gls_rule"]["primary_final"])
    print(OUT)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    return analyze(a) if a.analyze else run(a)


if __name__ == "__main__":
    sys.exit(main())
