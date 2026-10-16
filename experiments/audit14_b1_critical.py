"""
Auditoria A14 - B14.1: valores criticos simulados de MSB-GLS y MZ_t-GLS para el suplemento
(protocol_audit14.md, lecturas 3 a 7). Ninguna simulacion nueva; sin numeros aleatorios.

Muestras: audit10_cal/cal_n<n>.npz (N_cal = 500 000, semilla de calibracion 42), columnas
<c|ct>|<msb|mzt> (Ng-Perron sobre residuos GLS, retardo por MAIC). Cuantil de cola inferior
numpy.nanquantile(x, alpha) (metodo lineal, la llamada de audit9_engine.rejector) para
alpha in {0.01, 0.025, 0.05, 0.10} y n in {100, 200, 500, 1000}; EE bootstrap exacto
(audit14_exact_bootstrap) y EE de Maritz-Jarrett como control.

Paso 0: columnas usadas, el 5 % calculado es igual (|D| = 0) a b101 sim_thresholds y a
bA_ma iid_quantiles; resto de columnas comunes (dfgls, adf, pp y los cuantiles RM de bA_ma),
<= 1e-12 con declaracion.

Salida: experiments/results/b1_critical_audit14.json.
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit14_common as C                                         # noqa: E402
import audit14_exact_bootstrap as EB                               # noqa: E402
import audit10_engine as E10                                       # noqa: E402

OUT = os.path.join(C.RESULTS, "b1_critical_audit14.json")
NS = (100, 200, 500, 1000)
CASES = {"c": "dm", "ct": "ct"}
LEVELS = (0.01, 0.025, C.ALPHA, 0.1)
STATS = {"msb": "MSB-GLS", "mzt": "MZ_t-GLS"}
OTHER = ("dfgls", "adf", "pp")                     # resto de columnas comunes con umbral guardado
TOL_OTHER = 10 ** -12


def existing_5pct():
    """Umbrales al 5 % ya guardados: (fuente, ruta, n, caso, columna) -> valor."""
    b101 = C.read_json("b101_theta_audit10.json")
    bA = C.read_json("bA_ma_audit12.json")
    out = []
    for n in NS:
        for case, lab in CASES.items():
            c = b101["cells"].get("%s|%d" % (lab, n))
            if c is not None:
                for p, v in c["sim_thresholds"].items():
                    out.append({"json": "b101_theta_audit10.json", "path": "cells.%s|%d.sim_thresholds.%s" % (lab, n, p),
                                "n": n, "case": case, "column": p, "value": v})
            q = bA["config"]["iid_quantiles"].get("%d|%s" % (n, case))
            if q is not None:
                for p, v in q.items():
                    col = p.replace(" (cuantil)", "")
                    out.append({"json": "bA_ma_audit12.json", "path": "config.iid_quantiles.%d|%s.%s" % (n, case, p),
                                "n": n, "case": case, "column": col, "value": v})
    return out


def main():
    t0 = time.time()
    ex = existing_5pct()
    samples, values, paso0 = {}, [], []
    for n in NS:
        path = os.path.join(E10.CKPT_CAL, "cal_n%d.npz" % n)
        rows, cols, info = E10.load_cal(n)
        I = {c: i for i, c in enumerate(cols)}
        samples[str(n)] = {"path": C.rel(path), "sha256": C.sha256_file(path), "rows": int(rows.shape[0]),
                           "nan": {"%s|%s" % (case, p): int(np.isnan(rows[:, I["%s|%s" % (case, p)]]).sum())
                                   for case in CASES for p in STATS}}
        for case in CASES:
            for p in STATS:
                x = rows[:, I["%s|%s" % (case, p)]]
                xf = x[np.isfinite(x)]
                for a in LEVELS:
                    q = float(np.nanquantile(x, a))
                    eb = EB.exact_bootstrap(xf, a)
                    values.append({"stat": p, "stat_label": STATS[p], "case": case, "n": n, "alpha": a,
                                   "critical_value": q, "bootstrap_se": eb["se"], "se_maritz_jarrett": eb["se_maritz_jarrett"],
                                   "se_ratio_mj": eb["se_maritz_jarrett"] / eb["se"],
                                   "bootstrap_mean_minus_estimate": eb["bootstrap_mean_minus_estimate"],
                                   "quantile_eb_equals_nanquantile": eb["quantile"] == q,
                                   "truncation_ok": eb["truncation_ok"], "mass": [eb["mass_r"], eb["mass_r1"], eb["mass_mj"]],
                                   "gap_truncation_residual": eb["gap_truncation_residual"],
                                   "N_cal": int(xf.size), "nan": int(x.size - xf.size), "sample": C.rel(path),
                                   "new": a != C.ALPHA})
        for e in ex:
            if e["n"] != n:
                continue
            key = "%s|%s" % (e["case"], e["column"])
            if key not in I:
                e["common"] = False
                continue
            rec = float(np.nanquantile(rows[:, I[key]], C.ALPHA))
            used = e["column"] in STATS
            d = abs(rec - e["value"])
            paso0.append(dict(e, common=True, used=used, recomputed=rec, abs_diff=d,
                              passes=(d == 0) if used else (d <= TOL_OTHER)))
        del rows
    not_common = [dict(e) for e in ex if e.get("common") is False]
    used = [r for r in paso0 if r["used"]]
    other = [r for r in paso0 if not r["used"]]
    out = {"provenance": C.provenance(__file__, seed_family=None), "reading": "protocol_audit14.md, lecturas 3 a 7",
           "config": {"n": list(NS), "cases": list(CASES), "levels": list(LEVELS), "stats": STATS, "N_cal": E10.N_CAL,
                      "cal_seed": 42, "quantile": "numpy.nanquantile(x, alpha), metodo lineal (audit9_engine.rejector)",
                      "tail": "inferior: se rechaza si el estadistico < q_alpha",
                      "lag_selection": "MAIC de Ng-Perron (audit8_unitroot.np_statistics), residuos GLS",
                      "bootstrap": "EE bootstrap exacto (B -> infinito) del cuantil lineal; audit14_exact_bootstrap",
                      "random_numbers": False, "family": None},
           "samples": samples, "values": values,
           "paso0": {"used_columns": used, "other_columns": other, "not_common": not_common,
                     "used_max_abs_diff": max(r["abs_diff"] for r in used), "used_n": len(used),
                     "other_max_abs_diff": max(r["abs_diff"] for r in other), "other_n": len(other),
                     "other_nonzero": [r for r in other if r["abs_diff"] != 0],
                     "passes": all(r["passes"] for r in paso0),
                     "all_used_5pct_covered": sorted({(v["case"], v["n"], v["stat"]) for v in values}) ==
                     sorted({(r["case"], r["n"], r["column"]) for r in used})},
           "checks": {"truncation_ok": all(v["truncation_ok"] for v in values),
                      "quantile_eb_equals_nanquantile": all(v["quantile_eb_equals_nanquantile"] for v in values),
                      "no_nan": all(v["nan"] == 0 for v in values),
                      "n_values": len(values), "n_new": sum(1 for v in values if v["new"])},
           "elapsed_sec": time.time() - t0}
    C.write_result(OUT, out, __file__)
    print("valores: %d (nuevos %d); truncamiento %s; cuantil identico %s; NaN %s" % (
        len(values), out["checks"]["n_new"], out["checks"]["truncation_ok"], out["checks"]["quantile_eb_equals_nanquantile"],
        out["checks"]["no_nan"]))
    print("Paso 0 columnas usadas: %d, max |D| = %.3e; resto: %d, max |D| = %.3e; pasa %s; cubre los 16: %s" % (
        len(used), out["paso0"]["used_max_abs_diff"], len(other), out["paso0"]["other_max_abs_diff"], out["paso0"]["passes"],
        out["paso0"]["all_used_5pct_covered"]))
    for v in values:
        print("  %-4s %-2s n=%4d a=%-5g q=% .6f se=%.2e mj/se=%.3f" % (v["stat"], v["case"], v["n"], v["alpha"], v["critical_value"],
                                                                     v["bootstrap_se"], v["se_ratio_mj"]))
    print("%.1f s" % out["elapsed_sec"])
    return 0 if out["paso0"]["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
