"""
Auditoria A10 - B10.1: decision limpia del theta primario (DURA).

RM-GLS con theta in {0, 0.02, 0.05, 0.1, 0.2}, casos demeaned y con tendencia;
comparadores en la misma tabla: RM (anclado en la media), MSB-HAC, variante (b)
de B9.3, ADF-sim, DF-GLS-sim, MZt-GLS-sim, MSB-GLS-sim.

  - n in {200, 500, 1000}; dos muestras independientes de N = 50 000 por
    (caso, n) (familia 111, celdas a1_<caso>_n<n>_s<k>, hijos distintos por caso y
    por muestra); en cada celda solo se calcula su caso.
  - Calibracion de N_cal = 500 000 en los caminos de produccion
    (audit10_engine.calibration; Paso 0 frente a A9 y control de produccion).
  - A1': |tamano agregado (N = 100 000) - 0.05| <= 0.0025 en las seis celdas.
  - A2 y P(theta): reutilizados de b92_theta_audit9.json (no se recalculan).
  - Regla: protocol_audit10.md, REGLA B10.1 y lecturas 2-8.

Modos:
  --probe    sonda de tiempo por configuracion a n = 1000 (compuerta de 20 min)
  --run      calibraciones y las 12 celdas (reanudable)
  --analyze  tablas, A1', regla y cierre de la anomalia de A9
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

import audit10_common as C                                         # noqa: E402
import audit10_design as D                                         # noqa: E402
import audit10_engine as E10                                       # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402

FAM = C.FAMILY["B10.1"]
CKPT = os.path.join(C.CKPT_ROOT, "audit10_b101")
OUT = os.path.join(C.RESULTS, "b101_theta_audit10.json")
OUT_PROBE = os.path.join(C.RESULTS, "b101_timing_audit10.json")
A9_THETA = "b92_theta_audit9.json"
TOL = 0.0025
GATE_MINUTES = 20.0
PROBE_N = 1000
PROBE_PER_CORE = 20
LOW_MARK = 0.047
THETA_PROCS = tuple(E.tname(t) for t in E.THETAS)
COMPARATORS = ("rm_t0.1", "msbhac", "glsb_t0", "adf", "dfgls", "mzt", "msb")
PROCS = THETA_PROCS + COMPARATORS
TIE_PP = 1.0


def cell_flags(case):
    return {"cases": (D.CASE_DET[case],), "adfpp": True, "kpss": False, "za": False, "pt": False}


# ---------------------------------------------------------------------------
# Sonda de tiempo (lectura 4)
# ---------------------------------------------------------------------------
def _probe_worker(seed, n, k):
    rng = np.random.default_rng(seed)
    ys = [np.concatenate([[0.0], np.cumsum(rng.standard_normal(n))]) for _ in range(k)]
    t = {}

    def clock(name, f):
        f(ys[0])                        # calentamiento: importaciones y compilacion fuera del cronometro
        t0 = time.perf_counter()
        for y in ys:
            f(y)
        t[name] = (time.perf_counter() - t0) / k
    clock("s2", hac_sigma_sq)
    s2 = [hac_sigma_sq(y) for y in ys]
    for det in E.CASES:
        for th in E.THETAS:
            clock("%s|%s" % (det, E.tname(th)), lambda y: E.rmgls(y, n, th, s2[0], det))
        clock("%s|rm_t0.1" % det, lambda y: E.rm_mean(y, n, E.THETA_A8, s2[0], det))
        clock("%s|msbhac" % det, lambda y: E.rm_mean(y, n, E.THETA_A8, s2[0], det, zero=True))
        clock("%s|np" % det, lambda y: U.np_statistics(y, det))
        npr = U.np_statistics(ys[0], det)
        clock("%s|glsb_t0" % det, lambda y: E.rmgls(y, n, 0.0, npr["s2_ar"], det))
        clock("%s|dfgls" % det, lambda y: U.dfgls_maic(y, det, npr["k"]))
        clock("%s|adf" % det, lambda y: U.adf_aic(y, det))
    return t


def probe(a):
    E.warm(a.cores)
    res = Parallel(n_jobs=a.cores, backend="loky")(delayed(_probe_worker)(1000 + j, PROBE_N, PROBE_PER_CORE)
                                                     for j in range(a.cores))
    comp = {k: float(np.mean([r[k] for r in res])) for k in res[0]}
    minutes = {}
    for det in E.CASES:
        for p in PROCS:
            if p in THETA_PROCS or p in ("rm_t0.1", "msbhac"):
                sec = comp["s2"] + comp["%s|%s" % (det, p)]
            elif p == "glsb_t0":
                sec = comp["%s|np" % det] + comp["%s|glsb_t0" % det]
            elif p in ("mzt", "msb"):
                sec = comp["%s|np" % det]
            elif p == "dfgls":
                sec = comp["%s|np" % det] + comp["%s|dfgls" % det]
            else:
                sec = comp["%s|adf" % det]
            minutes["%s|%s" % (det, p)] = sec * D.N_CAL / a.cores / 60.0
    worst = max(minutes, key=minutes.get)
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "n": PROBE_N, "cores": a.cores,
           "paths_per_core": PROBE_PER_CORE, "N_cal": D.N_CAL, "gate_minutes": GATE_MINUTES,
           "rule": "protocol_audit10.md, lectura 4: configuracion = (procedimiento, caso); minutos = coste por "
                   "camino de sus componentes x N_cal / nucleos",
           "component_sec_per_path": comp, "projected_minutes_per_configuration": minutes,
           "worst_configuration": worst, "worst_minutes": minutes[worst],
           "projected_minutes_all_configurations_n1000": (comp["s2"] + sum(
               comp["%s|%s" % (d, p)] for d in E.CASES for p in THETA_PROCS + ("rm_t0.1", "msbhac", "np", "glsb_t0",
                                                                                "dfgls", "adf"))) * D.N_CAL / a.cores / 60.0,
           "within_gate": bool(minutes[worst] <= GATE_MINUTES),
           "warmup": "cada componente se llama una vez antes de cronometrar (la primera sonda, sin calentamiento, "
                     "queda en b101_timing_coldstart_audit10.json)",
           "attribution_note": ("sigma_hat HAC se imputa a cada configuracion basada en HAC; Ng-Perron (MAIC) a "
                                "DF-GLS, MZt, MSB y la variante (b)")}
    C.write_result(OUT_PROBE, out, __file__)
    print("peor configuracion %s: %.1f min (compuerta %.0f); todas a n = 1000: %.1f min" % (
        worst, minutes[worst], GATE_MINUTES, out["projected_minutes_all_configurations_n1000"]))
    return 0 if out["within_gate"] else 3


# ---------------------------------------------------------------------------
# Ejecucion
# ---------------------------------------------------------------------------
def jobs():
    out = []
    for case in D.CASES:
        for n in D.A1_N:
            for k in D.A1_SAMPLES:
                out.append(("a1_%s_n%d_s%d" % (case, n, k), n,
                            lambda i, cs=case, nn=n, kk=k: D.a1_path(cs, nn, kk, i), cell_flags(case)))
    return out


def run(a):
    pr = C.read_json(os.path.basename(OUT_PROBE))
    if not pr["within_gate"]:
        print("la sonda supera la compuerta de %.0f min: no se lanza la rejilla" % GATE_MINUTES)
        return 3
    resume = "python experiments/audit10_b101_theta.py --run --cores %d" % a.cores
    t_block = time.time()
    E.warm(a.cores)
    try:
        for n in D.A1_N:
            t0 = time.time()
            _, _, info = E10.calibration(n, a.cores, t_block, a.max_seconds, resume, log=lambda *x: print(*x, flush=True))
            print("[CAL] n=%d lista: %.1f min (nuevos), Paso 0 %s" % (n, (time.time() - t0) / 60, info), flush=True)
        for tag, n, fn, fl in jobs():
            print("\n[CELDA] %s" % tag, flush=True)
            C.run_cell(tag, D.N_A1, E.make_batch_fn(fn, n, a.cores, **fl), CKPT, a.cores, t_block, a.max_seconds,
                       resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


# ---------------------------------------------------------------------------
# Analisis
# ---------------------------------------------------------------------------
def a2_and_p():
    b = C.read_json(A9_THETA)
    r = b["theta_rule"]
    return {"source": "experiments/results/" + A9_THETA,
            "source_sha256": C.sha256_file(os.path.join(C.RESULTS, A9_THETA)),
            "P": r["P"], "P_path": "theta_rule.P", "A2_ok": r["A2_ok"], "A2_path": "theta_rule.A2_ok",
            "A2_mean_delta": r["A2_mean_delta"], "A2_best_mean": r["A2_best_mean"],
            "A2_threshold_pp": r["A2_threshold_pp"], "P_c": r["P_c"]}


def decide(a1_ok, reuse):
    P, a2 = reuse["P"], reuse["A2_ok"]
    adm = [t for t in THETA_PROCS if a1_ok[t] and a2[t]]
    winner, tie, top = None, [], None
    if adm:
        top = max(adm, key=lambda t: P[t])
        tie = [t for t in adm if P[t] > P[top] - TIE_PP / 100]
        winner = max(tie, key=lambda t: E.THETAS[THETA_PROCS.index(t)])
    return {"admissible": adm, "top_P": top, "tie_group": tie, "tie_pp": TIE_PP, "winner": winner,
            "winner_theta": None if winner is None else E.THETAS[THETA_PROCS.index(winner)]}


def big_quantiles():
    """Cuantil 5% de la muestra de n = 20 000 de B9.4 (familia 104) por (caso, theta)."""
    import audit9_b94_finite_sample as B94
    import audit9_design as D9
    big, _ = C.load_rows(B94.CKPT, "big_n%d" % D9.N_BIG_N, D9.N_BIG)
    JB = {c: i for i, c in enumerate(B94.BIG_COLS)}
    return {(det, t): float(np.quantile(big[:, JB["%s|%s" % (det, t)]], C.ALPHA)) for det in E.CASES for t in THETA_PROCS}


def analyze(a):
    t0 = time.time()
    qbig = big_quantiles()
    region = C.exact_region(2 * D.N_A1)
    region1 = C.exact_region(D.N_A1)
    cal, ctrl, rej = {}, {}, {}
    for n in D.A1_N:
        rows, cols, info = E10.load_cal(n)
        ctrl[str(n)] = E10.production_control(n, rows, cols, a.cores)
        cal[str(n)] = dict(info, N_cal=int(rows.shape[0]),
                           nan_by_column={c: int(np.isnan(rows[:, i]).sum()) for i, c in enumerate(cols)})
        for det in E.CASES:
            rej[(n, det)] = E.rejector(rows, cols, det)
        del rows
    cells, a1 = {}, {p: {} for p in PROCS}
    elapsed = {}
    for case in D.CASES:
        det = D.CASE_DET[case]
        cols = E.columns(**cell_flags(case))
        for n in D.A1_N:
            f, qs = rej[(n, det)]
            per, big, pub = {}, {t: [] for t in THETA_PROCS}, []
            J = E.index(cols)
            for k in D.A1_SAMPLES:
                tag = "a1_%s_n%d_s%d" % (case, n, k)
                rows, el = C.load_rows(CKPT, tag, D.N_A1)
                elapsed[tag] = el
                per[k] = {p: f(rows, cols, p) for p in PROCS}
                for t in THETA_PROCS:
                    big[t].append(rows[:, J["%s|%s" % (det, t)]] < qbig[(det, t)])
                pub.append(E.reject_published(rows, cols, det, "msb"))
            key = "%s|%d" % (case, n)
            rec = {}
            for p in PROCS:
                pooled = C.rate_pooled([per[k][p] for k in D.A1_SAMPLES], region)
                pooled["abs_dev_from_alpha"] = abs(pooled["rate"] - C.ALPHA)
                pooled["within_tolerance"] = bool(pooled["abs_dev_from_alpha"] <= TOL + 1e-15)
                rec[p] = {"sample_%d" % k: C.rate_record(per[k][p], region1) for k in D.A1_SAMPLES}
                rec[p]["pooled"] = pooled
                rec[p]["samples_diff"] = C.diff_independent(rec[p]["sample_1"], rec[p]["sample_2"])
                a1[p][key] = pooled
            cells[key] = {"case": case, "n": n, "sim_thresholds": qs, "rates": rec,
                          "size_with_cv_n20000": {t: dict(C.rate_pooled(big[t], region), cv_n20000=qbig[(det, t)])
                                                  for t in THETA_PROCS},
                          "msb_published_cv": dict(C.rate_pooled(pub, region), cv=E.MSB_CV5_PUBLISHED[det])}
    a1_ok = {p: all(v["within_tolerance"] for v in a1[p].values()) for p in PROCS}
    reuse = a2_and_p()
    dec = decide(a1_ok, reuse)
    # cierre de la anomalia de A9: celda tendencia n = 200
    ct200 = cells["ct|200"]["rates"]
    below = [p for p in PROCS if ct200[p]["pooled"]["rate"] < LOW_MARK]
    a9 = C.read_json(A9_THETA)
    a9_ct200 = {p: a9["gaussian_size"]["ct|200"][p]["rate"] for p in PROCS if p in a9["gaussian_size"]["ct|200"]}
    anomaly = {"cell": "ct|200", "mark": LOW_MARK,
               "rates": {p: {"pooled": ct200[p]["pooled"]["rate"], "sample_1": ct200[p]["sample_1"]["rate"],
                             "sample_2": ct200[p]["sample_2"]["rate"],
                             "wilson": [ct200[p]["pooled"]["wilson_lower"], ct200[p]["pooled"]["wilson_upper"]]}
                         for p in PROCS},
               "below_mark": below, "count_below": len(below), "procedures": len(PROCS),
               "pattern_repeats": bool(len(below) >= 7),
               "a9_rates_same_cell": a9_ct200,
               "a9_count_below": sum(1 for v in a9_ct200.values() if v < LOW_MARK)}
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"thetas": list(E.THETAS), "comparators": list(COMPARATORS), "n": list(D.A1_N),
                      "N_per_sample": D.N_A1, "samples": len(D.A1_SAMPLES), "N_pooled": 2 * D.N_A1,
                      "N_cal": D.N_CAL, "cal_seed": E.CAL_SEED, "tolerance": TOL,
                      "rule": "protocol_audit10.md, REGLA B10.1 y lecturas 2-8"},
           "exact_region_100000": region, "exact_region_50000": region1,
           "calibration": cal, "production_control": ctrl,
           "timing_probe": C.read_json(os.path.basename(OUT_PROBE)),
           "cells": cells, "A1prime": a1, "A1prime_ok": a1_ok, "reused_from_a9": reuse, "decision": dec,
           "primary_theta": dec["winner_theta"],
           "gate_stop": dec["winner"] is None and not any(a1_ok[t] for t in THETA_PROCS),
           "anomaly_ct200": anomaly, "cell_elapsed_sec": elapsed,
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("A1'", a1_ok)
    print("P", {k: round(v, 4) for k, v in reuse["P"].items()}, "A2", reuse["A2_ok"])
    print("decision", dec)
    print("ct|200 bajo %.3f: %d de %d" % (LOW_MARK, len(below), len(PROCS)))
    print("control", ctrl)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.probe:
        return probe(a)
    if a.analyze:
        return analyze(a)
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
