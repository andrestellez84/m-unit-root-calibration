"""
Auditoria A8 - B6: aplicacion pre-registrada con la primaria.

Datos congelados (hashes verificados contra data_registry.json y protocol.md
contra protocol_hash.json antes de nada). Ventanas como en
real_data_validation.py: para cada fecha i >= D, la ventana es
log_price[i - D : i] (D puntos, n = D - 1 incrementos) y la fecha es la de i.

Procedimientos por ventana:
  - primaria: RM (R = 0, theta = 0.1) con sigma_hat HAC; p = F_null(stat) con la
    nula hac de N_cal = 50000 y semilla 42 calibrada a n = D - 1 (la n de la
    ventana); si B4 adopta RM-GLS, tambien RM-GLS con su nula hac;
  - R-hat pre-registrado: p-valores publicados (rolling_<indice>_D<D>.json), sin
    recomputar salvo el Paso 0;
  - ADF, PP, KPSS y DF-GLS (AIC, post hoc publicado): p-valores publicados;
  - DF-GLS (MAIC) y MZt-GLS (MAIC): calculados aqui (MZt con el valor critico
    asintotico de Ng-Perron; para la comparacion a tasa igualada se usa el
    estadistico como puntuacion).
Variantes de la primaria para la tabla de desviaciones: calibracion "one"
(N_cal = 50000, n = D - 1), N_cal = 10000 (hac, n = D - 1) y n = D (hac,
N_cal = 50000, la convencion de la calibracion publicada).

Metricas (como real_data_validation.py y audit6_real_data_roc.py): FP por celda
de control (48), media y maximo; detecciones sobre 88 celdas y latencia media
condicional; tasa de falsas alarmas igualada a la de la primaria (umbral =
cuantil de las puntuaciones de control agrupadas), episodios agrupando
rechazos contiguos (tolerancia 5 dias), racha media y latencia censurada a 120
dias; celdas adversas bajo la regla pre-registrada (FP de la primaria
estrictamente mayor que el de alguna linea base pre-registrada: ADF, PP, KPSS).
Tamano fuera de muestra de la configuracion desplegada: 5000 paseos gaussianos
de D puntos por D (familia 96). Paso 0: R-hat, ADF, PP, KPSS y DF-GLS (AIC)
recomputados en las primeras PASO0_WINDOWS ventanas de tres celdas.

Salidas: b6_application_audit8.json y deviation_table_audit8.json.
Uso: python experiments/audit8_b6_application.py --cores 14
"""
import argparse
import hashlib
import json
import os
import sys
import time
import warnings

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_design as D                                          # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
import audit8_b2_size as B2                                        # noqa: E402
import real_data_validation as RDV                                 # noqa: E402
import audit6_real_data_roc as ROC                                 # noqa: E402
from stationarity_test.rm_core import path_statistic, hac_sigma_sq  # noqa: E402
from stationarity_test.empirical_eigenvalues import build_null_cdf  # noqa: E402

FAM = C.FAMILY["B6"]
OUT = os.path.join(C.RESULTS, "b6_application_audit8.json")
OUT_DEV = os.path.join(C.RESULTS, "deviation_table_audit8.json")
CKPT = os.path.join(C.CKPT_ROOT, "audit8_b6")
N_CAL = 50000
N_CAL_PREREG = 10000
CAL_SEED = 42
N_OOS = 5000
PASO0_WINDOWS = 300
PASO0_CELLS = (("SP500", 150), ("NIKKEI", 300), ("DAX", 250))
PREREG_BASELINES = ("adf", "pp", "kpss")


def primary_is_gls():
    b4 = C.read_json("b4_local_power_audit8.json")
    return bool(b4["gls_rule"]["adopt_gls"])


def window_stats(windows):
    out = []
    for w in windows:
        n = len(w) - 1
        s2 = hac_sigma_sq(w)
        t1, t2 = B2.taus(0.1, n, "theta")
        rm = path_statistic(w, n, t1, t2, 0.0, s2, B2.C1, B2.C2, anchor="mean", need_g2=False)[0]
        gls = path_statistic(w, n, t1, t2, 0.0, s2, B2.C1, B2.C2, anchor="gls", need_g2=False)[0]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                r = U.np_statistics(w, "c")
                mzt, k = r["MZt"], r["k"]
                dfgls_p = U.dfgls_maic(w, "c", k)[1]
            except Exception:
                mzt, dfgls_p = float("nan"), float("nan")
        out.append([rm, gls, mzt, dfgls_p])
    return out


def rolling_rows(index, Dw, cores):
    path = os.path.join(CKPT, "rows_%s_D%d.json" % (index, Dw))
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete"):
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
    res = Parallel(n_jobs=cores)(delayed(window_stats)(p) for p in parts)
    rows = [None] * len(wins)
    for j, r in enumerate(res):
        rows[j::cores] = r
    d = {"index": index, "D": Dw, "dates": dates, "rows": rows, "columns": ["rm", "rmgls", "mzt", "dfgls_maic_p"],
         "complete": True}
    C.atomic_write_json(path, d)
    return d


def nulls(Dw):
    """CDF de la primaria y variantes para ventanas de D puntos."""
    n = Dw - 1
    th = (0.1, 0.1)
    return {
        "rm_hac": build_null_cdf(th, 0.0, n, N_cal=N_CAL, seed=CAL_SEED, cal_sigma="hac", use_cache=False),
        "rmgls_hac": build_null_cdf(th, 0.0, n, N_cal=N_CAL, seed=CAL_SEED, cal_sigma="hac", anchor="gls", use_cache=False),
        "rm_one": build_null_cdf(th, 0.0, n, N_cal=N_CAL, seed=CAL_SEED, use_cache=False),
        "rm_hac_10k": build_null_cdf(th, 0.0, n, N_cal=N_CAL_PREREG, seed=CAL_SEED, cal_sigma="hac", use_cache=False),
        "rm_hac_nD": build_null_cdf(th, 0.0, Dw, N_cal=N_CAL, seed=CAL_SEED, cal_sigma="hac", use_cache=False),
    }


def arr(x):
    return np.array([np.nan if v is None else float(v) for v in x], dtype=float)


def scores_for(index, Dw, cores):
    rows = rolling_rows(index, Dw, cores)
    with open(os.path.join(C.RESULTS, "rolling_%s_D%d.json" % (index, Dw)), encoding="utf-8") as f:
        pub = json.load(f)
    if pub["dates"] != rows["dates"]:
        raise RuntimeError("%s D=%d: fechas distintas de las publicadas" % (index, Dw))
    R = np.asarray(rows["rows"], dtype=float)
    cd = nulls(Dw)
    s = {
        "primary_rm": np.clip(cd["rm_hac"](R[:, 0]), 0.0, 1.0),
        "primary_rmgls": np.clip(cd["rmgls_hac"](R[:, 1]), 0.0, 1.0),
        "rm_one": np.clip(cd["rm_one"](R[:, 0]), 0.0, 1.0),
        "rm_hac_10k": np.clip(cd["rm_hac_10k"](R[:, 0]), 0.0, 1.0),
        "rm_hac_nD": np.clip(cd["rm_hac_nD"](R[:, 0]), 0.0, 1.0),
        "rhat_prereg": arr(pub["p_ours"]), "adf": arr(pub["p_adf"]), "pp": arr(pub["p_pp"]),
        "kpss": arr(pub["p_kpss"]), "dfgls_aic": arr(pub["p_dfgls"]), "dfgls_maic": R[:, 3],
        "mzt_stat": R[:, 2],
    }
    # MZt-GLS a nivel nominal: rechazo si MZt < valor critico asintotico; puntuacion equivalente a un p-valor
    s["mzt"] = np.where(np.isnan(R[:, 2]), np.nan, np.where(R[:, 2] < U.NP_CV5["c"]["MZt"], 0.0, 1.0))
    return rows["dates"], s


NOMINAL_TESTS = ("primary_rm", "primary_rmgls", "rhat_prereg", "adf", "pp", "dfgls_aic", "dfgls_maic", "mzt", "kpss",
                 "rm_one", "rm_hac_10k", "rm_hac_nD")
MATCHED_TESTS = {"primary_rm": "primary_rm", "primary_rmgls": "primary_rmgls", "rhat_prereg": "rhat_prereg",
                 "adf": "adf", "pp": "pp", "dfgls_aic": "dfgls_aic", "dfgls_maic": "dfgls_maic", "mzt": "mzt_stat"}


def cell_metrics(data):
    fp, lat = {t: {} for t in NOMINAL_TESTS}, {t: {} for t in NOMINAL_TESTS}
    for (idx, Dw), (dates, s) in data.items():
        roll = {"dates": dates}
        for t in NOMINAL_TESTS:
            pk = "p_" + t
            roll[pk] = [None if np.isnan(v) else float(v) for v in s[t]]
        for t in NOMINAL_TESTS:
            for c_name, (a, b) in RDV.CONTROL_PERIODS.items():
                rr = {"dates": dates, "p_ours": roll["p_" + t], "p_adf": roll["p_" + t], "p_pp": roll["p_" + t],
                      "p_kpss": roll["p_" + t]}
                fp[t]["%s|%d|%s" % (idx, Dw, c_name)] = RDV.compute_false_positive_rate(rr, a, b)["ours"]
            for e_name, e_date in RDV.EVENTS.items():
                if (idx, e_name) in RDV.EXCLUSIONS:
                    continue
                rr = {"dates": dates, "p_ours": roll["p_" + t], "p_adf": roll["p_" + t], "p_pp": roll["p_" + t],
                      "p_kpss": roll["p_" + t]}
                lat[t]["%s|%d|%s" % (idx, Dw, e_name)] = RDV.compute_latency(rr, e_date)["ours"]
    summary = {}
    for t in NOMINAL_TESTS:
        f = [v for v in fp[t].values() if v is not None]
        l_ = [v for v in lat[t].values() if v is not None]
        summary[t] = {"fp_cells": len(f), "fp_mean": float(np.mean(f)), "fp_max": float(np.max(f)),
                      "event_cells": len(lat[t]), "detections": len(l_),
                      "mean_latency_detected": float(np.mean(l_)) if l_ else None}
    return fp, lat, summary


def primary_key():
    return "primary_rmgls" if primary_is_gls() else "primary_rm"


def matched(data):
    ctrl = {t: [] for t in MATCHED_TESTS}
    for (idx, Dw), (dates, s) in data.items():
        for c_name, (a, b) in RDV.CONTROL_PERIODS.items():
            m = ROC.extract_period_mask(dates, a, b)
            for t, key in MATCHED_TESTS.items():
                ctrl[t].extend(s[key][m].tolist())
    ctrl = {t: np.array(v, dtype=float) for t, v in ctrl.items()}
    pk = primary_key()
    target = float(np.mean(ctrl[pk][~np.isnan(ctrl[pk])] < C.ALPHA))
    out = {"target_fpr_pooled_primary": target, "primary_key": pk, "gap_tolerance": ROC.CLUSTER_GAP_TOLERANCE,
           "censor_days": ROC.LATENCY_MAX_WINDOW, "tests": {}}
    for t, key in MATCHED_TESTS.items():
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


def _paso0_windows(index, Dw):
    from stationarity_test.statistic import compute_statistic
    from stationarity_test.empirical_eigenvalues import build_null_cdf_adaptive
    lp = RDV.load_log_prices(index)
    vals = lp.values
    cdf = build_null_cdf_adaptive((0.1, 0.1), Dw, N_CAL_PREREG, CAL_SEED)
    out = []
    for i in range(Dw, Dw + PASO0_WINDOWS):
        w = vals[i - Dw:i]
        r = compute_statistic(w, (0.1, 0.1), R=0.5, eps=1e-3, andrews_pilot="alpha2")
        g1, g2 = r["g1_std"], r["g2_std"]
        den = g1 ** 2 + g2 ** 2
        rh = g2 ** 2 / den if den > 1e-12 else 0.5
        st = np.sqrt((1 - rh) ** 2 * g1 ** 2 + rh ** 2 * g2 ** 2)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out.append([float(cdf(st)), RDV.run_adf(w), RDV.run_pp(w), RDV.run_kpss(w), U.dfgls_aic(w)[1]])
    return out


def paso0(cores):
    res = Parallel(n_jobs=min(cores, len(PASO0_CELLS)))(delayed(_paso0_windows)(i, d) for i, d in PASO0_CELLS)
    out = {}
    for (idx, Dw), rows in zip(PASO0_CELLS, res):
        with open(os.path.join(C.RESULTS, "rolling_%s_D%d.json" % (idx, Dw)), encoding="utf-8") as f:
            pub = json.load(f)
        mine = np.array(rows, dtype=float)
        cols = ("p_ours", "p_adf", "p_pp", "p_kpss", "p_dfgls")
        ref = np.array([[np.nan if pub[c][j] is None else pub[c][j] for c in cols] for j in range(PASO0_WINDOWS)])
        d = np.abs(np.where(np.isnan(mine) & np.isnan(ref), 0.0, mine - ref))
        out["%s_D%d" % (idx, Dw)] = {c: float(np.nanmax(d[:, k])) for k, c in enumerate(cols)}
    worst = {c: max(v[c] for v in out.values()) for c in ("p_ours", "p_adf", "p_pp", "p_kpss", "p_dfgls")}
    return {"windows": PASO0_WINDOWS, "pilot_rhat": "alpha2 (el registrado)", "N_cal_rhat": N_CAL_PREREG,
            "cells": out, "worst": worst}


def _oos_rates(Dw, cell, idx):
    out = []
    for i in idx:
        y = D.gauss_rw(Dw - 1, C.rep_rng(FAM, cell, i))
        n = Dw - 1
        s2 = hac_sigma_sq(y)
        t1, t2 = B2.taus(0.1, n, "theta")
        out.append([path_statistic(y, n, t1, t2, 0.0, s2, B2.C1, B2.C2, anchor=a, need_g2=False)[0] for a in ("mean", "gls")])
    return out


def oos(cores):
    out = {}
    reg = C.exact_region(N_OOS)
    for Dw in D.B6_D:
        cell = D.cell_index(FAM, "oos_D%d" % Dw)
        parts = [list(range(N_OOS))[j::cores] for j in range(cores)]
        res = Parallel(n_jobs=cores)(delayed(_oos_rates)(Dw, cell, p) for p in parts)
        rows = np.zeros((N_OOS, 2))
        for p, r in zip(parts, res):
            rows[p] = r
        cd = nulls(Dw)
        out[str(Dw)] = {"primary_rm": C.rate_record(np.clip(cd["rm_hac"](rows[:, 0]), 0, 1) < C.ALPHA, reg),
                        "primary_rmgls": C.rate_record(np.clip(cd["rmgls_hac"](rows[:, 1]), 0, 1) < C.ALPHA, reg)}
    return {"N": N_OOS, "region": reg, "family": FAM, "by_D": out}


def data_hashes():
    with open(os.path.join(HERE, "data", "data_registry.json"), encoding="utf-8") as f:
        reg = json.load(f)
    out = {}
    for k, v in reg["indices"].items():
        with open(os.path.join(HERE, "data", "%s_daily.csv" % k), "rb") as f:
            b = f.read()
        h, hl = hashlib.sha256(b).hexdigest(), hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()
        out[k] = {"registered": v["sha256"], "disk": h, "disk_lf": hl, "match": v["sha256"] in (h, hl)}
    with open(os.path.join(HERE, "protocol_hash.json"), encoding="utf-8") as f:
        ph = json.load(f)
    with open(os.path.join(HERE, "protocol.md"), "rb") as f:
        b = f.read()
    prot = {"registered": ph["sha256"], "match": ph["sha256"] in (hashlib.sha256(b).hexdigest(),
                                                                  hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest())}
    return out, prot


def adverse(fp):
    cells = []
    for key, v in fp[primary_key()].items():
        worse = [b for b in PREREG_BASELINES if fp[b][key] is not None and v is not None and v > fp[b][key]]
        if worse:
            cells.append({"cell": key, "primary": v, **{b: fp[b][key] for b in PREREG_BASELINES}, "exceeds": worse})
    return cells


def effect(summary, t):
    s = summary[t]
    return {"fp_mean": s["fp_mean"], "fp_max": s["fp_max"], "detections": s["detections"],
            "mean_latency_detected": s["mean_latency_detected"]}


def deviations(summary):
    a7 = C.read_json("deviation_table_audit7.json")
    rows = list(a7["rows"])
    new = [
        {"id": "viii", "audit": "A8", "element": "estadistico de la aplicacion", "preregistered": "R-hat adaptativo",
         "deployed": "RM con R = 0, theta = 0.1, anclado en la media", "preregistered_value": "R-hat",
         "deployed_value": "R = 0", "effect_before": effect(summary, "rhat_prereg"), "effect_after": effect(summary, "primary_rm")},
        {"id": "ix", "audit": "A8", "element": "calibracion de la nula", "preregistered": "sigma = 1 en la calibracion (one)",
         "deployed": "sigma_hat HAC en cada camino (hac)", "preregistered_value": "one", "deployed_value": "hac",
         "effect_before": effect(summary, "rm_one"), "effect_after": effect(summary, "primary_rm")},
        {"id": "x", "audit": "A8", "element": "N_cal", "preregistered": "10000 por D", "deployed": "50000 por D",
         "preregistered_value": N_CAL_PREREG, "deployed_value": N_CAL,
         "effect_before": effect(summary, "rm_hac_10k"), "effect_after": effect(summary, "primary_rm")},
        {"id": "xi", "audit": "A8", "element": "n de la calibracion", "preregistered": "n = D (convencion publicada)",
         "deployed": "n = D - 1 (incrementos de la ventana de D puntos)", "preregistered_value": "D",
         "deployed_value": "D - 1", "effect_before": effect(summary, "rm_hac_nD"), "effect_after": effect(summary, "primary_rm")},
        {"id": "xii", "audit": "A8", "element": "DF-GLS (comparador post hoc)", "preregistered": "no registrado; publicado con AIC",
         "deployed": "MAIC de Ng-Perron", "preregistered_value": "AIC", "deployed_value": "MAIC",
         "effect_before": effect(summary, "dfgls_aic"), "effect_after": effect(summary, "dfgls_maic")},
    ]
    if primary_is_gls():
        new.append({"id": "xiii", "audit": "A8", "element": "anclaje del estadistico (regla GLS de B4)",
                    "preregistered": "RM anclado en la media", "deployed": "RM-GLS (anclado por GLS)",
                    "preregistered_value": "media", "deployed_value": "GLS",
                    "effect_before": effect(summary, "primary_rm"), "effect_after": effect(summary, "primary_rmgls")})
    return rows + new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    hashes, prot = data_hashes()
    if not all(v["match"] for v in hashes.values()) or not prot["match"]:
        print("HASHES NO COINCIDEN: se detiene B6", hashes, prot)
        return 6
    os.makedirs(CKPT, exist_ok=True)
    data = {}
    for idx in RDV.INDICES:
        for Dw in RDV.WINDOW_SIZES:
            t1 = time.time()
            data[(idx, Dw)] = scores_for(idx, Dw, a.cores)
            print("  %s D=%d  %.0f s" % (idx, Dw, time.time() - t1), flush=True)
    fp, lat, summary = cell_metrics(data)
    mt = matched(data)
    p0 = paso0(a.cores)
    oo = oos(a.cores)
    gls = primary_is_gls()
    out = {"provenance": C.provenance(__file__, seed_family=FAM),
           "data_hashes": hashes, "protocol_hash": prot, "primary_is_gls": gls, "primary_key": primary_key(),
           "config": {"N_cal": N_CAL, "cal_seed": CAL_SEED, "calibration_n": "D - 1",
                      "window": "log_price[i - D : i], fecha i", "alpha": C.ALPHA,
                      "prereg_baselines_for_adverse_rule": PREREG_BASELINES,
                      "mzt_nominal": "MZt < %s" % U.NP_CV5["c"]["MZt"]},
           "summary": summary, "fp_cells": fp, "latency_cells": lat, "matched_rate": mt,
           "adverse_cells_primary": adverse(fp), "paso0": p0, "oos_size": oo,
           "elapsed_sec": round(time.time() - t0, 1)}
    C.write_result(OUT, out, __file__)
    dev = {"provenance": C.provenance(__file__, seed_family=FAM), "source_a7": "deviation_table_audit7.json",
           "rows": deviations(summary)}
    C.write_result(OUT_DEV, dev, __file__)
    for t, s in summary.items():
        print("%-14s FP media %.4f max %.3f  detecciones %d/%d  latencia %s" % (
            t, s["fp_mean"], s["fp_max"], s["detections"], s["event_cells"], s["mean_latency_detected"]))
    print("tasa igualada", mt["target_fpr_pooled_primary"], {t: (v["false_alarm_episodes"], round(v["censored_latency_mean"], 1))
                                                              for t, v in mt["tests"].items()})
    print("Paso 0", p0["worst"], "OOS", {k: v["primary_rm"]["rate"] for k, v in oo["by_D"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
