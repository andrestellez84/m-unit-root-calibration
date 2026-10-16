"""
Auditoria A8 - B0: inventario y procedencia (sin computo pesado).

1. Artefactos del encargo: sha256, bytes, mtime y estado git.
2. Procedencia de la Tabla 8 publicada (tab:heavytails de sec5_montecarlo.tex del
   manuscrito v11): valores leidos del .tex dentro del zip, comparados celda por
   celda con los tres JSON de colas pesadas; lineas de codigo del generador y del
   generador de reporte de A5.
3. Figuras: sha256 de las figuras del manuscrito (paper_v11/figures/*.pdf dentro
   del zip; el repositorio no tiene paper/figures) frente a experiments/figures/*.pdf.
4. Mapa de solape de semillas de las familias 90-98 frente a todas las anteriores
   (mapa de A7, paso0_pairing_audit7.json): comparacion de las dos primeras
   palabras del estado inicial de PCG64 (128 bits) de cada replica.

Salida: experiments/results/inventory_audit8.json.
Uso: python experiments/audit8_b0_inventory.py [--manuscript RUTA_ZIP]
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import sys
import time
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_design as D                                          # noqa: E402

OUT = os.path.join(C.RESULTS, "inventory_audit8.json")
DEFAULT_ZIP = os.path.join(os.path.expanduser("~"), "Desktop", "paper_latex_v11.zip")

ARTIFACTS = (
    "experiments/results/garch_size_audit7.json", "experiments/results/garch_size_ext_audit7.json",
    "experiments/results/garch_size_ext_large_audit7.json", "experiments/results/dgp5_mixed_audit7.json",
    "experiments/results/ct_case_audit7.json", "experiments/results/deviation_table_audit7.json",
    "experiments/results/size_audit5.json", "experiments/results/size_robustness_heavy_tails_audit5.json",
    "experiments/results/wild_bootstrap_r_audit6.json", "experiments/results/dgp2_break_tests_audit6.json",
    "experiments/results/manifest_audit7.json", "experiments/results/paso0_pairing_audit7.json",
    "experiments/results/size_robustness_heavy_tails_audit5b.json",
    "experiments/results/size_robustness_heavy_tails.json", "experiments/results/small_n_size_audit5.json",
    "experiments/results/real_data_results.json",
    "experiments/protocol.md", "experiments/protocol_hash.json", "experiments/data/data_registry.json",
)
ARTIFACT_GLOBS = ("src/stationarity_test/*.py", "experiments/data/*.csv", "experiments/*.R")
LINE_PATTERNS = {
    "audit5b_tarea_r3.py": [r"seed_base = 900000", r"generate_rw_heavy\(n, df, scale, rng\)",
                            r"build_null_cdf\(THETA, r_val, n, N_cal=50000, seed=42\)", r"size_robustness_heavy_tails_audit5b.json"],
    "size_robustness_heavy_tails.py": [r"'t5': \{", r"'t3': \{", r"def generate_rw_heavy", r"rng.standard_t\(df"],
    "audit5_tarea2.py": [r"seed = 200000", r"standard_t\(df=dof", r"dof / \(dof - 2.0\)", r"results\[str\(dof\)\]\[str\(n\)\]",
                         r"size_robustness_heavy_tails_audit5.json"],
    "audit5_generate_report.py": [r"\(\"chisquare\", \[3, 5\]\)", r"d\[pilot\]\[str\(dof\)\]\[n\]"],
}


def file_record(rel):
    p = os.path.join(C.REPO, rel)
    if not os.path.exists(p):
        return {"exists": False}
    with open(p, "rb") as f:
        data = f.read()
    tracked = bool(C.git("ls-files", rel))
    rec = {"exists": True, "sha256": hashlib.sha256(data).hexdigest(),
           "sha256_lf": hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest(), "bytes": len(data),
           "mtime_utc": datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc).isoformat(),
           "git_tracked": tracked}
    if tracked:
        rec["git_blob_sha256"] = C.git_blob_sha256(rel)
    return rec


def find_lines(path, patterns):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    out = {}
    for pat in patterns:
        hits = [{"line": i + 1, "text": l.strip()} for i, l in enumerate(lines) if re.search(pat, l)]
        out[pat] = hits
    return out


def parse_heavytails(tex):
    """Filas de tab:heavytails: (dist, n) -> R=0.5, ADF, PP, DF-GLS."""
    block = tex[tex.index(r"\label{tab:heavytails}"):]
    block = block[:block.index(r"\end{tabular}")]
    rows = {}
    num = r"\\textbf\{([0-9.]+)\}|([0-9.]+)"
    pat = re.compile(r"\$t\((\d)\)\$\s*&\s*(\d+)\s*&(.*?)\\\\", re.S)
    for m in pat.finditer(block):
        vals = [a or b for a, b in re.findall(num, m.group(3))]
        rows["t%s_n%s" % (m.group(1), m.group(2))] = {"R050": float(vals[0]), "R050_ci": [float(vals[1]), float(vals[2])],
                                                      "adf": float(vals[3]), "pp": float(vals[4]), "dfgls": float(vals[5])}
    return rows


def tex_line(tex, needle):
    for i, l in enumerate(tex.splitlines()):
        if needle in l:
            return i + 1
    return None


def table8(zpath):
    with zipfile.ZipFile(zpath) as z:
        tex = z.read("paper_v11/sec5_montecarlo.tex").decode("utf-8")
    pub = parse_heavytails(tex)
    srcs = {
        "size_robustness_heavy_tails_audit5b.json[alpha1]":
            lambda d, n: C.read_json("size_robustness_heavy_tails_audit5b.json")["alpha1"][d][str(n)],
        "size_robustness_heavy_tails_audit5b.json[alpha2]":
            lambda d, n: C.read_json("size_robustness_heavy_tails_audit5b.json")["alpha2"][d][str(n)],
        "size_robustness_heavy_tails_audit5.json[alpha1]":
            lambda d, n: C.read_json("size_robustness_heavy_tails_audit5.json")["alpha1"][d[1:]][str(n)],
        "size_robustness_heavy_tails_audit5.json[alpha2]":
            lambda d, n: C.read_json("size_robustness_heavy_tails_audit5.json")["alpha2"][d[1:]][str(n)],
    }
    legacy = C.read_json("size_robustness_heavy_tails.json")
    comparison = {}
    for src, get in srcs.items():
        cells = {}
        for key, p in pub.items():
            d, n = key.split("_n")
            r = get(d, int(n))
            got = {"R050": r["ours_R050"], "adf": r["adf"], "pp": r["pp"], "dfgls": r["dfgls"]}
            cells[key] = {"source": got, "published": {k: p[k] for k in got},
                          "match": all(abs(got[k] - p[k]) < 5e-5 for k in got)}
        comparison[src] = {"cells": cells, "all_match": all(c["match"] for c in cells.values()),
                           "cells_matching": sum(c["match"] for c in cells.values())}
    a5_dup = {}
    rep = open(os.path.join(C.RESULTS, "resultados_auditoria_5.md"), encoding="utf-8").read().splitlines()
    rows = [l for l in rep if re.match(r"\| \d+ \| (chisquare|student-t)\(\d\) \| alpha\d \|", l)]
    parsed = {}
    for l in rows:
        c = [x.strip() for x in l.strip("|").split("|")]
        parsed[(c[1], c[2], c[0])] = c[3:]
    for (dist, pilot, n), vals in parsed.items():
        if dist.startswith("chisquare"):
            twin = ("student-t(%s)" % dist[-2], pilot, n)
            js = C.read_json("size_robustness_heavy_tails_audit5.json")[pilot][dist[-2]][n]
            js_vals = [js["ours_R025"], js["ours_R050"], js["ours_R075"], js["dfgls"]]
            a5_dup["%s|%s|n=%s" % (dist, pilot, n)] = {
                "row_R025_R050_R075_dfgls": [float(v) for v in vals], "same_dof_student_t_row": parsed.get(twin),
                "json_key_used": "%s[%s][%s]" % (pilot, dist[-2], n), "json_values": js_vals,
                "identical_to_json_t_same_dof": all(abs(float(v) - w) < 1e-12 for v, w in zip(vals, js_vals))}
    lines = {f: find_lines(os.path.join(HERE, f), pats) for f, pats in LINE_PATTERNS.items()}
    return {
        "manuscript_table": "tab:heavytails", "tex_file": "paper_v11/sec5_montecarlo.tex",
        "tex_label_line": tex_line(tex, r"\label{tab:heavytails}"),
        "published": pub, "comparison": comparison,
        "legacy_size_robustness_heavy_tails_json_keys": list(legacy.keys()),
        "a5_report_chisquare_rows": a5_dup,
        "code_lines": lines,
        "git_tracked": {f: bool(C.git("ls-files", "experiments/" + f)) for f in LINE_PATTERNS},
        "script_sha256": {f: C.sha256_file(os.path.join(HERE, f)) for f in LINE_PATTERNS},
    }


def figures(zpath):
    out = {"paper_figures_dir_in_repo": os.path.isdir(os.path.join(C.REPO, "paper", "figures")), "manuscript": {}, "experiments": {}}
    with zipfile.ZipFile(zpath) as z:
        for name in z.namelist():
            if name.startswith("paper_v11/figures/") and name.endswith(".pdf"):
                out["manuscript"][os.path.basename(name)] = hashlib.sha256(z.read(name)).hexdigest()
    for p in sorted(glob.glob(os.path.join(HERE, "figures", "*.pdf"))):
        out["experiments"][os.path.basename(p)] = C.sha256_file(p)
    out["comparison"] = {k: {"manuscript": v, "experiments_a7": out["experiments"].get(k),
                             "identical": v == out["experiments"].get(k)} for k, v in out["manuscript"].items()}
    return out


def prior_seed_blocks():
    fams = C.read_json("paso0_pairing_audit7.json")["families"]
    blocks = []
    for name, f in fams.items():
        for g in f["by_group"].values():
            for b in g["seed_bases"]:
                blocks.append((name, int(b), int(f["n_sim"])))
    return blocks


def state_words(ss_iter):
    return np.fromiter((int(ss.generate_state(1, dtype=np.uint64)[0]) for ss in ss_iter), dtype=np.uint64)


def seed_map():
    t0 = time.time()
    blocks = prior_seed_blocks()
    prior_ints = np.unique(np.concatenate([np.arange(b, b + n, dtype=np.int64) for _, b, n in blocks]))
    # semillas enteras de otros scripts reutilizados en A8 (no incluidas en el mapa de A7)
    extra = {"calibracion build_null_cdf": [42], "audit5_tarea2 (200000 + n*100 + dof*10 + i)":
             list(range(200000 + 200 * 100 + 30, 200000 + 1000 * 100 + 50 + 5000))}
    prior_ints = np.unique(np.concatenate([prior_ints, np.array(sum(extra.values(), []), dtype=np.int64)]))
    prior_words = state_words(np.random.SeedSequence(int(s)) for s in prior_ints)
    new = {}
    all_new = []
    for fam, cells in D.CELLS.items():
        words = []
        for name in cells:
            ci = D.cell_index(fam, name)
            reps = D.cell_reps(fam, name)
            w = state_words(C.rep_seedseq(fam, ci, i) for i in range(reps))
            words.append(w)
        w = np.concatenate(words) if words else np.array([], dtype=np.uint64)
        new[str(fam)] = {"cells": len(cells), "replicate_streams": int(w.size),
                         "distinct_state_words": int(np.unique(w).size)}
        all_new.append(w)
    all_new = np.concatenate(all_new)
    coll_prior = np.intersect1d(all_new, prior_words)
    # coherencia con spawn(): el hijo (cell, i) es el hijo i del hijo cell
    ss = np.random.SeedSequence(92)
    spawn_ok = bool(ss.spawn(3)[2].spawn(5)[4].generate_state(4).tolist()
                    == C.rep_seedseq(92, 2, 4).generate_state(4).tolist())
    return {
        "method": "palabra 0 de SeedSequence.generate_state(uint64), que fija el estado inicial de PCG64; las semillas previas son "
                  "enteros usados como default_rng(entero) = SeedSequence(entero) sin spawn_key",
        "prior_families": sorted({b[0] for b in blocks}), "prior_integer_seeds": int(prior_ints.size),
        "prior_extra_sources": {k: len(v) for k, v in extra.items()},
        "new_families": new, "new_streams_total": int(all_new.size),
        "new_distinct": int(np.unique(all_new).size),
        "collisions_new_vs_prior": int(coll_prior.size),
        "collisions_within_new": int(all_new.size - np.unique(all_new).size),
        "spawn_key_equals_spawn": spawn_ok,
        "a7_integer_family_name_clash": "A7 uso los nombres de familia 91-94 en el esquema entero family*10^8 + cell*10^5 + i "
                                        "(semillas >= 9.1e9); A8 usa SeedSequence(family, spawn_key): streams distintos, "
                                        "comprobado arriba con las semillas enteras de A7 incluidas en el mapa",
        "elapsed_sec": round(time.time() - t0, 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manuscript", default=DEFAULT_ZIP)
    a = ap.parse_args()
    arts = {r: file_record(r) for r in ARTIFACTS}
    for g in ARTIFACT_GLOBS:
        for p in sorted(glob.glob(os.path.join(C.REPO, g))):
            arts[C.rel(p)] = file_record(C.rel(p))
    with open(os.path.join(HERE, "data", "data_registry.json"), encoding="utf-8") as f:
        reg = json.load(f)
    data_hash = {k: {"registered": v["sha256"], "disk": arts["experiments/data/%s_daily.csv" % k]["sha256"],
                     "disk_lf": arts["experiments/data/%s_daily.csv" % k]["sha256_lf"],
                     "match": v["sha256"] in (arts["experiments/data/%s_daily.csv" % k]["sha256"],
                                              arts["experiments/data/%s_daily.csv" % k]["sha256_lf"])}
                 for k, v in reg["indices"].items()}
    ph = json.load(open(os.path.join(HERE, "protocol_hash.json")))
    prot = arts["experiments/protocol.md"]
    manuscript = {"path": a.manuscript, "sha256": C.sha256_file(a.manuscript),
                  "mtime_utc": datetime.datetime.fromtimestamp(os.path.getmtime(a.manuscript), datetime.timezone.utc).isoformat()}
    print("tabla 8 ...", flush=True)
    t8 = table8(a.manuscript)
    print("figuras ...", flush=True)
    figs = figures(a.manuscript)
    print("mapa de semillas ...", flush=True)
    seeds = seed_map()
    out = {
        "provenance": C.provenance(__file__, seed_family=C.FAMILY["B0"]),
        "manuscript": manuscript,
        "artifacts": arts,
        "missing_artifacts": sorted(k for k, v in arts.items() if not v["exists"]),
        "frozen_data_hashes": data_hash,
        "protocol_hash": {"registered": ph["sha256"], "disk": prot["sha256"], "disk_lf": prot["sha256_lf"],
                          "match": ph["sha256"] in (prot["sha256"], prot["sha256_lf"])},
        "table8_provenance": t8,
        "figures": figs,
        "seed_map": seeds,
    }
    C.write_result(OUT, out, __file__)
    print(json.dumps({"missing": out["missing_artifacts"], "data": {k: v["match"] for k, v in data_hash.items()},
                      "protocol": out["protocol_hash"]["match"],
                      "t8": {k: v["cells_matching"] for k, v in t8["comparison"].items()},
                      "figs": {k: v["identical"] for k, v in figs["comparison"].items()},
                      "seeds": {k: seeds[k] for k in ("new_streams_total", "collisions_new_vs_prior", "collisions_within_new",
                                                       "spawn_key_equals_spawn", "elapsed_sec")}}, indent=1))
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
