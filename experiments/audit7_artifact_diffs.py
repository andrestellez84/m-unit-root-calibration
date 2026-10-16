"""
Auditoria A7 - Bloque 4: diffs contra el control, persistidos para el reporte.

1. Artefactos de A7 regenerados: para cada JSON de experiments/results/*_audit7.json
   con mas de una version commiteada en A7, comparacion hoja por hoja entre versiones
   consecutivas, excluyendo la procedencia. Distingue "valor cambiado" (regresion),
   "clave eliminada" y "clave anadida" (ampliacion de esquema).
2. Archivos que A7 no debia tocar: los JSON de resultados de auditorias anteriores y
   los pre-registrados de solo lectura (experiments/data/*.csv, experiments/protocol.md,
   experiments/results/real_data_results.json). Se compara el blob de git en el commit
   base de A7 con el de HEAD y con el disco.

Salida: experiments/results/artifact_diffs_audit7.json.
Uso: python experiments/audit7_artifact_diffs.py
"""
import fnmatch
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                        # noqa: E402

OUT = os.path.join(C.RESULTS, "artifact_diffs_audit7.json")
PREREG_FILE = "experiments/prediccion_dgp5_audit7.md"
READ_ONLY = ("experiments/data/*.csv", "experiments/protocol.md", "experiments/results/real_data_results.json")
VOLATILE = ("provenance",)
# Hojas de tiempo: cambian en cada ejecucion y no son resultados (igual que VOLATILE_LEAVES de A6)
VOLATILE_LEAVES = ("elapsed_sec", "block_elapsed_sec", "cell_elapsed_sec", "written_utc", "generated_utc",
                   "sec_per_series", "probe_sec_per_series", "projected_sec")


def git_bytes(*args):
    return subprocess.run(["git", *args], cwd=C.REPO, capture_output=True).stdout


def flat(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flat(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from flat(v, p + "/%d" % i)
    else:
        yield p, o


def leaves(blob):
    d = json.loads(blob.decode("utf-8"))
    return {k: v for k, v in flat(d) if k.split("/")[1] not in VOLATILE
            and k.rsplit("/", 1)[-1] not in VOLATILE_LEAVES}


def main():
    prereg = C._git("log", "--diff-filter=A", "--format=%H", "--", PREREG_FILE).splitlines()[-1]
    base = C._git("rev-parse", prereg + "^")

    regenerated = {}
    tracked = C._git("ls-files", "experiments/results").splitlines()
    for path in sorted(p for p in tracked if fnmatch.fnmatch(os.path.basename(p), "*_audit7.json")):
        commits = C._git("log", "--format=%H", "--reverse", base + "..HEAD", "--", path).splitlines()
        if len(commits) < 2:
            continue
        steps = []
        for a, b in zip(commits, commits[1:]):
            la = leaves(git_bytes("show", "%s:%s" % (a, path)))
            lb = leaves(git_bytes("show", "%s:%s" % (b, path)))
            changed = sorted(k for k in la if k in lb and la[k] != lb[k])
            steps.append({"from": a, "to": b, "leaves_before": len(la), "leaves_after": len(lb),
                          "values_changed": len(changed), "keys_removed": len([k for k in la if k not in lb]),
                          "keys_added": len([k for k in lb if k not in la]),
                          "changed_keys": changed,
                          "changed_sample": [{"key": k, "before": la[k], "after": lb[k]} for k in changed[:10]]})
        regenerated[path] = steps

    base_files = C._git("ls-tree", "-r", "--name-only", base).splitlines()
    prior_results = [p for p in base_files if p.startswith("experiments/results/") and p.endswith(".json")
                     and "_audit7" not in p and "/checkpoints/" not in p]
    read_only = [p for p in base_files if any(fnmatch.fnmatch(p, pat) for pat in READ_ONLY)]

    def status(paths):
        rows = {}
        for p in paths:
            b_base = C._git("rev-parse", "%s:%s" % (base, p))
            b_head = C._git("rev-parse", "HEAD:%s" % p)
            disk = os.path.join(C.REPO, p)
            disk_blob, eol_only = None, False
            if os.path.exists(disk):
                with open(disk, "rb") as f:
                    data = f.read()
                disk_blob = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
                if disk_blob != b_base:
                    # core.autocrlf convierte LF -> CRLF al hacer checkout en Windows
                    base_bytes = git_bytes("show", "%s:%s" % (base, p))
                    eol_only = data.replace(b"\r\n", b"\n") == base_bytes.replace(b"\r\n", b"\n")
            rows[p] = {"unchanged_in_git": b_base == b_head, "disk_matches_base": disk_blob == b_base,
                       "disk_differs_only_in_line_endings": eol_only}
        return rows

    prior, ro = status(prior_results), status(read_only)
    C.atomic_write_json(OUT, {
        "provenance": C.provenance(dgp="artifact_diffs", n_sim=None, seed_formula=None),
        "audit_base_commit": base, "prereg_commit": prereg,
        "regenerated_audit7_artifacts": regenerated,
        "regenerated_with_value_changes": sorted(p for p, s in regenerated.items()
                                                 if any(x["values_changed"] or x["keys_removed"] for x in s)),
        "volatile_leaves_excluded": list(VOLATILE_LEAVES),
        "prior_audit_results": {"files": len(prior),
                                "changed_in_git": sorted(p for p, r in prior.items() if not r["unchanged_in_git"]),
                                "disk_differs_only_line_endings": sorted(p for p, r in prior.items()
                                                                         if r["disk_differs_only_in_line_endings"]),
                                "disk_content_differs_from_base": sorted(p for p, r in prior.items()
                                                                         if not r["disk_matches_base"]
                                                                         and not r["disk_differs_only_in_line_endings"])},
        "read_only_preregistered": {"files": sorted(ro),
                                    "changed_in_git": sorted(p for p, r in ro.items() if not r["unchanged_in_git"]),
                                    "disk_differs_only_line_endings": sorted(p for p, r in ro.items()
                                                                             if r["disk_differs_only_in_line_endings"]),
                                    "disk_content_differs_from_base": sorted(p for p, r in ro.items()
                                                                             if not r["disk_matches_base"]
                                                                             and not r["disk_differs_only_in_line_endings"])},
    })
    for p, s in regenerated.items():
        print("%-60s %s" % (p, [(x["values_changed"], x["keys_removed"], x["keys_added"]) for x in s]))
    print("resultados previos: %d archivos, cambiados en git %d, disco distinto solo por fin de linea %d, contenido distinto %d"
          % (len(prior), sum(not r["unchanged_in_git"] for r in prior.values()),
             sum(r["disk_differs_only_in_line_endings"] for r in prior.values()),
             sum(not r["disk_matches_base"] and not r["disk_differs_only_in_line_endings"] for r in prior.values())))
    print("pre-registrados de solo lectura: %d, cambiados %d" % (len(ro), sum(not r["unchanged_in_git"] for r in ro.values())))
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
