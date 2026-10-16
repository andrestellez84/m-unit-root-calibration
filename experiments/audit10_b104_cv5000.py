"""
Auditoria A10 - B10.4: cierre de la anomalia de valores criticos a n = 5000.

Celda: demeaned, n = 5000, alpha = 0.05, RM-GLS theta in {0.1, 0.2}, calibracion
hac. Cinco replicas independientes de N_cal = 100 000 (familia 114, celdas
cv5000_r<k>). Valor critico = np.quantile(., 0.05) (convencion de B9.7).
Valores previos de la misma celda: tabla de B9.7 (cv), auditoria cruzada de B9.7
(cvx), calibracion de A9 con semilla 42 (audit9_cal/cal_n5000.npz, N_cal = 50 000)
y B7 de A8. Regla de cierre: protocol_audit10.md, lectura 11.

Checkpoints en npz por trozo de 20 000 replicas (reanudable).
Salida: experiments/results/b104_cv5000_audit10.json.
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
import audit9_engine as E                                          # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402

FAM = C.FAMILY["B10.4"]
CKPT = os.path.join(C.CKPT_ROOT, "audit10_b104")
OUT = os.path.join(C.RESULTS, "b104_cv5000_audit10.json")
THETAS = (0.1, 0.2)
ALPHA_CV = 0.05
CHUNK = 20000
SD_K = 3.0
COLS = ("s2",) + tuple(E.tname(t) for t in THETAS)


def rows_for(k, idx):
    out = []
    for i in idx:
        y = D.cv5000_path(k, i)
        s2 = hac_sigma_sq(y)
        out.append([s2] + [E.rmgls(y, D.CV_N, t, s2, "c") for t in THETAS])
    return out


def replica_rows(k, cores, t_block, max_seconds, resume):
    tag = "cv5000_r%d" % k
    os.makedirs(CKPT, exist_ok=True)
    parts = []
    for i0 in range(0, D.N_CV, CHUNK):
        p = os.path.join(CKPT, "%s_i%06d.npz" % (tag, i0))
        if os.path.exists(p):
            with np.load(p) as z:
                if bool(z["complete"]) and z["rows"].shape == (min(CHUNK, D.N_CV - i0), len(COLS)):
                    parts.append(z["rows"])
                    continue
        if time.time() - t_block > max_seconds:
            raise C.BudgetExhausted("%s: tope antes de i0=%d.\nREANUDAR CON:\n  %s" % (tag, i0, resume))
        t0 = time.time()
        idx = list(range(i0, min(i0 + CHUNK, D.N_CV)))
        split = [idx[j::cores] for j in range(cores)]
        res = Parallel(n_jobs=cores, backend="loky")(delayed(rows_for)(k, s) for s in split)
        rows = np.zeros((len(idx), len(COLS)))
        for s, r in zip(split, res):
            rows[np.array(s) - i0] = r
        tmp = p + ".tmp.npz"
        np.savez(tmp, rows=rows, complete=True, elapsed=time.time() - t0)
        os.replace(tmp, p)
        print("    %s i0=%d  %.1f s" % (tag, i0, time.time() - t0), flush=True)
        parts.append(rows)
    return np.vstack(parts)


def previous(theta):
    key = "%g" % ALPHA_CV
    b97 = C.read_json("b97_critical_values_audit9.json")
    cell = "dm|%g|%d" % (theta, D.CV_N)
    out = {"b97_cv": {"value": b97["table"][cell]["cv"][key], "se": b97["table"][cell]["se"][key],
                      "source": "experiments/results/b97_critical_values_audit9.json",
                      "path": "table.%s.cv.%s" % (cell, key), "N_cal": b97["config"]["N_cal"], "family": 107}}
    by = b97["cross_seed_audit"]["by_cell"]
    if cell in by:
        out["b97_cvx"] = {"value": by[cell]["cv_independent"][key],
                          "source": "experiments/results/b97_critical_values_audit9.json",
                          "path": "cross_seed_audit.by_cell.%s.cv_independent.%s" % (cell, key),
                          "N_cal": b97["config"]["N_cal"], "family": 107}
    p42 = os.path.join(C.CKPT_ROOT, "audit9_cal", "cal_n%d.npz" % D.CV_N)
    if os.path.exists(p42):
        with np.load(p42) as z:
            cols = [str(c) for c in z["cols"]]
            x = z["rows"][:, cols.index("c|%s" % E.tname(theta))]
        out["a9_seed42"] = {"value": float(np.quantile(x, ALPHA_CV)), "N_cal": int(x.size), "family": "semilla 42",
                            "source": C.rel(p42), "path": "rows[:, c|%s], np.quantile(., 0.05)" % E.tname(theta),
                            "source_sha256": C.sha256_file(p42)}
    a8 = C.read_json("b7_critical_values_audit8.json")["table"].get("dm|gls|%g|%d" % (theta, D.CV_N))
    if a8:
        out["a8_b7"] = {"value": a8["cv"][key], "source": "experiments/results/b7_critical_values_audit8.json",
                        "path": "table.dm|gls|%g|%d.cv.%s" % (theta, D.CV_N, key), "family": 97}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=C.BLOCK_MAX_SECONDS)
    a = ap.parse_args()
    resume = "python experiments/audit10_b104_cv5000.py --cores %d" % a.cores
    t_block = time.time()
    E.warm(a.cores)
    data = {}
    try:
        for k in D.CV_REPLICAS:
            print("[REPLICA] cv5000_r%d" % k, flush=True)
            data[k] = replica_rows(k, a.cores, t_block, a.max_seconds, resume)
    except C.BudgetExhausted as exc:
        print("  [TOPE] %s" % exc, flush=True)
        return 2
    res = {}
    for th in THETAS:
        col = COLS.index(E.tname(th))
        vals = [float(np.quantile(data[k][:, col], ALPHA_CV)) for k in D.CV_REPLICAS]
        mean, sd = float(np.mean(vals)), float(np.std(vals, ddof=1))
        lo, hi = min(vals), max(vals)
        prev = previous(th)
        for v in prev.values():
            v["in_range"] = bool(lo <= v["value"] <= hi)
            v["dev_in_sd"] = (v["value"] - mean) / sd
            v["within_3sd"] = bool(abs(v["dev_in_sd"]) <= SD_K)
            v["consistent"] = bool(v["in_range"] or v["within_3sd"])
        res["%g" % th] = {"replicas": {"cv5000_r%d" % k: v for k, v in zip(D.CV_REPLICAS, vals)},
                          "mean": mean, "sd": sd, "min": lo, "max": hi, "range": hi - lo,
                          "previous": prev,
                          "b97_both_consistent": bool(prev["b97_cv"]["consistent"] and prev.get("b97_cvx", {"consistent": True})["consistent"])}
    closed = all(v["b97_both_consistent"] for v in res.values())
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "config": {"case": "dm", "n": D.CV_N, "alpha": ALPHA_CV, "thetas": list(THETAS), "N_cal": D.N_CV,
                      "replicas": len(D.CV_REPLICAS), "calibration": "hac", "anchor": "gls",
                      "rule": "protocol_audit10.md, lectura 11 (rango de las replicas o |desv.| <= 3 DT)"},
           "by_theta": res, "anomaly_closed": closed, "elapsed_sec": round(time.time() - t_block, 1)}
    C.write_result(OUT, out, __file__)
    for th, v in res.items():
        print(th, [round(x, 4) for x in v["replicas"].values()], "media %.4f DT %.4f" % (v["mean"], v["sd"]),
              {k: (round(p["value"], 4), p["consistent"]) for k, p in v["previous"].items()})
    print("anomalia cerrada:", closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
