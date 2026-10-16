"""
Auditoria A7 - Bloque 2: verificaciones previas del caso "ct" (PUERTA).

V1 Regresion dura. compute_statistic con deterministics="c" (por omision) sobre
   100 series, en dos procesos limpios: uno importa el paquete de src/ del
   commit anterior al que anadio deterministics.py (git archive) y otro el
   actual. Exigido: max|diff| = 0.0 en statistic y p_value, y en toda clave
   numerica del resultado.
V2 Invariancia de escala. El estadistico "ct" (qd y ols) sobre Y y sobre
   a*Y + b + c*t, a in {0.1, 10}, (b, c) en dos pares, n in {200, 500, 1000}.
   Exigido: |diff| relativo <= 1e-9 (tolerancia registrada en el diseno).
Paso 0 (regla 5)
   - generadores: 50 series por celda; la parte sin componente determinista
     identica a power_comparison.py y la serie observada identica a esa parte
     mas el termino determinista. Exigido max|diff| = 0.
   - componentes: la ruta del runner frente a compute_statistic (ct qd, ct ols
     y c sobre la parte sin determinista), 50 series por n. Exigido <= 1e-12.
   - semillas: solape entre todas las bases del Bloque 2.

Si V1 o V2 fallan se detiene todo y se avisa (puerta del prompt).
Salida: experiments/results/ct_verification_audit7.json. Exit 0 PASA, 3 FALLA.

Uso: python experiments/audit7_ct_verify.py
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                   # noqa: E402
import audit7_ct_design as D                                # noqa: E402
import audit7_ct_runner as RUN                              # noqa: E402
from power_comparison import generate_ar1, generate_rw_break_variance  # noqa: E402
from stationarity_test.statistic import compute_statistic   # noqa: E402

OUT = os.path.join(C.RESULTS, "ct_verification_audit7.json")
DET_FILE = "src/stationarity_test/deterministics.py"

CHILD = r'''
import json, os, sys
import numpy as np
src, series_path, out_path, theta0, theta1, R = sys.argv[1:7]
sys.path.insert(0, src)
import stationarity_test
from stationarity_test.statistic import compute_statistic
theta = (float(theta0), float(theta1))
with open(series_path) as f:
    series = json.load(f)
rows = []
for y in series:
    r = compute_statistic(np.asarray(y, dtype=np.float64), theta, float(R))
    rows.append({k: float(v) for k, v in r.items() if isinstance(v, (int, float, np.integer, np.floating))})
with open(out_path, "w") as f:
    json.dump({"module_file": os.path.abspath(stationarity_test.__file__), "rows": rows}, f)
'''


def baseline_commit():
    added = C._git("log", "--diff-filter=A", "--format=%H", "--", DET_FILE).splitlines()
    if not added:
        raise SystemExit("%s no esta commiteado: commitea el codigo antes de verificar" % DET_FILE)
    return C._git("rev-parse", added[-1] + "^"), added[-1]


def run_child(src_dir, series_path, out_path):
    proc = subprocess.run([sys.executable, "-c", CHILD, src_dir, series_path, out_path,
                           repr(D.THETA[0]), repr(D.THETA[1]), repr(D.R)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("proceso de regresion fallo:\n%s" % proc.stderr[-3000:])
    with open(out_path, encoding="utf-8") as f:
        d = json.load(f)
    if not os.path.abspath(d["module_file"]).startswith(os.path.abspath(src_dir)):
        raise SystemExit("el proceso importo %s, no el paquete de %s" % (d["module_file"], src_dir))
    return d


def v1_regression(tmp):
    base, added = baseline_commit()
    tar_bytes = subprocess.run(["git", "archive", "--format=tar", base, "src"], cwd=C.REPO,
                               capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
        tf.extractall(os.path.join(tmp, "baseline"))
    sb = C.seed_base(D.FAM_VERIFY, 0)
    series = []
    for i in range(D.N_REGRESSION):
        n = D.NULL_N[i % len(D.NULL_N)]
        rng = np.random.default_rng(sb + i)
        y = generate_rw_break_variance(n=n, ratio=1.0, rng=rng) if i % 2 == 0 \
            else generate_ar1(n=n, rho=0.93, rng=rng)
        series.append(y.tolist())
    sp = os.path.join(tmp, "series.json")
    with open(sp, "w") as f:
        json.dump(series, f)
    old = run_child(os.path.join(tmp, "baseline", "src"), sp, os.path.join(tmp, "old.json"))
    new = run_child(os.path.join(C.REPO, "src"), sp, os.path.join(tmp, "new.json"))
    keys = sorted(set(old["rows"][0]) | set(new["rows"][0]))
    diffs = {}
    for k in keys:
        a = np.array([r.get(k, np.nan) for r in old["rows"]])
        b = np.array([r.get(k, np.nan) for r in new["rows"]])
        same_nan = np.array_equal(np.isnan(a), np.isnan(b))
        diffs[k] = float(np.nanmax(np.abs(a - b))) if same_nan else float("inf")
    ok = all(v == 0.0 for v in diffs.values())
    return {"baseline_commit": base, "commit_adding_deterministics": added,
            "n_series": D.N_REGRESSION, "seed_formula": "76*10^8 + i; n cicla 200/500/1000; RW si i par, AR(0.93) si impar",
            "max_abs_diff_by_key": diffs, "passed": ok,
            "golden_baseline_rows": old["rows"]}


def v2_invariance():
    sb = C.seed_base(D.FAM_VERIFY, 0) + 50000
    worst_rel, worst_p, by = 0.0, 0.0, {}
    for n in D.NULL_N:
        t = np.arange(n + 1, dtype=np.float64)
        ys = [D.generate("dgp1", n, 0.93, sb, i)[0] for i in range(10)]
        ys += [D.generate("dgp3", n, 2.0, sb, 100 + i)[0] for i in range(10)]
        for d in D.DETRENDS:
            wr = wp = 0.0
            for y in ys:
                ref = compute_statistic(y, D.THETA, D.R, andrews_pilot=D.PILOT,
                                        deterministics="ct", detrend=d)
                for a in D.INVARIANCE_A:
                    for b, c in D.INVARIANCE_BC:
                        r = compute_statistic(a * y + b + c * t, D.THETA, D.R, andrews_pilot=D.PILOT,
                                              deterministics="ct", detrend=d)
                        wr = max(wr, abs(r["statistic"] - ref["statistic"]) / ref["statistic"])
                        wp = max(wp, abs(r["p_value"] - ref["p_value"]))
            by["n%d_%s" % (n, d)] = {"max_rel_diff_statistic": wr, "max_abs_diff_p_value": wp}
            worst_rel, worst_p = max(worst_rel, wr), max(worst_p, wp)
    return {"a": list(D.INVARIANCE_A), "b_c": [list(x) for x in D.INVARIANCE_BC],
            "series_per_n": 20, "tolerance_rel": D.REL_TOL_INVARIANCE,
            "worst_rel_diff_statistic": worst_rel, "worst_abs_diff_p_value": worst_p,
            "by_n_detrend": by, "passed": bool(worst_rel <= D.REL_TOL_INVARIANCE)}


def paso0():
    gen, worst = {}, 0.0
    for kind, grid in (("size", D.size_cells()), ("dgp1", D.dgp1_cells()), ("dgp3", D.dgp3_cells())):
        for n, param in grid:
            sb = D.seed_base(kind, n, param)
            t = np.arange(n + 1, dtype=np.float64)
            d_base = d_obs = 0.0
            for i in range(D.N_PAIRING):
                Y, base = D.generate(kind, n, param, sb, i)
                rng = np.random.default_rng(sb + i)
                if kind == "dgp1":
                    ref, slope = generate_ar1(n=n, rho=param, rng=rng), D.TREND_SLOPE
                elif kind == "size":
                    ref, slope = generate_rw_break_variance(n=n, ratio=1.0, rng=rng), param
                else:
                    ref, slope = generate_rw_break_variance(n=n, ratio=param, rng=rng), D.DRIFT
                d_base = max(d_base, float(np.max(np.abs(base - ref))))
                d_obs = max(d_obs, float(np.max(np.abs(Y - (ref + slope * t)))))
            gen[D.tag(kind, n, param)] = {"seed_base": sb, "max_abs_diff_base": d_base,
                                          "max_abs_diff_observed": d_obs}
            worst = max(worst, d_base, d_obs)

    comp, worst_c = {}, 0.0
    for n in D.NULL_N:
        sb = D.seed_base("size", n, None)
        m = {}
        for i in range(D.N_PAIRING):
            Y, base = D.generate("size", n, D.DRIFT, sb, i)
            r = RUN.row("size", n, D.DRIFT, sb, i)
            for label, series, kw, cols in (("ct_qd", Y, {"deterministics": "ct", "detrend": "qd"}, ("g1_qd", "g2_qd")),
                                            ("ct_ols", Y, {"deterministics": "ct", "detrend": "ols"}, ("g1_ols", "g2_ols")),
                                            ("c_nodet", base, {}, ("g1_c_nodet", "g2_c_nodet"))):
                ref = compute_statistic(series, D.THETA, D.R, andrews_pilot=D.PILOT, **kw)
                dd = max(abs(r[RUN.IDX[cols[0]]] - ref["g1_std"]), abs(r[RUN.IDX[cols[1]]] - ref["g2_std"]))
                m[label] = max(m.get(label, 0.0), dd)
        comp["n%d" % n] = m
        worst_c = max(worst_c, *m.values())

    overlap = C.seed_overlap_report(D.all_seed_bases(), D.N_CAL)
    ok = (worst == 0.0 and worst_c <= D.COMPONENT_TOL
          and overlap["exact_collisions"] == 0 and overlap["overlapping_pairs"] == 0)
    return {"generators": {"series_per_cell": D.N_PAIRING, "worst": worst, "cells": gen},
            "components_runner_vs_compute_statistic": {"tolerance": D.COMPONENT_TOL,
                                                       "worst": worst_c, "by_n": comp},
            "seed_overlap": overlap,
            "deliberate_common_random_numbers": "tamano: la misma base por n para mu in %s" % list(D.SIZE_MUS),
            "passed": bool(ok)}


def main():
    tmp = tempfile.mkdtemp(prefix="a7ct_")
    try:
        print("[V1] regresion dura de deterministics='c'", flush=True)
        v1 = v1_regression(tmp)
        print("     max|diff| statistic=%s p_value=%s  -> %s"
              % (v1["max_abs_diff_by_key"].get("statistic"), v1["max_abs_diff_by_key"].get("p_value"),
                 "PASA" if v1["passed"] else "FALLA"), flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("[V2] invariancia de escala de 'ct'", flush=True)
    v2 = v2_invariance()
    print("     peor |diff| relativo = %.3e (tol %.0e)  -> %s"
          % (v2["worst_rel_diff_statistic"], D.REL_TOL_INVARIANCE, "PASA" if v2["passed"] else "FALLA"), flush=True)
    print("[P0] apareamiento, componentes y semillas", flush=True)
    p0 = paso0()
    print("     generadores %.1e | componentes %.1e | colisiones %d, solapes %d  -> %s"
          % (p0["generators"]["worst"], p0["components_runner_vs_compute_statistic"]["worst"],
             p0["seed_overlap"]["exact_collisions"], p0["seed_overlap"]["overlapping_pairs"],
             "PASA" if p0["passed"] else "FALLA"), flush=True)

    gate = v1["passed"] and v2["passed"]
    verdict = "PASA" if (gate and p0["passed"]) else "FALLA"
    C.atomic_write_json(OUT, {
        "provenance": C.provenance(dgp="ct_verification", n_sim=D.N_REGRESSION,
                                   seed_formula="ver audit7_ct_design.py (familias 71-76)",
                                   extra_code_files=[os.path.join(C.REPO, DET_FILE)]),
        "V1_regression_c": v1, "V2_scale_invariance_ct": v2, "paso0": p0,
        "gate_v1_v2_passed": bool(gate), "verdict": verdict})
    print("VEREDICTO: %s -> %s" % (verdict, OUT))
    return 0 if verdict == "PASA" else 3


if __name__ == "__main__":
    sys.exit(main())
