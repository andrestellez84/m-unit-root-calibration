"""
Auditoria A12 - B12.A: errores MA(1) y AR(1) (familia 130; sonda en la 137).

--probe   sonda de presupuesto (lectura 12): 14 x 50 caminos a n = 500, ct, psi = -0.8,
          fila completa, tras calentar; proyeccion del bloque. Detiene si > 10 h.
--run     36 celdas de tamano (20 000 caminos) y 48 de potencia (5000), fila completa
          (audit12_unitroot.row_a) en el caso de la celda.
--analyze tamanos al cv iid (A10 N_cal = 500 000 para el lado NP; familia 136 para PQ),
          al asintotico publicado y al "limite" n = 20 000 de RM-GLS; potencia al cv iid
          y ajustada al tamano; diagnosticos; factor de Bartlett; G-A1 (Bonferroni), G-A2;
          clasificacion A/B/Intermedio y contraste de la prediccion.

Salidas: bA_probe_audit12.json, bA_ma_audit12.json.
"""
import argparse
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit12_common as C                                         # noqa: E402
import audit12_design as D                                         # noqa: E402
import audit12_unitroot as P                                       # noqa: E402
import audit12_runner as R                                         # noqa: E402
import audit12_cal as CAL                                          # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
import audit9_engine as E                                          # noqa: E402

FAM = C.FAMILY["A"]
CKPT = os.path.join(C.CKPT_ROOT, "audit12_bA")
OUT = os.path.join(C.RESULTS, "bA_ma_audit12.json")
OUT_PROBE = os.path.join(C.RESULTS, "bA_probe_audit12.json")
BUDGET_HOURS = 10.0
J = {c: i for i, c in enumerate(P.COLS_A)}
# Valores criticos asintoticos publicados al 5 % (lectura 7)
ASY_NP = {"mzt": "MZt", "msb": "MSB", "mzt_pq": "MZt", "msb_pq": "MSB"}
DFGLS_PUB = E.DFGLS_CV5_PUBLISHED
ASY_P = ("adf", "pp")
# NP (2000), Tablas 5.a y 6.a, psi = -0.8, n = 100 (G-A2, del encargo)
NP2000 = {"c": 0.036, "ct": 0.059}
GA2_TOL = 0.03
PRED = {"psi08_gt": 0.30, "psi05_lo": 0.08, "psi05_hi": 0.20, "phi05_lt": 0.05}
A_MZT_PP_08, A_MAX_08, A_MZT_PP_05 = 0.02, 0.10, 0.01
B_ABS, B_MZT_PP = 0.15, 0.05
BARTLETT_B_GRID = tuple(range(0, 13))


def row_fn(name, spec):
    def f(i):
        return P.row_a(D.a_path(name, spec, i), spec["n"], spec["case"])
    return f


# ---------------------------------------------------------------------------
# Sonda
# ---------------------------------------------------------------------------
def probe(cores):
    R.warm(cores)
    for i in range(2):                                            # calentamiento de las rutinas en este proceso
        P.row_a(D.probe_path(i), D.PROBE_N, D.PROBE_CASE)
    from joblib import Parallel, delayed

    def rows(idx):
        for i in idx[:1]:
            P.row_a(D.probe_path(i), D.PROBE_N, D.PROBE_CASE)       # calentamiento en cada trabajador
        t0 = time.time()
        for i in idx:
            P.row_a(D.probe_path(i), D.PROBE_N, D.PROBE_CASE)
        return time.time() - t0, len(idx)
    idx = list(range(D.PROBE_PATHS))
    split = [idx[j::cores] for j in range(cores)]
    t0 = time.time()
    res = Parallel(n_jobs=cores, backend="loky")(delayed(rows)(s) for s in split)
    wall = time.time() - t0
    per_path = sum(t for t, _ in res) / sum(k for _, k in res)
    cells = D.a_cells()
    a_paths = sum(s["reps"] for s in cells.values())
    cal_paths = D.N_CAL * sum(1 for n in D.CAL_N if n <= max(D.A_N))
    proj_h = per_path * (a_paths + cal_paths) / cores / 3600
    out = {"provenance": C.provenance(__file__, seed_family=C.FAMILY["PROBE"]),
           "config": {"paths": D.PROBE_PATHS, "n": D.PROBE_N, "case": D.PROBE_CASE, "err": list(D.PROBE_ERR),
                      "cores": cores, "budget_hours": BUDGET_HOURS,
                      "rule": "coste por camino (fila completa, n = 500) x (caminos de B12.A + calibracion PQ n <= 500) / nucleos"},
           "per_path_sec": per_path, "wall_sec": wall, "a_paths": a_paths, "cal_paths_n_le_500": cal_paths,
           "projected_hours": proj_h, "within_budget": proj_h <= BUDGET_HOURS}
    C.write_result(OUT_PROBE, out, __file__)
    print("sonda: %.4f s/camino; proyeccion %.2f h (tope %g h)" % (per_path, proj_h, BUDGET_HOURS))
    return 0 if out["within_budget"] else 3


def run(cores, max_seconds):
    t_block = time.time()
    resume = "python experiments/audit12_bA_ma.py --run --cores %d" % cores
    R.warm(cores)
    cells = D.a_cells()
    order = [k for k in cells if cells[k]["kind"] == "size"] + [k for k in cells if cells[k]["kind"] == "power"]
    try:
        for name in order:
            spec = cells[name]
            print("[CELDA] %s" % name, flush=True)
            R.run_cell(name, spec["reps"], row_fn(name, spec), len(P.COLS_A), CKPT, cores, t_block, max_seconds, resume,
                       per_core=100, log=lambda s: print(s, flush=True))
    except C.BudgetExhausted as exc:
        print("[TOPE] %s" % exc, flush=True)
        return 2
    print("bloque A: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


# ---------------------------------------------------------------------------
# Analisis
# ---------------------------------------------------------------------------
def iid_rules(ns=D.A_N):
    """Por (n, caso): funcion de rechazo al cv iid para cada procedimiento y sus umbrales."""
    from stationarity_test.empirical_eigenvalues import cdf_from_null_stats
    rules = {}
    for n in ns:
        a10, a10c = CAL.load_a10(n)
        I10 = {c: i for i, c in enumerate(a10c)}
        pq, pqc, _ = CAL.load_pq(n)
        Ipq = {c: i for i, c in enumerate(pqc)}
        for case in D.CASES:
            def col(p):
                key = "%s|%s" % (case, p)
                return a10[:, I10[key]] if key in I10 else pq[:, Ipq[key]]
            cdfs = {p: cdf_from_null_stats(col(p)) for p in P.RM_LIKE}
            qs = {p: float(np.nanquantile(col(p), C.ALPHA)) for p in P.SIM_LOWER}
            qrm = {p: float(np.nanquantile(col(p), C.ALPHA)) for p in P.RM_LIKE}
            src = {p: ("A10 N_cal = 500 000 (semilla 42)" if "%s|%s" % (case, p) in I10 else "familia 136 N_cal = 500 000")
                   for p in P.PROCS}
            rules[(n, case)] = {"cdfs": cdfs, "qs": qs, "q_rm": qrm, "source": src,
                                "N_cal": {p: int(np.sum(np.isfinite(col(p)))) for p in P.PROCS}}
        del a10, pq
    return rules


def reject_iid(rule, rows, p):
    x = rows[:, J[p]]
    if p in rule["cdfs"]:
        return np.clip(rule["cdfs"][p](x), 0.0, 1.0) < C.ALPHA
    return np.nan_to_num(x, nan=np.inf) < rule["qs"][p]


def reject_asy(rows, p, case):
    x = rows[:, J[p]]
    if p in ASY_NP:
        return np.nan_to_num(x, nan=np.inf) < U.NP_CV5[case][ASY_NP[p]]
    if p in ("dfgls", "dfgls_pq"):
        return np.nan_to_num(x, nan=np.inf) < DFGLS_PUB[case]
    if p in ASY_P:
        return np.nan_to_num(rows[:, J[p + "_p"]], nan=1.0) < C.ALPHA
    return None


def big_limit():
    import audit10_b101_theta as B101
    q = B101.big_quantiles()
    return {(det, t): v for (det, t), v in q.items() if t in ("gls_t0", "gls_t0.02")}


def quart(x):
    x = x[np.isfinite(x)]
    return {"q25": float(np.quantile(x, 0.25)), "median": float(np.median(x)), "q75": float(np.quantile(x, 0.75))}


def diagnostics(rows, err):
    w2 = P.omega2(err)
    return {"s2_over_omega2": quart(rows[:, J["s2"]] / w2), "s2ar_over_omega2": quart(rows[:, J["s2ar"]] / w2),
            "s2ar_pq_over_omega2": quart(rows[:, J["s2ar_pq"]] / w2), "B": quart(rows[:, J["B"]]),
            "k": quart(rows[:, J["k"]]), "kpq": quart(rows[:, J["kpq"]]),
            "nan": {c: int(np.sum(~np.isfinite(rows[:, J[c]]))) for c in P.COLS_A}}


def analyze():
    t0 = time.time()
    cells = D.a_cells()
    rules = iid_rules()
    lim = big_limit()
    region95 = C.exact_region(D.N_SIZE)
    region_pow = C.exact_region(D.N_POW)
    K = len(P.PROCS) * len(D.A_N) * len(D.CASES)
    region_bonf = C.exact_region(D.N_SIZE, level=1.0 - C.ALPHA / K)
    data, elapsed = {}, {}
    for name, spec in cells.items():
        rows, el = R.load_cell(CKPT, name, spec["reps"])
        data[name] = rows
        elapsed[name] = el
    size, power = {}, {}
    for name, spec in cells.items():
        if spec["kind"] != "size":
            continue
        rows, n, case, err = data[name], spec["n"], spec["case"], spec["err"]
        rule = rules[(n, case)]
        rec = {"err": list(err), "err_tag": P.err_tag(err), "n": n, "case": case, "omega2": P.omega2(err), "iid": {},
               "asy": {}, "limit": {}, "diagnostics": diagnostics(rows, err)}
        for p in P.PROCS:
            rec["iid"][p] = C.rate_record(reject_iid(rule, rows, p), region95)
            ra = reject_asy(rows, p, case)
            if ra is not None:
                rec["asy"][p] = C.rate_record(ra, region95)
        for (det, t), q in lim.items():
            if det == case:
                rec["limit"][t] = dict(C.rate_record(np.nan_to_num(rows[:, J[t]], nan=np.inf) < q, region95), cv_n20000=q)
        rec["size_adjusted_q"] = {p: float(np.nanquantile(rows[:, J[p]], C.ALPHA)) for p in P.PROCS}
        med_B = int(round(rec["diagnostics"]["B"]["median"]))
        rec["bartlett_factor_at_median_B"] = {"B": med_B, "factor": P.bartlett_factor(err, med_B),
                                              "S_multiplier": 1.0 / math.sqrt(P.bartlett_factor(err, med_B))}
        size[name] = rec
    for name, spec in cells.items():
        if spec["kind"] != "power":
            continue
        rows, n, case, err = data[name], spec["n"], spec["case"], spec["err"]
        rule = rules[(n, case)]
        sz = size[spec["size_cell"]]
        rec = {"err": list(err), "err_tag": P.err_tag(err), "n": n, "case": case, "rho": spec["rho"], "size_cell": spec["size_cell"],
               "iid": {}, "adjusted": {}, "diagnostics": diagnostics(rows, err)}
        for p in P.PROCS:
            rec["iid"][p] = C.rate_record(reject_iid(rule, rows, p))
            rec["adjusted"][p] = C.rate_record(np.nan_to_num(rows[:, J[p]], nan=np.inf) < sz["size_adjusted_q"][p])
        power[name] = rec
    # G-A1 (Bonferroni, decision del autor) sobre las celdas psi = 0
    ga1 = {"K": K, "region_bonferroni": region_bonf, "region_literal": region95, "checks": {}, "outside_bonferroni": [],
           "outside_literal": []}
    for name, r in size.items():
        if r["err_tag"] != P.err_tag(("ma", 0.0)):
            continue
        for p in P.PROCS:
            x = r["iid"][p]["rate"]
            key = "%s|%d|%s" % (r["case"], r["n"], p)
            ga1["checks"][key] = x
            if not (region_bonf[0] <= x <= region_bonf[1]):
                ga1["outside_bonferroni"].append(key)
            if not (region95[0] <= x <= region95[1]):
                ga1["outside_literal"].append(key)
    ga1["n_checks"] = len(ga1["checks"])
    ga1["expected_outside_literal"] = C.ALPHA * ga1["n_checks"]
    ga1["passes"] = not ga1["outside_bonferroni"] and ga1["n_checks"] == K
    # G-A2
    ga2 = {}
    for case in D.CASES:
        r = size[D.size_cell(("ma", -0.8), 100, case)]["asy"]["mzt"]["rate"]
        ga2[case] = {"mzt_np_asy": r, "np2000_mzalpha": NP2000[case], "diff": r - NP2000[case],
                     "within": abs(r - NP2000[case]) <= GA2_TOL}
    # Clasificacion (lectura 10)
    def s(err, n, case, p, kind="iid"):
        return size[D.size_cell(err, n, case)][kind][p]["rate"]
    termsA, termsB = [], []
    for n in (100, 200):
        for case in D.CASES:
            g, m = s(("ma", -0.8), n, case, "gls_t0"), s(("ma", -0.8), n, case, "mzt", "asy")
            termsA.append({"psi": -0.8, "n": n, "case": case, "gls_t0": g, "mzt_asy": m,
                           "ok": g <= m + A_MZT_PP_08 and g <= A_MAX_08})
            g5, m5 = s(("ma", -0.5), n, case, "gls_t0"), s(("ma", -0.5), n, case, "mzt", "asy")
            termsA.append({"psi": -0.5, "n": n, "case": case, "gls_t0": g5, "mzt_asy": m5, "ok": g5 <= m5 + A_MZT_PP_05})
    for case in D.CASES:
        g, m = s(("ma", -0.8), 200, case, "gls_t0"), s(("ma", -0.8), 200, case, "mzt", "asy")
        termsB.append({"psi": -0.8, "n": 200, "case": case, "gls_t0": g, "mzt_asy": m,
                       "ge_abs": g >= B_ABS, "ge_mzt": g >= m + B_MZT_PP, "ok": g >= B_ABS or g >= m + B_MZT_PP})
    isA, isB = all(t["ok"] for t in termsA), any(t["ok"] for t in termsB)
    outcome = "A" if isA else ("B" if isB else "Intermedio")
    pred = {"psi08": {"value": s(("ma", -0.8), 200, "c", "gls_t0"), "rule": "> %g" % PRED["psi08_gt"]},
            "psi05": {"value": s(("ma", -0.5), 200, "c", "gls_t0"), "rule": "en [%g, %g]" % (PRED["psi05_lo"], PRED["psi05_hi"])},
            "phi05": {"value": s(("ar", 0.5), 200, "c", "gls_t0"), "rule": "< %g" % PRED["phi05_lt"]},
            "outcome": {"value": outcome, "rule": "B"}}
    pred["psi08"]["holds"] = pred["psi08"]["value"] > PRED["psi08_gt"]
    pred["psi05"]["holds"] = PRED["psi05_lo"] <= pred["psi05"]["value"] <= PRED["psi05_hi"]
    pred["phi05"]["holds"] = pred["phi05"]["value"] < PRED["phi05_lt"]
    pred["outcome"]["holds"] = outcome == "B"
    bartlett = {P.err_tag(e): {"err": list(e), "omega2": P.omega2(e),
                               "factor_by_B": {str(b): P.bartlett_factor(e, b) for b in BARTLETT_B_GRID}} for e in P.ERRORS}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"errors": [list(e) for e in P.ERRORS], "n": list(D.A_N), "cases": list(D.CASES), "N_size": D.N_SIZE,
                      "N_power": D.N_POW, "N_cal": D.N_CAL, "procs": list(P.PROCS), "theta_final": P.THETA_FINAL,
                      "cbar_power": D.CBAR_POW, "rho_extra": list(D.POW_RHO_EXTRA),
                      "asy": {"np2001": U.NP_CV5, "dfgls_published": DFGLS_PUB, "adf_pp": "p-valor MacKinnon < 0.05"},
                      "limit": "cuantil 5 % de n = 20 000 (B9.4, familia 104), usado por A10",
                      "calibration_source": {"%d|%s" % k: v["source"] for k, v in rules.items()},
                      "N_cal_finite": {"%d|%s" % k: v["N_cal"] for k, v in rules.items()},
                      "iid_quantiles": {"%d|%s" % k: dict(v["qs"], **{"%s (cuantil)" % p: q for p, q in v["q_rm"].items()})
                                        for k, v in rules.items()}},
           "exact_region_20000": region95, "exact_region_5000": region_pow, "size": size, "power": power,
           "bartlett_population": bartlett, "G_A1": ga1, "G_A2": ga2, "gate_stop": not ga1["passes"],
           "classification": {"A_terms": termsA, "B_terms": termsB, "A": isA, "B": isB, "outcome": outcome},
           "prediction": pred, "compute_elapsed_sec": elapsed, "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("G-A1 pasa:", ga1["passes"], "fuera Bonferroni:", ga1["outside_bonferroni"], "fuera literal:", len(ga1["outside_literal"]))
    print("G-A2:", ga2)
    print("desenlace:", outcome, {k: (round(v["value"], 4) if isinstance(v["value"], float) else v["value"], v["holds"])
                                   for k, v in pred.items()})
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    a = ap.parse_args()
    if a.probe:
        return probe(a.cores)
    if a.run:
        rc = run(a.cores, a.max_seconds)
        if rc:
            return rc
    if a.analyze:
        return analyze()
    return 0


if __name__ == "__main__":
    sys.exit(main())
