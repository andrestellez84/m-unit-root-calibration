"""
Auditoria A13 - B13.E(2): aplicacion con theta = 0 (tab:fp, tab:deviations).

B10.3.5 (audit10_b103_application) con RM-GLS theta = 0 (sigma_hat HAC; nula
build_null_cdf de produccion, semilla 42, N_cal = 50 000, tau_mode = "zero",
calibrada a n = D - 1) sobre los datos congelados. Hashes de los datos y de
experiments/protocol.md verificados antes de calcular (si no coinciden, se
detiene). La variante AWB se calcula siempre (lectura 11): p-valor AWB (B = 399)
por ventana con SeedSequence(143, spawn_key = (awbapp_<indice>_D<D>, j)). Tamano
fuera de muestra sobre los paseos de B9.6 (familia 106, celdas oos_D<D>); AWB fuera
de muestra con remuestreo de la familia 143 (awboos_D<D>). Comparadores:
checkpoints de B6 de A8. La fila theta = 0.02 publicada se recompone en la misma
corrida desde los checkpoints de A10 (estadisticos y p-valores AWB por ventana).

Paso 0 (max |Delta| = 0):
  (a) RM-GLS theta = 0.02 recalculado en las 50 primeras ventanas de cada
      (indice, D) frente a los checkpoints de A10;
  (b) la fila theta = 0.02 recompuesta reproduce el resumen de A10 (FP media y
      maxima, detecciones, latencia; con y sin AWB);
  (c) el tamano fuera de muestra con theta = 0.02 sobre los paseos de la familia 106
      reproduce las tasas de A10.
Tasa comun: objetivo = tasa de FP agregada de la primaria (theta = 0), el
mecanismo registrado; informativa, la comparacion al objetivo del v13 (A10).

Salida: experiments/results/e_application_audit13.json.
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

import audit13_common as C                                         # noqa: E402
import audit13_design as D                                         # noqa: E402
import audit9_design as D9                                         # noqa: E402
import audit9_engine as E                                          # noqa: E402
import audit9_b96_application as B96                               # noqa: E402
import audit8_b6_application as B6                                 # noqa: E402
import audit8_design as D8                                         # noqa: E402
import audit10_b103_application as B103A                           # noqa: E402
import real_data_validation as RDV                                 # noqa: E402
import audit6_real_data_roc as ROC                                 # noqa: E402
from stationarity_test.rm_core import hac_sigma_sq                 # noqa: E402

FAM = C.FAMILY["APP"]
FAM_OOS = B103A.FAM_OOS
CKPT = os.path.join(C.CKPT_ROOT, "audit13_app")
CKPT_A10 = B103A.CKPT
OUT = os.path.join(C.RESULTS, "e_application_audit13.json")
FINAL, AWB, V13, V13_AWB = "final", "final_awb", "v13", "v13_awb"


def a10_ckpt(kind, index, Dw):
    with open(os.path.join(CKPT_A10, "%s_%s_D%d.json" % (kind, index, Dw)), encoding="utf-8") as f:
        return json.load(f)


def final_rows(index, Dw, cores):
    path = os.path.join(CKPT, "final_%s_D%d.json" % (index, Dw))
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete") and d.get("theta") == C.THETA:
            return d
    dates, wins = B103A.windows(index, Dw)
    parts = [wins[j::cores] for j in range(cores)]
    res = Parallel(n_jobs=cores, backend="loky")(delayed(B96._stats)(p, C.THETA) for p in parts)
    st = [None] * len(wins)
    for j, r in enumerate(res):
        st[j::cores] = r
    d = {"index": index, "D": Dw, "theta": C.THETA, "dates": dates, "stat": st, "complete": True}
    os.makedirs(CKPT, exist_ok=True)
    C.atomic_write_json(path, d)
    return d


def _awb(wins, js, cell):
    return [E.awb_pvalue(np.asarray(w, dtype=np.float64), len(w) - 1, C.THETA, "c", D9.B_AWB, C.rep_rng(FAM, cell, j))[0]
            for w, j in zip(wins, js)]


def awb_rows(index, Dw, cores):
    path = os.path.join(CKPT, "awb_%s_D%d.json" % (index, Dw))
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete") and d.get("theta") == C.THETA:
            return d
    dates, wins = B103A.windows(index, Dw)
    if len(wins) > D.N_APP_MAX:
        raise RuntimeError("%s D=%d: %d ventanas > N_APP_MAX" % (index, Dw, len(wins)))
    cell = D.cell_index(FAM, "awbapp_%s_D%d" % (index, Dw))
    js = list(range(len(wins)))
    parts = [js[j::cores] for j in range(cores)]
    res = Parallel(n_jobs=cores, backend="loky")(delayed(_awb)([wins[k] for k in p], p, cell) for p in parts)
    pv = [None] * len(wins)
    for p, r in zip(parts, res):
        for k, v in zip(p, r):
            pv[k] = v
    d = {"index": index, "D": Dw, "theta": C.THETA, "dates": dates, "p_awb": pv, "complete": True}
    os.makedirs(CKPT, exist_ok=True)
    C.atomic_write_json(path, d)
    return d


def paso0_windows(index, Dw):
    _, wins = B103A.windows(index, Dw)
    ref = a10_ckpt("final", index, Dw)["stat"]
    mine = B96._stats(wins[:D.PASO0], C.THETA_V13)
    return float(np.max(np.abs(np.asarray(mine) - np.asarray(ref[:D.PASO0]))))


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
    return {"N": D.N_OOS, "region": reg, "family_paths": FAM_OOS, "theta": theta, "by_D": out}


def _oos_awb(Dw, cell, cell_awb, idx):
    return [E.awb_pvalue(D8.gauss_rw(Dw - 1, C.rep_rng(FAM_OOS, cell, i)), Dw - 1, C.THETA, "c", D9.B_AWB,
                         C.rep_rng(FAM, cell_awb, i))[0] for i in idx]


def oos_awb(cores):
    out, reg = {}, C.exact_region(D.N_OOS)
    for Dw in D.B6_D:
        path = os.path.join(CKPT, "oos_awb_D%d.json" % Dw)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("complete") and d.get("theta") == C.THETA:
                out[str(Dw)] = C.rate_record(np.asarray(d["p"]) < C.ALPHA, reg)
                continue
        cell, ca = D9.cell_index(FAM_OOS, "oos_D%d" % Dw), D.cell_index(FAM, "awboos_D%d" % Dw)
        parts = [list(range(D.N_OOS))[j::cores] for j in range(cores)]
        res = Parallel(n_jobs=cores, backend="loky")(delayed(_oos_awb)(Dw, cell, ca, p) for p in parts)
        x = np.zeros(D.N_OOS)
        for p, r in zip(parts, res):
            x[p] = r
        os.makedirs(CKPT, exist_ok=True)
        C.atomic_write_json(path, {"D": Dw, "theta": C.THETA, "p": x.tolist(), "complete": True})
        out[str(Dw)] = C.rate_record(x < C.ALPHA, reg)
        print("  OOS AWB D=%d" % Dw, flush=True)
    return {"N": D.N_OOS, "region": reg, "family_paths": FAM_OOS, "family_resampling": FAM, "by_D": out}


def matched_at(data, tests, target):
    """B6.matched con el objetivo dado (informativo, lectura 11)."""
    ctrl = {t: [] for t in tests}
    for (idx, Dw), (dates, s) in data.items():
        for c_name, (a, b) in RDV.CONTROL_PERIODS.items():
            m = ROC.extract_period_mask(dates, a, b)
            for t, key in tests.items():
                ctrl[t].extend(s[key][m].tolist())
    ctrl = {t: np.array(v, dtype=float) for t, v in ctrl.items()}
    out = {"target_fpr": target, "tests": {}}
    for t, key in tests.items():
        th = ROC.calibrate_threshold_for_target_fpr(ctrl[t], target)
        runs, clusters, lats = [], 0, []
        for (idx, Dw), (dates, s) in data.items():
            sc = s[key]
            for c_name, (a, b) in RDV.CONTROL_PERIODS.items():
                m = ROC.extract_period_mask(dates, a, b)
                _, nc, rl = ROC.compute_clustered_arl0(np.array(dates)[m].tolist(), sc[m], th, ROC.CLUSTER_GAP_TOLERANCE)
                runs.extend(rl)
                clusters += nc
            for e_name, e_date in RDV.EVENTS.items():
                if (idx, e_name) in RDV.EXCLUSIONS:
                    continue
                lats.append(ROC.compute_event_latency(dates, sc, e_date, th, ROC.LATENCY_MAX_WINDOW))
        out["tests"][t] = {"threshold": float(th), "achieved_fpr": float(np.mean(ctrl[t][~np.isnan(ctrl[t])] < th)),
                           "false_alarm_episodes": int(clusters), "mean_run_length": float(np.mean(runs)),
                           "censored_latency_mean": float(np.mean(lats)), "event_cells": len(lats)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    hashes, prot = B6.data_hashes()
    if not all(v["match"] for v in hashes.values()) or not prot["match"]:
        print("HASHES NO COINCIDEN: se detiene", hashes, prot)
        return 6
    E.warm(a.cores)
    data, p0a = {}, {}
    for idx in RDV.INDICES:
        for Dw in RDV.WINDOW_SIZES:
            dates, s = B6.scores_for(idx, Dw, a.cores)
            fr = final_rows(idx, Dw, a.cores)
            ar = awb_rows(idx, Dw, a.cores)
            f10, w10 = a10_ckpt("final", idx, Dw), a10_ckpt("awb", idx, Dw)
            if fr["dates"] != dates or ar["dates"] != dates or f10["dates"] != dates or w10["dates"] != dates:
                raise RuntimeError("%s D=%d: fechas distintas de las de A8" % (idx, Dw))
            s[FINAL] = np.clip(B96.null_cdf(Dw, C.THETA)(np.asarray(fr["stat"], dtype=float)), 0.0, 1.0)
            s[AWB] = np.asarray(ar["p_awb"], dtype=float)
            s[V13] = np.clip(B96.null_cdf(Dw, C.THETA_V13)(np.asarray(f10["stat"], dtype=float)), 0.0, 1.0)
            s[V13_AWB] = np.asarray(w10["p_awb"], dtype=float)
            p0a["%s_D%d" % (idx, Dw)] = paso0_windows(idx, Dw)
            data[(idx, Dw)] = (dates, s)
            print("  %s D=%d" % (idx, Dw), flush=True)
    B6.NOMINAL_TESTS = (FINAL, AWB, V13, V13_AWB, "primary_rmgls", "primary_rm", "rhat_prereg", "adf", "pp", "dfgls_aic",
                        "dfgls_maic", "mzt", "kpss")
    B6.MATCHED_TESTS = {FINAL: FINAL, AWB: AWB, V13: V13, V13_AWB: V13_AWB, "primary_rmgls": "primary_rmgls",
                        "rhat_prereg": "rhat_prereg", "adf": "adf", "pp": "pp", "dfgls_aic": "dfgls_aic",
                        "dfgls_maic": "dfgls_maic", "mzt": "mzt_stat"}
    B6.primary_key = lambda: FINAL
    fp, lat, summary = B6.cell_metrics(data)
    mt = B6.matched(data)
    adv = B6.adverse(fp)
    B6.primary_key = lambda: V13
    adv_v13 = B6.adverse(fp)
    B6.primary_key = lambda: FINAL
    a10 = C.read_json("b103_application_audit10.json")
    mt_v13_target = matched_at(data, B6.MATCHED_TESTS, a10["matched_rate"]["target_fpr_pooled_primary"])
    oo = oos(C.THETA, a.cores)
    oo_v13 = oos(C.THETA_V13, a.cores)
    oo_awb = oos_awb(a.cores)
    keys = ("fp_mean", "fp_max", "detections", "mean_latency_detected")
    p0b = max(abs(summary[mine][k] - a10["summary"][ref][k]) for mine, ref in ((V13, "final"), (V13_AWB, "final_awb"))
              for k in keys)
    p0c = max(abs(oo_v13["by_D"][d]["rate"] - a10["oos_size"]["by_D"][d]["rate"]) for d in oo_v13["by_D"])
    p0mt = abs(mt["tests"][V13]["false_alarm_episodes"] - a10["matched_rate"]["tests"]["final"]["false_alarm_episodes"])
    dev = [{"id": "xvi", "audit": "A13", "element": "theta del estadistico primario (B13.E, confirmado por el autor)",
            "preregistered_value": "0.02 (primaria de A10-A12)", "deployed_value": "%g" % C.THETA,
            "effect_before": B6.effect(summary, V13), "effect_after": B6.effect(summary, FINAL)},
           {"id": "xvii", "audit": "A13", "element": "calibracion AWB con theta = 0",
            "preregistered_value": "nula hac simulada", "deployed_value": "AWB del propio estadistico (B = %d)" % D9.B_AWB,
            "effect_before": B6.effect(summary, FINAL), "effect_after": B6.effect(summary, AWB)},
           {"id": "statistic", "audit": "A13", "element": "estadistico registrado frente a RM-GLS theta = 0",
            "preregistered_value": "R-hat registrado", "deployed_value": "RM-GLS theta = %g" % C.THETA,
            "effect_before": B6.effect(summary, "rhat_prereg"), "effect_after": B6.effect(summary, FINAL)}]
    out = {"provenance": C.provenance(__file__, seed_family=FAM), "data_hashes": hashes, "protocol_hash": prot,
           "theta": C.THETA, "reference_theta": C.THETA_V13,
           "config": {"N_cal": E.N_CAL, "cal_seed": E.CAL_SEED, "calibration_n": "D - 1", "alpha": C.ALPHA,
                      "null": "build_null_cdf de produccion (semilla 42, N_cal = %d, tau_mode = zero)" % E.N_CAL,
                      "prereg_baselines_for_adverse_rule": list(B6.PREREG_BASELINES),
                      "comparators": "p-valores publicados y checkpoints de B6 de A8",
                      "v13_rows": "estadisticos y p-valores AWB por ventana de los checkpoints de A10 (audit10_b103_app)",
                      "reading": "protocol_audit13.md, lectura 11"},
           "paso0": {"a_windows_v13_vs_a10": p0a, "a_max_abs_diff": max(p0a.values()), "b_summary_v13_vs_a10": p0b,
                     "c_oos_v13_vs_a10": p0c, "d_matched_episodes_v13_vs_a10": p0mt,
                     "passes": max(p0a.values()) == 0 and p0b == 0 and p0c == 0 and p0mt == 0},
           "summary": summary, "fp_cells": fp, "latency_cells": lat, "matched_rate": mt,
           "matched_rate_at_v13_target": mt_v13_target, "adverse_cells_primary": adv, "adverse_cells_v13": adv_v13,
           "oos_size": oo, "oos_size_v13": oo_v13, "oos_size_awb": oo_awb, "deviation_rows": dev,
           "elapsed_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    for t, s in summary.items():
        print("%-14s FP %.4f max %.3f det %d/%d lat %s" % (t, s["fp_mean"], s["fp_max"], s["detections"], s["event_cells"],
                                                            s["mean_latency_detected"]))
    print("tasa igualada", mt["target_fpr_pooled_primary"], "adversas", len(adv), "OOS", {k: v["rate"] for k, v in oo["by_D"].items()})
    print("Paso 0", out["paso0"]["a_max_abs_diff"], p0b, p0c, p0mt)
    return 0 if out["paso0"]["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
