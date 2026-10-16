"""
=============================================================================
Auditoria A6 - Experimento 1: wild bootstrap (bootUR) sobre DGP 1 y DGP 3.

Series generadas en Python con las semillas exactas de power_comparison.py y
transferidas a R por disco, para preservar el pareo celda a celda con las
columnas ya publicadas de ADF, PP, DF-GLS y el test propuesto (verificado en
audit6_paso0_pairing.py).

DISCIPLINA DE EJECUCION (impuesta tras la interrupcion de la corrida previa):

  1. El checkpoint es por LOTE, no por celda. Cada lote se escribe a disco de
     forma atomica (os.replace) en cuanto termina. La perdida maxima por una
     interrupcion es un lote, no una celda: la version anterior perdio 32.5 h
     de una sola celda a n=1000.
  2. Cada celda arranca con un lote SONDA de `cores` series, mide el costo real
     por serie y proyecta el tiempo de la celda ANTES de comprometerlo. No se
     extrapola desde un n mas pequeno.
  3. --max-seconds acota el bloque (por omision 4 h). Antes de cada lote se
     comprueba que quepa; si no, el proceso termina limpiamente e imprime el
     comando de reanudacion.
  4. Reanudar = volver a ejecutar el mismo comando. Los lotes ya completos se
     saltan.
  5. La celda de control r=1.0 de DGP 3 es una compuerta: si su tamano cae
     fuera de la region binomial de aceptacion, el barrido se detiene.

Uso:
  python experiments/audit6_wild_bootstrap_sweep.py --cells dgp1:200 \
      --tests both --n-sim 2000 --cores 14 --max-seconds 14400
=============================================================================
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np
from scipy.stats import beta

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")
CHUNK_DIR = os.path.join(RESULTS_DIR, "checkpoints", "bootur_chunks")
WORKER_R = os.path.join(HERE, "audit6_wild_bootstrap_worker.R")
MASTER = os.path.join(RESULTS_DIR, "wild_bootstrap_r_audit6.json")

ALPHA = 0.05
# Region binomial exacta de aceptacion para la compuerta de control (N_sim=2000,
# nivel nominal 0.05); se recalcula segun N_sim en check_control_gate().
TARGET_CHUNK_SEC = 900.0          # ~15 min por lote
DEFAULT_MAX_SECONDS = 4 * 3600    # 4 h por bloque

DGP3_RATIOS = [1.0, 2.0, 3.0, 4.0]
DGP3_N = [200, 1000]
DGP1_RHOS = [0.95, 0.97, 0.99]
DGP1_N = [200, 500, 1000]


def find_rscript():
    for cand in (os.environ.get("RSCRIPT"),
                 r"C:\Program Files\R\R-4.6.1\bin\x64\Rscript.exe",
                 shutil.which("Rscript")):
        if cand and os.path.exists(cand):
            return cand
    for root in (r"C:\Program Files\R", r"C:\Program Files (x86)\R"):
        if os.path.isdir(root):
            for d in sorted(os.listdir(root), reverse=True):
                p = os.path.join(root, d, "bin", "x64", "Rscript.exe")
                if os.path.exists(p):
                    return p
    raise RuntimeError("No encuentro Rscript.exe; exporta RSCRIPT=<ruta>")


RSCRIPT = find_rscript()


# --- generadores pareados con power_comparison.py ---------------------------
def dgp3_seed_base(n, ratio):
    """power_comparison.py:496"""
    return 300000 + n * 100 + int(ratio * 10)


def dgp1_seed_base(n, rho):
    """power_comparison.py:408"""
    return 100000 + n * 100 + int(rho * 100)


def generate_dgp3_series(n, ratio, n_series, i0=0):
    """RW con quiebre de varianza; replica generate_rw_break_variance."""
    seed_base = dgp3_seed_base(n, ratio)
    t_break = n // 2
    out = np.empty((n + 1, n_series), dtype=np.float64)
    for j in range(n_series):
        rng = np.random.default_rng(seed_base + i0 + j)
        eps = np.empty(n)
        eps[:t_break] = rng.standard_normal(t_break)
        eps[t_break:] = rng.standard_normal(n - t_break) * ratio
        out[0, j] = 0.0
        np.cumsum(eps, out=out[1:, j])
    return out


def generate_dgp1_series(n, rho, n_series, i0=0):
    """AR(1) persistente; replica generate_ar1."""
    seed_base = dgp1_seed_base(n, rho)
    out = np.empty((n + 1, n_series), dtype=np.float64)
    for j in range(n_series):
        rng = np.random.default_rng(seed_base + i0 + j)
        eps = rng.standard_normal(n)
        y = out[:, j]
        y[0] = 0.0
        for t in range(n):
            y[t + 1] = rho * y[t] + eps[t]
    return out


GENERATORS = {"dgp3": generate_dgp3_series, "dgp1": generate_dgp1_series}
PARAM_NAME = {"dgp3": "r", "dgp1": "rho"}
PARAM_FMT = {"dgp3": "{:.1f}", "dgp1": "{:.2f}"}


def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return round(lo, 6), round(hi, 6)


def atomic_write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def cell_tag(dgp, n, param):
    return "%s_n%d_%s%s" % (dgp, n, PARAM_NAME[dgp],
                            PARAM_FMT[dgp].format(param))


def run_chunk(dgp, n, param, i0, n_series, B, cores, tests):
    """Ejecuta un lote (o lo lee del checkpoint). Devuelve su dict."""
    tag = cell_tag(dgp, n, param)
    ck = os.path.join(CHUNK_DIR, "%s_i%06d_k%04d_%s.json"
                      % (tag, i0, n_series, tests))
    if os.path.exists(ck):
        with open(ck, encoding="utf-8") as f:
            d = json.load(f)
        if len(d.get("p_adf") or d.get("p_union") or []) == n_series:
            print("    [CACHE] lote i0=%d k=%d" % (i0, n_series))
            return d

    mat = GENERATORS[dgp](n, param, n_series, i0=i0)
    bin_path = os.path.join(CHUNK_DIR, "_tmp_%s_i%06d.bin" % (tag, i0))
    mat.T.tofile(bin_path)                      # disposicion columnar para R
    expected5 = ",".join("%.6f" % v for v in mat[:5, 0])
    out_json = os.path.join(CHUNK_DIR, "_tmp_%s_i%06d.json" % (tag, i0))

    cmd = [RSCRIPT, WORKER_R, bin_path, str(n), str(n_series), str(B),
           str(cores), out_json, expected5, tests]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        os.path.exists(bin_path) and os.remove(bin_path)
        raise RuntimeError("worker de R fallo (rc=%d):\n%s"
                           % (proc.returncode, proc.stdout + proc.stderr))

    with open(out_json, encoding="utf-8") as f:
        d = json.load(f)
    d.update({"dgp": dgp, "param_name": PARAM_NAME[dgp], "param_val": param,
              "i0": i0, "seed_base": (dgp3_seed_base(n, param) if dgp == "dgp3"
                                      else dgp1_seed_base(n, param))})
    atomic_write_json(ck, d)
    for p in (bin_path, out_json):
        if os.path.exists(p):
            os.remove(p)
    return d


def aggregate(chunks, n_sim, tests):
    """Agrega lotes en tasas de rechazo con IC binomial exacto."""
    out = {}
    for comp in ("adf", "union"):
        if tests not in (comp, "both"):
            continue
        pv = []
        for c in chunks:
            vals = c.get("p_" + comp)
            if vals is None:
                continue
            pv.extend(vals)
        if not pv:
            continue
        k = int(sum(1 for v in pv if v is not None and v < ALPHA))
        lo, hi = clopper_pearson(k, len(pv), ALPHA)
        out[comp] = {"rejections": k, "n_evaluated": len(pv),
                     "rate": round(k / len(pv), 6),
                     "ci_lower": lo, "ci_upper": hi,
                     "complete": len(pv) == n_sim}
    return out


def check_control_gate(res, n_sim):
    """Compuerta de la celda r=1.0: el IC debe contener el nivel nominal."""
    msgs, ok = [], True
    for comp, d in res.items():
        inside = d["ci_lower"] <= ALPHA <= d["ci_upper"]
        ok &= inside
        msgs.append("%s=%.4f IC [%.4f, %.4f] -> %s"
                    % (comp, d["rate"], d["ci_lower"], d["ci_upper"],
                       "DENTRO" if inside else "FUERA"))
    return ok, "; ".join(msgs)


def parse_cells(spec):
    """'all' | 'dgp1' | 'dgp3' | 'dgp1:500' | 'dgp3:1000,4.0' (repetible con ';')"""
    if spec in ("", "all"):
        return ([("dgp3", n, r) for n in DGP3_N for r in DGP3_RATIOS]
                + [("dgp1", n, p) for n in DGP1_N for p in DGP1_RHOS])
    cells = []
    for part in spec.split(";"):
        part = part.strip()
        if not part:
            continue
        dgp, _, rest = part.partition(":")
        dgp = dgp.strip()
        if dgp not in ("dgp1", "dgp3"):
            raise ValueError("dgp desconocido: %r" % dgp)
        ns = DGP3_N if dgp == "dgp3" else DGP1_N
        ps = DGP3_RATIOS if dgp == "dgp3" else DGP1_RHOS
        if rest:
            bits = [b for b in rest.split(",") if b.strip()]
            if bits:
                ns = [int(bits[0])]
            if len(bits) > 1:
                ps = [float(b) for b in bits[1:]]
        cells.extend((dgp, n, p) for n in ns for p in ps)
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="all")
    ap.add_argument("--tests", default="both", choices=["adf", "union", "both"])
    ap.add_argument("--n-sim", type=int, default=2000)
    ap.add_argument("--cores", type=int, default=14)
    ap.add_argument("--B", type=int, default=999)
    ap.add_argument("--B-extreme", type=int, default=1999,
                    help="B en las celdas extremas r=4.0 / rho=0.99")
    ap.add_argument("--max-seconds", type=float, default=DEFAULT_MAX_SECONDS)
    ap.add_argument("--target-chunk-seconds", type=float,
                    default=TARGET_CHUNK_SEC)
    ap.add_argument("--dry-run", action="store_true",
                    help="solo sonda y proyeccion; no ejecuta la celda completa")
    args = ap.parse_args()

    os.makedirs(CHUNK_DIR, exist_ok=True)
    cells = parse_cells(args.cells)
    t_start = time.time()

    print("=" * 78)
    print("  A6 / Experimento 1 - wild bootstrap (bootUR)")
    print("  Rscript      : %s" % RSCRIPT)
    print("  celdas       : %d  (%s)" % (len(cells), args.cells))
    print("  tests        : %s   N_sim=%d   cores=%d"
          % (args.tests, args.n_sim, args.cores))
    print("  tope bloque  : %.2f h   lote objetivo: %.0f s"
          % (args.max_seconds / 3600.0, args.target_chunk_seconds))
    print("=" * 78)

    master = {"dgp3": {}, "dgp1": {}}
    if os.path.exists(MASTER):
        with open(MASTER, encoding="utf-8") as f:
            master = json.load(f)
        master.setdefault("dgp3", {})
        master.setdefault("dgp1", {})

    stopped_early, pending = False, []

    for dgp, n, param in cells:
        if stopped_early:
            pending.append((dgp, n, param))
            continue
        tag = cell_tag(dgp, n, param)
        is_extreme = (dgp == "dgp3" and param == 4.0) or \
                     (dgp == "dgp1" and abs(param - 0.99) < 1e-9)
        B = args.B_extreme if is_extreme else args.B

        n_key = str(n)
        p_key = PARAM_FMT[dgp].format(param)
        done = master.get(dgp, {}).get(n_key, {}).get(p_key)
        same_cfg = bool(done) and done.get("tests") == args.tests and \
            done.get("N_sim") == args.n_sim and done.get("B") == B
        # 'complete' es imprescindible: sin el, una celda interrumpida por el
        # tope de tiempo se salta como si estuviera terminada.
        if same_cfg and done.get("complete"):
            print("\n[LISTA] %s completa (%s/%s series, rate adf=%s)"
                  % (tag, done.get("n_evaluated"), done.get("N_sim"),
                     done.get("adf", {}).get("rate")))
            continue
        if same_cfg:
            print("\n[REANUDA] %s quedo parcial (%s/%s series); continuo."
                  % (tag, done.get("n_evaluated"), done.get("N_sim")))

        print("\n" + "-" * 78)
        print("[CELDA] %s   B=%d   N_sim=%d   tests=%s"
              % (tag, B, args.n_sim, args.tests))

        chunks, i0 = [], 0
        # --- lote sonda: mide el costo real antes de comprometer la celda ----
        probe_k = min(args.cores, args.n_sim)
        print("  sonda de %d series para medir el costo real..." % probe_k)
        probe = run_chunk(dgp, n, param, 0, probe_k, B, args.cores, args.tests)
        chunks.append(probe)
        i0 = probe_k
        sec_per_series = float(probe["sec_per_series"])
        proj = sec_per_series * args.n_sim
        print("  costo medido : %.3f s/serie de pared" % sec_per_series)
        print("  proyeccion   : %.0f s = %.2f h para %d series"
              % (proj, proj / 3600.0, args.n_sim))

        chunk_k = int(max(args.cores,
                          round(args.target_chunk_seconds / max(sec_per_series, 1e-9))))
        chunk_k = int(max(args.cores, (chunk_k // args.cores) * args.cores))
        print("  lote elegido : %d series (~%.0f s por lote)"
              % (chunk_k, chunk_k * sec_per_series))

        if args.dry_run:
            print("  [DRY-RUN] no ejecuto el resto de la celda.")
            pending.append((dgp, n, param))
            continue

        while i0 < args.n_sim:
            k = min(chunk_k, args.n_sim - i0)
            elapsed = time.time() - t_start
            est = k * sec_per_series
            if elapsed + est > args.max_seconds:
                print("  [TOPE] el proximo lote (%d series, ~%.0f s) excederia "
                      "el tope de %.2f h (transcurrido %.2f h). Paro limpio."
                      % (k, est, args.max_seconds / 3600.0, elapsed / 3600.0))
                stopped_early = True
                pending.append((dgp, n, param))
                break
            print("  lote i0=%d k=%d  (%d/%d, transcurrido %.2f h)"
                  % (i0, k, i0, args.n_sim, elapsed / 3600.0))
            c = run_chunk(dgp, n, param, i0, k, B, args.cores, args.tests)
            chunks.append(c)
            sec_per_series = 0.7 * sec_per_series + \
                0.3 * float(c["sec_per_series"])   # promedio movil del costo
            i0 += k

        res = aggregate(chunks, args.n_sim, args.tests)
        n_eval = max((d["n_evaluated"] for d in res.values()), default=0)
        complete = n_eval == args.n_sim
        cell_rec = {"N_sim": args.n_sim, "n": n, "B": B, "cores": args.cores,
                    "tests": args.tests, "n_evaluated": n_eval,
                    "complete": complete,
                    "seed_base": (dgp3_seed_base(n, param) if dgp == "dgp3"
                                  else dgp1_seed_base(n, param)),
                    "seed_formula": ("300000 + n*100 + int(r*10)" if dgp == "dgp3"
                                     else "100000 + n*100 + int(rho*100)"),
                    "elapsed_sec": round(sum(float(c["elapsed_sec"])
                                             for c in chunks), 2),
                    "n_chunks": len(chunks),
                    "param_name": PARAM_NAME[dgp], "param_val": param}
        cell_rec.update(res)
        master.setdefault(dgp, {}).setdefault(n_key, {})[p_key] = cell_rec
        atomic_write_json(MASTER, master)

        state = "COMPLETA" if complete else "PARCIAL (%d/%d)" % (n_eval, args.n_sim)
        print("  [%s] %s -> %s" % (state, tag,
              ", ".join("%s=%.4f IC [%.4f, %.4f]"
                        % (c, d["rate"], d["ci_lower"], d["ci_upper"])
                        for c, d in res.items())))

        # --- compuerta de control -------------------------------------------
        if dgp == "dgp3" and param == 1.0 and complete:
            ok, msg = check_control_gate(res, args.n_sim)
            print("  [COMPUERTA r=1.0] %s" % msg)
            if not ok:
                print("  >> El tamano de la celda de control NO contiene el "
                      "nivel nominal. Detengo el barrido: no tiene sentido "
                      "interpretar las demas celdas.")
                stopped_early = True

    total = time.time() - t_start
    print("\n" + "=" * 78)
    print("  bloque terminado en %.0f s = %.2f h" % (total, total / 3600.0))
    if pending:
        print("  celdas pendientes (%d):" % len(pending))
        for dgp, n, param in pending:
            print("    - %s" % cell_tag(dgp, n, param))
        print("\n  REANUDAR con el mismo comando; los lotes completos se saltan.")
        print("  Los valores de B deben repetirse: con otro B la celda cuenta")
        print("  como otra configuracion y se recalcularia entera.")
        print("    python experiments/audit6_wild_bootstrap_sweep.py \\")
        print("      --cells '%s' --tests %s --n-sim %d --cores %d \\"
              % (args.cells, args.tests, args.n_sim, args.cores))
        print("      --B %d --B-extreme %d --max-seconds %.0f"
              % (args.B, args.B_extreme, args.max_seconds))
    else:
        print("  sin celdas pendientes en esta seleccion.")
    print("  maestro: %s" % MASTER)
    print("=" * 78)


if __name__ == "__main__":
    main()
