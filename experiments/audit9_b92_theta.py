"""
Auditoria A9 - B9.2: escalera de theta (incluido theta = 0) para RM-GLS, calibracion hac (CARO, 12 h).

1. Potencia local asintotica: n = 2000, c in {0, ..., 30} y 13.5, N = 20000 por c,
   familia 102, casos demeaned y con tendencia (caminos independientes por caso,
   como en B4). Umbrales en la muestra de calibracion de produccion en n = 2000
   (semilla 42, N_cal = 50000). Envolvente recalculada: P_T de ERS con cbar = -c,
   w2 = s2_AR (MAIC) del caso, umbral = cuantil 5% de P_T(cbar) en la calibracion.
   Comparadores DF-GLS, MSB-GLS, MZt-GLS (sim); la variante (b) de B9.3 y MSB-GLS
   con su valor asintotico se leen de las mismas filas. c = 0 (lp_<caso>_test0,
   N = 5000) se reporta como informacion.
2. Tamano gaussiano: N = 20000 trayectorias independientes por n in {60, ..., 5000}
   (familia 102; las mismas para los dos casos).
3. Las 22 celdas de mala especificacion de A8 (colas pesadas publicadas y GARCH de
   A7), ambos casos, con Delta frente a la referencia del punto 2. Paso 0 frente a
   los checkpoints de A8 (B2 en demeaned; B5 ct_garch en tendencia).
4. DGP 1 y caso con tendencia a tamano igualado: filas de B9.1.
5. DGP 3 (15 celdas de B5, tamano con la nula verdadera).

Regla del theta primario (DURA): protocolo_audit9.md, seccion REGLA B9.2.

Modos: --budget (sonda y proyeccion; se detiene si excede 12 h), --run, --analyze.
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

import audit9_common as C                                          # noqa: E402
import audit9_design as D                                          # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_calibrate as CAL                                     # noqa: E402
import audit9_b91_equalized as B91                                 # noqa: E402

FAM = C.FAMILY["B9.2"]
CKPT = os.path.join(C.CKPT_ROOT, "audit9_b92")
CKPT_A8_B2 = os.path.join(C.CKPT_ROOT, "audit8_b2")
CKPT_A8_B5 = os.path.join(C.CKPT_ROOT, "audit8_b5")
OUT = os.path.join(C.RESULTS, "b92_theta_audit9.json")
OUT_BUDGET = os.path.join(C.RESULTS, "b92_budget_audit9.json")
BUDGET_HOURS = 12.0
CAL_N_EXTRA = (60, 100, 150, 2000, 5000)
P_C = (5.0, 10.0, 15.0)
GAP_C = (5.0, 10.0, 20.0)
A1_N = (200, 500, 1000)
A2_PP = 0.30
TIE_PP = 1.0
DGP3_COST = "dgp3_r4_n200"
PASO0 = 50
LP_FLAGS = {"adfpp": False, "pt": True}
SIZE_FLAGS = {"cases": E.CASES, "adfpp": True}
LP_PROCS = tuple(E.tname(t) for t in E.THETAS) + ("glsb_t0", "dfgls", "mzt", "msb")


def dgp3_cells():
    return [k for k in D.b5()[1] if k.startswith("dgp3_")]


def lp_jobs():
    out = []
    for case in D.LP_CASES:
        det = D.CASE_DET[case]
        for c in D.C_GRID:
            out.append(("lp_%s_c%s" % (case, D.cname(c)), D.N_POWER,
                        lambda i, cs=case, cc=c: D.lp_path(cs, cc, i), D.N_LP, dict(LP_FLAGS, cases=(det,))))
        out.append(("lp_%s_test0" % case, D.N_TEST0, lambda i, cs=case: D.test0_path(cs, i), D.N_LP,
                    dict(LP_FLAGS, cases=(det,))))
    return out


def size_jobs():
    out = [("indep_n%d" % n, D.N_INDEP, lambda i, nn=n: D.indep_path(nn, i), n, SIZE_FLAGS) for n in D.N_ALL]
    for k, s in D.misspec_cells().items():
        out.append((k, D.N_SIM, lambda i, kk=k: D.misspec_path(kk, i), s["n"], SIZE_FLAGS))
    for k in dgp3_cells():
        out.append((k, D.N_SIM, lambda i, kk=k: D.b5_path(kk, i), D.b5_spec(k)["n"], B91.flags_for(k)))
    return out


def all_jobs():
    return lp_jobs() + size_jobs()


# ---------------------------------------------------------------------------
# Presupuesto
# ---------------------------------------------------------------------------
def probe_cal(n, cores):
    rng = np.random.default_rng(12345)
    blocks = [rng.standard_normal((1, n)) for _ in range(cores)]
    t0 = time.time()
    Parallel(n_jobs=cores, backend="loky")(delayed(E._cal_rows)(b, n, E.cal_flags(n)) for b in blocks)
    return (time.time() - t0) / cores


def budget(a):
    E.warm(a.cores)
    t_block = time.time()
    proj, per = 0.0, {}
    for n in CAL_N_EXTRA:
        if os.path.exists(os.path.join(CAL.CKPT, "cal_n%d.npz" % n)):
            per["cal_n%d" % n] = 0.0
            continue
        sps = probe_cal(n, a.cores)
        per["cal_n%d" % n] = sps * E.N_CAL
    # un camino por tipo de celda (la sonda de 14 series queda en disco y se reutiliza)
    for tag, reps, fn, n, fl in all_jobs():
        _, info = C.C8.C7.run_cell_batched(tag, reps, E.make_batch_fn(fn, n, a.cores, **fl), CKPT, a.cores, t_block,
                                           1e12, "", log=lambda *x: None, probe_only=True)
        per[tag] = info["probe_sec_per_series"] * reps
    proj = sum(per.values())
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "budget_hours": BUDGET_HOURS, "cores": a.cores,
           "rule": "sonda de 14 series en cada celda y de 14 caminos de calibracion por n; proyeccion = suma de sondas x replicas",
           "per_cell_projected_sec": per, "projected_total_hours": proj / 3600,
           "within_budget": bool(proj / 3600 <= BUDGET_HOURS)}
    C.write_result(OUT_BUDGET, out, __file__)
    print("B9.2 proyeccion %.2f h (presupuesto %.0f h): %s" % (proj / 3600, BUDGET_HOURS, out["within_budget"]))
    return 0 if out["within_budget"] else 3


def run(a):
    b = C.read_json(os.path.basename(OUT_BUDGET))
    if not b["within_budget"]:
        print("presupuesto excedido: no se lanza B9.2")
        return 3
    resume = "python experiments/audit9_b92_theta.py --run --cores %d" % a.cores
    t_block = time.time()
    E.warm(a.cores)
    try:
        for n in CAL_N_EXTRA:
            E.calibration(n, a.cores, CAL.CKPT, t_block, a.max_seconds, resume)
            print("[CAL] n=%d lista" % n, flush=True)
        for tag, reps, fn, n, fl in all_jobs():
            print("\n[CELDA] %s" % tag, flush=True)
            C.run_cell(tag, reps, E.make_batch_fn(fn, n, a.cores, **fl), CKPT, a.cores, t_block, a.max_seconds, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


# ---------------------------------------------------------------------------
# Analisis
# ---------------------------------------------------------------------------
def local_power(rejectors):
    rows_cal, cols_cal = CAL.load(D.N_LP)
    Jc = E.index(cols_cal)
    res = {}
    region = C.exact_region(D.N_TEST0)
    a8 = C.read_json("b4_local_power_audit8.json")
    for case in D.LP_CASES:
        det = D.CASE_DET[case]
        rej, qs = rejectors[(D.N_LP, det)]
        qenv = {c: float(np.nanquantile(rows_cal[:, Jc["%s|pt_%g" % (det, c)]], C.ALPHA)) for c in D.C_GRID if c > 0}
        cols = E.columns(cases=(det,), **LP_FLAGS)
        J = E.index(cols)
        power, rejs = {}, {}
        for c in sorted(D.C_GRID):
            rows, _ = C.load_rows(CKPT, "lp_%s_c%s" % (case, D.cname(c)), D.N_POWER)
            r = {p: rej(rows, cols, p) for p in LP_PROCS}
            r["msb_asy"] = E.reject_asy(rows, cols, det, "msb")
            rejs[str(c)] = r
            power[str(c)] = {p: float(v.mean()) for p, v in r.items()}
            power[str(c)]["envelope"] = C.ALPHA if c == 0 else float(
                (rows[:, J["%s|pt_%g" % (det, c)]] < qenv[c]).mean())
            power[str(c)]["nan"] = {p: int(np.isnan(rows[:, J["%s|%s" % (det, p)]]).sum()) for p in LP_PROCS}
        t0rows, _ = C.load_rows(CKPT, "lp_%s_test0" % case, D.N_TEST0)
        gate = {p: C.rate_record(rej(t0rows, cols, p), region) for p in LP_PROCS}
        gaps = {p: {str(c): power[str(c)]["envelope"] - power[str(c)][p] for c in GAP_C}
                for p in LP_PROCS + ("msb_asy",)}
        env_a8 = {str(c): power[str(c)]["envelope"] - a8["cases"][case]["power"][str(c)]["envelope"]
                  for c in D.C_GRID}
        res[case] = {"power": power, "gap_to_envelope": gaps, "c0_test_informative": gate,
                     "sim_thresholds": qs, "envelope_thresholds": {str(k): v for k, v in qenv.items()},
                     "envelope_minus_a8": env_a8,
                     "envelope_max_abs_diff_vs_a8": max(abs(v) for v in env_a8.values())}
    return res


def size_block(rejectors):
    region = C.exact_region(D.N_INDEP)
    region5 = C.exact_region(D.N_SIM)
    cols = E.columns(**SIZE_FLAGS)
    procs = tuple(E.tname(t) for t in E.THETAS) + ("glsb_t0", "rm_t0.1", "msbhac", "adf", "pp", "dfgls", "mzt", "msb")
    gauss, gauss_rej = {}, {}
    for n in D.N_ALL:
        rows, _ = C.load_rows(CKPT, "indep_n%d" % n, D.N_INDEP)
        for case in E.CASES:
            rej, _ = rejectors[(n, case)]
            r = {p: rej(rows, cols, p) for p in procs}
            for p in ("adf", "pp", "dfgls", "mzt", "msb"):
                r[p + "_asy"] = E.reject_asy(rows, cols, case, p)
            gauss_rej[(n, case)] = r
            gauss["%s|%d" % (case, n)] = {p: C.rate_record(v, region) for p, v in r.items()}
    mis, mis_rej, paso0 = {}, {}, {}
    for k, s in D.misspec_cells().items():
        n = s["n"]
        rows, _ = C.load_rows(CKPT, k, D.N_SIM)
        paso0[k] = paso0_misspec(k, s, rows, cols)
        for case in E.CASES:
            rej, _ = rejectors[(n, case)]
            r = {p: rej(rows, cols, p) for p in procs}
            for p in ("adf", "pp", "dfgls", "mzt", "msb"):
                r[p + "_asy"] = E.reject_asy(rows, cols, case, p)
            mis_rej[(k, case)] = r
            g = gauss["%s|%d" % (case, n)]
            rr = {p: C.rate_record(v, region5) for p, v in r.items()}
            mis["%s|%s" % (case, k)] = {"cell": k, "case": case, "n": n, "kind": s["kind"], "rates": rr,
                                        "delta_vs_independent": {p: C.diff_independent(rr[p], g[p]) for p in rr}}
    return gauss, gauss_rej, mis, mis_rej, paso0, region, region5


def paso0_misspec(k, s, rows, cols):
    import audit8_b2_size as B2
    J = E.index(cols)
    ref = C.load_prefix(CKPT_A8_B2, k, PASO0)
    pairs = {"stat_rmgls": "c|gls_t0.1", "stat_R0_t0.1": "c|rm_t0.1", "stat_msbhac": "c|msbhac", "s2": "s2",
             "adf_stat": "c|adf", "pp_stat": "c|pp", "dfgls_stat": "c|dfgls", "dfgls_k": "c|k", "mzt": "c|mzt",
             "msb": "c|msb"}
    worst = {a: float(np.max(np.abs(ref[:, B2.IDX[a]] - rows[:PASO0, J[m]]))) for a, m in pairs.items()}
    out = {"reps": int(ref.shape[0]), "max_abs_diff_dm_by_column": worst}
    if s["kind"] == "garch":
        import audit8_b5_power as B5
        ref5 = C.load_prefix(CKPT_A8_B5, "ct_" + k, PASO0)
        worst_ct = {a: float(np.max(np.abs(ref5[:, B5.ICT[a]] - rows[:PASO0, J[m]])))
                    for a, m in B91.A8_COLS_CT.items()}
        out["max_abs_diff_ct_by_column"] = worst_ct
    out["max_abs_diff"] = max(list(worst.values()) + list(out.get("max_abs_diff_ct_by_column", {}).values()))
    return out


def theta_rule(lp, gauss, mis):
    thetas = [E.tname(t) for t in E.THETAS]
    P = {t: float(np.mean([lp["dm"]["power"][str(c)][t] for c in P_C])) for t in thetas}
    a1 = {t: {"%s|%d" % (case, n): gauss["%s|%d" % (case, n)][t] for case in E.CASES for n in A1_N} for t in thetas}
    a1_ok = {t: all(v["in_region"] for v in a1[t].values()) for t in thetas}
    garch = [v for v in mis.values() if v["kind"] == "garch" and v["n"] <= 500]
    mean_d = {t: C.mean_with_se([v["delta_vs_independent"][t] for v in garch]) for t in thetas}
    best = min(mean_d[t]["mean"] for t in thetas)
    a2_ok = {t: bool((mean_d[t]["mean"] - best) * 100 <= A2_PP + 1e-12) for t in thetas}
    # lecturas alternativas (solo se reportan)
    garch_dm = [v for v in garch if v["case"] == "c"]
    mean_dm = {t: C.mean_with_se([v["delta_vs_independent"][t] for v in garch_dm]) for t in thetas}
    best_dm = min(mean_dm[t]["mean"] for t in thetas)
    best_abs = min(abs(mean_d[t]["mean"]) for t in thetas)
    alt = {"only_demeaned": {t: bool((mean_dm[t]["mean"] - best_dm) * 100 <= A2_PP + 1e-12) for t in thetas},
           "abs_mean": {t: bool((abs(mean_d[t]["mean"]) - best_abs) * 100 <= A2_PP + 1e-12) for t in thetas},
           "mean_delta_only_demeaned": mean_dm}
    adm = [t for t in thetas if a1_ok[t] and a2_ok[t]]
    winner, tie = None, []
    if adm:
        top = max(adm, key=lambda t: P[t])
        tie = [t for t in adm if P[t] > P[top] - TIE_PP / 100]
        winner = max(tie, key=lambda t: E.THETAS[thetas.index(t)])

    def pick(ok):
        a = [t for t in thetas if a1_ok[t] and ok[t]]
        if not a:
            return None
        top = max(a, key=lambda t: P[t])
        return max([t for t in a if P[t] > P[top] - TIE_PP / 100], key=lambda t: E.THETAS[thetas.index(t)])
    alt["winner_only_demeaned"] = pick(alt["only_demeaned"])
    alt["winner_abs_mean"] = pick(alt["abs_mean"])
    return {"P": P, "P_c": list(P_C), "A1": a1, "A1_ok": a1_ok, "A1_region": C.exact_region(D.N_INDEP),
            "A2_cells": sorted({v["cell"] for v in garch}), "A2_cell_cases": len(garch),
            "A2_mean_delta": mean_d, "A2_best_mean": best, "A2_ok": a2_ok, "A2_threshold_pp": A2_PP,
            "admissible": adm, "tie_group": tie, "tie_pp": TIE_PP, "winner": winner,
            "winner_theta": None if winner is None else E.THETAS[thetas.index(winner)],
            "alternative_readings": alt}


def analyze(a):
    t0 = time.time()
    rejectors, thr = B91.rejectors_for(D.N_ALL, E.CASES)
    ctrl = {}
    for n in D.N_ALL:
        rows, cols = CAL.load(n)
        ctrl[str(n)] = E.production_control(n, rows, cols)
    lp = local_power(rejectors)
    gauss, _, mis, _, paso0_mis, region, region5 = size_block(rejectors)
    rule = theta_rule(lp, gauss, mis)
    # 4. DGP 1 y tendencia a tamano igualado (filas de B9.1) y 5. DGP 3
    a8 = C.read_json("b5_power_audit8.json")
    b91_cells = list(B91.cells())
    thetas = tuple(E.tname(t) for t in E.THETAS) + ("glsb_t0",)
    eq, _ = B91.analyze_cells(b91_cells, rejectors, C.exact_region(D.N_SIM), a8, extra_procs=thetas)
    eq = {k: {"n": v["n"], "case": v["case"], "rho": v.get("rho"),
              "rates": {p: v["rates_sim"][p] for p in thetas + ("dfgls", "mzt", "msb", "adf")},
              "rates_asy": v["rates_asy"],
              "mcnemar_vs_primary_a8": {p: v["mcnemar_primary_vs_sim"][p] for p in thetas if p != B91.PRIMARY}}
          for k, v in eq.items() if k.startswith(("dgp1_", "ct_power_"))}
    saved = B91.CKPT
    try:
        B91.CKPT = CKPT
        d3, _ = B91.analyze_cells(dgp3_cells(), rejectors, C.exact_region(D.N_SIM), a8, extra_procs=thetas)
    finally:
        B91.CKPT = saved
    d3 = {k: {"n": v["n"], "r": v.get("r"), "rates": v["rates_sim"], "rates_asy": v["rates_asy"], "paso0": v["paso0"]}
          for k, v in d3.items()}
    w = rule["winner"]
    cost = {t: d3[DGP3_COST]["rates"][t] for t in {w, E.tname(0.0)} if t is not None}
    worst_p0 = max([v["max_abs_diff"] for v in paso0_mis.values()] + [v["paso0"]["max_abs_diff"] for v in d3.values()])
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"thetas": list(E.THETAS), "N_power": D.N_POWER, "n_local": D.N_LP, "N_indep": D.N_INDEP,
                      "N_sim": D.N_SIM, "N_cal": E.N_CAL, "cal_seed": E.CAL_SEED, "c_grid": list(D.C_GRID),
                      "rule": "protocol_audit9.md, REGLA B9.2 y lecturas 7-10"},
           "exact_region_20000": region, "exact_region_5000": region5, "sim_thresholds": thr,
           "production_control": ctrl, "local_power": lp, "gaussian_size": gauss, "misspec": mis,
           "paso0_misspec": paso0_mis, "paso0_worst": worst_p0, "equalized_power": eq, "dgp3": d3,
           "dgp3_cost_r4_n200": cost, "theta_rule": rule,
           "primary_theta": rule["winner_theta"],
           "primary_final": None if w is None else ("RM-GLS, theta = %g" % rule["winner_theta"]),
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("P", {k: round(v, 4) for k, v in rule["P"].items()})
    print("A1", rule["A1_ok"], "\nA2", rule["A2_ok"], {k: round(v["mean"] * 100, 3) for k, v in rule["A2_mean_delta"].items()})
    print("admisibles", rule["admissible"], "empate", rule["tie_group"], "ganador", rule["winner"])
    print("Paso 0 peor", worst_p0)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    ap.add_argument("--budget", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.budget:
        return budget(a)
    if a.analyze:
        return analyze(a)
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
