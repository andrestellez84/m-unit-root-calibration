"""
Auditoria A7 - Bloque 1: analisis de DGP 5.

Aplica las reglas registradas en la primera enmienda (commit 187300b), en la
segunda (experiments/enmienda2_dgp5_audit7.md) y en audit7_readout.py. Este
archivo se commitea ANTES de ejecutar cualquier celda de DGP 5: la lectura
precede a los datos.

Entradas (checkpoints por serie del runner, nunca agregados previos):
  cal_rw_n{n}        calibracion bajo la nula compuesta, 5000 series, n in CAL_N_ACTIVE
  adaptnull_n{n}     nula nominal del test adaptativo (A5), 50000 series
  dgp5_n..._rho..._r celdas activas (registradas y extension), 2000 series
Mas kappa2_simcv_audit7.json (valor critico simulado) y
kappa2_handicap_audit7.json (advertencia del handicap).
Las celdas de n=1000 retiradas por la segunda enmienda se listan como retiradas,
no como ausentes.

Reglas
------
Puntaje por procedimiento, mayor = mas evidencia contra H0:
  propuesto R=0.50 / R_hat : -estadistico            (cola inferior)
  ADF, PP, DF-GLS          : -(p + 1e-12 u)          (u: desempate por serie)
  bootstrap DF-GLS         : -(p + u/(B+1))          (p-valor aleatorizado dentro
                                                      de su celda de la rejilla)
  kappa_2                  : kappa_2                  (cola superior)
Tamano igualado: rechaza si el puntaje supera su cuantil 0.95 sobre la
calibracion del mismo n.
Union calibrada conjuntamente: p empirico de cada componente sobre la
calibracion, p(s) = #{calibracion >= s} / N_cal; rechaza si min(p_boot, p_k2)
< alpha*, con alpha* hallado por biseccion como el mayor nivel cuya tasa sobre
la calibracion no supera 0.05 (se reporta la tasa alcanzada).
Union Bonferroni: cada componente a 0.025 sobre la misma escala.
Quien gana: RO.paired_winner (McNemar exacto pareado, p < 0.05).

Prediccion 1 (segunda enmienda), por version del test propuesto y por n:
  registered  interior registrado RO.INTERIOR_P1: veredicto literal de la
              condicion de falsacion. GOBIERNA la consecuencia registrada y es el
              resultado primario, con su diagnostico de techo: potencia de kappa_2
              en la medicion pre-registrada del handicap y potencias a tamano
              igualado de la union, kappa_2 y bootstrap en los datos de DGP 5.
  extension   RO.EXTENSION_P1: contraste POST-REGISTRO etiquetado, con veredicto
              propio; no anula ni sustituye al registrado.

Uso: python experiments/audit7_dgp5_analysis.py
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                   # noqa: E402
import audit7_design as D                                   # noqa: E402
import audit7_dgp5_runner as RUN                            # noqa: E402
import audit7_readout as RO                                 # noqa: E402
from audit7_kappa2 import KAPPA2_CRITICAL                   # noqa: E402

OUT = os.path.join(C.RESULTS, "dgp5_mixed_audit7.json")
SIMCV = os.path.join(C.RESULTS, "kappa2_simcv_audit7.json")
HANDICAP = os.path.join(C.RESULTS, "kappa2_handicap_audit7.json")
SIMCV_CKPT = os.path.join(C.CKPT_ROOT, "audit7_calibration_kappa2")
HANDICAP_CKPT = os.path.join(C.CKPT_ROOT, "audit7_kappa2_handicap")
PREREG_COMMIT = "62216ee3f51f800bbf643a43cf7343d46952a18d"

PROCS = ("proposed_R050", "proposed_adaptive", "adf", "pp", "dfgls",
         "bootstrap_dfgls", "kappa2")
VERSIONS = ("proposed_R050", "proposed_adaptive")
REGIONS = (("registered", RO.INTERIOR_P1, "primario_registrado"),
           ("extension", RO.EXTENSION_P1, "contraste_post_registro"))
CEILING_PROCS = ("union_joint", "kappa2", "bootstrap_dfgls")
TIE_EPS = 1e-12
CAL_QUANTILE = 1.0 - RO.ALPHA
BONFERRONI_LEVEL = RO.ALPHA / 2.0
TIEBREAK_CHECK = 50


def added_commit(path):
    """Commit que anadio el archivo (None si no esta en git)."""
    out = C._git("log", "--diff-filter=A", "--format=%H", "--", path).splitlines()
    return out[-1] if out else None


def last_commit(path):
    """Ultimo commit que modifico el archivo: la version vigente de una enmienda.

    La primera ejecucion del analisis solo registraba added_commit y citaba la
    version inicial de la segunda enmienda (3767f6e) en lugar de la regenerada
    antes de los datos (a8761be).
    """
    out = C._git("log", "-1", "--format=%H", "--", path).splitlines()
    return out[0] if out else None


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------
def load_rows(ckpt_dir, tag, n_sim):
    """Filas por serie de una celda. (array, None) o (None, motivo)."""
    files = [f for f in glob.glob(os.path.join(ckpt_dir, tag + "_i*_k*.json"))
             if not f.endswith(".timing.json")]
    if not files:
        return None, "sin checkpoints"
    chunks = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        if d.get("tag") != tag:
            continue
        if d.get("complete") is not True:
            return None, "lote incompleto %s" % os.path.basename(f)
        chunks.append(d)
    chunks.sort(key=lambda d: d["i0"])
    rows, nxt = [], 0
    for d in chunks:
        if d["i0"] != nxt:
            return None, "hueco de lotes en i0=%d" % nxt
        rows.extend(d["rows"])
        nxt += d["k"]
    if nxt != n_sim:
        return None, "%d de %d series" % (nxt, n_sim)
    return np.asarray(rows, dtype=float), None


# ---------------------------------------------------------------------------
# Puntajes, umbrales y uniones
# ---------------------------------------------------------------------------
def scores(rows, B):
    I, u = RUN.IDX, rows[:, RUN.IDX["tiebreak_u"]]
    p_boot = rows[:, I["p_boot_dfgls"]]
    k2 = rows[:, I["kappa2"]]
    return {
        "proposed_R050": -rows[:, I["stat_R050"]],
        "proposed_adaptive": -rows[:, I["stat_adaptive"]],
        "adf": -(rows[:, I["p_adf"]] + TIE_EPS * u),
        "pp": -(rows[:, I["p_pp"]] + TIE_EPS * u),
        "dfgls": -(rows[:, I["p_dfgls"]] + TIE_EPS * u),
        "bootstrap_dfgls": -(np.where(np.isnan(p_boot), 1.0, p_boot) + u / (B + 1.0)),
        "kappa2": np.where(np.isnan(k2), -np.inf, k2),
    }


def empirical_p(values, cal_sorted):
    """#{calibracion >= s} / N para cada s."""
    return 1.0 - np.searchsorted(cal_sorted, values, side="left") / cal_sorted.size


def bisect_joint_alpha(m_cal, target_count):
    """Mayor nivel a con #(m_cal < a) <= target_count, por biseccion."""
    def count(a):
        return int((m_cal < a).sum())
    lo, hi = 0.0, 1.0 + 1e-9
    if count(hi) <= target_count:
        return hi, count(hi)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if count(mid) <= target_count:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-15:
            break
    # verificacion independiente por estadisticos de orden
    ms = np.sort(m_cal)
    k = min(target_count, ms.size)
    while k > 0 and k < ms.size and ms[k - 1] == ms[k]:
        k -= 1
    if count(lo) != k:
        raise RuntimeError("biseccion (%d) y estadisticos de orden (%d) no coinciden"
                           % (count(lo), k))
    return lo, count(lo)


def rate(mask):
    mask = np.asarray(mask, dtype=bool)
    k = int(mask.sum())
    lo, hi = C.clopper_pearson(k, mask.size)
    return {"rate": k / mask.size, "rejections": k, "n": int(mask.size),
            "ci_lower": lo, "ci_upper": hi}


def calibrate(cal_rows, B):
    s = scores(cal_rows, B)
    N = cal_rows.shape[0]
    target = int(round(RO.ALPHA * N))
    thr = {p: float(np.quantile(s[p], CAL_QUANTILE)) for p in PROCS}
    achieved = {p: rate(s[p] > thr[p]) for p in PROCS}
    sorted_boot = np.sort(s["bootstrap_dfgls"])
    sorted_k2 = np.sort(s["kappa2"])
    m_cal = np.minimum(empirical_p(s["bootstrap_dfgls"], sorted_boot),
                       empirical_p(s["kappa2"], sorted_k2))
    alpha_star, cnt = bisect_joint_alpha(m_cal, target)
    bonf_cal = (np.minimum(empirical_p(s["bootstrap_dfgls"], sorted_boot),
                           empirical_p(s["kappa2"], sorted_k2)) < BONFERRONI_LEVEL)
    k2_cv_025 = float(np.quantile(cal_rows[:, RUN.IDX["kappa2"]], 1.0 - BONFERRONI_LEVEL))
    return {"thresholds": thr, "achieved_size": achieved,
            "joint_union_alpha_star": alpha_star,
            "joint_union_achieved_size": {"rejections": cnt, "n": N, "rate": cnt / N},
            "bonferroni_union_achieved_size": rate(bonf_cal),
            "kappa2_cv_0.025_calibrated": k2_cv_025,
            "_sorted_boot": sorted_boot, "_sorted_k2": sorted_k2}


def rejections_size_matched(rows, B, cal):
    s = scores(rows, B)
    rej = {p: s[p] > cal["thresholds"][p] for p in PROCS}
    pb = empirical_p(s["bootstrap_dfgls"], cal["_sorted_boot"])
    pk = empirical_p(s["kappa2"], cal["_sorted_k2"])
    rej["union_joint"] = np.minimum(pb, pk) < cal["joint_union_alpha_star"]
    rej["union_bonferroni"] = np.minimum(pb, pk) < BONFERRONI_LEVEL
    return rej


def rejections_nominal(rows, n, adapt_null_sorted, cv_sim, k2_cv_025):
    I = RUN.IDX
    p_boot = rows[:, I["p_boot_dfgls"]]
    k2 = rows[:, I["kappa2"]]
    out = {
        "proposed_R050": rows[:, I["p_R050_nominal"]] < RO.ALPHA,
        "adf": rows[:, I["p_adf"]] < RO.ALPHA,
        "pp": rows[:, I["p_pp"]] < RO.ALPHA,
        "dfgls": rows[:, I["p_dfgls"]] < RO.ALPHA,
        "bootstrap_dfgls": np.nan_to_num(p_boot, nan=1.0) < RO.ALPHA,
        "kappa2_asymptotic_1.358": np.nan_to_num(k2, nan=-np.inf) > KAPPA2_CRITICAL[0.05],
        "kappa2_simulated_cv": np.nan_to_num(k2, nan=-np.inf) > cv_sim,
        "union_bonferroni_nominal": ((np.nan_to_num(p_boot, nan=1.0) < BONFERRONI_LEVEL)
                                     | (np.nan_to_num(k2, nan=-np.inf) > k2_cv_025)),
    }
    if adapt_null_sorted is not None:
        p_adapt = np.searchsorted(adapt_null_sorted, rows[:, I["stat_adaptive"]],
                                  side="right") / adapt_null_sorted.size
        out["proposed_adaptive"] = p_adapt < RO.ALPHA
    return out


def winner(rej, a, b):
    w, p, na, nb = RO.paired_winner(rej[a], rej[b])
    return {"winner": a if w == "A" else (b if w == "B" else "empate"),
            "mcnemar_p": p, "only_%s" % a: na, "only_%s" % b: nb}


# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------
def status_from(wins, total):
    if total == 0:
        return "sin_celdas"
    if wins == 0:
        return "no_se_cumple"
    if wins == total:
        return "se_cumple"
    return "se_cumple_parcialmente"


def main():
    with open(SIMCV, encoding="utf-8") as f:
        simcv = json.load(f)
    handicap = None
    if os.path.exists(HANDICAP):
        with open(HANDICAP, encoding="utf-8") as f:
            handicap = json.load(f)

    B = D.DGP5_B
    missing, controls, by_n = {}, {}, {}
    withdrawn = {D.dgp5_tag(*c): "retirada por la segunda enmienda" for c in D.DGP5_CONFIRM}
    for n in D.CAL_N_GRID:
        if n not in D.CAL_N_ACTIVE:
            withdrawn[D.cal_tag(n)] = "retirada por la segunda enmienda"
            withdrawn["adaptnull_n%d" % n] = "retirada por la segunda enmienda"

    for n in D.CAL_N_ACTIVE:
        cal_rows, why = load_rows(RUN.CKPT, D.cal_tag(n), D.N_CAL)
        if cal_rows is None:
            missing[D.cal_tag(n)] = why
            continue
        cal = calibrate(cal_rows, B)
        # control: kappa_2 de la calibracion == el de la compuerta simulada
        ref, why_ref = load_rows(SIMCV_CKPT, D.cal_tag(n), D.N_CAL)
        controls["kappa2_calibration_vs_simcv_n%d" % n] = (
            float(np.nanmax(np.abs(cal_rows[:, RUN.IDX["kappa2"]] - ref[:, 0])))
            if ref is not None else "referencia ausente: %s" % why_ref)
        controls["tiebreak_recomputed_cal_n%d" % n] = float(max(
            abs(cal_rows[i, RUN.IDX["tiebreak_u"]] - RUN.tiebreak_u(D.cal_seed_base(n), i))
            for i in range(TIEBREAK_CHECK)))
        adapt_rows, why_a = load_rows(RUN.CKPT, "adaptnull_n%d" % n, RUN.ADAPT_NULL_N)
        adapt_sorted = None
        if adapt_rows is None:
            missing["adaptnull_n%d" % n] = why_a
        else:
            adapt_sorted = np.sort([RO.statistic(g1, g2, RO.adaptive_R(g1, g2))
                                    for g1, g2 in adapt_rows])
        by_n[n] = {"cal": cal, "adapt_sorted": adapt_sorted,
                   "cv_sim": simcv["cells"][str(n)]["simulated_critical_values"]["0.05"],
                   "cells": {}}

    cells_out = {}
    for (n, rho, r) in D.dgp5_cells_active():
        tag = D.dgp5_tag(n, rho, r)
        if n not in by_n:
            missing[tag] = "calibracion de n=%d ausente" % n
            continue
        rows, why = load_rows(RUN.CKPT, tag, D.DGP5_N_SIM)
        if rows is None:
            missing[tag] = why
            continue
        ctx = by_n[n]
        sm = rejections_size_matched(rows, B, ctx["cal"])
        nom = rejections_nominal(rows, n, ctx["adapt_sorted"], ctx["cv_sim"],
                                 ctx["cal"]["kappa2_cv_0.025_calibrated"])
        I = RUN.IDX
        shares = {v: {"median": float(np.nanmedian(rows[:, I[c]])),
                      "mean": float(np.nanmean(rows[:, I[c]]))}
                  for v, c in (("proposed_R050", "g2_share_R050"),
                               ("proposed_adaptive", "g2_share_adaptive"))}
        wins = {}
        for v in VERSIONS:
            for other in ("union_joint", "union_bonferroni", "bootstrap_dfgls", "kappa2", "dfgls"):
                wins["%s_vs_%s" % (v, other)] = winner(sm, v, other)
        rec = {"tag": tag, "n": n, "rho": rho, "r": r, "seed_base": D.dgp5_seed_base(n, rho, r),
               "n_sim": D.DGP5_N_SIM, "B": B,
               "grid": "extension_enmienda2" if D.is_weak(r) else "registrada",
               "interior_prediction_1": (rho, r) in RO.INTERIOR_P1,
               "extension_prediction_1": (rho, r) in RO.EXTENSION_P1,
               "power_size_matched": {k: rate(v) for k, v in sm.items()},
               "power_nominal": {k: rate(v) for k, v in nom.items()},
               "winners_size_matched": wins,
               "g2_energy_share": shares,
               "mean_R_hat": float(np.nanmean(rows[:, I["R_hat"]])),
               "nan_counts": {"p_boot_dfgls": int(np.isnan(rows[:, I["p_boot_dfgls"]]).sum()),
                              "kappa2": int(np.isnan(rows[:, I["kappa2"]]).sum())}}
        if r > 1.0:
            h_tag = "k2h_ar_n%d_rho%.2f_r%s" % (n, rho, D.fmt_r(r))
            href, why_h = load_rows(HANDICAP_CKPT, h_tag, D.DGP5_N_SIM)
            controls["kappa2_dgp5_vs_handicap_%s" % tag] = (
                float(np.nanmax(np.abs(rows[:, I["kappa2"]] - href[:, 0])))
                if href is not None else "referencia ausente: %s" % why_h)
        controls["tiebreak_recomputed_%s" % tag] = float(max(
            abs(rows[i, I["tiebreak_u"]] - RUN.tiebreak_u(rec["seed_base"], i))
            for i in range(TIEBREAK_CHECK)))
        cells_out[tag] = rec

    # --- predicciones por n y version -----------------------------------
    predictions = {}
    declared = (handicap or {}).get("declared_by_n", {})
    declared_ext = (handicap or {}).get("declared_by_n_extension", {})
    for n in sorted({c["n"] for c in cells_out.values()}):
        at_n = [v for v in cells_out.values() if v["n"] == n]
        h_reg = declared.get(str(n), {}).get("handicap_declared")
        h_ext = declared_ext.get(str(n), {}).get("handicap_declared")
        interior = [c for c in at_n if (c["rho"], c["r"]) in RO.INTERIOR_P1]
        pn = {"handicap_kappa2_declared": h_reg,
              "handicap_kappa2_declared_extension": h_ext,
              "ceiling_registered_interior": (
                  {p: {"min": min(c["power_size_matched"][p]["rate"] for c in interior),
                       "max": max(c["power_size_matched"][p]["rate"] for c in interior)}
                   for p in CEILING_PROCS} if interior else None)}
        handicap_of = {"registered": h_reg, "extension": h_ext}
        k2_interior = [c["power_ar_break"]["rate"] for c in (handicap or {}).get("cells", {}).values()
                       if c["n"] == n and c["interior_prediction_1"]]
        for v in VERSIONS:
            for region, cellset, kind in REGIONS:
                expected = [c for c in D.dgp5_cells_active() if c[0] == n and (c[1], c[2]) in cellset]
                avail = [c for c in at_n if (c["rho"], c["r"]) in cellset]
                won = [c for c in avail
                       if c["winners_size_matched"]["%s_vs_union_joint" % v]["winner"] == v]
                bands = {}
                for c in won:
                    b = RO.share_band(c["g2_energy_share"][v]["median"])
                    bands[b] = bands.get(b, 0) + 1
                st = status_from(len(won), len(avail))
                if len(avail) < len(expected):
                    st = "incompleta"
                label = "P1_%s" % v if region == "registered" else "P1_%s_%s" % (region, v)
                pn[label] = {"kind": kind, "status": st, "wins": len(won), "cells": len(avail),
                             "cells_expected": len(expected),
                             "won_cells": sorted(c["tag"] for c in won),
                             "share_bands_of_wins": bands,
                             "clean_contrast": not bool(handicap_of[region])}
            lit = pn["P1_%s" % v]["status"]
            pn["falsification_%s" % v] = {
                "registered_literal_triggered_governs_consequence":
                    None if lit == "incompleta" else lit == "no_se_cumple",
                "diagnostic_ceiling": {
                    "declared_non_informative_in_amendment2": True,
                    "kappa2_power_min_registered_interior_handicap_measurement":
                        min(k2_interior) if k2_interior else None,
                    "size_matched_power_registered_interior": pn["ceiling_registered_interior"],
                    "source": "kappa2_handicap_audit7.json, medicion prevista en la primera enmienda"},
                "post_registration_extension_status": pn["P1_extension_%s" % v]["status"],
                "extension_does_not_override": True}
            r1 = [c for c in at_n if c["r"] == RO.EXTREME_MEAN_P2_R]
            won2 = [c for c in r1 if c["winners_size_matched"]["%s_vs_bootstrap_dfgls" % v]["winner"]
                    == "bootstrap_dfgls"]
            pn["P2_%s" % v] = {"status": status_from(len(won2), len(r1)),
                               "bootstrap_wins": len(won2), "cells": len(r1)}
            p3 = [c for c in at_n if (c["rho"], c["r"]) == RO.EXTREME_VARIANCE_P3]
            won3 = [c for c in p3 if c["winners_size_matched"]["%s_vs_kappa2" % v]["winner"] == "kappa2"]
            pn["P3_%s" % v] = {"status": status_from(len(won3), len(p3)),
                               "kappa2_wins": len(won3), "cells": len(p3)}
        predictions[str(n)] = pn

    calib_out = {str(n): {k: v for k, v in ctx["cal"].items() if not k.startswith("_")}
                 for n, ctx in by_n.items()}
    regression = [k for k, v in controls.items() if isinstance(v, float) and v != 0.0]
    amendments = {path: {"added": added_commit(path), "in_force": last_commit(path)}
                  for path in RUN.AMENDMENTS}

    C.atomic_write_json(OUT, {
        "provenance": C.provenance(
            dgp="dgp5_mixed_deviation", n_sim=D.DGP5_N_SIM,
            seed_formula="dgp5 60*10^8+idx*10^5; calibracion 70*10^8+n_idx*10^5; desempate [69, seed_base, i]",
            prereg_commit=PREREG_COMMIT, amendment_commits=amendments,
            extra_code_files=[RUN.WORKER_R]),
        "rules": {"win_alpha": RO.WIN_ALPHA, "share_low": RO.SHARE_LOW,
                  "share_high": RO.SHARE_HIGH, "calibration_quantile": CAL_QUANTILE,
                  "bonferroni_level": BONFERRONI_LEVEL,
                  "interior_prediction_1": sorted([list(x) for x in RO.INTERIOR_P1]),
                  "extension_prediction_1_post_registration": sorted([list(x) for x in RO.EXTENSION_P1]),
                  "consequence_governed_by": "veredicto literal sobre el interior registrado"},
        "calibration_by_n": calib_out,
        "cells": cells_out,
        "predictions_by_n": predictions,
        "regression_controls": controls,
        "regression_controls_nonzero": regression,
        "withdrawn": withdrawn,
        "missing_or_incomplete": missing,
        "complete": not missing,
    })
    print("celdas analizadas: %d de %d   ausentes/incompletas: %d   retiradas: %d   "
          "controles con diferencia: %d"
          % (len(cells_out), len(D.dgp5_cells_active()), len(missing), len(withdrawn), len(regression)))
    for n, pn in predictions.items():
        print("n=%s: %s" % (n, {k: (v.get("status", v) if isinstance(v, dict) else v)
                               for k, v in pn.items()}))
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
