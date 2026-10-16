"""
Auditoria A15 - B15.8: mantenimiento del repositorio (enmienda 5, lecturas 8.1-8.3), confirmado por el autor.

1. git bundle create ../backup_pre_gc.bundle --all ; git bundle verify (si falla, no sigue).
2. git reflog expire --expire-unreachable=now --all ; git gc --prune=now ; count-objects -vH antes y despues.
3. Control del .gitignore: git ls-files -ci --exclude-standard vacio y ningun *.npz versionado.

Salida: experiments/results/maintenance_audit15.json.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "maintenance_audit15.json")
BUNDLE = os.path.join(os.path.dirname(C.REPO), "backup_pre_gc.bundle")


def git(*args):
    r = subprocess.run(["git", *args], cwd=C.REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {"cmd": "git " + " ".join(args), "code": r.returncode, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}


def counts():
    r = git("count-objects", "-vH")
    return dict(l.split(": ", 1) for l in r["stdout"].splitlines() if ": " in l)


def main(stage):
    out = C.read_json("maintenance_audit15.json") if C.have("maintenance_audit15.json") else {}
    if stage in ("all", "gc"):
        t0 = time.time()
        before = counts()
        steps = [git("bundle", "create", BUNDLE, "--all")]
        steps.append(git("bundle", "verify", BUNDLE))
        verified = steps[-1]["code"] == 0
        after = None
        if verified:
            steps.append(git("reflog", "expire", "--expire-unreachable=now", "--all"))
            steps.append(git("gc", "--prune=now"))
            after = counts()
        out["gc"] = {"bundle": {"path": "../backup_pre_gc.bundle", "bytes": os.path.getsize(BUNDLE) if os.path.exists(BUNDLE) else None,
                                "sha256": C.sha256_file(BUNDLE) if os.path.exists(BUNDLE) else None, "verified": verified},
                     "count_objects_before": before, "count_objects_after": after,
                     "steps": [{k: (v[-2000:] if isinstance(v, str) else v) for k, v in s.items()} for s in steps],
                     "elapsed_sec": time.time() - t0}
    if stage in ("all", "ignore"):
        ign = git("ls-files", "-ci", "--exclude-standard")
        npz = git("ls-files", "*.npz")
        st = git("status", "--porcelain", "--untracked-files=no")
        out["gitignore"] = {"content": open(os.path.join(C.REPO, ".gitignore"), encoding="utf-8").read()
                            if os.path.exists(os.path.join(C.REPO, ".gitignore")) else None,
                            "tracked_but_ignored": [l for l in ign["stdout"].splitlines() if l],
                            "tracked_npz": [l for l in npz["stdout"].splitlines() if l],
                            "status_tracked_changes": [l for l in st["stdout"].splitlines() if l and "__pycache__" not in l]}
        out["gitignore"]["ok"] = not out["gitignore"]["tracked_but_ignored"] and not out["gitignore"]["tracked_npz"]
    out["provenance"] = C.provenance(__file__)
    out["reading"] = "enmienda 5, lecturas 8.1-8.3"
    C.write_result(OUT, out, __file__)
    if "gc" in out:
        g = out["gc"]
        print("bundle verificado:", g["bundle"]["verified"], g["bundle"]["bytes"], "bytes")
        print("antes:", g["count_objects_before"])
        print("despues:", g["count_objects_after"])
    if "gitignore" in out:
        print("gitignore ok:", out["gitignore"]["ok"], "| ignorados versionados:", out["gitignore"]["tracked_but_ignored"][:5])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "all"))
