"""
Auditoria A12 - ejecucion por lotes con checkpoint npz atomico y tope por bloque.

run_cell(tag, reps, row_fn, ncols, ckpt_dir, cores, t_block, max_seconds, resume):
calcula row_fn(i) para i = 0..reps-1 en oleadas de `wave` indices repartidos entre
los nucleos; cada oleada se guarda en <ckpt_dir>/<tag>_i<i0>.npz (rows, i0, elapsed).
Es reanudable: las oleadas ya escritas no se recalculan. load_cell devuelve las filas
en orden de replica.
"""
import os
import time

import numpy as np
from joblib import Parallel, delayed

import audit12_common as C


def _rows(row_fn, idx):
    return [row_fn(i) for i in idx]


def warm(cores):
    Parallel(n_jobs=cores, backend="loky")(delayed(len)([k]) for k in range(cores))


def wave_size(cores, per_core):
    return cores * per_core


def ckpt_file(ckpt_dir, tag, i0):
    return os.path.join(ckpt_dir, "%s_i%07d.npz" % (tag, i0))


def run_cell(tag, reps, row_fn, ncols, ckpt_dir, cores, t_block, max_seconds, resume, per_core=100, log=print):
    os.makedirs(ckpt_dir, exist_ok=True)
    step = wave_size(cores, per_core)
    done = 0
    for i0 in range(0, reps, step):
        p = ckpt_file(ckpt_dir, tag, i0)
        if os.path.exists(p):
            done += 1
            continue
        if time.time() - t_block > max_seconds:
            raise C.BudgetExhausted("%s: tope antes de i0=%d.\nREANUDAR CON:\n  %s" % (tag, i0, resume))
        t0 = time.time()
        idx = list(range(i0, min(i0 + step, reps)))
        split = [s for s in (idx[j::cores] for j in range(cores)) if s]
        res = Parallel(n_jobs=len(split), backend="loky")(delayed(_rows)(row_fn, s) for s in split)
        rows = np.full((len(idx), ncols), np.nan)
        for s, r in zip(split, res):
            rows[np.array(s) - i0] = r
        tmp = p + ".tmp.npz"
        np.savez(tmp, rows=rows, i0=i0, elapsed=time.time() - t0)
        os.replace(tmp, p)
        log("    %s i0=%d/%d  %.1f s" % (tag, i0, reps, time.time() - t0))
    return done


def load_cell(ckpt_dir, tag, reps, per_core=None):
    parts, el, i0 = [], 0.0, 0
    while i0 < reps:
        p = ckpt_file(ckpt_dir, tag, i0)
        if not os.path.exists(p):
            raise KeyError("%s: falta el lote i0=%d" % (tag, i0))
        with np.load(p) as z:
            parts.append(z["rows"])
            el += float(z["elapsed"])
            i0 += z["rows"].shape[0]
    R = np.vstack(parts)
    if R.shape[0] != reps:
        raise KeyError("%s: %d filas, se esperaban %d" % (tag, R.shape[0], reps))
    return R, el


def cell_complete(ckpt_dir, tag, reps):
    try:
        load_cell(ckpt_dir, tag, reps)
        return True
    except KeyError:
        return False
