"""
Auditoria A15 - B15.0b: tamano condicionado al retardo elegido por la MAIC GLS, solo
descriptivo y sin numeros aleatorios (protocol_audit15.md, lecturas 0b.1 y 0b.2).

(1) Filas por camino de checkpoints/audit12_bA para sz_ar_0p5_n100_ct, sz_ma_0p5_n100_ct,
sz_ma_m0p8_n200_c y sz_ma_0_n100_ct: tasa iid (q de bA_ma config.iid_quantiles) y asintotica
(NP_CV5) de mzt y msb por k in {0, 1, 2, >=3}, con Wilson y caminos por k. Paso 0: la tasa
agregada es igual a iid.rate y asy.rate de bA_ma_audit12.json.
(2) Lo mismo bajo la nula iid de A10 (audit10_cal/cal_n<n>.npz, columnas <caso>|k) para los
(n, caso) de esas celdas.

Salida: experiments/results/b0b_lag_audit15.json.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit12_runner as R12                                       # noqa: E402
import audit12_unitroot as P12                                     # noqa: E402
import audit12_design as D12                                       # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
import audit10_engine as E10                                       # noqa: E402

OUT = os.path.join(C.RESULTS, "b0b_lag_audit15.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit12_bA")
CELLS = ("sz_ar_0p5_n100_ct", "sz_ma_0p5_n100_ct", "sz_ma_m0p8_n200_c", "sz_ma_0_n100_ct")
PROCS = {"mzt": "MZt", "msb": "MSB"}
KBINS = (("0", 0, 0), ("1", 1, 1), ("2", 2, 2), (">=3", 3, None))


def by_k(stat, k, q_iid, cv_asy):
    x = np.nan_to_num(stat, nan=np.inf)
    rej = {"iid": x < q_iid, "asy": x < cv_asy}
    out = {}
    for lab, lo, hi in KBINS:
        m = (k >= lo) if hi is None else ((k >= lo) & (k <= hi))
        n = int(m.sum())
        out[lab] = {"paths": n, "share": n / len(k)}
        for blk, r in rej.items():
            j = int(r[m].sum())
            w = C.wilson(j, n) if n else (None, None)
            out[lab][blk] = {"rejections": j, "rate": j / n if n else None, "wilson_lower": w[0], "wilson_upper": w[1]}
    pooled = {blk: float(r.mean()) for blk, r in rej.items()}
    nan_k = int(np.sum(~np.isfinite(k)))
    return out, pooled, nan_k


def main():
    bA = C.read_json("bA_ma_audit12.json")
    J = {c: i for i, c in enumerate(P12.COLS_A)}
    res, paso0, a10 = {}, [], {}
    for name in CELLS:
        rows, _ = R12.load_cell(CKPT, name, D12.N_SIZE)
        cell = bA["size"][name]
        n, case = cell["n"], cell["case"]
        q = bA["config"]["iid_quantiles"]["%d|%s" % (n, case)]
        k = rows[:, J["k"]]
        res[name] = {"n": n, "case": case, "err_tag": cell["err_tag"], "N": int(rows.shape[0]), "procs": {}}
        for p, npk in PROCS.items():
            tab, pooled, nan_k = by_k(rows[:, J[p]], k, q[p], U.NP_CV5[case][npk])
            res[name]["procs"][p] = {"q_iid": q[p], "cv_asy": U.NP_CV5[case][npk], "by_k": tab, "nan_k": nan_k}
            for blk in ("iid", "asy"):
                ref = cell[blk][p]["rate"]
                paso0.append({"cell": name, "proc": p, "block": blk, "pooled": pooled[blk], "bA": ref,
                              "abs_diff": abs(pooled[blk] - ref)})
    for n, case in sorted({(res[c]["n"], res[c]["case"]) for c in CELLS}):
        rows, cols, _ = E10.load_cal(n)
        I = {c: i for i, c in enumerate(cols)}
        key = "%s|k" % case
        if key not in I:
            a10["%d|%s" % (n, case)] = {"executed": False, "reason": "sin columna %s" % key}
            continue
        q = bA["config"]["iid_quantiles"]["%d|%s" % (n, case)]
        k = rows[:, I[key]]
        a10["%d|%s" % (n, case)] = {"executed": True, "sample": C.rel(os.path.join(E10.CKPT_CAL, "cal_n%d.npz" % n)),
                                    "N": int(rows.shape[0]), "procs": {}}
        for p, npk in PROCS.items():
            tab, pooled, nan_k = by_k(rows[:, I["%s|%s" % (case, p)]], k, q[p], U.NP_CV5[case][npk])
            a10["%d|%s" % (n, case)]["procs"][p] = {"q_iid": q[p], "cv_asy": U.NP_CV5[case][npk], "by_k": tab,
                                                     "pooled": pooled, "nan_k": nan_k}
        del rows
    out = {"provenance": C.provenance(__file__), "reading": "protocol_audit15.md, lecturas 0b.1 y 0b.2",
           "cells": res, "a10_null": a10,
           "paso0": {"rows": paso0, "max_abs_diff": max(r["abs_diff"] for r in paso0), "passes": all(r["abs_diff"] == 0 for r in paso0)},
           "k_bins": [b[0] for b in KBINS], "descriptive_only": True}
    C.write_result(OUT, out, __file__)
    print("Paso 0: max |D| = %.3e, pasa %s" % (out["paso0"]["max_abs_diff"], out["paso0"]["passes"]))
    for name, r in res.items():
        for p in PROCS:
            print(name, p, {lab: (v["paths"], None if v["iid"]["rate"] is None else round(v["iid"]["rate"], 4),
                                  None if v["asy"]["rate"] is None else round(v["asy"]["rate"], 4))
                            for lab, v in r["procs"][p]["by_k"].items()})
    for key, r in a10.items():
        for p in PROCS:
            print("A10", key, p, {lab: (v["paths"], round(v["iid"]["rate"], 4) if v["iid"]["rate"] is not None else None,
                                        round(v["asy"]["rate"], 4) if v["asy"]["rate"] is not None else None)
                                  for lab, v in r["procs"][p]["by_k"].items()})
    return 0 if out["paso0"]["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
