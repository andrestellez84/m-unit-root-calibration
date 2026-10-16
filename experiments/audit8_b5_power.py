"""
Auditoria A8 - B5: tablas de potencia en muestra finita con la primaria (CARO; 30 h).

Familia 95, N_sim = 5000 (bootstrap 2000), calibracion hac para RM / RM-GLS.
Se calculan siempre RM (R = 0, theta = 0.1) y RM-GLS; la primaria se lee de B4
(b4_local_power_audit8.json) al analizar. Todos los procedimientos de una celda
usan las mismas trayectorias.

1. DGP 1: AR(1), rho in {0.80, ..., 0.99} x n in {200, 500, 1000}. Columnas:
   primaria (y RM si la primaria es RM-GLS), R = 0.5 (hac), ADF, PP, DF-GLS
   (MAIC), MZt-GLS, MSB-GLS, KPSS; AWB en rho in {0.95, 0.99} (enmienda 2).
2. DGP 2: AR(0.95) con quiebre de media delta sigma_unc a n/2, delta in
   {0, 0.5, 1, 2, 3, 5}; columnas primaria, ADF, PP, DF-GLS, MZt-GLS, ZA; tamano
   de ZA bajo paseo aleatorio y bajo paseo con quiebre de nivel 1
   (audit6_dgp2_break_tests.generate_rw_break_mean).
3. DGP 3: paseo aleatorio con quiebre de varianza r in {1, 1.5, 2, 3, 4};
   columnas primaria, R = 0.5 (hac), ADF, PP, DF-GLS asy, MZt-GLS; AWB en
   r in {1, 2, 4} (enmienda 2). Todas son tasas de tamano. McNemar.
4. DGP 5 (n = 200): trayectorias de A7 (Paso 0 frente a sus checkpoints),
   umbrales a tamano igualado como en A7 (celda de calibracion cal_rw_n200) para
   la primaria, R = 0.5, R-hat, la union conjunta y el bootstrap (p-valores de
   A7); primaria y R = 0.5 tambien a nivel nominal con la nula hac; cuota de
   energia de g2 con R = 0.5; McNemar primaria frente a R = 0.5 y al bootstrap.
5. Caso con tendencia: tamano de la primaria-ct con deriva mu in {0, 0.05, 0.2}
   y numeros aleatorios comunes (estadisticos identicos entre mu) en
   n in {200, 500, 1000}; tasas gaussianas de la referencia independiente de la
   familia 92 (enmienda 2) en n in {200, ..., 5000}; potencia frente a AR(1)
   alrededor de una tendencia lineal, rho in {0.90, 0.95, 0.97, 0.99}; tamano de
   primaria-ct, ADF-sim(ct), DF-GLS-sim(ct) y MZt-GLS-sim(ct) en las 16 celdas
   GARCH de A7 con Delta pareado frente a la referencia independiente.

Modos: --budget (regla de presupuesto), --run, --analyze.
Salidas: b5_budget_audit8.json, b5_power_audit8.json.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import warnings

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_design as D                                          # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
import audit8_b2_size as B2                                        # noqa: E402
import audit8_b3_comparators as B3                                 # noqa: E402
import power_comparison as PC                                      # noqa: E402
from audit6_dgp2_break_tests import generate_rw_break_mean         # noqa: E402
from audit6_wild_bootstrap_sweep import find_rscript               # noqa: E402
from stationarity_test.rm_core import path_statistic, hac_sigma_sq  # noqa: E402
from stationarity_test.empirical_eigenvalues import build_null_cdf, cdf_from_null_stats  # noqa: E402

FAM = C.FAMILY["B5"]
CKPT = os.path.join(C.CKPT_ROOT, "audit8_b5")
OUT = os.path.join(C.RESULTS, "b5_power_audit8.json")
OUT_BUDGET = os.path.join(C.RESULTS, "b5_budget_audit8.json")
BUDGET_HOURS = 30.0
N3 = (200, 500, 1000)
BOOT_DGP1_RHO = (0.95, 0.99)
BOOT_DGP3_R = (1, 2, 4)
DRIFT_MU = (0.0, 0.05, 0.2)
TREND_SLOPE = 0.2
BREAK_MU = 1.0
DGP2_RHO = 0.95
CT_N = D.N_MAIN
BUDGET_FULL_CELL = "dgp3_r4_n1000"

DM_COLS = ("rm", "rmgls", "r05", "adf_p", "pp_p", "dfgls_p", "dfgls_k", "mzt", "msb", "kpss_p", "za_p")
CT_COLS = ("rm", "rmgls", "adf_stat", "adf_p", "pp_stat", "pp_p", "dfgls_stat", "dfgls_p", "mzt", "msb")
DRIFT_COLS = tuple("%s_mu%g" % (v, m) for v in ("rm", "rmgls") for m in DRIFT_MU)
IDM = {c: i for i, c in enumerate(DM_COLS)}
ICT = {c: i for i, c in enumerate(CT_COLS)}
IDR = {c: i for i, c in enumerate(DRIFT_COLS)}


# ---------------------------------------------------------------------------
# Celdas
# ---------------------------------------------------------------------------
def cells():
    out = {}
    for r in D.B5_DGP1_RHO:
        for n in N3:
            out["dgp1_rho%s_n%d" % (D.fmt(r), n)] = {"kind": "dm", "gen": "ar1", "rho": r, "n": n,
                                                     "boot": r in BOOT_DGP1_RHO}
    for d in D.B5_DGP2_DELTA:
        for n in N3:
            out["dgp2_delta%s_n%d" % (D.fmt(d), n)] = {"kind": "dm", "gen": "ar1_break_mean", "delta": d, "n": n,
                                                       "za": True, "boot": False}
    for n in N3:
        out["za_rw_n%d" % n] = {"kind": "dm", "gen": "ar1", "rho": 1.0, "n": n, "za": True, "boot": False}
        out["za_rwbreak_n%d" % n] = {"kind": "dm", "gen": "rw_break_mean", "n": n, "za": True, "boot": False}
    for r in D.B5_DGP3_R:
        for n in N3:
            out["dgp3_r%s_n%d" % (D.fmt(r), n)] = {"kind": "dm", "gen": "rw_break_var", "r": r, "n": n,
                                                   "boot": r in BOOT_DGP3_R}
    for n in N3:
        out["ct_size_n%d" % n] = {"kind": "drift", "n": n}
    for r in D.B5_CT_RHO:
        for n in N3:
            out["ct_power_rho%s_n%d" % (D.fmt(r), n)] = {"kind": "ct", "gen": "ar1_trend", "rho": r, "n": n}
    for n in CT_N:
        out["cal_ct_n%d" % n] = {"kind": "ct", "gen": "cal", "n": n, "reps": D.N_CAL}
    for k, s in D.size_cells().items():
        if s["kind"] == "garch":
            out["ct_" + k] = {"kind": "ct", "gen": "reuse_garch", "src": k, "spec": s, "n": s["n"]}
    for k, s in D.indep_cells().items():
        if s["n"] in CT_N:
            out["ct_" + k] = {"kind": "ct", "gen": "reuse_indep", "src": k, "spec": s, "n": s["n"], "reps": D.N_INDEP}
    return out


def reps(name, c):
    return c.get("reps", D.N_SIM)


def path(name, c, i):
    n = c["n"]
    if c["gen"] == "reuse_garch" or c["gen"] == "reuse_indep":
        return D.size_path(c["src"], c["spec"], i)
    rng = C.rep_rng(FAM, D.cell_index(FAM, name), i)
    if c["gen"] == "ar1":
        return PC.generate_ar1(n=n, rho=c["rho"], rng=rng)
    if c["gen"] == "ar1_break_mean":
        return PC.generate_ar1_break_mean(n=n, rho=DGP2_RHO, delta=c["delta"], rng=rng)
    if c["gen"] == "rw_break_mean":
        return generate_rw_break_mean(n=n, delta_mu=BREAK_MU, rng=rng)
    if c["gen"] == "rw_break_var":
        return PC.generate_rw_break_variance(n=n, ratio=c["r"], rng=rng)
    if c["gen"] == "ar1_trend":
        return PC.generate_ar1(n=n, rho=c["rho"], rng=rng) + TREND_SLOPE * np.arange(n + 1)
    if c["gen"] == "cal":
        return D.gauss_rw(n, rng)
    raise ValueError(c["gen"])


def rm_pair(y, n, det):
    s2 = hac_sigma_sq(y)
    t1, t2 = B2.taus(0.1, n, "theta")
    return [path_statistic(y, n, t1, t2, 0.0, s2, B2.C1, B2.C2, deterministics=det, anchor=a, need_g2=False)[0]
            for a in ("mean", "gls")], s2, t1, t2


def row(name, c, i):
    n = c["n"]
    if c["kind"] == "drift":
        eps = C.rep_rng(FAM, D.cell_index(FAM, name), i).standard_normal(n)
        out = {}
        for m in DRIFT_MU:
            y = np.concatenate([[0.0], np.cumsum(eps + m)])
            (a, b), _, _, _ = rm_pair(y, n, "ct")
            out["rm_mu%g" % m], out["rmgls_mu%g" % m] = a, b
        return [out[k] for k in DRIFT_COLS]
    y = path(name, c, i)
    if c["kind"] == "ct":
        (a, b), _, _, _ = rm_pair(y, n, "ct")
        r = U.comparator_row(y, "ct", with_dfgls_aic=False)
        vals = {"rm": a, "rmgls": b, "adf_stat": r["adf_stat"], "adf_p": r["adf_p"], "pp_stat": r["pp_stat"],
                "pp_p": r["pp_p"], "dfgls_stat": r["dfgls_stat"], "dfgls_p": r["dfgls_p"], "mzt": r["np_MZt"],
                "msb": r["np_MSB"]}
        return [float(vals[k]) for k in CT_COLS]
    (a, b), s2, t1, t2 = rm_pair(y, n, "c")
    r05 = path_statistic(y, n, t1, t2, 0.5, s2, B2.C1, B2.C2)[0]
    r = U.comparator_row(y, "c", with_kpss=True, with_dfgls_aic=False)
    za_p = U.za(y)[1] if c.get("za") else float("nan")
    vals = {"rm": a, "rmgls": b, "r05": r05, "adf_p": r["adf_p"], "pp_p": r["pp_p"], "dfgls_p": r["dfgls_p"],
            "dfgls_k": r["np_k"], "mzt": r["np_MZt"], "msb": r["np_MSB"], "kpss_p": r["kpss_p"], "za_p": za_p}
    return [float(vals[k]) for k in DM_COLS]


def _rows(name, c, idx):
    return [row(name, c, i) for i in idx]


def batch_fn(name, c, cores):
    def fn(indices):
        parts = [p for p in (indices[j::cores] for j in range(cores)) if p]
        res = Parallel(n_jobs=len(parts), backend="loky")(delayed(_rows)(name, c, p) for p in parts)
        by = {}
        for p, rr in zip(parts, res):
            by.update(zip(p, rr))
        return [by[i] for i in indices]
    return fn


def boot_fn(name, c, cores):
    def fn(indices):
        n = c["n"]
        mat = np.column_stack([path(name, c, i) for i in indices])
        rcell = D.cell_index(FAM, "rseed_" + name)
        seeds = np.array([C.r_seed(FAM, rcell, i) for i in indices], dtype=np.int32)
        os.makedirs(CKPT, exist_ok=True)
        stem = os.path.join(CKPT, "_tmp_%s_i%06d" % (name, indices[0]))
        binp, seedp, outj = stem + ".bin", stem + ".seeds", stem + ".json"
        mat.T.astype(np.float64).tofile(binp)
        seeds.tofile(seedp)
        exp5 = ",".join("%.6f" % v for v in mat[:5, 0])
        try:
            r = subprocess.run([find_rscript(), B3.WORKER, binp, str(n), str(len(indices)), str(B3.B_BOOT), str(cores),
                                outj, exp5, seedp], capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError("worker de R fallo:\n%s" % (r.stdout + r.stderr)[-3000:])
            with open(outj, encoding="utf-8") as f:
                d = json.load(f)
        finally:
            for p in (binp, seedp, outj):
                if os.path.exists(p):
                    os.remove(p)
        return [[float("nan") if v is None else float(v)] for v in d["p_adf"]]
    return fn


def jobs():
    cs = cells()
    out = [(name, c, "rows") for name, c in cs.items()]
    out += [(name, c, "boot") for name, c in cs.items() if c.get("boot")]
    return sorted(out, key=lambda x: (x[2] == "boot", x[1]["n"], x[0]))


def run(a):
    bud = C.read_json(os.path.basename(OUT_BUDGET))
    if not bud["within_budget"]:
        print("presupuesto excedido: no se lanza")
        return 5
    resume = "python experiments/audit8_b5_power.py --run --cores %d --max-seconds %.0f" % (a.cores, a.max_seconds)
    t_block = time.time()
    for name, c, what in jobs():
        tag = ("boot_" if what == "boot" else "") + name
        N = D.N_SIM_BOOT if what == "boot" else reps(name, c)
        fn = boot_fn(name, c, a.cores) if what == "boot" else batch_fn(name, c, a.cores)
        print("\n[CELDA] %s" % tag, flush=True)
        try:
            C.run_cell(tag, N, fn, CKPT, a.cores, t_block, a.max_seconds, resume)
        except C.BudgetExhausted as exc:
            print("  [TOPE] %s" % exc, flush=True)
            return 2
    print("bloque: %.2f h" % ((time.time() - t_block) / 3600), flush=True)
    return 0


def budget(a):
    resume = "python experiments/audit8_b5_power.py --budget --cores %d" % a.cores
    t_block = time.time()
    cs = cells()
    c = cs[BUDGET_FULL_CELL]
    print("[PRESUPUESTO] celda completa boot_%s" % BUDGET_FULL_CELL, flush=True)
    _, info = C.run_cell("boot_" + BUDGET_FULL_CELL, D.N_SIM_BOOT, boot_fn(BUDGET_FULL_CELL, c, a.cores), CKPT,
                         a.cores, t_block, a.max_seconds, resume)
    sps_boot = {c["n"]: info["elapsed_sec"] / D.N_SIM_BOOT}
    measured = {"boot_n%d" % c["n"]: {"cell": "boot_" + BUDGET_FULL_CELL, "series": D.N_SIM_BOOT,
                                      "sec_per_series": sps_boot[c["n"]], "kind": "celda completa"}}
    for n in N3:
        if n == c["n"]:
            continue
        name = "dgp3_r4_n%d" % n
        _, p = C.C7.run_cell_batched("boot_" + name, D.N_SIM_BOOT, boot_fn(name, cs[name], a.cores), CKPT, a.cores,
                                     t_block, a.max_seconds, resume, probe_only=True)
        sps_boot[n] = p["probe_sec_per_series"]
        measured["boot_n%d" % n] = {"cell": "boot_" + name, "series": C.C7.PROBE_SERIES,
                                    "sec_per_series": sps_boot[n], "kind": "sonda"}
    # filas de python: una sonda de 14 series por celda (el coste por fila varia con el tipo, n y
    # los comparadores de la celda: ZA solo esta en DGP 2 y en las celdas de tamano de ZA)
    sps_rows, sps_kind = {}, {}
    for name, cc, what in jobs():
        if what == "boot":
            continue
        _, p = C.C7.run_cell_batched(name, reps(name, cc), batch_fn(name, cc, a.cores), CKPT, a.cores,
                                     t_block, a.max_seconds, resume, probe_only=True, log=lambda *x: None)
        sps_rows[name] = p["probe_sec_per_series"]
        sps_kind.setdefault(cc["kind"], []).append(p["probe_sec_per_series"])
    measured["rows_por_celda"] = {"cells": len(sps_rows), "series_per_probe": C.C7.PROBE_SERIES,
                                  "kind": "sonda por celda",
                                  "sec_per_series_max_by_kind": {k: max(v) for k, v in sps_kind.items()},
                                  "sec_per_series_min_by_kind": {k: min(v) for k, v in sps_kind.items()}}
    per_cell, per_cell_upper = {}, {}
    upper = {k: max(v) for k, v in sps_kind.items()}
    for name, cc, what in jobs():
        if what == "boot":
            per_cell["boot_" + name] = D.N_SIM_BOOT * sps_boot[cc["n"]]
            per_cell_upper["boot_" + name] = per_cell["boot_" + name]
        else:
            per_cell[name] = reps(name, cc) * sps_rows[name]
            per_cell_upper[name] = reps(name, cc) * upper[cc["kind"]]
    total = sum(per_cell.values())
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "budget_hours": BUDGET_HOURS, "cores": a.cores,
           "measured": measured, "per_cell_projected_sec": per_cell, "projected_total_hours": total / 3600,
           "within_budget": total / 3600 <= BUDGET_HOURS,
           "per_cell_projected_sec_upper_bound": per_cell_upper,
           "projected_total_hours_upper_bound": sum(per_cell_upper.values()) / 3600,
           "bootstrap_hours": sum(v for k, v in per_cell.items() if k.startswith("boot_")) / 3600,
           "rows_hours": sum(v for k, v in per_cell.items() if not k.startswith("boot_")) / 3600,
           "rule": "una celda completa de bootstrap (DGP 3, r = 4, n = 1000), sondas de 14 series por n para el resto del "
                   "bootstrap y una sonda de 14 series por cada celda de filas; se reporta tambien la cota superior que "
                   "resulta de proyectar cada celda de filas con la sonda mas cara de su tipo"}
    C.write_result(OUT_BUDGET, out, __file__)
    print("[PRESUPUESTO] proyeccion total %.1f h frente a %.0f h -> %s" % (
        total / 3600, BUDGET_HOURS, "dentro" if out["within_budget"] else "EXCEDE: no se lanza"), flush=True)
    return 0 if out["within_budget"] else 5


# ---------------------------------------------------------------------------
# Analisis
# ---------------------------------------------------------------------------
def _load(tag, N):
    saved = B2.CKPT
    try:
        B2.CKPT = CKPT
        return B2.load_rows(tag, N)[0]
    finally:
        B2.CKPT = saved


def mcn(a, b):
    return C.mcnemar_exact(a, b)


def ct_nulls(cores):
    jobs_ = [(n, an) for n in CT_N for an in ("mean", "gls")]
    res = Parallel(n_jobs=min(cores, len(jobs_)))(
        delayed(build_null_cdf)((0.1, 0.1), 0.0, n, N_cal=D.N_CAL, seed=D.CAL_SEED_PUBLISHED, deterministics="ct",
                                cal_sigma="hac", anchor=an, use_cache=False) for n, an in jobs_)
    return {(n, an): r for (n, an), r in zip(jobs_, res)}


def analyze(a):
    t0 = time.time()
    b4 = C.read_json("b4_local_power_audit8.json")
    gls = bool(b4["gls_rule"]["adopt_gls"])
    prim, prim_ct = ("rmgls", "rmgls") if gls else ("rm", "rm")
    cs = cells()
    reg5, reg2, reg20 = C.exact_region(D.N_SIM), C.exact_region(D.N_SIM_BOOT), C.exact_region(D.N_INDEP)
    c_idx = {v: B2.NULL_COLS.index(k) for v, k in (("rm", ("R0_t0.1", "hac")), ("r05", ("R0.5_t0.1", "hac")),
                                                    ("rmgls", ("rmgls", "hac")))}
    dm_null = {n: B2.rm_null(n, a.cores) for n in N3}
    dm_cdf = {(n, v): cdf_from_null_stats(dm_null[n][:, i]) for n in N3 for v, i in c_idx.items()}

    def rm_rej(n, v, stat):
        return np.clip(dm_cdf[(n, v)](stat), 0.0, 1.0) < C.ALPHA

    def dm_rejections(name, c, rows):
        n = c["n"]
        rej = {"rm": rm_rej(n, "rm", rows[:, IDM["rm"]]), "rmgls": rm_rej(n, "rmgls", rows[:, IDM["rmgls"]]),
               "r05": rm_rej(n, "r05", rows[:, IDM["r05"]])}
        for t in ("adf", "pp", "dfgls", "kpss", "za"):
            rej[t] = np.nan_to_num(rows[:, IDM[t + "_p"]], nan=1.0) < C.ALPHA
        rej["mzt"] = np.nan_to_num(rows[:, IDM["mzt"]], nan=np.inf) < U.NP_CV5["c"]["MZt"]
        rej["msb"] = np.nan_to_num(rows[:, IDM["msb"]], nan=np.inf) < U.NP_CV5["c"]["MSB"]
        if c.get("boot"):
            p = _load("boot_" + name, D.N_SIM_BOOT)[:, 0]
            rej["awb"] = np.nan_to_num(p, nan=1.0) < C.ALPHA
        return rej

    def table(prefix, cols, mc_against):
        out = {}
        for name, c in cs.items():
            if not name.startswith(prefix) or c["kind"] != "dm":
                continue
            rows = _load(name, D.N_SIM)
            rej = dm_rejections(name, c, rows)
            rec = {"n": c["n"], "rates": {}, "mcnemar_primary_vs": {}, "nan": {k: int(np.isnan(rows[:, IDM[k]]).sum()) for k in DM_COLS}}
            for t in cols + (["awb"] if "awb" in rej else []):
                rec["rates"][t] = C.rate_record(rej[t], reg2 if t == "awb" else reg5)
            for t in mc_against + (["awb"] if "awb" in rej else []):
                if t == prim:
                    continue
                a_, b_ = (rej[prim][:D.N_SIM_BOOT], rej[t]) if t == "awb" else (rej[prim], rej[t])
                rec["mcnemar_primary_vs"][t] = mcn(a_, b_)
            for key in ("rho", "delta", "r"):
                if key in c:
                    rec[key] = c[key]
            out[name] = rec
        return out

    base_cols = [prim] + (["rm"] if gls else [])
    dgp1 = table("dgp1_", base_cols + ["r05", "adf", "pp", "dfgls", "mzt", "msb", "kpss"], ["r05", "adf", "pp", "dfgls", "mzt", "msb"])
    dgp2 = table("dgp2_", base_cols + ["adf", "pp", "dfgls", "mzt", "za"], ["adf", "pp", "dfgls", "mzt", "za"])
    za = table("za_", base_cols + ["adf", "pp", "dfgls", "mzt", "za"], [])
    dgp3 = table("dgp3_", base_cols + ["r05", "adf", "pp", "dfgls", "mzt"], ["r05"])
    # ---- DGP 5 --------------------------------------------------------------
    dgp5 = dgp5_block(prim, a)
    # ---- caso con tendencia ---------------------------------------------------
    cdfs = ct_nulls(a.cores)
    an = {"rm": "mean", "rmgls": "gls"}

    def ct_rej(n, v, stat):
        return np.clip(cdfs[(n, an[v])](stat), 0.0, 1.0) < C.ALPHA

    sim = {n: _load("cal_ct_n%d" % n, D.N_CAL) for n in CT_N}
    q = {n: {t: float(np.nanquantile(sim[n][:, ICT[t]], C.ALPHA)) for t in ("adf_stat", "pp_stat", "dfgls_stat", "mzt", "msb")}
         for n in CT_N}

    def ct_rejections(n, rows):
        rej = {"rm": ct_rej(n, "rm", rows[:, ICT["rm"]]), "rmgls": ct_rej(n, "rmgls", rows[:, ICT["rmgls"]])}
        for t in ("adf", "pp", "dfgls"):
            rej[t] = np.nan_to_num(rows[:, ICT[t + "_p"]], nan=1.0) < C.ALPHA
            rej[t + "_sim"] = np.nan_to_num(rows[:, ICT[t + "_stat"]], nan=np.inf) < q[n][t + "_stat"]
        for t, key in (("mzt", "MZt"), ("msb", "MSB")):
            st = np.nan_to_num(rows[:, ICT[t]], nan=np.inf)
            rej[t] = st < U.NP_CV5["ct"][key]
            rej[t + "_sim"] = st < q[n][t]
        return rej

    drift = {}
    for n in N3:
        rows = _load("ct_size_n%d" % n, D.N_SIM)
        rec = {}
        for v in ("rm", "rmgls"):
            cols_ = [rows[:, IDR["%s_mu%g" % (v, m)]] for m in DRIFT_MU]
            spread = np.max(np.abs(np.max(cols_, axis=0) - np.min(cols_, axis=0)) / np.min(cols_, axis=0))
            rj = [ct_rej(n, v, x) for x in cols_]
            rec[v] = {"max_rel_diff_across_mu": float(spread),
                      "rejection_vectors_identical": bool(all(np.array_equal(rj[0], x) for x in rj[1:])),
                      "rates_by_mu": {"%g" % m: C.rate_record(x, reg5) for m, x in zip(DRIFT_MU, rj)}}
        drift[str(n)] = rec
    ct_gauss, ct_gauss_rej = {}, {}
    for n in CT_N:
        rows = _load("ct_indep_gauss_n%d" % n, D.N_INDEP)
        rj = ct_rejections(n, rows)
        ct_gauss_rej[n] = rj
        ct_gauss[str(n)] = {t: C.rate_record(v, reg20) for t, v in rj.items()}
    ct_power = {}
    for name, c in cs.items():
        if not name.startswith("ct_power"):
            continue
        rows = _load(name, D.N_SIM)
        rj = ct_rejections(c["n"], rows)
        ct_power[name] = {"n": c["n"], "rho": c["rho"],
                          "rates": {t: C.rate_record(rj[t], reg5) for t in base_cols + ["adf", "pp", "dfgls", "mzt", "msb"]},
                          "mcnemar_primary_vs": {t: mcn(rj[prim_ct], rj[t]) for t in ["adf", "pp", "dfgls", "mzt", "msb"]}}
    ct_garch = {}
    procs_g = [prim_ct] + (["rm"] if gls else []) + ["adf_sim", "dfgls_sim", "mzt_sim"]
    for name, c in cs.items():
        if c.get("gen") != "reuse_garch":
            continue
        rows = _load(name, D.N_SIM)
        rj = ct_rejections(c["n"], rows)
        rates = {t: C.rate_record(rj[t], reg5) for t in procs_g}
        ct_garch[name] = {"n": c["n"], "rates": rates,
                          "delta_vs_independent_gaussian": {t: C.diff_independent(rates[t], ct_gauss[str(c["n"])][t]) for t in procs_g}}
    ct_mean = {}
    for n in sorted({v["n"] for v in ct_garch.values()}):
        ks = [k for k, v in ct_garch.items() if v["n"] == n]
        ct_mean[str(n)] = {t: C.mean_with_se([ct_garch[k]["delta_vs_independent_gaussian"][t] for k in ks]) for t in procs_g}
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "amendment": "experiments/protocol_audit8_amend2.md",
           "primary": "RM-GLS" if gls else "RM", "primary_is_gls": gls, "N_sim": D.N_SIM, "N_boot": D.N_SIM_BOOT,
           "B": B3.B_BOOT, "exact_region_5000": reg5, "exact_region_2000": reg2, "exact_region_20000": reg20,
           "config": {"theta": 0.1, "calibration_dm": "B2 (semilla 42, N_cal = 50000, hac)",
                      "calibration_ct": "build_null_cdf(deterministics = ct, cal_sigma = hac, N_cal = 50000, semilla 42)",
                      "np_asy": U.NP_CV5, "dgp2_rho": DGP2_RHO, "za_break_mu": BREAK_MU, "trend_slope": TREND_SLOPE,
                      "boot_dgp1_rho": BOOT_DGP1_RHO, "boot_dgp3_r": BOOT_DGP3_R},
           "dgp1": dgp1, "dgp2": dgp2, "za_size": za, "dgp3": dgp3, "dgp5": dgp5,
           "ct": {"drift_invariance": drift, "gaussian_size_independent": ct_gauss, "sim_critical_values": q,
                  "power": ct_power, "garch": ct_garch, "garch_mean_delta_by_n": ct_mean},
           "elapsed_analysis_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    print("B5 escrito; primaria", out["primary"], "; drift", {n: v[prim_ct]["rejection_vectors_identical"] for n, v in drift.items()})
    print(OUT)
    return 0


def dgp5_block(prim, a):
    import audit7_design as D7
    import audit7_dgp5_runner as RUN
    import audit7_dgp5_analysis as AN
    B = D7.DGP5_B
    n = 200
    def a7_rows(tag, n_sim):
        rows, why = AN.load_rows(RUN.CKPT, tag, n_sim)
        if rows is None:
            raise KeyError("checkpoints de A7 no disponibles para %s: %s" % (tag, why))
        return rows

    cal_rows = a7_rows(D7.cal_tag(n), D7.N_CAL)
    cal = AN.calibrate(cal_rows, B)
    I = RUN.IDX

    def gls_stats(kind, rho, r, reps_):
        """Estadistico RM-GLS sobre las trayectorias de A7 (recomputado; cache en npz)."""
        tag = D7.cal_tag(n) if kind == "cal" else D7.dgp5_tag(n, rho, r)
        path_npz = os.path.join(CKPT, "dgp5_gls_%s.npz" % tag)
        if os.path.exists(path_npz):
            with np.load(path_npz) as z:
                if bool(z["complete"]) and z["stat"].shape == (reps_,):
                    return z["stat"]
        sb = RUN.cell_seed_base(kind, n, rho, r)
        t1, t2 = B2.taus(0.1, n, "theta")

        def chunk(idx):
            out = []
            for i in idx:
                y = RUN.generate(kind, n, rho, r, sb, i)
                out.append(path_statistic(y, n, t1, t2, 0.0, hac_sigma_sq(y), B2.C1, B2.C2, anchor="gls",
                                          need_g2=False)[0])
            return out
        parts = [list(range(reps_))[j::a.cores] for j in range(a.cores)]
        res = Parallel(n_jobs=a.cores)(delayed(chunk)(pp) for pp in parts)
        stat = np.zeros(reps_)
        for pp, rr in zip(parts, res):
            stat[np.array(pp)] = rr
        np.savez(path_npz + ".tmp.npz", stat=stat, complete=True)
        os.replace(path_npz + ".tmp.npz", path_npz)
        return stat

    def prim_stat(rows, kind=None, rho=None, r=None, reps_=None):
        if prim == "rm":
            return np.sqrt((1.0 - 0.0) ** 2 * rows[:, I["g1_std"]] ** 2)
        return gls_stats(kind, rho, r, reps_)

    thr_prim = float(np.quantile(-prim_stat(cal_rows, "cal", None, None, D7.N_CAL), AN.CAL_QUANTILE))
    null = B2.rm_null(n, a.cores)
    cdf_rm = cdf_from_null_stats(null[:, B2.NULL_COLS.index((("rmgls" if prim == "rmgls" else "R0_t0.1"), "hac"))])
    cdf_05 = cdf_from_null_stats(null[:, B2.NULL_COLS.index(("R0.5_t0.1", "hac"))])
    worst = 0.0
    cellsd = {}
    for (nn, rho, r) in D7.dgp5_cells():
        if nn != n:
            continue
        tag = D7.dgp5_tag(nn, rho, r)
        rows = a7_rows(tag, D7.DGP5_N_SIM)
        sb = RUN.cell_seed_base("dgp5", nn, rho, r)
        for i in range(B2.PASO0_REPS):
            y = RUN.generate("dgp5", nn, rho, r, sb, i)
            s2 = hac_sigma_sq(y)
            t1, t2 = B2.taus(0.1, nn, "theta")
            _, g1, g2 = path_statistic(y, nn, t1, t2, 0.5, s2, B2.C1, B2.C2)
            worst = max(worst, abs(g1 - rows[i, I["g1_std"]]), abs(g2 - rows[i, I["g2_std"]]))
        sm = AN.rejections_size_matched(rows, B, cal)
        ps = prim_stat(rows, "dgp5", rho, r, D7.DGP5_N_SIM)
        sm["primary"] = -ps > thr_prim
        nom = {"primary_hac": np.clip(cdf_rm(ps), 0, 1) < C.ALPHA,
               "r05_hac": np.clip(cdf_05(rows[:, I["stat_R050"]]), 0, 1) < C.ALPHA}
        cellsd[tag] = {"rho": rho, "r": r,
                       "size_matched": {k: C.rate_record(sm[k]) for k in ("primary", "proposed_R050", "proposed_adaptive",
                                                                          "union_joint", "bootstrap_dfgls")},
                       "nominal_hac": {k: C.rate_record(v) for k, v in nom.items()},
                       "g2_share_R050_median": float(np.median(rows[:, I["g2_share_R050"]])),
                       "mcnemar_primary_vs_R050": mcn(sm["primary"], sm["proposed_R050"]),
                       "mcnemar_primary_vs_bootstrap": mcn(sm["primary"], sm["bootstrap_dfgls"])}
    a7 = C.read_json("dgp5_mixed_audit7.json")
    return {"n": n, "B": B, "primary": prim, "calibration_cell": D7.cal_tag(n), "threshold_primary": thr_prim,
            "primary_statistic_source": ("componentes de A7" if prim == "rm" else
                                         "RM-GLS recomputado sobre las trayectorias de A7 (cache npz en audit8_b5)"),
            "a7_thresholds": cal["thresholds"], "a7_joint_alpha_star": cal["joint_union_alpha_star"],
            "paso0": {"reps": B2.PASO0_REPS, "max_abs_diff_components": worst},
            "a7_source_sha256": C.sha256_file(os.path.join(C.RESULTS, "dgp5_mixed_audit7.json")),
            "a7_generated_utc": a7["provenance"]["generated_utc"], "cells": cellsd}


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
    if a.run:
        return run(a)
    return analyze(a)


if __name__ == "__main__":
    sys.exit(main())
