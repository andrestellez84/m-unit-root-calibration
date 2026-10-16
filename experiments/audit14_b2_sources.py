"""
Auditoria A14 - B14.2: origen de las cinco cifras sin fuente (protocol_audit14.md, lectura 8).

(1) Busqueda literal, con fronteras de digito, en todo archivo de texto del repositorio
(fuera de .git y __pycache__; incluye experiments/results/, sus checkpoints y paper/, la
fuente del v11). (2) Registro de las fuentes localizadas leyendo archivos: para cada una,
el archivo, la clave, el valor, si su redondeo binario a los decimales impresos da la cifra,
el script productor (sha256, estado en git, si escribe ese archivo) y el commit que anadio el
resultado. No se recalcula ningun estadistico ni se combina ningun valor almacenado: si la
cifra no esta almacenada como tal, se dice y se listan los insumos almacenados.

Salida: experiments/results/b2_sources_audit14.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit14_common as C                                         # noqa: E402
import audit13_tables as TB                                        # noqa: E402

OUT = os.path.join(C.RESULTS, "b2_sources_audit14.json")
EXT = (".json", ".csv", ".md", ".log", ".tex", ".txt", ".py", ".bib")
TOKENS = {
    "i_0.003": r"(?<![\d.])0\.003(?!\d)",
    "ii_0.0301": r"(?<![\d.])0\.0301(?!\d)",
    "iii_6.9%": r"(?<![\d.])6\.9(?!\d)\s*\\?%",
    "iii_0.6%": r"(?<![\d.])0\.6(?!\d)\s*\\?%",
    "iv_0.333": r"(?<![\d.])0\.333(?!\d)",
}
# Archivos de las propias auditorias A13/A14 que citan las cifras (no son fuentes)
AUDIT_REFS = re.compile(r"(audit13_q_|q_claims_audit13|q_phrases_audit13|resultados_auditoria_13|protocol_audit14|audit14_|"
                        r"logs_audit13|logs_audit14|b2_sources_audit14)")
HAC_FIX = "f78bc3f"            # commit "Fix HAC Bartlett formula bandwidth (Audit 4)": piloto alpha(2) -> alpha(1)
PILOT_A2 = "(1.0 - rho_hat)**4"
PILOT_A1 = "(1.0 - rho_hat**2)**2"


def search():
    hits = {k: {} for k in TOKENS}
    scanned = 0
    for root, dirs, files in os.walk(C.REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for fn in files:
            if not fn.endswith(EXT):
                continue
            p = os.path.join(root, fn)
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            scanned += 1
            for k, pat in TOKENS.items():
                n = len(re.findall(pat, text))
                if n:
                    hits[k][C.rel(p)] = n
    out = {}
    for k, h in hits.items():
        refs = {p: n for p, n in h.items() if AUDIT_REFS.search(p)}
        ckpt = {p: n for p, n in h.items() if "/checkpoints/" in p and p not in refs}
        rest = {p: n for p, n in h.items() if p not in refs and p not in ckpt}
        out[k] = {"files_with_hits": len(h), "total_hits": sum(h.values()), "audit_references": refs,
                  "checkpoint_files": len(ckpt), "checkpoint_hits": sum(ckpt.values()), "other_files": rest}
    return {"scanned_text_files": scanned, "extensions": list(EXT), "tokens": TOKENS, "by_token": out}


def jget(path, keys):
    with open(os.path.join(C.REPO, path), encoding="utf-8") as f:
        d = json.load(f)
    for k in keys:
        d = d[k]
    return d


def md_row(path, first, col):
    """Celda (fila cuya primera columna es `first`, columna `col`) de una tabla markdown."""
    with open(os.path.join(C.REPO, path), encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip().startswith("|")]
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    for l in lines[2:]:
        cells = [c.strip() for c in l.strip("|").split("|")]
        if cells[0] == first:
            return cells[head.index(col)], {h: c for h, c in zip(head, cells)}
    raise KeyError(first)


def rounds_to(printed, value):
    d = len(printed.split(".")[1]) if "." in printed else 0
    return TB.fdec(float(value), d, "binary") == printed


def script_info(path, writes, extra_terms=()):
    full = os.path.join(C.REPO, path)
    with open(full, encoding="utf-8") as f:
        src = f.read()
    info = dict(C.last_commit(path), sha256=C.sha256_file(full), mtime_utc=mtime(full), writes_file=writes in src)
    info["contains"] = {t: t in src for t in extra_terms}
    return info


def mtime(p):
    import datetime
    return datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc).isoformat()


def result_info(path):
    full = os.path.join(C.REPO, path)
    return dict(C.committed(path), bytes=os.path.getsize(full), mtime_utc=mtime(full))


def value_rec(path, keys, printed):
    v = jget(path, keys)
    return {"file": path, "key": "/".join(keys), "value": v, "printed": printed, "rounds_to_printed": rounds_to(printed, v)}


def fig_i():
    f = "experiments/results/rhat_distribution_audit5.json"
    f5b = "experiments/results/rhat_distribution_audit5b.json"
    vals = [value_rec(f, ["alpha1", "H0_n%d" % n, "r_hat", "mean"], "0.003") for n in (200, 500, 1000)]
    conc = [value_rec(f, ["alpha2", "H0_n%d" % n, "r_hat", "mean"], "0.003") for n in (200, 500, 1000)]
    conc += [value_rec(f5b, [m, "H0_n%d" % n, "r_hat", "mean"], "0.003") for m in ("sigma_known", "alpha1_hac", "alpha2_hac")
             for n in (200, 500, 1000)]
    return {"figure": "(i) media 0.003 del peso adaptativo bajo la nula", "status": "localizada",
            "stored_as_such": True, "stored_rounding": "binaria a 3 decimales",
            "values": vals, "concordant": conc, "result": result_info(f),
            "script": script_info("experiments/audit5_tarea5.py", "rhat_distribution_audit5.json"),
            "concordant_result": result_info(f5b),
            "concordant_script": script_info("experiments/audit5b_tarea_r4.py", "rhat_distribution_audit5b.json"),
            "manuscript_trail": ["paper/sec2_statistic.tex (v11): 'mean $0.003$, $95$th percentile below $0.008$'",
                                 "v14 sec5_montecarlo.tex §5.12 '(mean $0.003$)'"],
            "all_round_to_printed": all(v["rounds_to_printed"] for v in vals + conc)}


def fig_ii():
    f = "experiments/results/real_data_comparison_audit5b.json"
    f6 = "experiments/results/size_robustness_dkw_audit6.json"
    v = value_rec(f, ["summary", "a1_50k", "mean_fp", "ours"], "0.0301")
    det = {k: jget(f, ["summary", k, "detections", "ours"]) for k in ("repro", "a1_10k", "a1_50k")}
    copy = value_rec(f6, ["pilot_deviations", "real_data", "alpha1_50k", "mean_fp"], "0.0301")
    return {"figure": "(ii) FP media 0.0301 del estadistico registrado con N_cal = 5e4", "status": "localizada",
            "stored_as_such": True, "values": [v], "concordant": [copy],
            "configuration": "a1_50k: piloto alpha(1), N_cal = 50 000 (docstring de audit5b_tarea_r5.py)",
            "detections_by_configuration": det, "result": result_info(f),
            "script": script_info("experiments/audit5b_tarea_r5.py", "real_data_comparison_audit5b.json", ("N_cal 50,000",)),
            "concordant_result": result_info(f6),
            "concordant_script": script_info("experiments/audit6_tables_dkw.py", "size_robustness_dkw_audit6.json", ("real_data_comparison_audit5b.json",)),
            "manuscript_trail": ["paper/sec6_application.tex (v11): 'moves it to $0.0301$, with the same $13$ detections'",
                                 "deviation_table_audit8.json rows[0].sources cita el mismo archivo (summary/{repro,a1_10k})"],
            "all_round_to_printed": v["rounds_to_printed"] and copy["rounds_to_printed"]}


def fig_iii():
    f = "experiments/results/audit2_results_audit2.json"
    base = ["task3", "rho=0.5", "by_n"]
    inputs = [value_rec(f, base + ["200", "sigma_hac_median"], "0.552"), value_rec(f, base + ["5000", "sigma_hac_median"], "0.244")]
    bw = {n: jget(f, base + [n, "bw_median"]) for n in ("200", "5000")}
    stamp = jget(f, ["timestamp"])
    fix_time = C.git("show", "-s", "--format=%cI", HAC_FIX).strip()
    res = result_info(f)
    scr = script_info("experiments/audit2_presend_audit2.py", "audit2_results_audit2.json", (PILOT_A2, PILOT_A1, "sigma_hac_median"))
    return {"figure": "(iii) 6.9 % y 0.6 % de desviacion relativa de la mediana de sigma2_HAC frente a la identidad de Bartlett, "
                      "AR(0.5), n = 200 y 5000",
            "status": "no aparece como cifra almacenada; si sus insumos observados",
            "stored_as_such": False,
            "inputs": inputs, "bw_median": bw,
            "inputs_note": "medianas observadas de sigma2_HAC (500 replicas por n); los valores predichos por la identidad "
                           "(0.517 y 0.242) y las desviaciones (6.9 % y 0.6 %) solo aparecen en texto de manuscrito",
            "result": res, "result_timestamp": stamp, "hac_fix_commit": HAC_FIX, "hac_fix_time": fix_time,
            "result_before_hac_fix": stamp < fix_time,
            "script": scr, "script_bandwidth_pilot": "alpha(2)" if scr["contains"][PILOT_A2] and not scr["contains"][PILOT_A1] else "?",
            "manuscript_trail": ["paper/sec5_montecarlo.tex (v11), nota de tab:rates: predichos 0.517 y 0.242, observados 0.552 y "
                                 "0.244, 'a relative deviation falling from $6.9\\%$ to $0.6\\%$'",
                                 "paper/CHANGELOG_v8.md: 'desviacion 6.9%->0.6%'"],
            "all_inputs_round_to_v11": all(v["rounds_to_printed"] for v in inputs)}


def fig_iv():
    f = "experiments/results/resultados_auditoria_4_E.md"
    cell, row = md_row(f, "AR 0.5", "slope_B_pre")
    scr = script_info("experiments/audit4_tarea_E.py", "resultados_auditoria_4_E.md", (PILOT_A1, PILOT_A2, "np.mean([x['B_pre']",
                                                                                       "np.median"))
    return {"figure": "(iv) pendiente 0.333 del ancho de banda en log n", "status": "localizada",
            "stored_as_such": True,
            "values": [{"file": f, "key": "tabla markdown, fila 'AR 0.5', columna 'slope_B_pre'", "value": float(cell),
                        "printed": "0.333", "rounds_to_printed": rounds_to("0.333", cell)}],
            "row": row, "result": result_info(f), "script": scr,
            "script_bandwidth_pilot": "alpha(1)" if scr["contains"][PILOT_A1] and not scr["contains"][PILOT_A2] else "?",
            "aggregation": "media de B antes del techo sobre 500 replicas por n (np.mean); la nota de tab:rates del v11 dice "
                           "'medians'" if scr["contains"]["np.mean([x['B_pre']"] else "?",
            "manuscript_trail": ["paper/sec5_montecarlo.tex (v11), tab:rates: 'B, unrounded +0.333, R^2 1.000' y nota 'slope ... "
                                 "is $0.333$ with $R^{2} = 0.9999$'", "paper/CHANGELOG_v8.md: '+0.333, R2=0.9999'"],
            "all_round_to_printed": rounds_to("0.333", cell)}


def main():
    s = search()
    figs = {"i": fig_i(), "ii": fig_ii(), "iii": fig_iii(), "iv": fig_iv()}
    out = {"provenance": C.provenance(__file__, seed_family=None), "reading": "protocol_audit14.md, lectura 8",
           "search": s, "figures": figs, "recalculated": False}
    C.write_result(OUT, out, __file__)
    print("archivos de texto recorridos:", s["scanned_text_files"])
    for k, t in s["by_token"].items():
        print("  %-10s archivos %d (aciertos %d); checkpoints %d; referencias de auditoria %d; otros %d" % (
            k, t["files_with_hits"], t["total_hits"], t["checkpoint_files"], len(t["audit_references"]), len(t["other_files"])))
    for k, f in figs.items():
        print(k, f["status"], "| script", f["script"]["path"], "tracked" if f["script"]["tracked"] else "NO TRACKED",
              "| resultado", f["result"]["path"], (f["result"]["commit_added"] or "")[:7])
        for v in f.get("values", []) + f.get("inputs", []):
            print("     ", v["key"], v["value"], "->", v["printed"], v["rounds_to_printed"])
    print("iii antes de la correccion del piloto:", figs["iii"]["result_before_hac_fix"], figs["iii"]["script_bandwidth_pilot"])
    print("iv piloto:", figs["iv"]["script_bandwidth_pilot"], "|", figs["iv"]["aggregation"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
