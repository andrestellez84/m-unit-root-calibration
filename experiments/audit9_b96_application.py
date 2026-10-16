"""
Auditoria A9 - B9.6: aplicacion con la configuracion final (solo si B9.2 cambia theta
respecto de 0.1 o si B9.5 recomienda la variante AWB).

Repite B6 de A8 (audit8_b6_application.py, cuyas funciones se reutilizan) con la
primaria final: RM-GLS con el theta de B9.2 (theta = 0: tau_1 = 0), sigma_hat HAC,
nula hac de N_cal = 50000 con la semilla 42 de produccion, calibrada a n = D - 1.
Ventanas, periodos de control, eventos, exclusiones, agrupacion de episodios y
latencia censurada: los de A8. Comparadores: los p-valores publicados (R-hat, ADF,
PP, KPSS, DF-GLS AIC) y DF-GLS (MAIC) y MZt-GLS de los checkpoints de B6 de A8;
la primaria de A8 (RM-GLS theta = 0.1) se conserva como fila para la tabla de
desviaciones. Hashes de los datos congelados verificados antes de calcular.
Tamano fuera de muestra por D: 5000 paseos gaussianos de D puntos (familia 106).

Si B9.5 recomienda la variante AWB, se calcula ademas su p-valor en cada ventana
(audit9_engine.awb_pvalue, B = 399, la misma construccion que B9.5; semilla de la
ventana j de (indice, D): SeedSequence(106, spawn_key = (awbapp_<indice>_D<D>, j)))
y su tamano fuera de muestra sobre los mismos paseos (celdas awboos_D<D>). Las
celdas de remuestreo se anadieron al final de la familia 106; el mapa de semillas
se recalcula y se guarda en el JSON.

Salida: experiments/results/b96_application_audit9.json.
Uso: python experiments/audit9_b96_application.py --cores 14
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

import audit9_common as C                                          # noqa: E402
import audit9_design as D                                          # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit8_b6_application as B6                                 # noqa: E402
import audit8_design as D8                                         # noqa: E402
import real_data_validation as RDV                                 # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402
from stationarity_test.empirical_eigenvalues import build_null_cdf  # noqa: E402

FAM = C.FAMILY["B9.6"]
CKPT = os.path.join(C.CKPT_ROOT, "audit9_b96")
OUT = os.path.join(C.RESULTS, "b96_application_audit9.json")
FINAL = "final"
AWB = "final_awb"


def theta_final():
    return C.read_json("b92_theta_audit9.json")["primary_theta"]


def null_cdf(Dw, theta):
    return build_null_cdf((theta, theta), 0.0, Dw - 1, N_cal=E.N_CAL, seed=E.CAL_SEED, cal_sigma="hac", anchor="gls",
                          tau_mode="zero" if theta == 0 else "theta", use_cache=False)


def _stats(wins, theta):
    out = []
    for w in wins:
        n = len(w) - 1
        out.append(E.rmgls(np.asarray(w, dtype=np.float64), n, theta, hac_sigma_sq(w), "c"))
    return out


def final_rows(index, Dw, theta, cores):
    path = os.path.join(CKPT, "final_%s_D%d.json" % (index, Dw))
    if os.path.exists(path):
        import json
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete") and d.get("theta") == theta:
            return d
    lp = RDV.load_log_prices(index)
    vals = lp.values
    dates, wins = [], []
    for i in range(Dw, len(vals)):
        w = vals[i - Dw:i]
        if np.any(np.isnan(w)):
            continue
        dates.append(str(lp.index[i].date()))
        wins.append(np.asarray(w, dtype=np.float64))
    parts = [wins[j::cores] for j in range(cores)]
    res = Parallel(n_jobs=cores, backend="loky")(delayed(_stats)(p, theta) for p in parts)
    st = [None] * len(wins)
    for j, r in enumerate(res):
        st[j::cores] = r
    d = {"index": index, "D": Dw, "theta": theta, "dates": dates, "stat": st, "complete": True}
    os.makedirs(CKPT, exist_ok=True)
    C.atomic_write_json(path, d)
    return d


def awb_recommended():
    p = os.path.join(C.RESULTS, "b95_awb_audit9.json")
    return os.path.exists(p) and bool(C.read_json("b95_awb_audit9.json")["rule"]["recommend_awb"])


def _awb(wins, j0s, cell, theta):
    out = []
    for w, j in zip(wins, j0s):
        out.append(E.awb_pvalue(np.asarray(w, dtype=np.float64), len(w) - 1, theta, "c", D.B_AWB, C.rep_rng(FAM, cell, j))[0])
    return out


def awb_rows(index, Dw, theta, cores):
    import json
    path = os.path.join(CKPT, "awb_%s_D%d.json" % (index, Dw))
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete") and d.get("theta") == theta:
            return d
    lp = RDV.load_log_prices(index)
    vals = lp.values
    dates, wins = [], []
    for i in range(Dw, len(vals)):
        w = vals[i - Dw:i]
        if np.any(np.isnan(w)):
            continue
        dates.append(str(lp.index[i].date()))
        wins.append(np.asarray(w, dtype=np.float64))
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


def _oos_awb(Dw, cell, cell_awb, idx, theta):
    return [E.awb_pvalue(D8.gauss_rw(Dw - 1, C.rep_rng(FAM, cell, i)), Dw - 1, theta, "c", D.B_AWB,
                         C.rep_rng(FAM, cell_awb, i))[0] for i in idx]


def oos_awb(theta, cores):
    out, reg = {}, C.exact_region(D.N_OOS)
    for Dw in D.B6_D:
        cell, ca = D.cell_index(FAM, "oos_D%d" % Dw), D.cell_index(FAM, "awboos_D%d" % Dw)
        parts = [list(range(D.N_OOS))[j::cores] for j in range(cores)]
        res = Parallel(n_jobs=cores, backend="loky")(delayed(_oos_awb)(Dw, cell, ca, p, theta) for p in parts)
        x = np.zeros(D.N_OOS)
        for p, r in zip(parts, res):
            x[p] = r
        out[str(Dw)] = C.rate_record(x < C.ALPHA, reg)
    return {"N": D.N_OOS, "region": reg, "family": FAM, "by_D": out}


def _oos(Dw, cell, idx, theta):
    return [E.rmgls(y, Dw - 1, theta, hac_sigma_sq(y), "c")
            for y in (D8.gauss_rw(Dw - 1, C.rep_rng(FAM, cell, i)) for i in idx)]


def oos(theta, cores):
    out, reg = {}, C.exact_region(D.N_OOS)
    for Dw in D.B6_D:
        cell = D.cell_index(FAM, "oos_D%d" % Dw)
        parts = [list(range(D.N_OOS))[j::cores] for j in range(cores)]
        res = Parallel(n_jobs=cores, backend="loky")(delayed(_oos)(Dw, cell, p, theta) for p in parts)
        x = np.zeros(D.N_OOS)
        for p, r in zip(parts, res):
            x[p] = r
        out[str(Dw)] = C.rate_record(np.clip(null_cdf(Dw, theta)(x), 0, 1) < C.ALPHA, reg)
    return {"N": D.N_OOS, "region": reg, "family": FAM, "by_D": out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    hashes, prot = B6.data_hashes()
    if not all(v["match"] for v in hashes.values()) or not prot["match"]:
        print("HASHES NO COINCIDEN: se detiene B9.6", hashes, prot)
        return 6
    theta = theta_final()
    awb = awb_recommended()
    E.warm(a.cores)
    seeds = None
    if awb:
        import audit9_b90_protocol as B90
        seeds = B90.seed_map()
        print("mapa de semillas tras anadir celdas:", seeds["collisions_new_vs_prior"], seeds["collisions_within_new"], flush=True)
    data, same = {}, {}
    for idx in RDV.INDICES:
        for Dw in RDV.WINDOW_SIZES:
            dates, s = B6.scores_for(idx, Dw, a.cores)          # comparadores y primaria de A8 (checkpoints de A8)
            fr = final_rows(idx, Dw, theta, a.cores)
            if fr["dates"] != dates:
                raise RuntimeError("%s D=%d: fechas distintas de las de A8" % (idx, Dw))
            s[FINAL] = np.clip(null_cdf(Dw, theta)(np.asarray(fr["stat"], dtype=float)), 0.0, 1.0)
            if awb:
                ar = awb_rows(idx, Dw, theta, a.cores)
                if ar["dates"] != dates:
                    raise RuntimeError("%s D=%d: fechas AWB distintas" % (idx, Dw))
                s[AWB] = np.asarray(ar["p_awb"], dtype=float)
            same[(idx, Dw)] = float(np.nanmax(np.abs(s[FINAL] - s["primary_rmgls"])))
            data[(idx, Dw)] = (dates, s)
            print("  %s D=%d" % (idx, Dw), flush=True)
    extra = (AWB,) if awb else ()
    B6.NOMINAL_TESTS = (FINAL,) + extra + ("primary_rmgls", "primary_rm", "rhat_prereg", "adf", "pp", "dfgls_aic", "dfgls_maic", "mzt", "kpss")
    B6.MATCHED_TESTS = {FINAL: FINAL, **({AWB: AWB} if awb else {}), "primary_rmgls": "primary_rmgls", "rhat_prereg": "rhat_prereg", "adf": "adf", "pp": "pp",
                        "dfgls_aic": "dfgls_aic", "dfgls_maic": "dfgls_maic", "mzt": "mzt_stat"}
    B6.primary_key = lambda: FINAL
    fp, lat, summary = B6.cell_metrics(data)
    mt = B6.matched(data)
    adv = B6.adverse(fp)
    oo = oos(theta, a.cores)
    oo_awb = oos_awb(theta, a.cores) if awb else None
    dev = []
    if theta != E.THETA_A8:
        dev.append({"id": "xiv", "audit": "A9", "element": "theta del estadistico primario (regla de B9.2)",
                    "preregistered_value": "0.1 (primaria de A8)", "deployed_value": "%g" % theta,
                    "effect_before": B6.effect(summary, "primary_rmgls"), "effect_after": B6.effect(summary, FINAL)})
    if awb:
        dev.append({"id": "xv" if dev else "xiv", "audit": "A9", "element": "calibracion (variante recomendada por B9.5)",
                    "preregistered_value": "nula hac simulada", "deployed_value": "AWB del propio estadistico (B = %d)" % D.B_AWB,
                    "effect_before": B6.effect(summary, FINAL), "effect_after": B6.effect(summary, AWB)})
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "data_hashes": hashes, "protocol_hash": prot,
           "theta": theta, "awb_variant": awb, "seed_map_after_append": seeds,
           "final_vs_a8_primary_max_abs_diff_p": max(same.values()), "config": {"N_cal": E.N_CAL, "cal_seed": E.CAL_SEED, "calibration_n": "D - 1", "alpha": C.ALPHA,
                                      "prereg_baselines_for_adverse_rule": list(B6.PREREG_BASELINES),
                                      "comparators": "p-valores publicados y checkpoints de B6 de A8"},
           "summary": summary, "fp_cells": fp, "latency_cells": lat, "matched_rate": mt, "adverse_cells_primary": adv,
           "oos_size": oo, "oos_size_awb": oo_awb, "deviation_rows": dev, "elapsed_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for t, s in summary.items():
        print("%-14s FP %.4f max %.3f det %d/%d lat %s" % (t, s["fp_mean"], s["fp_max"], s["detections"], s["event_cells"],
                                                            s["mean_latency_detected"]))
    print("tasa igualada", mt["target_fpr_pooled_primary"], "adversas", len(adv), "OOS", {k: v["rate"] for k, v in oo["by_D"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
