"""
Auditoria A10 - B10.3.5 (condicional): aplicacion con el theta final.

Solo si el theta de B10.1 != 0.1. Repite B9.6 de A9 (audit9_b96_application) con
la primaria de B10.1: RM-GLS con el theta final, sigma_hat HAC, nula hac de
produccion (semilla 42, N_cal = 50 000, la de build_null_cdf que usa B9.6)
calibrada a n = D - 1. Ventanas, periodos de control, eventos, exclusiones,
episodios y latencia censurada: los de B6 de A8 (sus funciones se reutilizan).
Comparadores: p-valores publicados y checkpoints de B6 de A8; la primaria de A9
(RM-GLS theta = 0.1) se conserva como fila. Variante AWB si B10.3.4 la
recomienda: p-valor AWB (B = 399) por ventana con semilla
SeedSequence(113, spawn_key = (awbapp_<indice>_D<D>, j)); tamano fuera de muestra
sobre los mismos paseos gaussianos de B9.6 (familia 106, celdas oos_D<D>) con
remuestreo de la familia 113 (celdas awboos_D<D>). Hashes de los datos congelados
verificados antes de calcular.

Salida: experiments/results/b103_application_audit10.json.
"""
import argparse
import json
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
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b96_application as B96                               # noqa: E402
import audit8_b6_application as B6                                 # noqa: E402
import audit8_design as D8                                         # noqa: E402
import real_data_validation as RDV                                 # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402

FAM = C.FAMILY["B10.3"]
FAM_OOS = 106                     # paseos gaussianos fuera de muestra de B9.6 (A9)
CKPT = os.path.join(C.CKPT_ROOT, "audit10_b103_app")
OUT = os.path.join(C.RESULTS, "b103_application_audit10.json")
FINAL = "final"
AWB = "final_awb"


def final_theta():
    return C.read_json("b101_theta_audit10.json")["primary_theta"]


def awb_recommended():
    p = os.path.join(C.RESULTS, "b103_awb_audit10.json")
    return os.path.exists(p) and bool(C.read_json("b103_awb_audit10.json")["rule"]["recommend_awb"])


def windows(index, Dw):
    lp = RDV.load_log_prices(index)
    vals = lp.values
    dates, wins = [], []
    for i in range(Dw, len(vals)):
        w = vals[i - Dw:i]
        if np.any(np.isnan(w)):
            continue
        dates.append(str(lp.index[i].date()))
        wins.append(np.asarray(w, dtype=np.float64))
    return dates, wins


def final_rows(index, Dw, theta, cores):
    path = os.path.join(CKPT, "final_%s_D%d.json" % (index, Dw))
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete") and d.get("theta") == theta:
            return d
    dates, wins = windows(index, Dw)
    parts = [wins[j::cores] for j in range(cores)]
    res = Parallel(n_jobs=cores, backend="loky")(delayed(B96._stats)(p, theta) for p in parts)
    st = [None] * len(wins)
    for j, r in enumerate(res):
        st[j::cores] = r
    d = {"index": index, "D": Dw, "theta": theta, "dates": dates, "stat": st, "complete": True}
    os.makedirs(CKPT, exist_ok=True)
    C.atomic_write_json(path, d)
    return d


def _awb(wins, js, cell, theta):
    return [E.awb_pvalue(np.asarray(w, dtype=np.float64), len(w) - 1, theta, "c", D9.B_AWB, C.rep_rng(FAM, cell, j))[0]
            for w, j in zip(wins, js)]


def awb_rows(index, Dw, theta, cores):
    path = os.path.join(CKPT, "awb_%s_D%d.json" % (index, Dw))
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete") and d.get("theta") == theta:
            return d
    dates, wins = windows(index, Dw)
    if len(wins) > D.N_APP_MAX:
        raise RuntimeError("%s D=%d: %d ventanas > N_APP_MAX" % (index, Dw, len(wins)))
    cell = D.cell_index(FAM, "awbapp_%s_D%d" % (index, Dw))
    js = list(range(len(wins)))
    parts = [js[j::cores] for j in range(cores)]
    res = Parallel(n_jobs=cores, backend="loky")(delayed(_awb)([wins[k] for k in p], p, cell, theta) for p in parts)
    pv = [None] * len(wins)
    for p, r in zip(parts, res):
        for k, v in zip(p, r):
            pv[k] = v
    d = {"index": index, "D": Dw, "theta": theta, "dates": dates, "p_awb": pv, "complete": True}
    os.makedirs(CKPT, exist_ok=True)
    C.atomic_write_json(path, d)
    return d


def _oos(Dw, cell, idx, theta):
    return [E.rmgls(y, Dw - 1, theta, hac_sigma_sq(y), "c")
            for y in (D8.gauss_rw(Dw - 1, C.rep_rng(FAM_OOS, cell, i)) for i in idx)]


def oos(theta, cores):
    out, reg = {}, C.exact_region(D.N_OOS)
    for Dw in D.B6_D:
        cell = D9.cell_index(FAM_OOS, "oos_D%d" % Dw)
        parts = [list(range(D.N_OOS))[j::cores] for j in range(cores)]
        res = Parallel(n_jobs=cores, backend="loky")(delayed(_oos)(Dw, cell, p, theta) for p in parts)
        x = np.zeros(D.N_OOS)
        for p, r in zip(parts, res):
            x[p] = r
        out[str(Dw)] = C.rate_record(np.clip(B96.null_cdf(Dw, theta)(x), 0, 1) < C.ALPHA, reg)
    return {"N": D.N_OOS, "region": reg, "family_paths": FAM_OOS, "by_D": out}


def _oos_awb(Dw, cell, cell_awb, idx, theta):
    return [E.awb_pvalue(D8.gauss_rw(Dw - 1, C.rep_rng(FAM_OOS, cell, i)), Dw - 1, theta, "c", D9.B_AWB,
                         C.rep_rng(FAM, cell_awb, i))[0] for i in idx]


def oos_awb(theta, cores):
    out, reg = {}, C.exact_region(D.N_OOS)
    for Dw in D.B6_D:
        path = os.path.join(CKPT, "oos_awb_D%d.json" % Dw)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("complete") and d.get("theta") == theta:
                out[str(Dw)] = C.rate_record(np.asarray(d["p"]) < C.ALPHA, reg)
                continue
        cell, ca = D9.cell_index(FAM_OOS, "oos_D%d" % Dw), D.cell_index(FAM, "awboos_D%d" % Dw)
        parts = [list(range(D.N_OOS))[j::cores] for j in range(cores)]
        res = Parallel(n_jobs=cores, backend="loky")(delayed(_oos_awb)(Dw, cell, ca, p, theta) for p in parts)
        x = np.zeros(D.N_OOS)
        for p, r in zip(parts, res):
            x[p] = r
        os.makedirs(CKPT, exist_ok=True)
        C.atomic_write_json(path, {"D": Dw, "theta": theta, "p": x.tolist(), "complete": True})
        out[str(Dw)] = C.rate_record(x < C.ALPHA, reg)
        print("  OOS AWB D=%d" % Dw, flush=True)
    return {"N": D.N_OOS, "region": reg, "family_paths": FAM_OOS, "family_resampling": FAM, "by_D": out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    theta = final_theta()
    if theta == 0.1:
        print("theta final = 0.1: B10.3 no se ejecuta")
        return 0
    hashes, prot = B6.data_hashes()
    if not all(v["match"] for v in hashes.values()) or not prot["match"]:
        print("HASHES NO COINCIDEN: se detiene B10.3.5", hashes, prot)
        return 6
    awb = awb_recommended()
    E.warm(a.cores)
    data = {}
    for idx in RDV.INDICES:
        for Dw in RDV.WINDOW_SIZES:
            dates, s = B6.scores_for(idx, Dw, a.cores)          # comparadores y primaria de A8 (checkpoints de A8)
            fr = final_rows(idx, Dw, theta, a.cores)
            if fr["dates"] != dates:
                raise RuntimeError("%s D=%d: fechas distintas de las de A8" % (idx, Dw))
            s[FINAL] = np.clip(B96.null_cdf(Dw, theta)(np.asarray(fr["stat"], dtype=float)), 0.0, 1.0)
            if awb:
                ar = awb_rows(idx, Dw, theta, a.cores)
                if ar["dates"] != dates:
                    raise RuntimeError("%s D=%d: fechas AWB distintas" % (idx, Dw))
                s[AWB] = np.asarray(ar["p_awb"], dtype=float)
            data[(idx, Dw)] = (dates, s)
            print("  %s D=%d" % (idx, Dw), flush=True)
    extra = (AWB,) if awb else ()
    B6.NOMINAL_TESTS = (FINAL,) + extra + ("primary_rmgls", "primary_rm", "rhat_prereg", "adf", "pp", "dfgls_aic",
                                           "dfgls_maic", "mzt", "kpss")
    B6.MATCHED_TESTS = {FINAL: FINAL, **({AWB: AWB} if awb else {}), "primary_rmgls": "primary_rmgls",
                        "rhat_prereg": "rhat_prereg", "adf": "adf", "pp": "pp", "dfgls_aic": "dfgls_aic",
                        "dfgls_maic": "dfgls_maic", "mzt": "mzt_stat"}
    B6.primary_key = lambda: FINAL
    fp, lat, summary = B6.cell_metrics(data)
    mt = B6.matched(data)
    adv = B6.adverse(fp)
    oo = oos(theta, a.cores)
    oo_awb = oos_awb(theta, a.cores) if awb else None
    a9 = C.read_json("b96_application_audit9.json")
    dev = [{"id": "xvi", "audit": "A10", "element": "theta del estadistico primario (regla B10.1, criterio A1')",
            "preregistered_value": "0.1 (primaria de A8 y de A9)", "deployed_value": "%g" % theta,
            "effect_before": B6.effect(summary, "primary_rmgls"), "effect_after": B6.effect(summary, FINAL)}]
    if awb:
        dev.append({"id": "xvii", "audit": "A10", "element": "calibracion (variante AWB recomendada por B10.3.4)",
                    "preregistered_value": "nula hac simulada", "deployed_value": "AWB del propio estadistico (B = %d)" % D9.B_AWB,
                    "effect_before": B6.effect(summary, FINAL), "effect_after": B6.effect(summary, AWB)})
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "data_hashes": hashes, "protocol_hash": prot,
           "theta": theta, "awb_variant": awb,
           "config": {"N_cal": E.N_CAL, "cal_seed": E.CAL_SEED, "calibration_n": "D - 1", "alpha": C.ALPHA,
                      "null": "build_null_cdf de produccion (semilla 42, N_cal = %d), como B9.6" % E.N_CAL,
                      "prereg_baselines_for_adverse_rule": list(B6.PREREG_BASELINES),
                      "comparators": "p-valores publicados y checkpoints de B6 de A8"},
           "summary": summary, "fp_cells": fp, "latency_cells": lat, "matched_rate": mt, "adverse_cells_primary": adv,
           "oos_size": oo, "oos_size_awb": oo_awb, "deviation_rows": dev,
           "a9_reference": {"source": "experiments/results/b96_application_audit9.json",
                            "summary_final": a9["summary"].get("final"), "summary_final_awb": a9["summary"].get("final_awb")},
           "elapsed_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for t, s in summary.items():
        print("%-14s FP %.4f max %.3f det %d/%d lat %s" % (t, s["fp_mean"], s["fp_max"], s["detections"], s["event_cells"],
                                                            s["mean_latency_detected"]))
    print("tasa igualada", mt["target_fpr_pooled_primary"], "adversas", len(adv), "OOS", {k: v["rate"] for k, v in oo["by_D"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
