"""
Auditoria A15 - infraestructura comun (protocol_audit15.md, lecturas G1-G4).

Reutiliza la de A14 (audit14_common, que envuelve la de A13 y A10) sin modificarla. Cambian
el manifiesto (manifest_audit15.json), la carpeta de logs, la de tabulares, las familias
(151-159; 150 reservada sin uso) y la procedencia, que anade provenance.assistant.
"""
import datetime
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit14_common as C14                                       # noqa: E402

REPO = C14.REPO
RESULTS = C14.RESULTS
CKPT_ROOT = C14.CKPT_ROOT
MANIFEST = os.path.join(RESULTS, "manifest_audit15.json")
LOGS = os.path.join(RESULTS, "logs_audit15")
TABLES = os.path.join(RESULTS, "tables_audit15")
PROTOCOL = "experiments/protocol_audit15.md"
PREDICTION = "experiments/prediccion_boot_audit15.md"

ALPHA = C14.ALPHA
PP = C14.PP
FAMILY = {"PROBE1": 151, "SIZE1": 152, "POWER1": 153, "PASO0_BOOTUR": 154, "CAL3": 155, "SIZE3": 156,
          "POWER3": 157, "PROBE3": 158, "PASO0_V2": 159}          # 159: reserva usada por la enmienda 3 (E3.1)
RESERVED_UNUSED = 150
PRIOR_FAMILIES = tuple(range(90, 151))
ASSISTANT_TOOL = "Claude Code"
ASSISTANT_MODEL = "claude-opus-5-5"

sha256_file = C14.sha256_file
git = C14.git
plain = C14.plain
rel = C14.rel
versions = C14.versions
read_json = C14.read_json
atomic_write_json = C14.atomic_write_json
utc_now = C14.utc_now
committed = C14.committed
last_commit = C14.last_commit
wilson = C14.C13.wilson
exact_region = C14.C13.exact_region
mcnemar_exact = C14.C13.mcnemar_exact
rep_rng = C14.C13.rep_rng
rep_seedseq = C14.C13.rep_seedseq

_ASSISTANT = {}


def assistant():
    """{herramienta, modelo, version} del agente que produce el JSON (lectura G2)."""
    if not _ASSISTANT:
        version = None
        try:
            out = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=30, shell=os.name == "nt")
            version = out.stdout.strip() or None
        except (OSError, subprocess.SubprocessError):
            version = None
        _ASSISTANT.update({"herramienta": ASSISTANT_TOOL, "modelo": ASSISTANT_MODEL, "version": version})
    return dict(_ASSISTANT)


def code_files():
    pats = ("audit15_*.py", "audit14_*.py", "audit13_*.py", "audit12_*.py", "audit10_*.py", "audit9_*.py", "audit8_*.py",
            "audit4_tarea_E.py", "audit5_tarea5.py")
    files = [f for p in pats for f in glob.glob(os.path.join(HERE, p))]
    files += glob.glob(os.path.join(REPO, "src", "stationarity_test", "*.py"))
    return sorted(set(os.path.abspath(f) for f in files))


def provenance(script, seed_family=None, **extra):
    tracked = set(git("ls-files").splitlines())
    modified = set(git("diff", "--name-only", "HEAD").splitlines())
    code = {}
    for f in code_files():
        r = rel(f)
        code[r] = {"sha256": sha256_file(f),
                   "git_state": "untracked" if r not in tracked else ("modified" if r in modified else "committed")}
    dirty = [l for l in git("status", "--porcelain", "--untracked-files=no").splitlines() if "__pycache__" not in l]
    rec = {"script": rel(script), "script_sha256": sha256_file(script), "commit": git("rev-parse", "HEAD"),
           "worktree_dirty": bool(dirty), "dirty_files": dirty, "generated_utc": utc_now(),
           "seed_family": seed_family, "versions": versions(), "code": code,
           "code_all_committed": all(v["git_state"] == "committed" for v in code.values()),
           "assistant": assistant()}
    rec.update(extra)
    return rec


def register_outputs(script, outputs, prov=None):
    man = {"entries": {}}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            man = json.load(f)
    prov = prov or provenance(script)
    for out in outputs:
        man["entries"][rel(out)] = {
            "sha256": sha256_file(out), "bytes": os.path.getsize(out),
            "mtime_utc": datetime.datetime.fromtimestamp(os.path.getmtime(out), datetime.timezone.utc).isoformat(),
            "script": prov["script"], "script_sha256": prov["script_sha256"], "commit": prov["commit"],
            "worktree_dirty": prov["worktree_dirty"], "code_all_committed": prov["code_all_committed"],
            "versions": prov["versions"], "assistant": prov.get("assistant"), "registered_utc": utc_now()}
    man["updated_utc"] = utc_now()
    atomic_write_json(MANIFEST, man)


def write_result(path, obj, script):
    obj = plain(obj)
    atomic_write_json(path, obj)
    register_outputs(script, [path], obj.get("provenance"))


def write_text(path, text, script, prov=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)
    register_outputs(script, [path], prov)


def have(name):
    return os.path.exists(os.path.join(RESULTS, name))
