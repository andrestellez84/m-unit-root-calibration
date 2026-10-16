"""
Auditoria A8 - B2: R = 0 frente a R = 0.5, y calibracion one frente a hac.

Una sola pasada por replica calcula todos los estadisticos sin bootstrap que usan
B2 y B3 (las columnas de B3 no se analizan aqui):
  RM (compute_statistic, sigma_hat HAC de los datos): R = 0 y R = 0.5 con
  theta = 0.1; R = 0 con theta in {0.02, 0.05, 0.2}; MSB-HAC (tau = 0); RM-GLS
  (theta = 0.1). ADF (AIC), PP, DF-GLS (MAIC y AIC publicado), MZt-GLS y MSB-GLS
  (MAIC), con estadistico y p-valor asintotico.

Celdas: gaussianas n in {60, 100, 150, 200, 500, 1000} con las trayectorias
publicadas (default_rng(0 + i)), gaussianas n in {2000, 5000} de la familia 92,
colas pesadas t(5), t(3) con las trayectorias publicadas y las 16 GARCH de A7.

Calibraciones:
  RM: los N_cal = 50000 caminos de build_null_cdf(seed = 42) (los de las tablas
  publicadas), iguales para R = 0 y R = 0.5 y para "one" y "hac". Se generan
  con el mismo flujo del generador que produccion y se evaluan con
  rm_core.path_statistic; control: igualdad bit a bit con
  _simulate_null_statistics para (R = 0.5, one) y (R = 0, hac) en cada n.
  Comparadores "sim": 50000 paseos gaussianos por n (familia 92), con la
  seleccion de retardos dentro del bucle; umbral = cuantil 5% (cola inferior).

Paso 0: (i) primeras 50 replicas de cada celda reutilizada: la serie del
pipeline frente a la del generador original, max|delta| = 0; el estadistico
R = 0.5 frente a compute_statistic; en GARCH, componentes y p-valores frente a
los checkpoints de A7. (ii) Reproduccion de las tasas publicadas (R = 0.5 one,
ADF, PP, DF-GLS AIC) en todas las celdas reutilizadas.

Salidas: experiments/results/b2_size_audit8.json (y checkpoints).
Uso:
  python experiments/audit8_b2_size.py --cores 14 --max-seconds 14400
  python experiments/audit8_b2_size.py --analyze
"""
import argparse
import glob
import json
import math
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
from stationarity_test.constants import DEFAULT_SCALING_EXPONENTS  # noqa: E402
from stationarity_test.rm_core import path_statistic, hac_sigma_sq  # noqa: E402
from stationarity_test.empirical_eigenvalues import (              # noqa: E402
    _simulate_null_statistics, cdf_from_null_stats)

OUT = os.path.join(C.RESULTS, "b2_size_audit8.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit8_b2")
FAM = C.FAMILY["B2"]
C1, C2 = DEFAULT_SCALING_EXPONENTS[1], DEFAULT_SCALING_EXPONENTS[2]
ALPHA = C.ALPHA
PASO0_REPS = 50
GATE_PP = 0.30
MCNEMAR_P = 0.01
COUNT_DIFF = 2
SIGN_P = 0.01
CV_N = (100, 200, 500, 1000, 2000, 5000)
B2B_GATE_N = (200, 500, 1000)

# variantes RM: nombre -> (R, theta, tau_mode, anchor)
RM_VARIANTS = {
    "R0_t0.1": (0.0, 0.1, "theta", "mean"),
    "R0.5_t0.1": (0.5, 0.1, "theta", "mean"),
    "R0_t0.02": (0.0, 0.02, "theta", "mean"),
    "R0_t0.05": (0.0, 0.05, "theta", "mean"),
    "R0_t0.2": (0.0, 0.2, "theta", "mean"),
    "msbhac": (0.0, 0.1, "zero", "mean"),
    "rmgls": (0.0, 0.1, "theta", "gls"),
}
# columnas de la muestra nula RM: (variante, modo de calibracion)
NULL_COLS = (("R0_t0.1", "one"), ("R0.5_t0.1", "one"), ("R0_t0.1", "hac"), ("R0.5_t0.1", "hac"),
             ("R0_t0.02", "hac"), ("R0_t0.05", "hac"), ("R0_t0.2", "hac"), ("msbhac", "hac"), ("rmgls", "hac"))
COMP = ("adf", "pp", "dfgls", "dfglsaic")
ROW_COLS = (["stat_" + v for v in RM_VARIANTS] + ["g1std_R0.5_t0.1", "g2std_R0.5_t0.1", "s2"]
            + ["%s_%s" % (c, k) for c in COMP for k in ("stat", "p")] + ["dfgls_k", "mzt", "msb"])
IDX = {c: i for i, c in enumerate(ROW_COLS)}
CAL_COLS = ("adf", "pp", "dfgls", "dfglsaic", "mzt", "msb")
CAL_IDX = {c: i for i, c in enumerate(CAL_COLS)}


def taus(theta, n, tau_mode):
    t1 = min(max(2, int(round(theta * n))), n // 2)
    t2 = t1
    return (0 if tau_mode == "zero" else t1), t2


def rm_stats(Y, s2, n):
    out = {}
    for name, (R, th, tm, an) in RM_VARIANTS.items():
        t1, t2 = taus(th, n, tm)
        out[name] = path_statistic(Y, n, t1, t2, R, s2, C1, C2, anchor=an, need_g2=(R != 0.0))
    return out


def replicate_row(cell, spec, i):
    Y = D.size_path(cell, spec, i)
    n = spec["n"]
    s2 = hac_sigma_sq(Y)
    rm = rm_stats(Y, s2, n)
    comp = U.comparator_row(Y, "c", with_dfgls_aic=True)
    row = [rm[v][0] for v in RM_VARIANTS] + [rm["R0.5_t0.1"][1], rm["R0.5_t0.1"][2], s2]
    row += [comp["%s_%s" % (c, k)] for c in COMP for k in ("stat", "p")]
    row += [comp["np_k"], comp["np_MZt"], comp["np_MSB"]]
    return [float(x) for x in row]


def cal_row(n, i):
    y = D.cal_path(n, i)
    comp = U.comparator_row(y, "c", with_dfgls_aic=True)
    return [float(comp["adf_stat"]), float(comp["pp_stat"]), float(comp["dfgls_stat"]),
            float(comp["dfglsaic_stat"]), float(comp["np_MZt"]), float(comp["np_MSB"])]


def _rows(kind, key, spec, idx):
    if kind == "cell":
        return [replicate_row(key, spec, i) for i in idx]
    return [cal_row(key, i) for i in idx]


def make_batch_fn(kind, key, spec, cores):
    def batch_fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(delayed(_rows)(kind, key, spec, p) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return batch_fn


# ---------------------------------------------------------------------------
# Calibracion RM (flujo de build_null_cdf, seed = 42)
# ---------------------------------------------------------------------------
def _null_chunk(n, block):
    out = np.empty((block.shape[0], len(NULL_COLS)))
    for j in range(block.shape[0]):
        Y = np.empty(n + 1, dtype=np.float64)
        Y[0] = 0.0
        np.cumsum(block[j], out=Y[1:])
        s2h = hac_sigma_sq(Y)
        for c, (v, mode) in enumerate(NULL_COLS):
            R, th, tm, an = RM_VARIANTS[v]
            t1, t2 = taus(th, n, tm)
            s2 = 1.0 if mode == "one" else s2h
            out[j, c] = path_statistic(Y, n, t1, t2, R, s2, C1, C2, anchor=an, need_g2=(R != 0.0))[0]
    return out


CHUNK_DOUBLES = 2500000


def rm_null(n, cores, n_cal=D.N_CAL):
    path = os.path.join(CKPT, "cal_rm_n%d.npz" % n)
    if os.path.exists(path):
        with np.load(path) as z:
            if bool(z["complete"]) and z["null"].shape == (n_cal, len(NULL_COLS)):
                return z["null"]
    chunk = max(1, min(2000, CHUNK_DOUBLES // n))
    rng = np.random.default_rng(D.CAL_SEED_PUBLISHED)

    def blocks():
        done = 0
        while done < n_cal:
            k = min(chunk, n_cal - done)
            # standard_normal((k, n)) consume el flujo en el mismo orden que k llamadas de tamano n
            yield rng.standard_normal((k, n))
            done += k
    parts = Parallel(n_jobs=cores, backend="loky", pre_dispatch="2*n_jobs")(
        delayed(_null_chunk)(n, b) for b in blocks())
    null = np.vstack(parts)
    os.makedirs(CKPT, exist_ok=True)
    tmp = path + ".tmp.npz"
    np.savez(tmp, null=null, cols=np.array(["%s|%s" % c for c in NULL_COLS]), complete=True)
    os.replace(tmp, path)
    return null


def calibrator_control(n, null):
    """Igualdad bit a bit con produccion para dos columnas."""
    ref_pub = _simulate_null_statistics((0.1, 0.1), 0.5, n, D.N_CAL, D.CAL_SEED_PUBLISHED)
    ref_hac = _simulate_null_statistics((0.1, 0.1), 0.0, n, D.N_CAL, D.CAL_SEED_PUBLISHED, cal_sigma="hac")
    c_pub = NULL_COLS.index(("R0.5_t0.1", "one"))
    c_hac = NULL_COLS.index(("R0_t0.1", "hac"))
    return {"R0.5_one_max_abs_diff": float(np.max(np.abs(null[:, c_pub] - ref_pub))),
            "R0_hac_max_abs_diff": float(np.max(np.abs(null[:, c_hac] - ref_hac)))}


# ---------------------------------------------------------------------------
# Paso 0
# ---------------------------------------------------------------------------
def paso0_cell(cell, spec):
    from stationarity_test.statistic import compute_statistic
    worst_y, worst_stat = 0.0, 0.0
    for i in range(PASO0_REPS):
        Y = D.size_path(cell, spec, i)
        if spec["kind"] == "gauss":
            from power_comparison import generate_ar1
            Z = generate_ar1(n=spec["n"], rho=1.0, rng=np.random.default_rng(0 + i))
        elif spec["kind"] == "heavy":
            from size_robustness_heavy_tails import DISTRIBUTIONS, generate_rw_heavy
            p = DISTRIBUTIONS[spec["dist"]]
            Z = generate_rw_heavy(spec["n"], p["df"], p["scale"],
                                  np.random.default_rng(900000 + spec["n"] * 100 + p["df"] * 10 + i))
        else:
            import audit7_garch_size as G
            Z = G.generate(spec["key"], spec["n"], G.cell_seed_base(spec["key"], spec["n"]), i)[0]
        worst_y = max(worst_y, float(np.max(np.abs(Y - Z))))
        s = rm_stats(Y, hac_sigma_sq(Y), spec["n"])["R0.5_t0.1"][0]
        worst_stat = max(worst_stat, abs(s - compute_statistic(Y, (0.1, 0.1), 0.5)["statistic"]))
    return {"reps": PASO0_REPS, "max_abs_diff_series": worst_y, "max_abs_diff_stat_R05_vs_compute_statistic": worst_stat}


def a7_garch_rows(key, n):
    import audit7_garch_size as G
    d = G.CKPT if key == "base" else (G.CKPT_EXT_LARGE if n in G.N_GRID_LARGE else G.CKPT_EXT)
    return np.asarray(G.checkpoint_rows(d, key, n, PASO0_REPS), dtype=float), G.COLUMNS


def paso0_garch_components(cell, spec, rows):
    ref, cols = a7_garch_rows(spec["key"], spec["n"])
    mine = np.column_stack([rows[:PASO0_REPS, IDX["g1std_R0.5_t0.1"]], rows[:PASO0_REPS, IDX["g2std_R0.5_t0.1"]],
                            rows[:PASO0_REPS, IDX["adf_p"]], rows[:PASO0_REPS, IDX["pp_p"]],
                            rows[:PASO0_REPS, IDX["dfglsaic_p"]]])
    theirs = np.column_stack([ref[:, cols.index(c)] for c in ("g1_std", "g2_std", "p_adf", "p_pp", "p_dfgls")])
    return float(np.max(np.abs(mine - theirs)))


# ---------------------------------------------------------------------------
# Ejecucion
# ---------------------------------------------------------------------------
def cell_order():
    cells = D.size_cells()
    return sorted(cells.items(), key=lambda kv: (kv[1]["n"], kv[0]))


def run(a):
    resume = "python experiments/audit8_b2_size.py --cores %d --max-seconds %.0f" % (a.cores, a.max_seconds)
    t_block = time.time()
    Parallel(n_jobs=a.cores, backend="loky")(delayed(len)([k]) for k in range(a.cores))
    status = {"calibration_rm": {}, "calibration_sim": {}, "cells": {}}
    for n in D.N_ALL:
        t0 = time.time()
        null = rm_null(n, a.cores)
        status["calibration_rm"][str(n)] = round(time.time() - t0, 1)
        print("[CAL RM] n=%d  %.1f s" % (n, time.time() - t0), flush=True)
    for n in D.N_ALL:
        tag = "cal_dm_n%d" % n
        print("\n[CAL SIM] %s" % tag, flush=True)
        try:
            rows, info = C.run_cell(tag, D.N_CAL, make_batch_fn("cal", n, None, a.cores), CKPT, a.cores,
                                    t_block, a.max_seconds, resume)
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc, flush=True)
            return 2
        status["calibration_sim"][tag] = info["elapsed_sec"]
    for name, spec in cell_order():
        print("\n[CELDA] %s" % name, flush=True)
        try:
            rows, info = C.run_cell(name, D.N_SIM, make_batch_fn("cell", name, spec, a.cores), CKPT, a.cores,
                                    t_block, a.max_seconds, resume)
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc, flush=True)
            return 2
        status["cells"][name] = info["elapsed_sec"]
        print("  [COMPLETA] %s en %.0f s" % (name, info["elapsed_sec"]), flush=True)
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def load_rows(tag, n_sim):
    chunks = []
    for p in glob.glob(os.path.join(CKPT, "%s_i*_k*.json" % tag)):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete") and d["tag"] == tag:
            chunks.append(d)
    chunks.sort(key=lambda d: d["i0"])
    rows, pos = [], 0
    for d in chunks:
        if d["i0"] != pos:
            continue
        rows.extend(d["rows"])
        pos += d["k"]
    if len(rows) != n_sim:
        raise KeyError("%s: %d filas, se esperaban %d" % (tag, len(rows), n_sim))
    return np.asarray(rows, dtype=float), sum(d["elapsed_sec"] for d in chunks)


def rejections(rows, null_all, sim_all, n):
    """Vectores de rechazo por procedimiento."""
    null = null_all[n]
    rej = {}
    for c, (v, mode) in enumerate(NULL_COLS):
        cdf = cdf_from_null_stats(null[:, c])
        p = np.clip(cdf(rows[:, IDX["stat_" + v]]), 0.0, 1.0)
        rej["rm_%s_%s" % (v, mode)] = p < ALPHA
    sim = sim_all[n]
    for c in COMP:
        pv = rows[:, IDX["%s_p" % c]]
        rej["%s_asy" % c] = np.nan_to_num(pv, nan=1.0) < ALPHA
        if c in CAL_IDX:
            q = np.nanquantile(sim[:, CAL_IDX[c]], ALPHA)
            rej["%s_sim" % c] = np.nan_to_num(rows[:, IDX["%s_stat" % c]], nan=np.inf) < q
    for c, key in (("mzt", "MZt"), ("msb", "MSB")):
        st = np.nan_to_num(rows[:, IDX[c]], nan=np.inf)
        rej["%s_asy" % c] = st < U.NP_CV5["c"][key]
        rej["%s_sim" % c] = st < np.nanquantile(sim[:, CAL_IDX[c]], ALPHA)
    return rej


def published_rates(name, spec):
    """Tasas publicadas (o de A7) de R = 0.5 one, ADF, PP y DF-GLS (AIC) para una celda reutilizada."""
    n = spec["n"]
    if spec["kind"] == "gauss":
        if n >= 200:
            r = C.read_json("size_audit5.json")["alpha1"][str(n)]
            return "size_audit5.json[alpha1][%d]" % n, {"rm_R0.5_t0.1_one": r["ours_R050"], "adf_asy": r["adf"],
                                                         "pp_asy": r["pp"], "dfglsaic_asy": r["dfgls"]}
        row = next(c for c in C.read_json("small_n_size_audit5.json") if c["n"] == n and c["theta"] == 0.1)
        return "small_n_size_audit5.json[n=%d, theta=0.1]" % n, {"rm_R0.5_t0.1_one": row["ours_R050"], "adf_asy": row["adf"],
                                                                 "pp_asy": row["pp"], "dfglsaic_asy": row["dfgls"]}
    if spec["kind"] == "heavy":
        r = C.read_json("size_robustness_heavy_tails_audit5b.json")["alpha1"][spec["dist"]][str(n)]
        return "size_robustness_heavy_tails_audit5b.json[alpha1][%s][%d]" % (spec["dist"], n), {
            "rm_R0.5_t0.1_one": r["ours_R050"], "adf_asy": r["adf"], "pp_asy": r["pp"], "dfglsaic_asy": r["dfgls"]}
    k = spec["key"]
    if k == "base":
        f, c = "garch_size_audit7.json", C.read_json("garch_size_audit7.json")["cells"][str(n)]
    elif n in (2000, 5000):
        f, c = "garch_size_ext_large_audit7.json", C.read_json("garch_size_ext_large_audit7.json")["configs"][k]["cells"][str(n)]
    else:
        f, c = "garch_size_ext_audit7.json", C.read_json("garch_size_ext_audit7.json")["configs"][k]["cells"][str(n)]
    rr = c["rejection_rates"]
    return "%s[%s][%d]" % (f, k, n), {"rm_R0.5_t0.1_one": rr["ours_R050"]["rate"], "adf_asy": rr["adf"]["rate"],
                                      "pp_asy": rr["pp"]["rate"], "dfglsaic_asy": rr["dfgls"]["rate"]}


def analyze(a):
    t0 = time.time()
    region = C.exact_region(D.N_SIM)
    cells = dict(cell_order())
    null_all, sim_all, cal_ctrl, sim_elapsed = {}, {}, {}, {}
    for n in D.N_ALL:
        null_all[n] = rm_null(n, a.cores)
        cal_ctrl[str(n)] = calibrator_control(n, null_all[n])
        sim_all[n], sim_elapsed[str(n)] = load_rows("cal_dm_n%d" % n, D.N_CAL)
        print("control calibrador n=%d %s" % (n, cal_ctrl[str(n)]), flush=True)
    rows_all, rej_all, elapsed = {}, {}, {}
    for name, spec in cells.items():
        rows_all[name], elapsed[name] = load_rows(name, D.N_SIM)
        rej_all[name] = rejections(rows_all[name], null_all, sim_all, spec["n"])
    # Paso 0
    paso0 = {}
    for name, spec in cells.items():
        if not spec["reused"]:
            continue
        p = paso0_cell(name, spec)
        if spec["kind"] == "garch":
            p["max_abs_diff_a7_components_and_pvalues"] = paso0_garch_components(name, spec, rows_all[name])
        src, pub = published_rates(name, spec)
        mine = {k: float(rej_all[name][k].mean()) for k in pub}
        p["published_source"] = src
        p["published_rates"] = pub
        p["reproduced_rates"] = mine
        p["max_abs_rate_diff"] = max(abs(mine[k] - pub[k]) for k in pub)
        paso0[name] = p
        print("Paso 0 %s %s" % (name, {k: v for k, v in p.items() if k.startswith("max")}), flush=True)
    worst = {k: max(p.get(k, 0.0) for p in paso0.values())
             for k in ("max_abs_diff_series", "max_abs_diff_stat_R05_vs_compute_statistic",
                       "max_abs_diff_a7_components_and_pvalues", "max_abs_rate_diff")}

    def rate(name, proc):
        return C.rate_record(rej_all[name][proc], region)

    misspec = [k for k, s in cells.items() if s["kind"] != "gauss"]
    garch = [k for k, s in cells.items() if s["kind"] == "garch"]
    gauss_pub = [k for k, s in cells.items() if s["kind"] == "gauss" and s["reused"]]
    b2a_cells = gauss_pub + misspec
    agg_cells = misspec + [k for k in gauss_pub if cells[k]["n"] >= 200]
    # ---- B2a ------------------------------------------------------------------
    b2a = {}
    for name in b2a_cells:
        r0, r5 = rate(name, "rm_R0_t0.1_one"), rate(name, "rm_R0.5_t0.1_one")
        mc = C.mcnemar_exact(rej_all[name]["rm_R0_t0.1_one"], rej_all[name]["rm_R0.5_t0.1_one"])
        b2a[name] = {"n": cells[name]["n"], "kind": cells[name]["kind"], "rate_R0": r0, "rate_R05": r5,
                     "b_only_R0": mc["only_first"], "c_only_R05": mc["only_second"], "mcnemar_p": mc["p_value"],
                     "delta_pp": (r0["rate"] - r5["rate"]) * 100}
    sb = sum(b2a[k]["b_only_R0"] for k in agg_cells)
    sc = sum(b2a[k]["c_only_R05"] for k in agg_cells)
    sign = C.sign_test(sb, sc)
    mean_garch_delta = float(np.mean([b2a[k]["delta_pp"] for k in garch]))
    cnt0 = sum(b2a[k]["rate_R0"]["in_region"] for k in garch)
    cnt5 = sum(b2a[k]["rate_R05"]["in_region"] for k in garch)
    pasa = (all(abs(v["delta_pp"]) <= GATE_PP for v in b2a.values())
            and all(v["mcnemar_p"] >= MCNEMAR_P for v in b2a.values()) and abs(cnt0 - cnt5) <= COUNT_DIFF)
    falla = sign["p_value"] < SIGN_P and mean_garch_delta >= GATE_PP
    verdict_a = "PASA" if pasa else ("FALLA" if falla else "INDETERMINADO")
    gate_a = {"verdict": verdict_a, "cells_evaluated": b2a_cells, "aggregate_cells": agg_cells,
              "max_abs_delta_pp": max(abs(v["delta_pp"]) for v in b2a.values()),
              "cell_max_abs_delta": max(b2a, key=lambda k: abs(b2a[k]["delta_pp"])),
              "min_mcnemar_p": min(v["mcnemar_p"] for v in b2a.values()),
              "cell_min_mcnemar_p": min(b2a, key=lambda k: b2a[k]["mcnemar_p"]),
              "sum_b": sb, "sum_c": sc, "sign_test_p": sign["p_value"],
              "mean_delta_pp_garch": mean_garch_delta, "count_in_region_garch_R0": cnt0,
              "count_in_region_garch_R05": cnt5, "garch_cells": len(garch)}
    # ---- B2b ------------------------------------------------------------------
    gauss_by_n = {cells[k]["n"]: k for k, s in cells.items() if s["kind"] == "gauss"}
    gsize = {str(n): {"one": rate(gauss_by_n[n], "rm_R0_t0.1_one"), "hac": rate(gauss_by_n[n], "rm_R0_t0.1_hac")}
             for n in sorted(gauss_by_n)}
    procs_b2b = ("rm_R0_t0.1_one", "rm_R0_t0.1_hac", "adf_asy", "adf_sim", "pp_asy", "pp_sim", "dfgls_asy", "dfgls_sim")
    misspec_rates = {k: {p: rate(k, p) for p in procs_b2b + ("dfglsaic_asy", "rm_R0.5_t0.1_one", "rm_R0.5_t0.1_hac")}
                     for k in misspec}
    gauss_rates = {k: {p: rate(k, p) for p in procs_b2b + ("dfglsaic_asy", "rm_R0.5_t0.1_one", "rm_R0.5_t0.1_hac")}
                   for k in gauss_by_n.values()}
    deltas = {}
    for k in misspec:
        g = gauss_by_n[cells[k]["n"]]
        deltas[k] = {p: C.diff_independent(misspec_rates[k][p], gauss_rates[g][p]) for p in procs_b2b}
    by_n = {}
    for n in sorted({cells[k]["n"] for k in misspec}):
        ks = [k for k in misspec if cells[k]["n"] == n]
        by_n[str(n)] = {"cells": ks, **{p: C.mean_with_se([deltas[k][p] for k in ks]) for p in procs_b2b}}
    in_region = {p: {"garch": sum(misspec_rates[k][p]["in_region"] for k in garch),
                     "heavy": sum(misspec_rates[k][p]["in_region"] for k in misspec if cells[k]["kind"] == "heavy")}
                 for p in procs_b2b}
    c_hac = NULL_COLS.index(("R0_t0.1", "hac"))
    cvs = {str(n): float(np.quantile(null_all[n][:, c_hac], ALPHA)) for n in CV_N}
    cv_vals = list(cvs.values())
    cv_var = (max(cv_vals) - min(cv_vals)) / min(cv_vals)
    gate_b = {"verdict": "PASA" if all(gsize[str(n)]["hac"]["in_region"] for n in B2B_GATE_N) else "FALLA",
              "sizes": {str(n): gsize[str(n)]["hac"]["rate"] for n in B2B_GATE_N}, "region": region}
    out = {
        "provenance": C.provenance(__file__, seed_family=FAM),
        "config": {"N_sim": D.N_SIM, "N_cal": D.N_CAL, "alpha": ALPHA, "cal_seed_rm": D.CAL_SEED_PUBLISHED,
                   "rm_variants": RM_VARIANTS, "null_columns": ["%s|%s" % c for c in NULL_COLS],
                   "comparators": list(COMP) + ["mzt", "msb"], "rule_rm": "p = F_null(stat) < alpha (build_null_cdf)",
                   "rule_sim": "stat < cuantil 5% de la calibracion (cola inferior)",
                   "rule_np_asy": U.NP_CV5["c"], "delta_note": "Delta = tasa mal especificada - tasa gaussiana al mismo n; "
                   "celdas con innovaciones distintas: EE de diferencia de proporciones independientes",
                   "gate_thresholds": {"pp": GATE_PP, "mcnemar_p": MCNEMAR_P, "count_diff": COUNT_DIFF, "sign_p": SIGN_P}},
        "exact_region": region,
        "calibrator_control": cal_ctrl,
        "paso0": {"cells": paso0, "worst": worst},
        "cells": {k: {"n": s["n"], "kind": s["kind"], "reused": s["reused"], "source": s["source"],
                      "nan_counts": {c: int(np.isnan(rows_all[k][:, IDX[c]]).sum()) for c in ROW_COLS},
                      "elapsed_sec": elapsed[k]} for k, s in cells.items()},
        "calibration_sim_elapsed_sec": sim_elapsed,
        "sim_critical_values": {str(n): {c: float(np.nanquantile(sim_all[n][:, CAL_IDX[c]], ALPHA)) for c in CAL_COLS}
                                for n in D.N_ALL},
        "B2a": {"cells": b2a, "gate": gate_a},
        "B2b": {"gaussian_size": gsize, "misspec_rates": misspec_rates, "gaussian_rates": gauss_rates,
                "paired_delta": deltas, "mean_delta_by_n": by_n, "count_in_region": in_region,
                "rm_hac_critical_values": cvs, "rm_hac_cv_max_rel_variation": cv_var, "gate": gate_b},
        "elapsed_analysis_sec": round(time.time() - t0, 1),
    }
    C.write_result(OUT, out, __file__)
    print("B2a", json.dumps(C.plain(gate_a))[:1500])
    print("B2b", json.dumps(C.plain(gate_b)))
    print(OUT)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze:
        return analyze(a)
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
