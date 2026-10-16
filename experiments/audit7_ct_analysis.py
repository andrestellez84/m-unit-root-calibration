"""
Auditoria A7 - Bloque 2: analisis del caso "ct". Se commitea antes de correr
las celdas.

Entradas: checkpoints por serie de audit7_ct_runner.py y
ct_verification_audit7.json (V1, V2 y Paso 0; debe decir PASA).

Nulas (N_cal = 50000 cada una)
  known  PRINCIPAL. build_null_cdf del paquete con deterministics="ct":
         paseos aleatorios con sigma = 1 conocida, detrendados igual.
  hac    SECUNDARIA. Estadistico de muestra finita completo (sigma_HAC en cada
         paseo simulado), detrendado igual.
  c_ref  Nula del paper para el caso "c" (seed 42), aplicada a la referencia
         "c" sobre la serie sin componente determinista.
La CDF se construye igual que en el paquete (interpolacion lineal de la ECDF).
Rechazo: p < 0.05.

V3 Tamano exacto (registrada antes de correr). Con la nula PRINCIPAL y detrend
   QD, la tasa de rechazo en cada una de las 9 celdas (n, mu) cae en la region
   binomial exacta al 95% de 5000 replicas con tasa 0.05, y no depende de mu:
   con numeros aleatorios comunes, el estadistico de cada serie es igual en los
   tres mu (|diff| relativo <= 1e-9) y los vectores de rechazo son identicos.
   Si V3 falla, el test propuesto "ct" se retira segun la regla 6 y se avisa.

DGP 1-ct y DGP 3-ct: tasas con IC de Clopper-Pearson de todos los
procedimientos; en DGP 3-ct, contraste pareado (McNemar exacto) entre el test
"ct" y la referencia "c" sobre las mismas innovaciones.

Salida: experiments/results/ct_case_audit7.json.
Exit 0 completo y V3 PASA; 3 si V3 FALLA; 2 si faltan celdas.

Uso: python experiments/audit7_ct_analysis.py --cores 14
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from joblib import Parallel, delayed
from scipy.interpolate import interp1d
from scipy.stats import binomtest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                   # noqa: E402
import audit7_ct_design as D                                # noqa: E402
import audit7_ct_runner as RUN                              # noqa: E402
from power_comparison import generate_rw_break_variance      # noqa: E402
from stationarity_test.deterministics import apply_deterministics  # noqa: E402
from stationarity_test.empirical_eigenvalues import build_null_cdf  # noqa: E402

OUT = os.path.join(C.RESULTS, "ct_case_audit7.json")
ALPHA = 0.05
HAC_CHUNK = 2500


# ---------------------------------------------------------------------------
# Nulas
# ---------------------------------------------------------------------------
def _null_known(n, d):
    cdf = build_null_cdf(D.THETA, D.R, n, N_cal=D.N_CAL, seed=D.null_seed("known", n, d),
                         use_cache=False, deterministics="ct", detrend=d)
    return np.asarray(cdf.x, dtype=np.float64)


def _null_c_ref(n):
    cdf = build_null_cdf(D.THETA, D.R, n, N_cal=D.N_CAL, seed=D.C_REFERENCE_NULL_SEED, use_cache=False)
    return np.asarray(cdf.x, dtype=np.float64)


def _null_hac_chunk(n, d, i0, k):
    sb = D.null_seed("hac", n, d)
    out = np.empty(k)
    for j, i in enumerate(range(i0, i0 + k)):
        rw = generate_rw_break_variance(n=n, ratio=1.0, rng=np.random.default_rng(sb + i))
        g1, g2, _ = RUN.components_from(apply_deterministics(rw, "ct", d), rw, n)
        out[j] = RUN.statistic(g1, g2)
    return out


def ecdf(sorted_stats):
    N = sorted_stats.size
    return interp1d(sorted_stats, np.arange(1, N + 1) / N, kind="linear",
                    bounds_error=False, fill_value=(0.0, 1.0))


def build_nulls(cores):
    tasks = [("known", n, d) for n in D.NULL_N for d in D.DETRENDS]
    tasks += [("c_ref", n, None) for n in D.NULL_N]
    res = Parallel(n_jobs=cores, backend="loky")(
        delayed(_null_known)(n, d) if kind == "known" else delayed(_null_c_ref)(n)
        for kind, n, d in tasks)
    nulls = {(kind, n, d): np.sort(x) for (kind, n, d), x in zip(tasks, res)}
    chunks = [(n, d, i0, min(HAC_CHUNK, D.N_CAL - i0))
              for n in D.NULL_N for d in D.DETRENDS for i0 in range(0, D.N_CAL, HAC_CHUNK)]
    res = Parallel(n_jobs=cores, backend="loky")(delayed(_null_hac_chunk)(*c) for c in chunks)
    for n in D.NULL_N:
        for d in D.DETRENDS:
            parts = [r for c, r in zip(chunks, res) if c[0] == n and c[1] == d]
            nulls[("hac", n, d)] = np.sort(np.concatenate(parts))
    return nulls


# ---------------------------------------------------------------------------
# Carga y tasas
# ---------------------------------------------------------------------------
def load_rows(tag, n_sim):
    files = [f for f in glob.glob(os.path.join(RUN.CKPT, tag + "_i*_k*.json"))
             if not f.endswith(".timing.json")]
    if not files:
        return None, "sin checkpoints"
    chunks = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        if d.get("tag") != tag:
            continue
        if d.get("complete") is not True:
            return None, "lote incompleto %s" % os.path.basename(f)
        chunks.append(d)
    chunks.sort(key=lambda d: d["i0"])
    rows, nxt = [], 0
    for d in chunks:
        if d["i0"] != nxt:
            return None, "hueco de lotes en i0=%d" % nxt
        rows.extend(d["rows"])
        nxt += d["k"]
    if nxt != n_sim:
        return None, "%d de %d series" % (nxt, n_sim)
    return np.asarray(rows, dtype=float), None


def rate(mask):
    mask = np.asarray(mask, dtype=bool)
    k = int(mask.sum())
    lo, hi = C.clopper_pearson(k, mask.size)
    return {"rate": k / mask.size, "rejections": k, "n": int(mask.size), "ci_lower": lo, "ci_upper": hi}


def cell_rejections(rows, n, cdfs):
    I = RUN.IDX
    stat_qd = RUN.statistic(rows[:, I["g1_qd"]], rows[:, I["g2_qd"]])
    stat_ols = RUN.statistic(rows[:, I["g1_ols"]], rows[:, I["g2_ols"]])
    stat_c = RUN.statistic(rows[:, I["g1_c_nodet"]], rows[:, I["g2_c_nodet"]])
    p = {"ours_ct_qd": cdfs[("known", n, "qd")](stat_qd),
         "ours_ct_ols": cdfs[("known", n, "ols")](stat_ols),
         "ours_ct_qd_hac_null": cdfs[("hac", n, "qd")](stat_qd),
         "ours_ct_ols_hac_null": cdfs[("hac", n, "ols")](stat_ols),
         "ours_c_reference_nodet": cdfs[("c_ref", n, None)](stat_c)}
    rej = {k: np.clip(v, 0.0, 1.0) < ALPHA for k, v in p.items()}
    nan = {}
    for name, col in (("adf_ct", "p_adf_ct"), ("pp_ct", "p_pp_ct"), ("dfgls_ct", "p_dfgls_ct")):
        v = rows[:, I[col]]
        nan[name] = int(np.isnan(v).sum())
        rej[name] = np.nan_to_num(v, nan=1.0) < ALPHA
    return rej, stat_qd, nan


def summarize(rows, n, cdfs):
    rej, stat_qd, nan = cell_rejections(rows, n, cdfs)
    I = RUN.IDX
    return rej, stat_qd, {
        "rejection_rates": {k: rate(v) for k, v in rej.items()},
        "E_g1_std_ct_qd": float(np.mean(rows[:, I["g1_qd"]])),
        "E_g2_std_ct_qd": float(np.mean(rows[:, I["g2_qd"]])),
        "E_g1_std_c_reference": float(np.mean(rows[:, I["g1_c_nodet"]])),
        "E_g2_std_c_reference": float(np.mean(rows[:, I["g2_c_nodet"]])),
        "nan_counts_comparators": nan}


def mcnemar(a, b):
    only_a, only_b = int((a & ~b).sum()), int((~a & b).sum())
    p = float(binomtest(min(only_a, only_b), only_a + only_b, 0.5).pvalue) if only_a + only_b else 1.0
    return {"only_first": only_a, "only_second": only_b, "p_value": p}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    with open(RUN.VERIFY, encoding="utf-8") as f:
        verify = json.load(f)
    if verify.get("verdict") != "PASA":
        raise SystemExit("ct_verification_audit7.json no dice PASA: %s" % verify.get("verdict"))

    print("construyendo nulas (N_cal=%d)..." % D.N_CAL, flush=True)
    nulls = build_nulls(a.cores)
    cdfs = {k: ecdf(v) for k, v in nulls.items()}
    null_summary = {"%s_n%d%s" % (k, n, "" if d is None else "_" + d): {
        "N_cal": int(v.size), "quantile_0.05": float(np.quantile(v, ALPHA)),
        "seed": (D.null_seed(k, n, d) if k != "c_ref" else D.C_REFERENCE_NULL_SEED)}
        for (k, n, d), v in nulls.items()}

    missing = {}
    # --- tamano y V3 --------------------------------------------------------
    band = C.binomial_acceptance_region(D.N_SIM)
    size, v3_cells, by_n_stats, by_n_rej = {}, {}, {}, {}
    for n, mu in D.size_cells():
        tg = D.tag("size", n, mu)
        rows, why = load_rows(tg, D.N_SIM)
        if rows is None:
            missing[tg] = why
            continue
        rej, stat_qd, summ = summarize(rows, n, cdfs)
        summ.update({"n": n, "mu": mu, "seed_base": D.seed_base("size", n, mu)})
        size[tg] = summ
        r = summ["rejection_rates"]["ours_ct_qd"]["rate"]
        v3_cells[tg] = {"rate": r, "in_band": bool(band[0] <= r <= band[1])}
        by_n_stats.setdefault(n, {})[mu] = stat_qd
        by_n_rej.setdefault(n, {})[mu] = rej["ours_ct_qd"]
    mu_dep = {}
    for n, st in by_n_stats.items():
        if set(st) != set(D.SIZE_MUS):
            continue
        ref, rref = st[D.SIZE_MUS[0]], by_n_rej[n][D.SIZE_MUS[0]]
        mu_dep["n%d" % n] = {
            "max_rel_diff_statistic_vs_mu0": float(max(np.max(np.abs(st[m] - ref) / ref) for m in D.SIZE_MUS[1:])),
            "rejection_vectors_identical": bool(all(np.array_equal(by_n_rej[n][m], rref) for m in D.SIZE_MUS[1:]))}
    v3_complete = len(v3_cells) == len(D.size_cells()) and len(mu_dep) == len(D.SIZE_N)
    v3_pass = bool(v3_complete and all(c["in_band"] for c in v3_cells.values())
                   and all(m["max_rel_diff_statistic_vs_mu0"] <= D.REL_TOL_INVARIANCE
                           and m["rejection_vectors_identical"] for m in mu_dep.values()))

    # --- DGP 1-ct y DGP 3-ct ------------------------------------------------
    dgp1, dgp3 = {}, {}
    for kind, grid, out in (("dgp1", D.dgp1_cells(), dgp1), ("dgp3", D.dgp3_cells(), dgp3)):
        for n, param in grid:
            tg = D.tag(kind, n, param)
            rows, why = load_rows(tg, D.N_SIM)
            if rows is None:
                missing[tg] = why
                continue
            rej, _, summ = summarize(rows, n, cdfs)
            summ.update({"n": n, ("rho" if kind == "dgp1" else "r"): param,
                         "seed_base": D.seed_base(kind, n, param)})
            if kind == "dgp3":
                summ["paired_ct_qd_vs_c_reference"] = mcnemar(rej["ours_ct_qd"], rej["ours_c_reference_nodet"])
            out[tg] = summ

    v1, v2 = verify["V1_regression_c"], verify["V2_scale_invariance_ct"]
    complete = not missing
    C.atomic_write_json(OUT, {
        "provenance": C.provenance(dgp="ct_case", n_sim=D.N_SIM,
                                   seed_formula="familias 71-76, ver audit7_ct_design.py",
                                   extra_code_files=[os.path.join(C.REPO, "src", "stationarity_test",
                                                                  "deterministics.py")]),
        "design": {"theta": list(D.THETA), "R": D.R, "pilot": D.PILOT, "main_detrend": D.MAIN_DETREND,
                   "main_null": "known (paquete, sigma=1)", "secondary_null": "hac",
                   "N_cal": D.N_CAL, "N_sim": D.N_SIM, "drift": D.DRIFT, "trend_slope": D.TREND_SLOPE,
                   "comparators": "adfuller(regression='ct', AIC); arch PhillipsPerron(trend='ct'); arch DFGLS(trend='ct')"},
        "verifications": {
            "V1_regression_c": {"passed": v1["passed"], "baseline_commit": v1["baseline_commit"],
                                "max_abs_diff_statistic": v1["max_abs_diff_by_key"]["statistic"],
                                "max_abs_diff_p_value": v1["max_abs_diff_by_key"]["p_value"],
                                "n_series": v1["n_series"]},
            "V2_scale_invariance_ct": {"passed": v2["passed"],
                                       "worst_rel_diff_statistic": v2["worst_rel_diff_statistic"],
                                       "tolerance_rel": v2["tolerance_rel"]},
            "paso0_passed": verify["paso0"]["passed"],
            "V3_exact_size": {"band": list(band), "cells": v3_cells, "mu_dependence": mu_dep,
                              "complete": v3_complete, "passed": v3_pass,
                              "rule_if_failed": "el test propuesto ct se retira (regla 6) y se avisa"}},
        "nulls": null_summary,
        "size_ct_under_h0_with_drift": size,
        "dgp1_ct": dgp1,
        "dgp3_ct": dgp3,
        "missing_or_incomplete": missing,
        "complete": complete,
    })
    print("V3 tamano exacto: %s   celdas ausentes: %d" % ("PASA" if v3_pass else "FALLA", len(missing)))
    for tg, c in v3_cells.items():
        print("  %-22s %.4f %s" % (tg, c["rate"], "" if c["in_band"] else "FUERA de [%.4f, %.4f]" % band))
    print(OUT)
    if not complete:
        return 2
    return 0 if v3_pass else 3


if __name__ == "__main__":
    sys.exit(main())
