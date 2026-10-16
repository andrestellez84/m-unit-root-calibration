"""
Auditoria A7 - infraestructura comun.

Cada funcion de este modulo existe por un fallo concreto de A5, A6 o A7:

- provenance():         un JSON sin procedencia no es un resultado (regla 4).
                        Registra el commit y ADEMAS el sha256 y el estado git de
                        cada script audit7_*: en la primera corrida de A7 un JSON
                        declaraba worktree_dirty=false mientras el codigo que lo
                        produjo aun no estaba en el commit que citaba, porque los
                        archivos sin rastrear no cuentan como cambios.
- atomic_write_json():  una interrupcion no puede dejar un JSON a medias (regla 2).
- seed_base():          esquema de semillas con bloques DISJUNTOS por construccion.
                        Formulas del tipo 600000 + n*100 + int(rho*100)*10 + int(r*10)
                        producen colisiones exactas entre celdas distintas.
- run_cell_batched():   sonda de 14 series, proyeccion del costo real, checkpoint
                        por lote, tope de tiempo con parada limpia entre lotes y
                        salto de lote que COMPRUEBA complete (en A6 una celda de
                        602/2000 se salto como "ya completa").
"""
import datetime
import glob
import hashlib
import json
import math
import os
import subprocess
import sys
import time

import numpy as np
from scipy.stats import beta, binom

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RESULTS = os.path.join(HERE, "results")
CKPT_ROOT = os.path.join(RESULTS, "checkpoints")

ALPHA = 0.05
PROBE_SERIES = 14
TARGET_BATCH_SEC = 900.0            # ~15 min: perdida maxima por interrupcion
DEFAULT_MAX_SECONDS = 4 * 3600      # regla 1: ningun bloque supera 4 h

# ---------------------------------------------------------------------------
# Semillas: FAMILIA * 10^8 + indice_de_celda * 10^5.
# Cada celda dispone de 10^5 semillas consecutivas, muy por encima del mayor
# N_sim de A7 (5000), de modo que dos celdas no pueden compartir un solo
# sorteo, y dos familias no pueden solaparse mientras haya menos de 1000
# celdas por familia. La disjuncion se DEMUESTRA en cada script, no se asume.
# ---------------------------------------------------------------------------
SEED_BLOCK = 10 ** 5
SEED_FAMILY_SPAN = 10 ** 8


def seed_base(family, cell_index):
    if not (0 <= cell_index < SEED_FAMILY_SPAN // SEED_BLOCK):
        raise ValueError("cell_index fuera de rango: %r" % (cell_index,))
    return int(family) * SEED_FAMILY_SPAN + int(cell_index) * SEED_BLOCK


def seed_overlap_report(bases, n_sim):
    """Pares de celdas cuyos bloques [base, base+n_sim) se solapan."""
    items = sorted(bases.items(), key=lambda kv: kv[1])
    pairs = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            gap = items[j][1] - items[i][1]
            if gap >= n_sim:
                break
            pairs.append({"a": items[i][0], "b": items[j][0],
                          "shared_draws": int(n_sim - gap)})
    distinct = len(set(bases.values()))
    return {"n_cells": len(bases), "distinct_seed_bases": distinct,
            "exact_collisions": len(bases) - distinct,
            "overlapping_pairs": len(pairs),
            "max_shared_draws": max((p["shared_draws"] for p in pairs), default=0),
            "pairs_sample": pairs[:20]}


# ---------------------------------------------------------------------------
# Procedencia
# ---------------------------------------------------------------------------
def _git(*args):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    return r.stdout.strip()


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def code_manifest(extra_files=()):
    """sha256 y estado git de cada script audit7_* y de los archivos extra."""
    files = sorted(set(glob.glob(os.path.join(HERE, "audit7_*.py"))
                       + glob.glob(os.path.join(HERE, "audit7_*.R"))
                       + [os.path.abspath(p) for p in extra_files]))
    tracked = set(_git("ls-files").splitlines())
    modified = set(_git("diff", "--name-only", "HEAD").splitlines())
    out = {}
    for p in files:
        rel = os.path.relpath(p, REPO).replace(os.sep, "/")
        if rel not in tracked:
            state = "untracked"
        elif rel in modified:
            state = "modified"
        else:
            state = "committed"
        out[rel] = {"sha256": _sha256_file(p), "git_state": state}
    return out


def provenance(dgp, n_sim, seed_formula, extra_code_files=(), **extra):
    dirty = [l for l in _git("status", "--porcelain",
                             "--untracked-files=no").splitlines()
             if "__pycache__" not in l]
    code = code_manifest(extra_code_files)
    rec = {"dgp": dgp, "n_sim": n_sim, "seed_formula": seed_formula,
           "generated_utc": utc_now(), "commit": _git("rev-parse", "HEAD"),
           "worktree_dirty": bool(dirty),
           "entry_point": os.path.relpath(os.path.abspath(sys.argv[0]),
                                          REPO).replace(os.sep, "/"),
           "code": code,
           "code_all_committed": all(v["git_state"] == "committed"
                                     for v in code.values())}
    rec.update(extra)
    return rec


# ---------------------------------------------------------------------------
# E/S y estadistica basica
# ---------------------------------------------------------------------------
def atomic_write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    # En Windows os.replace puede fallar con "Acceso denegado" si otro proceso
    # (antivirus, indexador) tiene abierto el destino un instante. A7 perdio asi
    # la primera ejecucion del bloque 1. Reintentos acotados; si persiste, falla.
    for attempt in range(REPLACE_RETRIES):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == REPLACE_RETRIES - 1:
                raise
            time.sleep(min(0.25 * (attempt + 1), 3.0))


REPLACE_RETRIES = 20


def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def binomial_acceptance_region(n, p=ALPHA, level=0.95):
    """Region central exacta de la tasa observada bajo tasa verdadera p."""
    lo = binom.ppf((1 - level) / 2, n, p) / n
    hi = binom.ppf(1 - (1 - level) / 2, n, p) / n
    return float(lo), float(hi)


# ---------------------------------------------------------------------------
# Ejecucion por lotes
# ---------------------------------------------------------------------------
class BudgetExhausted(Exception):
    """El siguiente lote no cabe en el tope del bloque."""


def run_cell_batched(tag, n_sim, batch_fn, ckpt_dir, cores, t_block_start,
                     max_seconds, resume_cmd, log=print, probe_only=False,
                     k_batch_override=None):
    """
    Ejecuta una celda de n_sim series en lotes con checkpoint atomico.

    batch_fn(indices) -> list de filas (una por serie, cada fila una lista de
    floats). Debe ser determinista en el indice global de la serie, de modo
    que el troceo en lotes no altere ninguna trayectoria.

    Devuelve (rows, info). Lanza BudgetExhausted si el tope impide terminar;
    los lotes ya calculados quedan en disco y la reanudacion los reutiliza.
    El llamador debe calentar su pool de procesos ANTES de la primera celda:
    si no, la sonda cronometra el arranque de los procesos y sobreestima.
    """
    os.makedirs(ckpt_dir, exist_ok=True)

    def ck_path(i0, k):
        return os.path.join(ckpt_dir, "%s_i%06d_k%05d.json" % (tag, i0, k))

    def load(i0, k):
        p = ck_path(i0, k)
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("complete") is True and len(d.get("rows", [])) == k:
            return d
        return None                          # lote corrupto o parcial: se rehace

    def compute(i0, k):
        t0 = time.time()
        rows = batch_fn(list(range(i0, i0 + k)))
        el = time.time() - t0
        if len(rows) != k:
            raise RuntimeError("%s: lote i0=%d devolvio %d filas, esperaba %d"
                               % (tag, i0, len(rows), k))
        d = {"tag": tag, "i0": i0, "k": k, "rows": rows,
             "elapsed_sec": round(el, 3), "sec_per_series": el / k,
             "complete": True, "written_utc": utc_now()}
        atomic_write_json(ck_path(i0, k), d)
        return d

    chunks = []

    # --- sonda: costo real antes de comprometer la celda --------------------
    probe_k = min(PROBE_SERIES, n_sim)
    probe = load(0, probe_k)
    if probe is None:
        probe = compute(0, probe_k)
        log("    sonda  %d series: %.3f s/serie de pared"
            % (probe_k, probe["sec_per_series"]))
    else:
        log("    [CACHE] sonda i0=0 k=%d" % probe_k)
    chunks.append(probe)
    sps = max(float(probe["sec_per_series"]), 1e-6)
    projected = sps * n_sim
    log("    proyeccion de la celda: %.0f s = %.2f h" % (projected, projected / 3600))

    # tamano de lote determinista a partir de la sonda, para que la reanudacion
    # reconstruya exactamente las mismas fronteras de lote
    k_batch = int(max(probe_k, math.floor(TARGET_BATCH_SEC / sps)))
    k_batch = max(probe_k, (k_batch // probe_k) * probe_k)
    # La sonda de 14 series no es fiable como medida de costo (A7: el mismo lote
    # vario hasta 6x). El llamador puede fijar el lote con un presupuesto medido
    # en varias oleadas; debe repetirlo al reanudar para encontrar los lotes.
    if k_batch_override is not None:
        k_batch = int(k_batch_override)
        if k_batch < probe_k or k_batch % probe_k:
            raise ValueError("%s: k_batch=%d debe ser multiplo de %d" % (tag, k_batch, probe_k))
        log("    lote fijado por el llamador: %d series" % k_batch)

    # Solo sonda: sirve para presupuestar sin comprometer la celda. El lote de
    # sonda queda en disco y la ejecucion completa posterior lo reutiliza.
    if probe_only:
        return None, {"probe_sec_per_series": float(probe["sec_per_series"]),
                      "projected_sec": round(projected, 1), "k_batch": k_batch,
                      "complete": False, "probe_only": True}

    i0 = probe_k
    while i0 < n_sim:
        k = min(k_batch, n_sim - i0)
        got = load(i0, k)
        if got is not None:
            log("    [CACHE] lote i0=%d k=%d" % (i0, k))
            chunks.append(got)
            i0 += k
            continue
        spent = time.time() - t_block_start
        need = k * sps
        if spent + need > max_seconds:
            raise BudgetExhausted(
                "%s: el lote i0=%d (%d series, ~%.0f s) no cabe: transcurrido "
                "%.2f h de un tope de %.2f h.\nREANUDAR CON:\n  %s"
                % (tag, i0, k, need, spent / 3600, max_seconds / 3600, resume_cmd))
        d = compute(i0, k)
        chunks.append(d)
        sps = 0.7 * sps + 0.3 * float(d["sec_per_series"])
        log("    lote i0=%d k=%d  %.3f s/serie  (%d/%d)"
            % (i0, k, d["sec_per_series"], i0 + k, n_sim))
        i0 += k

    rows = []
    for c in sorted(chunks, key=lambda c: c["i0"]):
        rows.extend(c["rows"])
    if len(rows) != n_sim:
        raise RuntimeError("%s: %d filas agregadas, esperaba %d" % (tag, len(rows), n_sim))
    return rows, {"n_chunks": len(chunks),
                  "elapsed_sec": round(sum(float(c["elapsed_sec"]) for c in chunks), 2),
                  "probe_sec_per_series": float(probe["sec_per_series"]),
                  "projected_sec": round(projected, 1), "complete": True}
