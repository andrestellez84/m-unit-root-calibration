"""
Auditoria A15 - B15.3: fixed-b sobre MSB-B (protocol_audit15.md, lecturas 3.1-3.7; enmienda 2,
seccion 4; enmienda 3, E3.5). Confirmado por escrito por el autor (enmienda 3, E3.5).

Configuraciones: b in {0.1, 0.3, 1.0} (B = min(ceil(b n), n - 1)) y LLSW (B = ceil(1.3 n^{1/2}) - 1);
sigma2 por FFT (audit15_fixedb) y MSB-B = audit9_engine.rmgls(y, n, 0, sigma2, caso).
  - Calibracion (familia 155): paseo aleatorio gaussiano, N_cal = 1e5 por n in {100, 200, 500};
    los mismos caminos para los dos casos y las cuatro configuraciones; en n = 200, caso c,
    tambien MSB-B con Andrews (gls_t0) y la variante (b) (s2_AR de la MAIC GLS).
  - Tamano (familia 156): las 36 celdas de tab:serial, N = 2e4.
  - Potencia (familia 157): DGP 1, AR(1) con errores iid, rho in {0.80, ..., 0.99}, n = 200, caso c,
    N = 5000; la nula iid es la de la calibracion, asi que la potencia calibrada es la ajustada.
Rechazo: FDA empirica de la calibracion (cdf_from_null_stats) < 0.05, la regla de MSB-B en A12.
Cota DKW: eps = [ln(2/0.05)/(2 N_cal)]^{1/2}, probabilidad 0.95.
Checkpoints en checkpoints/audit15_b3 (reanudable).

Salida: experiments/results/b3_fixedb_audit15.json.
"""
import argparse
import math
import os
import sys
import time
import warnings
from functools import partial

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit15_design as D                                         # noqa: E402
import audit15_fixedb as FB                                        # noqa: E402
import audit12_runner as R12                                       # noqa: E402
import audit12_unitroot as P12                                     # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
import audit9_engine as E9                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "b3_fixedb_audit15.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit15_b3")
FC, FS, FP = C.FAMILY["CAL3"], C.FAMILY["SIZE3"], C.FAMILY["POWER3"]
NAMES = [k for k, _ in FB.configs()]
PRED_B = ("b=0.1", "b=0.3", "b=1")          # prediccion de 14cbca7: b in {0.1, 0.3, 1.0}
DKW_LEVEL = C.ALPHA
M_THRESHOLD = 0.02                           # umbral de la prediccion registrada (14cbca7)
CAL_COLS = ["c|" + k for k in NAMES] + ["ct|" + k for k in NAMES] + ["c|gls_t0", "c|glsb_t0"]
POW_COLS = list(NAMES) + ["gls_t0", "glsb_t0"]
EXTRA_N = 200


def stats4(y, n, case):
    s2 = FB.s2_all(y)
    return [E9.rmgls(y, n, 0.0, s2[k][1], case) for k in NAMES]


def extras(y, n):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        npr = U._safe(lambda: U.np_statistics(y, "c"), 1)
    glsb = E9.rmgls(y, n, 0.0, npr["s2_ar"], "c") if isinstance(npr, dict) else float("nan")
    return [E9.rmgls(y, n, 0.0, E9.hac_sigma_sq(y), "c"), glsb]


def cal_row(n, cell, i):
    y = P12.null_path(("ma", 0.0), n, C.rep_rng(FC, cell, i))
    s2 = FB.s2_all(y)
    row = [E9.rmgls(y, n, 0.0, s2[k][1], "c") for k in NAMES] + [E9.rmgls(y, n, 0.0, s2[k][1], "ct") for k in NAMES]
    return row + (extras(y, n) if n == EXTRA_N else [float("nan")] * 2)


def size_row(err, n, case, cell, i):
    y = P12.null_path(err, n, C.rep_rng(FS, cell, i))
    return stats4(y, n, case)


def pow_row(rho, cell, i):
    n = EXTRA_N
    y = P12.alt_path(("ma", 0.0), n, rho, C.rep_rng(FP, cell, i))
    return stats4(y, n, "c") + extras(y, n)


def size_cells():
    out = []
    for e in P12.ERRORS:
        for n in D.A_N:
            for c in D.CASES:
                out.append((D.size_cell(e, n, c), e, n, c))
    return out


def run(cores, t_block, max_seconds, resume_cmd):
    for n in D.CAL3_N:
        name = "cal3_n%d" % n
        R12.run_cell(name, D.N_CAL3, partial(cal_row, n, D.cell_index(FC, name)), len(CAL_COLS), CKPT, cores, t_block,
                     max_seconds, resume_cmd, per_core=250)
    for name, e, n, c in size_cells():
        R12.run_cell("sz3_" + name, D.N_SIZE3, partial(size_row, e, n, c, D.cell_index(FS, name)), len(NAMES), CKPT, cores,
                     t_block, max_seconds, resume_cmd, per_core=250)
    for rho, name in zip(D.POW3_RHO, D.CELLS[FP]):
        R12.run_cell(name, D.N_POW3, partial(pow_row, rho, D.cell_index(FP, name)), len(POW_COLS), CKPT, cores, t_block,
                     max_seconds, resume_cmd, per_core=250)


def rate(mask, region=None):
    return C.C14.C13.rate_record(mask, region)


def analyze(elapsed):
    from stationarity_test.empirical_eigenvalues import cdf_from_null_stats
    region = C.exact_region(D.N_SIZE3)
    cal, cdfs = {}, {}
    for n in D.CAL3_N:
        rows, el = R12.load_cell(CKPT, "cal3_n%d" % n, D.N_CAL3)
        for j, col in enumerate(CAL_COLS):
            x = rows[:, j]
            if np.all(np.isnan(x)):
                continue
            key = "%d|%s" % (n, col)
            cdfs[key] = cdf_from_null_stats(x[np.isfinite(x)])
            cal[key] = {"N_cal": int(np.isfinite(x).sum()), "nan": int(np.isnan(x).sum()), "q05": float(np.nanquantile(x, C.ALPHA)),
                        "median": float(np.nanmedian(x))}
    eps = math.sqrt(math.log(2.0 / DKW_LEVEL) / (2.0 * D.N_CAL3))

    def rej(x, key):
        return np.clip(cdfs[key](np.nan_to_num(x, nan=np.inf)), 0.0, 1.0) < C.ALPHA
    size = {}
    for name, e, n, c in size_cells():
        rows, _ = R12.load_cell(CKPT, "sz3_" + name, D.N_SIZE3)
        size[name] = {"err": list(e), "err_tag": P12.err_tag(e), "n": n, "case": c,
                      "bandwidths": {k: FB.bandwidth(n, b) for k, b in FB.configs()},
                      "rates": {k: rate(rej(rows[:, j], "%d|%s|%s" % (n, c, k)), region) for j, k in enumerate(NAMES)}}
    nz = [k for k, v in size.items() if v["err_tag"] != "ma_0"]
    iid = [k for k, v in size.items() if v["err_tag"] == "ma_0"]
    summ = {}
    for k in NAMES:
        dev = [abs(size[c]["rates"][k]["rate"] - C.ALPHA) for c in nz]
        worst = max(nz, key=lambda c: abs(size[c]["rates"][k]["rate"] - C.ALPHA))
        summ[k] = {"D": float(np.mean(dev)), "M": float(max(dev)), "argmax": worst, "cells": len(nz),
                   "iid_in_region": sum(1 for c in iid if size[c]["rates"][k]["in_region"]), "iid_cells": len(iid)}
    power = {}
    for rho, name in zip(D.POW3_RHO, D.CELLS[FP]):
        rows, _ = R12.load_cell(CKPT, name, D.N_POW3)
        dec = {}
        for j, k in enumerate(POW_COLS):
            dec[k] = rej(rows[:, j], "%d|c|%s" % (EXTRA_N, k))
        rec = {"rho": rho, "rates": {k: rate(v) for k, v in dec.items()}, "vs_andrews": {}, "vs_b": {}}
        for k in NAMES:
            for ref, lab in (("gls_t0", "vs_andrews"), ("glsb_t0", "vs_b")):
                d = dec[k].astype(float) - dec[ref].astype(float)
                rec[lab][k] = {"diff_pp": float(d.mean()) * C.PP, "se_pp": float(d.std(ddof=1) / math.sqrt(d.size)) * C.PP,
                               "mcnemar": C.mcnemar_exact(dec[k], dec[ref])}
        power[name] = rec
    return {"calibration": cal, "dkw_eps": eps, "size": size, "size_summary": summ,
            "prediction": {"rule": "fixed-b controla el tamano si, para algun b in {0.1, 0.3, 1.0}, M(b) <= 0.02 sobre las 30 celdas "
                                   "con psi != 0 (14cbca7)", "threshold": M_THRESHOLD, "b_evaluated": list(PRED_B),
                           "M_by_b": {k: summ[k]["M"] for k in PRED_B}, "controls": [k for k in PRED_B if summ[k]["M"] <= M_THRESHOLD],
                           "outcome": any(summ[k]["M"] <= M_THRESHOLD for k in PRED_B),
                           "llsw_reported_apart": {"M": summ["LLSW"]["M"], "D": summ["LLSW"]["D"]}},
            "power": power, "exact_region_20000": region, "elapsed_compute_sec": elapsed}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=min(os.cpu_count() or 1, 16))
    ap.add_argument("--max-hours", type=float, default=12)
    a = ap.parse_args()
    t0 = time.time()
    R12.warm(a.cores)
    run(a.cores, t0, a.max_hours * 3600, "python experiments/audit15_b3_fixedb.py")
    res = analyze(time.time() - t0)
    out = {"provenance": C.provenance(__file__, seed_family=[FC, FS, FP]),
           "reading": "protocol_audit15.md, 3.1-3.7; enmienda 2, seccion 4; enmienda 3, E3.5",
           "config": {"configs": {k: ("ceil(%g n)" % b if b is not None else "ceil(1.3 n^(1/2)) - 1") for k, b in FB.configs()},
                      "N_cal": D.N_CAL3, "cal_n": list(D.CAL3_N), "N_size": D.N_SIZE3, "N_power": D.N_POW3, "power_rho": list(D.POW3_RHO),
                      "rejection": "FDA empirica de la calibracion (cdf_from_null_stats) < 0.05", "cores": a.cores},
           **res, "elapsed_sec": time.time() - t0}
    C.write_result(OUT, out, __file__)
    print("DKW eps = %.4f" % res["dkw_eps"])
    for k, v in res["size_summary"].items():
        print("%-6s D = %.4f  M = %.4f (%s)  iid en region %d/%d" % (k, v["D"], v["M"], v["argmax"], v["iid_in_region"], v["iid_cells"]))
    print("prediccion:", res["prediction"]["outcome"], res["prediction"]["controls"])
    for name, r in res["power"].items():
        print(name, {k: round(v["rate"], 3) for k, v in r["rates"].items()})
    print("%.0f s" % out["elapsed_sec"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
