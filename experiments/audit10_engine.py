"""
Auditoria A10 - motor: calibracion de N_cal = 500 000 sobre los caminos de produccion.

Las filas son las de A9 (audit9_engine.row: RM-GLS con los cinco theta, RM,
MSB-HAC, variante (b) de B9.3, DF-GLS, MZt, MSB, retardo, s2_AR, ADF, PP), sin
KPSS, ZA ni P_T. La calibracion recorre el mismo flujo de produccion que A9
(default_rng(42), un standard_normal(n) por camino, Y_0 = 0, Y = cumsum): los
primeros 50 000 caminos son los de audit9_cal/cal_n<n>.npz y se reutilizan tras
un Paso 0 de 50 filas; los caminos 50 000-499 999 se calculan nuevos continuando
el flujo. Checkpoint por trozo en npz; reanudable.
"""
import math
import os
import time

import numpy as np
from joblib import Parallel, delayed

import audit10_common as C
import audit9_engine as E

CAL_FLAGS = {"cases": E.CASES, "adfpp": True, "kpss": False, "za": False, "pt": False}
CAL_COLS = E.columns(**CAL_FLAGS)
CKPT_CAL = os.path.join(C.CKPT_ROOT, "audit10_cal")
CKPT_A9_CAL = os.path.join(C.CKPT_ROOT, "audit9_cal")
N_CAL = 500000
N_REUSE = E.N_CAL
PASO0 = 50


def _cal_rows(block, n):
    return E._cal_rows(block, n, CAL_FLAGS)


def a9_cal(n):
    p = os.path.join(CKPT_A9_CAL, "cal_n%d.npz" % n)
    if not os.path.exists(p):
        return None, None
    with np.load(p) as z:
        return z["rows"], tuple(str(c) for c in z["cols"])


def calibration(n, cores, t_block, max_seconds, resume_cmd, n_cal=N_CAL, log=print):
    """Muestra nula de n_cal caminos de produccion en n; devuelve (filas, columnas, info)."""
    final = os.path.join(CKPT_CAL, "cal_n%d.npz" % n)
    if os.path.exists(final):
        with np.load(final) as z:
            if bool(z["complete"]) and z["rows"].shape == (n_cal, len(CAL_COLS)):
                return z["rows"], CAL_COLS, {k: z[k].item() for k in ("paso0_max_abs_diff", "reused_rows",
                                                                     "wall_new_sec") if k in z}
    os.makedirs(CKPT_CAL, exist_ok=True)
    m = E.cal_chunk_size(n)
    n_chunks = int(math.ceil(n_cal / m))
    a9_rows, a9_cols = a9_cal(n)
    reuse = 0
    sel = None
    if a9_rows is not None and N_REUSE % m == 0:
        reuse = min(a9_rows.shape[0], N_REUSE) // m
        J9 = {c: i for i, c in enumerate(a9_cols)}
        sel = [J9[c] for c in CAL_COLS]
    rng = np.random.default_rng(E.CAL_SEED)

    def cpath(j):
        return os.path.join(CKPT_CAL, "cal_n%d_m%d_j%05d.npz" % (n, m, j))
    paso0 = None
    j = 0
    sps = None
    wall_new = 0.0
    while j < n_chunks:
        wave = []
        for jj in range(j, min(n_chunks, j + cores)):
            k = min(m, n_cal - jj * m)
            block = rng.standard_normal((k, n))   # mismo orden de consumo que k llamadas standard_normal(n)
            if jj < reuse:
                if jj == 0 and paso0 is None:
                    mine = _cal_rows(block[:PASO0], n)
                    paso0 = float(np.max(np.abs(mine - a9_rows[:PASO0][:, sel])))
                continue
            if not os.path.exists(cpath(jj)):
                wave.append((jj, block))
        if wave:
            need = (sps or 0.0) * sum(b.shape[0] for _, b in wave) / max(1, min(cores, len(wave)))
            if time.time() - t_block + need > max_seconds:
                raise C.BudgetExhausted("cal n=%d: trozo %d no cabe en el tope.\nREANUDAR CON:\n  %s" % (n, j, resume_cmd))
            t0 = time.time()
            res = Parallel(n_jobs=min(cores, len(wave)), backend="loky")(delayed(_cal_rows)(b, n) for _, b in wave)
            el = time.time() - t0
            wall_new += el
            for (jj, b), r in zip(wave, res):
                tmp = cpath(jj) + ".tmp.npz"
                np.savez(tmp, rows=r, complete=True, elapsed=el)
                os.replace(tmp, cpath(jj))
            sps = el * min(cores, len(wave)) / sum(b.shape[0] for _, b in wave)
            if (j // cores) % 20 == 0:
                log("    cal n=%d trozos %d-%d de %d  %.1f s" % (n, j, j + len(wave) - 1, n_chunks, el))
        j += cores
    if reuse and paso0 is None:
        raise RuntimeError("Paso 0 de la calibracion no evaluado")
    parts = [a9_rows[:reuse * m][:, sel]] if reuse else []
    for jj in range(reuse, n_chunks):
        with np.load(cpath(jj)) as z:
            parts.append(z["rows"])
            wall_prev = float(z["elapsed"])
    rows = np.vstack(parts)
    info = {"paso0_max_abs_diff": paso0 if paso0 is not None else float("nan"), "reused_rows": reuse * m,
            "wall_new_sec": wall_new}
    tmp = final + ".tmp.npz"
    np.savez(tmp, rows=rows, cols=np.array(CAL_COLS), complete=True, **info)
    os.replace(tmp, final)
    for jj in range(reuse, n_chunks):
        os.remove(cpath(jj))
    return rows, CAL_COLS, info


def load_cal(n):
    p = os.path.join(CKPT_CAL, "cal_n%d.npz" % n)
    with np.load(p) as z:
        info = {k: z[k].item() for k in ("paso0_max_abs_diff", "reused_rows", "wall_new_sec") if k in z}
        return z["rows"], tuple(str(c) for c in z["cols"]), info


def production_control(n, rows, cols, cores):
    """RM-GLS theta = 0.1 y theta = 0 (hac) frente a _simulate_null_statistics de produccion, N_cal filas."""
    from stationarity_test.empirical_eigenvalues import _simulate_null_statistics
    I = E.index(cols)
    jobs = [(case, mode) for case in E.CASES for mode in ("theta", "zero")]

    def one(case, mode):
        return _simulate_null_statistics((0.1, 0.1), 0.0, n, rows.shape[0], E.CAL_SEED, deterministics=case,
                                         cal_sigma="hac", anchor="gls", tau_mode=mode)
    res = Parallel(n_jobs=min(cores, len(jobs)), backend="loky")(delayed(one)(c, m) for c, m in jobs)
    out = {}
    for (case, mode), ref in zip(jobs, res):
        col = "%s|%s" % (case, E.tname(0.1 if mode == "theta" else 0.0))
        out[col] = float(np.max(np.abs(rows[:, I[col]] - ref)))
    return out
