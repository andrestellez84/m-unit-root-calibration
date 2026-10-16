"""
Auditoria A8 - B1: compuerta B1-NP (DURA) de la enmienda 1.

(a) MZt y MSB, demeaned y tendencia, a +-3% de Ng-Perron (2001) a n = 2000:
    se traslada de b1_validation_audit8.json (V5).
(b) Identidad MZt = MZa * MSB trayectoria a trayectoria: MZt del codigo frente a
    la forma cerrada (T^-1 yT^2 - s2) / (2 sqrt(S s2)), max |delta| relativo <= 1e-12,
    sobre los caminos de V5.
(c) Convergencia interna: cuantiles al 5% de MZt y MSB a T = 2001 (V5) y
    T = 10001 (b1_np_diagnostic_audit8.json) a <= 2 errores estandar combinados.
(d) Convencion de indices: lineas de audit8_unitroot.py que implementan
    MZa = (T^-1 yt_T^2 - s2) / (2 T^-2 sum_{t=1}^{T} yt_{t-1}^2) y
    MSB = (T^-2 sum_{t=1}^{T} yt_{t-1}^2 / s2)^{1/2}; los ocho cuantiles al 5% a
    n = 2000 recalculados con la convencion alternativa (yt_{T-1} y suma hasta
    T - 1) sobre los mismos caminos.

Correspondencia de indices (d): el articulo indexa la muestra t = 1..T y la suma
sum_{t=1}^{T} yt_{t-1}^2 = yt_0^2 + sum_{t=1}^{T-1} yt_t^2 con yt_0 = 0 (condicion
inicial). El codigo guarda los T puntos en y[0..T-1] (y[j] = y_{j+1}), usa
yT = yt[T-1] (= yt_T) y S = T^-2 sum_{j=0}^{T-2} yt[j]^2 (= T^-2 sum_{t=1}^{T-1} yt_t^2),
es decir, la formula del articulo con yt_0 = 0 y T = numero de observaciones.
La alternativa usa yt[T-2] (= yt_{T-1}) y la suma hasta T - 1 del articulo
(= T^-2 sum_{j=0}^{T-3} yt[j]^2).

Salida: experiments/results/b1_np_gate_audit8.json.
Uso: python experiments/audit8_b1_np_gate.py --cores 14
"""
import argparse
import math
import os
import re
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
import audit8_b1_validate as V                                     # noqa: E402

OUT = os.path.join(C.RESULTS, "b1_np_gate_audit8.json")
FAM = C.FAMILY["B1"]
KEEP = ("MZt", "MSB")
IDENTITY_TOL = 1e-12
SE_MULT = 2.0
T_LARGE = "10001"
CODE_PATTERNS = {"S": r"S = float\(yt\[:-1\] @ yt\[:-1\]\) / T \*\* 2",
                 "yT2": r"yT2 = yt\[-1\] \*\* 2 / T",
                 "MZa": r"mza = \(yT2 - s2\) / \(2\.0 \* S\)",
                 "MSB": r"msb = math\.sqrt\(S / s2\)",
                 "MZt": r"mzt = mza \* msb",
                 "s2_AR": r"s2 = \(ssr / rows\) / \(1\.0 - bsum\) \*\* 2",
                 "gls_detrend": r"def gls_detrend"}


def stats_alt(y, case):
    """Estadisticos M con la convencion alternativa, mismo s2 (retardo 0)."""
    cbar = U.NP_CBAR[case]
    yt = U.gls_detrend(y, case)
    T = len(yt)
    r = U.np_statistics(y, case, k=0)
    s2 = r["s2_ar"]
    S = float(yt[:-2] @ yt[:-2]) / T ** 2
    yT2 = yt[-2] ** 2 / T
    mza = (yT2 - s2) / (2.0 * S)
    msb = math.sqrt(S / s2)
    mpt = (cbar * cbar * S - cbar * yT2) / s2 if case == "c" else (cbar * cbar * S + (1.0 - cbar) * yT2) / s2
    return r, {"MZa": mza, "MZt": mza * msb, "MSB": msb, "MPT": mpt}


def _rows(case, cell, idx):
    out = []
    for i in idx:
        y = D.gauss_rw(V.NP_N, C.rep_rng(FAM, cell, i))
        r, alt = stats_alt(y, case)
        yt = U.gls_detrend(y, case)
        T = len(yt)
        S = float(yt[:-1] @ yt[:-1]) / T ** 2
        closed = (yt[-1] ** 2 / T - r["s2_ar"]) / (2.0 * math.sqrt(S * r["s2_ar"]))
        out.append([abs(r["MZt"] - closed) / abs(closed)] + [alt[s] for s in U.NP_STATS])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    v5 = C.read_json("b1_validation_audit8.json")["V5_ng_perron"]
    diag = C.read_json("b1_np_diagnostic_audit8.json")["D2_T_stability"]
    res = {"a": {}, "b": {}, "c": {}, "d": {"alternative_q05": {}}}
    for case, tag in (("c", "dm"), ("ct", "ct")):
        st = v5["cases"][case]["stats"]
        res["a"][case] = {s: {"empirical_q05": st[s]["empirical_q05"], "ng_perron_2001": st[s]["ng_perron_2001"],
                              "rel_diff": st[s]["rel_diff"], "passed": st[s]["passed"]} for s in KEEP}
        cell = D.cell_index(FAM, "np_validation_%s" % tag)
        parts = [list(range(V.NP_REPS))[j::a.cores] for j in range(a.cores)]
        rows = np.array(sum(Parallel(n_jobs=a.cores)(delayed(_rows)(case, cell, p) for p in parts), []))
        res["b"][case] = {"paths": int(len(rows)), "max_rel_diff": float(rows[:, 0].max()), "tolerance": IDENTITY_TOL,
                          "passed": bool(rows[:, 0].max() <= IDENTITY_TOL)}
        q_alt = np.quantile(rows[:, 1:], 0.05, axis=0)
        res["d"]["alternative_q05"][case] = {s: {"alternative": float(q_alt[j]), "code": st[s]["empirical_q05"],
                                                 "ng_perron_2001": st[s]["ng_perron_2001"],
                                                 "alternative_rel_diff": float(abs(q_alt[j] - st[s]["ng_perron_2001"])
                                                                               / abs(st[s]["ng_perron_2001"]))}
                                             for j, s in enumerate(U.NP_STATS)}
        big = diag[case]["by_T_points"][T_LARGE]
        cc = {}
        for s in KEEP:
            d = abs(st[s]["empirical_q05"] - big[s]["q05"])
            se = math.sqrt(st[s]["bootstrap_se"] ** 2 + big[s]["bootstrap_se"] ** 2)
            cc[s] = {"q05_T2001": st[s]["empirical_q05"], "se_T2001": st[s]["bootstrap_se"], "q05_T10001": big[s]["q05"],
                     "se_T10001": big[s]["bootstrap_se"], "abs_diff": d, "combined_se": se, "diff_in_se": d / se,
                     "passed": bool(d <= SE_MULT * se)}
        res["c"][case] = cc
    lines = U.__file__
    with open(lines, encoding="utf-8") as f:
        src = f.read().splitlines()
    res["d"]["code_lines"] = {k: [{"line": i + 1, "text": l.strip()} for i, l in enumerate(src) if re.search(p, l)]
                              for k, p in CODE_PATTERNS.items()}
    res["d"]["code_file"] = C.rel(lines)
    res["d"]["mapping"] = ("articulo: t = 1..T, sum_{t=1}^{T} yt_{t-1}^2 con yt_0 = 0 y yt_T la ultima observacion; "
                           "codigo: y[0..T-1], S = T^-2 sum_{j=0}^{T-2} yt[j]^2 e yT = yt[T-1]: coinciden")
    res["d"]["code_uses_paper_convention"] = all(len(v) == 1 for v in res["d"]["code_lines"].values())
    res["d"]["code_changed"] = False
    res["d"]["passed"] = res["d"]["code_uses_paper_convention"]
    gates = {"a": all(v["passed"] for c in res["a"].values() for v in c.values()),
             "b": all(v["passed"] for v in res["b"].values()),
             "c": all(v["passed"] for c in res["c"].values() for v in c.values()),
             "d": res["d"]["passed"]}
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "amendment": "experiments/protocol_audit8_amend1.md",
           "criteria": res, "gates": gates, "passed": all(gates.values()),
           "other_b1_gates": C.read_json("b1_validation_audit8.json")["gates"],
           "retired_reference_failures": [f for f in v5["failing"] if f.split("/")[1] not in KEEP],
           "elapsed_sec": round(time.time() - t0, 1)}
    others = {k: v for k, v in out["other_b1_gates"].items() if k != "V5_ng_perron"}
    out["b1_passed"] = out["passed"] and all(others.values())
    C.write_result(OUT, out, __file__)
    for k in ("a", "b", "c"):
        print(k, gates[k], res[k])
    print("d", gates["d"], res["d"]["alternative_q05"])
    print("B1-NP", "PASA" if out["passed"] else "FALLA", "| B1 completo", "PASA" if out["b1_passed"] else "FALLA")
    return 0 if out["b1_passed"] else 4


if __name__ == "__main__":
    sys.exit(main())
