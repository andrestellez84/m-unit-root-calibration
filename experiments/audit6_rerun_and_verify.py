"""
Auditoria A6 - Re-ejecucion con control de regresion.

Vuelve a correr los scripts deterministas de la auditoria, mide su tiempo de
pared y compara sus artefactos hoja por hoja contra el estado previo. El
veredicto distingue tres cosas que no son equivalentes:

  - valores cambiados  -> REGRESION (falla)
  - claves eliminadas  -> REGRESION (falla)
  - claves anadidas    -> ampliacion de esquema (pasa, se anota)

Los tiempos quedan en timings_audit6.json para que el generador del reporte no
lleve cifras escritas a mano.

Uso: python experiments/audit6_rerun_and_verify.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
TIMINGS = os.path.join(RESULTS, "timings_audit6.json")

JOBS = [
    ("audit6_compute_ours_size_control.py", ["dgp2_break_tests_audit6.json"]),
    ("audit6_real_data_roc.py", ["real_data_arl_roc_audit6.json"]),
    ("audit6_tables_dkw.py", ["size_robustness_dkw_audit6.json"]),
]
# hojas cuyo cambio no cuenta como regresion (sellos de tiempo y medidas de costo)
VOLATILE_LEAVES = ("timestamp_utc", "timestamp", "completed_at", "generated_at",
                   "ours_elapsed_sec", "elapsed_sec", "elapsed_total_sec",
                   "sec_per_series", "total_elapsed", "wall_sec")


def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, prefix + "/" + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten(v, prefix + "/%d" % i)
    else:
        yield prefix, obj


def leaves(path):
    with open(path, encoding="utf-8") as f:
        return {k: v for k, v in flatten(json.load(f))
                if not k.rsplit("/", 1)[-1] in VOLATILE_LEAVES}


def raw_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    report = {"jobs": {}, "regression": False, "schema_additions": 0}
    print("=" * 78)
    print("  A6 - re-ejecucion con control de regresion")
    print("=" * 78)

    for script, artifacts in JOBS:
        # respaldo del estado previo para comparar hoja por hoja
        prior = {}
        for a in artifacts:
            p = os.path.join(RESULTS, a)
            if os.path.exists(p):
                bak = p + ".prev"
                shutil.copy2(p, bak)
                prior[a] = bak

        print("\n[RUN] %s" % script)
        t0 = time.time()
        proc = subprocess.run([sys.executable, "-u", os.path.join(HERE, script)],
                              capture_output=True, text=True,
                              cwd=os.path.dirname(HERE))
        elapsed = time.time() - t0
        if proc.returncode != 0:
            print(proc.stdout[-3000:])
            print(proc.stderr[-3000:])
            raise SystemExit("%s fallo con rc=%d" % (script, proc.returncode))
        for line in [l for l in proc.stdout.splitlines() if l.strip()][-3:]:
            print("   | %s" % line)

        entry = {"wall_sec": round(elapsed, 2), "artifacts": {}}
        for a in artifacts:
            p = os.path.join(RESULTS, a)
            new = leaves(p)
            if a not in prior:
                entry["artifacts"][a] = {"status": "NUEVO", "sha256": raw_sha(p),
                                         "n_leaves": len(new)}
                print("   %-38s NUEVO (%d hojas)" % (a, len(new)))
                continue
            old = leaves(prior[a])
            added = sorted(set(new) - set(old))
            removed = sorted(set(old) - set(new))
            changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])
            is_reg = bool(changed or removed)
            report["regression"] |= is_reg
            report["schema_additions"] += len(added)
            status = ("REGRESION" if is_reg else
                      ("REPRODUCIDO + %d claves nuevas" % len(added) if added
                       else "REPRODUCIDO"))
            entry["artifacts"][a] = {
                "status": status, "sha256": raw_sha(p),
                "n_leaves": len(new), "keys_added": len(added),
                "keys_removed": len(removed), "values_changed": len(changed),
                "changed_sample": [{"key": k, "before": old[k], "after": new[k]}
                                   for k in changed[:10]],
                "added_sample": added[:10],
            }
            print("   %-38s %s" % (a, status))
            print("      hojas=%d  +%d  -%d  valores distintos=%d"
                  % (len(new), len(added), len(removed), len(changed)))
            for k in changed[:8]:
                print("      ~ %s : %r -> %r" % (k, old[k], new[k]))
            os.remove(prior[a])

        report["jobs"][script] = entry
        print("   tiempo de pared: %.2f s" % elapsed)

    with open(TIMINGS, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 78)
    if report["regression"]:
        print("  VEREDICTO: REGRESION DETECTADA - revisar arriba")
    else:
        print("  VEREDICTO: sin regresion. Todo valor preexistente se reprodujo")
        print("             (%d claves nuevas de ampliacion de esquema)."
              % report["schema_additions"])
    print("  tiempos en %s" % TIMINGS)
    print("=" * 78)
    return 1 if report["regression"] else 0


if __name__ == "__main__":
    sys.exit(main())
