"""
Auditoria A13 - infraestructura comun.

Reutiliza la de A10 (audit10_common, que envuelve audit9_common y audit8_common)
sin modificarla: semillas SeedSequence(familia, spawn_key=(celda, i)), Wilson,
McNemar exacto, region exacta, escritura atomica y checkpoint. Cambian el
manifiesto (manifest_audit13.json), la carpeta de logs, las familias (140-143;
144-149 reservadas para enmiendas) y el conjunto de modulos cuyo sha256 se
registra en la procedencia.
"""
import datetime
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
for _p in (HERE, os.path.join(REPO, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audit10_common as C10                                      # noqa: E402

C9 = C10.C9
C8 = C10.C8
RESULTS = C10.RESULTS
CKPT_ROOT = C10.CKPT_ROOT
MANIFEST = os.path.join(RESULTS, "manifest_audit13.json")
LOGS = os.path.join(RESULTS, "logs_audit13")
TABLES = os.path.join(RESULTS, "tables_audit13")
FIGURES = os.path.join(HERE, "figures")
PAPER_FIGURES = os.path.join(REPO, "paper", "figures")
MANUSCRIPT = os.path.join(os.path.dirname(REPO), "paper_latex_v13.zip")

ALPHA = C10.ALPHA
PP = 100.0
THETA = 0.0
THETA_V13 = 0.02
FAMILY = {"E": 140, "TAB": 141, "AWB": 142, "APP": 143,
          "AMEND1": 144, "AMEND2": 145, "AMEND3": 146, "AMEND4": 147, "AMEND5": 148, "AMEND6": 149}
PRIOR_FAMILIES = tuple(range(90, 138))

BudgetExhausted = C10.BudgetExhausted
atomic_write_json = C10.atomic_write_json
sha256_file = C10.sha256_file
git = C10.git
rep_seedseq = C10.rep_seedseq
rep_rng = C10.rep_rng
wilson = C10.wilson
plain = C10.plain
rel = C10.rel
versions = C10.versions
read_json = C10.read_json
exact_region = C10.exact_region
rate_record = C10.rate_record
mcnemar_exact = C10.mcnemar_exact
paired_diff = C10.paired_diff
mean_with_se = C10.mean_with_se
load_rows = C10.load_rows
run_cell = C10.run_cell


def tname(theta):
    return "gls_t%g" % theta


PRIM = tname(THETA)
PRIM_V13 = tname(THETA_V13)


def code_files():
    pats = ("audit13_*.py", "make_figures_audit13.py", "audit12_common.py", "audit12_unitroot.py", "audit11_figconfig.py",
            "make_figures_audit11.py", "audit10_*.py", "make_figures_audit10.py", "audit9_*.py", "audit8_*.py",
            "audit7_dgp5_*.py", "audit7_design.py")
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
           "worktree_dirty": bool(dirty), "dirty_files": dirty, "generated_utc": C8.C7.utc_now(),
           "seed_family": seed_family, "versions": versions(), "code": code,
           "code_all_committed": all(v["git_state"] == "committed" for v in code.values())}
    rec.update(extra)
    return rec


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
            "versions": prov["versions"], "registered_utc": C8.C7.utc_now()}
    man["updated_utc"] = C8.C7.utc_now()
    atomic_write_json(MANIFEST, man)


def have(name):
    return os.path.exists(os.path.join(RESULTS, name))
