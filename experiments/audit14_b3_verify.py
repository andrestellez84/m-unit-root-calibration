"""
Auditoria A14 - B14.3: verificacion del v15 (protocol_audit14.md, lecturas 9 y 10).

Q3 sobre lo que cambio: las frases de la tabla «Cifras» de CHANGELOG_v15.md y, por extension
declarada, las frases de reemplazo de «Cifras retiradas», con el registro, las plantillas y las
convenciones de Q3 de B13.Q (audit13_q_claims). Completitud del changelog (cada bloque del diff
v14 -> v15 asignado a una fila o a una figura) y cobertura de los numeros de las lineas
cambiadas. Busqueda de las cifras retiradas en el texto del v15.

Q4 con la regla corregida: patrones y zonas de B13.Q para las frases que no cambian de regla;
«rolling means» y «two-channel» clasificadas por la frase que las contiene (D diseno original,
G prueba general en theta, N resultados negativos, M afirma algo sobre MSB-B); solo se
informan las M.

Salida: experiments/results/b3_verify_audit14.json.
"""
import difflib
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit14_common as C                                         # noqa: E402
import audit13_q_claims as Q3                                      # noqa: E402
import audit13_q_phrases as Q4                                     # noqa: E402
import audit13_q_common as Q13                                     # noqa: E402

OUT = os.path.join(C.RESULTS, "b3_verify_audit14.json")
PRIM, V13P = C.PRIM, C.PRIM_V13
Q3REG = {k: (f, t, fn, b) for k, f, t, fn, b in Q3.CLAIMS}
SAT = 0.99                     # umbral de la definicion de sec4 del v15 ("strictly between 0 and 0.99")


# ---------------------------------------------------------------------------
# Frases verificadas
# ---------------------------------------------------------------------------
def c_serial2_v15():
    vals, src, checks = Q3.c_serial2()
    cells = Q3.serial_cells()

    def gapb(c):
        return max(abs(c["iid"]["msb"]["rate"] - c["iid"]["glsb_t0"]["rate"]), abs(c["iid"]["mzt"]["rate"] - c["iid"]["glsb_t0"]["rate"]))
    worst = max(cells, key=gapb)
    keep = [c for c in checks if not c[0].startswith("MSB-GLS y MZ_t-GLS")]
    return vals[:7] + [gapb(worst) * C.PP] + vals[7:], \
        src + "; max |MSB o MZ_t - (b)| sobre las celdas: %s n = %d %s" % (worst["err_tag"], worst["n"], worst["case"]), keep


def sec42_v15():
    """Seccion 4.2 con la definicion literal del v15 y comparacion con la de B13.Q."""
    e = Q3.S.J("b103_equalized_audit10.json")["cells"]
    pw = [k for k in e if k.startswith(("dgp1_", "ct_power_", "dgp2_"))]

    def r(k, p):
        return e[k]["rates_sim"][p]["rate"]

    def sig(k):
        return e[k]["mcnemar_primary_vs_sim"][PRIM]["p_value"] < C.ALPHA
    uns = [k for k in pw if any(0 < r(k, p) < SAT for p in (PRIM, V13P))]
    up = [k for k in uns if sig(k) and r(k, PRIM) > r(k, V13P)]
    dn = [k for k in uns if sig(k) and r(k, PRIM) < r(k, V13P)]
    old = Q3.theta_vs_v13()
    return {"cells": uns, "higher": up, "lower": dn, "max_lower_pp": max((r(k, V13P) - r(k, PRIM)) * C.PP for k in dn),
            "less_distorted": old["less_distorted"], "more_distorted": old["more_distorted"], "dgp3": old["dgp3"],
            "b13q_cells": old["unsaturated"], "same_cells_as_b13q": sorted(uns) == sorted(old["unsaturated"]),
            "only_v15": sorted(set(uns) - set(old["unsaturated"])), "only_b13q": sorted(set(old["unsaturated"]) - set(uns)),
            "definition": "al menos uno de theta 0 y theta 0.02 rechaza con probabilidad estrictamente entre 0 y 0.99"}


def c_sec42_v15():
    t = sec42_v15()
    return [len(t["higher"]), len(t["cells"]), 0, SAT, len(t["lower"]), t["max_lower_pp"], len(t["less_distorted"]), len(t["dgp3"])], \
        "b103_equalized_audit10.json cells.<celda>.mcnemar_primary_vs_sim.gls_t0 y rates_sim; %s" % t["definition"], \
        [("ninguna celda de DGP 3 mas distorsionada", not t["more_distorted"]),
         ("mismo conjunto de celdas que la definicion de B13.Q", t["same_cells_as_b13q"])]


def c_dev_ncal_v15():
    f = "real_data_comparison_audit5b.json"
    s = C.read_json(f)["summary"]
    return [s["a1_50k"]["detections"]["ours"]], \
        "%s summary.a1_50k.detections.ours (N_cal 5e4) frente a summary.a1_10k.detections.ours (N_cal 1e4); piloto alpha(1)" % f, \
        [("detecciones sin cambio de N_cal 1e4 a 5e4", s["a1_10k"]["detections"]["ours"] == s["a1_50k"]["detections"]["ours"])]


def c_hacrate_v15():
    return [], "frase cualitativa sin cifra; B14.2 (iii) y (iv) localizan sus insumos", []


def q3(key):
    return Q3REG[key]


CLAIMS = [
    # (clave, fila del changelog, archivo, plantilla, funcion, cota)
    ("sec5_calib_out", "Cifras: sec5 §5.2", *q3("sec5_calib_out")),
    ("sec5_lp_se", "Cifras: sec5, nota de tab:localpower", *q3("sec5_lp_se")),
    ("sec5_dgp5b", "Cifras: sec5 §5.11", *q3("sec5_dgp5b")),
    ("sec5_serial2", "Cifras: sec5 §5.6", "sec5_montecarlo.tex",
     "Over the $<>$ cells its size ranges from $<>$ to $<>$, against $<>$ to $<>$ for \\RMGLS{}, and at $\\psi = -0.8$ and $n = 200$ it "
     "rejects $<>$ and $<>$ in the two cases. MSB-GLS and MZ$_t$-GLS with their own simulated critical values are within $<>$ points of "
     "it; DF-GLS over-rejects moderately (up to $<>$), ADF more (up to $<>$)", c_serial2_v15, (7,)),
    ("sec3_within", "Cifras: sec3, Observación del ancla", *q3("sec3_within")),
    ("sec4_mcnemar", "Cifras: sec4 §4.2", "sec4_implementation.tex",
     "(McNemar $p < 0.05$) in <> of the <> cells in which at least one of the two rejects with probability strictly between $<>$ and "
     "$<>$, and lower power in <>, by at most $<>$ points; under a variance break with the null true it is less distorted in <> of <> "
     "cells", c_sec42_v15, (5,)),
    ("sec5_negative", "Cifras retiradas: sec5 §5.12", "sec5_montecarlo.tex",
     "dropping it changes size by at most $<>$ points in any of the null cells examined under Gaussian, heavy-tailed and GARCH "
     "innovations. Second, a signal-proportional weight between the two channels concentrated at zero under the null and handed control "
     "to the mean channel; rebalancing the channels to a common scale lowered power by $<>$ to $<>$ points. Third, measuring the rolling "
     "means from their own average rather than from the GLS anchor costs $<>$ points of local power at $c = 10$, measured with $\\theta "
     "= 0.1$; the centered statistic lies $<>$ points", Q3.c_negative, (0,)),
    ("dev_ncal", "Cifras retiradas: sec6, nota de tab:deviations", "sec6_application.tex",
     "raising it to $5\\times10^4$ left its <> detections unchanged", c_dev_ncal_v15, ()),
    ("appA_hacrate", "Cifras retiradas: appA, rem:hacrate", "appA_proofs.tex",
     "tracks \\cref{eq:bartlettidentity} increasingly closely as $n$ grows, and the selected bandwidth grows at the rate $n^{1/3}$",
     c_hacrate_v15, ()),
]
ATTRIB_ROW = "Cifras: tab:attrib"
CHANGELOG_KEYS = {"sec5 §5.2": "sec5_calib_out", "sec5, nota de tab:localpower": "sec5_lp_se", "sec5 §5.11": "sec5_dgp5b",
                  "sec5 §5.6": "sec5_serial2", "sec3, Observación del ancla": "sec3_within", "tab:attrib": "tab:attrib",
                  "sec4 §4.2": "sec4_mcnemar"}
RETIRED_KEYS = {"sec5 §5.12": "sec5_negative", "sec6, nota de tab:deviations": "dev_ncal", "appA, `rem:hacrate`": "appA_hacrate"}


def conventions(printed, value, kind):
    """Las de Q3 (audit13_q_claims.conventions) y, en una cota inferior ("at least"), la simetrica
    hacia abajo: la cifra que Q3.correct(..., "lower") daria para esa cota (desviacion declarada)."""
    conv = Q3.conventions(printed, value, kind == "upper")
    if kind == "lower" and not conv and printed not in Q3.WORDS and Q3.correct(printed, value, "lower") == printed.lstrip("+"):
        conv = ["hacia abajo (cota)"]
    return conv


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def evaluate(v):
    claims = {}
    for key, row, fname, template, fn, bound in CLAIMS:
        text = v.files[fname]
        m = re.search(Q3.pattern(template), text)
        if m is None:
            claims[key] = {"changelog_row": row, "file": "v15/" + fname, "found": False, "template": template}
            continue
        vals, src, checks = fn()
        printed = list(m.groups())
        rows = []
        bspec = bound if isinstance(bound, dict) else {i: "upper" for i in bound}
        for i, (p, x) in enumerate(zip(printed, list(vals) + [None] * (len(printed) - len(vals)))):
            if x is None:
                rows.append({"printed": p, "value": None, "conventions": [], "verdict": "sin fuente JSON", "correct": None})
                continue
            kind = bspec.get(i)
            conv = conventions(p, x, kind)
            pv = Q3.WORDS[p] if p in Q3.WORDS else float(p)
            holds = True if kind is None else (x <= pv + Q3.BOUND_EPS if kind == "upper" else x >= pv - Q3.BOUND_EPS)
            if conv and holds:
                verdict = "reproduce como cota" if conv in (["hacia arriba (cota)"], ["hacia abajo (cota)"]) else "reproduce"
            elif conv:
                verdict = "no reproduce"
                conv = conv + ["cota %s incumplida" % ("superior" if kind == "upper" else "inferior")]
            else:
                verdict = "no reproduce"
            rows.append({"printed": p, "value": x, "conventions": conv, "bound": kind, "bound_holds": holds, "verdict": verdict,
                         "correct": None if verdict != "no reproduce" else Q3.correct(p, x, kind if conv else None)})
        claims[key] = {"changelog_row": row, "file": "v15/" + fname, "line": line_of(text, m.start()),
                       "line_end": line_of(text, m.end()), "span": [m.start(), m.end()], "found": True,
                       "quote": re.sub(r"\s+", " ", m.group(0)), "source": src, "numbers": rows,
                       "checks": [{"check": c, "holds": bool(h)} for c, h in checks],
                       "all_reproduced": all(r["verdict"] != "no reproduce" for r in rows) and all(h for _, h in checks)}
    return claims


def attrib_check(v):
    text = v.files["sec5_montecarlo.tex"]
    out = {}
    for name in ("tab_attrib_audit13", "tab_attrib_note_audit13"):
        m = re.search(r"\\input\{tables/%s\}" % name, text)
        data = v.binary["tables/%s.tex" % name]
        local = os.path.join(C.TABLES_A13, name + ".tex")
        out[name] = {"input_line": line_of(text, m.start()) if m else None, "sha256_v15": hashlib.sha256(data).hexdigest(),
                     "sha256_export": C.sha256_file(local), "identical": hashlib.sha256(data).hexdigest() == C.sha256_file(local)}
    out["transcribed_block_left"] = "TRANSCRIBED" in text
    out["passes"] = all(x["input_line"] and x["identical"] for k, x in out.items() if k.startswith("tab_")) and not out["transcribed_block_left"]
    return out


# ---------------------------------------------------------------------------
# Changelog: filas, bloques del diff y cobertura
# ---------------------------------------------------------------------------
def changelog_rows(v):
    text = v.files["CHANGELOG_v15.md"]
    out = {}
    for sec in ("Cifras", "Cifras retiradas por no tener JSON localizado (B13.Q)"):
        m = re.search(r"^## %s\s*$(.*?)(?=^## |\Z)" % re.escape(sec), text, flags=re.M | re.S)
        rows = [l for l in m.group(1).splitlines() if l.startswith("|")][2:]
        out[sec] = [[c.strip() for c in l.strip().strip("|").split("|")] for l in rows]
    return out


def hunks(v14, v15):
    out = []
    for fname in C.TEXT_FILES:
        a, b = v14.lines(fname), v15.lines(fname)
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            out.append({"file": fname, "tag": tag, "v14_lines": [i1 + 1, i2], "v15_lines": [j1 + 1, j2],
                        "v14_text": a[i1:i2], "v15_text": b[j1:j2]})
    return out


def assign(h, claims, attrib):
    if h["v15_text"] and all("\\includegraphics" in l for l in h["v15_text"]):
        return "Figuras"
    lo, hi = h["v15_lines"][0], max(h["v15_lines"][1], h["v15_lines"][0])
    for k, c in claims.items():
        if c.get("found") and c["file"] == "v15/" + h["file"] and c["line"] <= hi and c["line_end"] >= lo:
            return k
    if h["file"] == "sec5_montecarlo.tex" and any(attrib[n]["input_line"] and lo <= attrib[n]["input_line"] <= hi
                                                   for n in ("tab_attrib_audit13", "tab_attrib_note_audit13")):
        return "tab:attrib"
    return None


def coverage(v, hs, claims):
    items = []
    for h in hs:
        if not h["v15_text"]:
            continue
        text = v.files[h["file"]]
        starts = [m.start() for m in re.finditer(r"^", text, flags=re.M)]
        lo, hi = h["v15_lines"]
        a0, a1 = starts[lo - 1], (starts[hi] if hi < len(starts) else len(text))
        spans = [(c["span"][0], c["span"][1], k) for k, c in claims.items() if c.get("found") and c["file"] == "v15/" + h["file"]]
        for m in re.finditer(r"(?<![A-Za-z_\d.])\d+\.\d+", text[a0:a1]):
            a = a0 + m.start()
            hit = next((k for x, y, k in spans if x <= a < y), None)
            ctx = re.sub(r"\s+", " ", text[max(0, a - 50):a + len(m.group(0)) + 30])
            if hit:
                st, why = "cubierta", hit
            else:
                why = next((lab for pat, lab in Q3.CONTEXT_DESIGN if re.search(pat, ctx)), None)
                st = "diseno" if why else "no verificada"
            items.append({"file": "v15/" + h["file"], "line": line_of(text, a), "token": m.group(0), "status": st, "reason": why,
                          "context": ctx})
    return items


RETIRED = {
    "mean $0.003$": r"mean\s+\$0\.003\$",
    "0.003": r"(?<![\d.])0\.003(?!\d)",
    "0.0301": r"(?<![\d.])0\.0301(?!\d)",
    "6.9": r"(?<![\d.])6\.9(?!\d)",
    "0.6 %": r"(?<![\d.])0\.6(?!\d)\s*\\?%",
    "0.333": r"(?<![\d.])0\.333(?!\d)",
    "0.6 (cualquier contexto)": r"(?<![\d.])0\.6(?!\d)",
}


def retired(v):
    out = {}
    for k, pat in RETIRED.items():
        hits = []
        for fname in C.TEXT_FILES:
            text = v.files[fname]
            for m in re.finditer(pat, text):
                ln = line_of(text, m.start())
                line = v.lines(fname)[ln - 1]
                hits.append({"file": "v15/" + fname, "line": ln, "in_comment": bool(re.search(r"(?<!\\)%", line[:m.start() - text.rfind("\n", 0, m.start()) - 1])),
                             "context": re.sub(r"\s+", " ", text[max(0, m.start() - 60):m.end() + 40])})
        out[k] = hits
    return out


# ---------------------------------------------------------------------------
# Q4 con la regla corregida
# ---------------------------------------------------------------------------
RECLASS = ("rolling means", "two-channel")
CLASSES = {"D": "diseno original o estadistico registrado", "G": "prueba general en theta", "N": "resultados negativos",
           "M": "afirma algo sobre MSB-B"}
# (archivo, fragmento que contiene la aparicion, clase, justificacion)
REGISTRY = [
    ("main.tex", "a two-channel extension, both evaluated under pre-registered rules, are reported as negative results", "N",
     "resumen: la extension de dos canales se reporta como resultado negativo"),
    ("sec1_introduction.tex", "measured the second moment of rolling means of the detrended series", "D",
     "sujeto 'An earlier design'"),
    ("sec1_introduction.tex", "anchored the rolling means at the sample mean rather than at the GLS estimate", "D",
     "misma frase: el diseno anterior anclaba en la media"),
    ("sec1_introduction.tex", "returned its falsifying outcome for the two-channel design", "N",
     "experimento registrado con resultado falsador"),
    ("sec2_statistic.tex", "define the rolling means of the detrended series", "G",
     "definicion de la familia S_theta, theta in [0, 1/2] (eq:rollmean, eq:stat)"),
    ("sec3_theory.tex", "the uncentered second moment of the rolling means", "G",
     "argumento de consistencia del numerador de eq:stat (theta general)"),
    ("sec3_theory.tex", "the mean-square fluctuation of stationary rolling means", "G", "misma frase del argumento general"),
    ("sec5_montecarlo.tex", "A pre-registered test of a two-channel extension", "N", "titulo de §5.11 (resultado negativo registrado)"),
    ("sec5_montecarlo.tex", "originally one channel of a two-channel construction", "D", "sujeto 'The statistic was originally'"),
    ("sec5_montecarlo.tex", "the two-channel statistic would exceed the union", "N", "prediccion registrada que fallo"),
    ("sec5_montecarlo.tex", "for the two-channel statistic. The variance channel", "N", "potencia del estadistico de dos canales"),
    ("sec5_montecarlo.tex", "exceeds the two-channel statistic by $19$ to $29$ points", "M",
     "sujeto 'It' = 'The one-channel \\RMGLS{}' de la frase anterior: afirma la ventaja de potencia de MSB-B sobre el estadistico "
     "de dos canales (dentro de §5.11)"),
    ("sec5_montecarlo.tex", "``Two-channel'': the original construction", "D", "nota de tab:dgp5: define la columna del diseno original"),
    ("sec5_montecarlo.tex", "measuring the rolling means from their own average rather than from the GLS anchor", "N",
     "tercer resultado negativo de §5.12"),
    ("sec6_application.tex", "The registered statistic was the two-channel construction", "D", "estadistico registrado"),
    ("sec6_application.tex", "The registered two-channel statistic had fewer false-alarm episodes", "D",
     "sujeto: el estadistico registrado; la comparacion con MSB-B es implicita"),
    ("sec6_application.tex", "The registered statistic is the two-channel construction with adaptive weight", "D",
     "nota de tab:fp: estadistico registrado"),
    ("sec6_application.tex", "Two-channel statistic, windows $(0.1, 0.1)$, adaptive weight", "D",
     "tab:deviations, columna 'Registered'"),
    ("appA_proofs.tex", "The rolling means are linear in", "G", "prueba de prop:invariance para eq:stat (theta general)"),
    ("highlights.tex", "A smoothed variant and a two-channel extension are reported as negative results", "N",
     "resaltado: resultados negativos"),
    ("cover_letter.md", "a two-channel extension were evaluated under pre-registered rules", "N",
     "carta: ambas extensiones se reportan como resultados negativos"),
]


def fragment_spans(text, frag):
    pat = r"\s+".join(re.escape(x) for x in frag.split())
    return [(m.start(), m.end()) for m in re.finditer(pat, text)]


def phrases(v):
    hits = []
    for fname in C.TEXT_FILES:
        text = v.files[fname]
        z = Q4.zones(text, fname)
        starts = [m.start() for m in re.finditer(r"^", text, flags=re.M)]
        for key, (pat, ci, allowed) in Q4.PATTERNS.items():
            for m in re.finditer(pat, text, flags=re.I if ci else 0):
                line = sum(1 for s in starts if s <= m.start())
                if fname.endswith(".tex") and re.search(r"(?<!\\)%", text[starts[line - 1]:m.start()]):
                    continue
                rec = {"pattern": key, "file": "v15/" + fname, "line": line, "zone": z[line - 1][0], "match": m.group(0),
                       "context": re.sub(r"\s+", " ", text[max(0, m.start() - 80):m.end() + 80])}
                if key in RECLASS:
                    reg = [(c, j) for f, frag, c, j in REGISTRY if f == fname
                           and any(a <= m.start() < b for a, b in fragment_spans(text, frag))]
                    if len(reg) == 1:
                        rec.update(rule="corregida", cls=reg[0][0], class_label=CLASSES[reg[0][0]], justification=reg[0][1],
                                   status="informar" if reg[0][0] == "M" else "permitida")
                    else:
                        rec.update(rule="corregida", cls=None, class_label=None, justification=None,
                                   status="sin clasificar" if not reg else "clasificacion ambigua")
                else:
                    rec.update(rule="B13.Q", status=Q4.status(z[line - 1], fname, allowed))
                hits.append(rec)
    used = {i for i, (f, frag, c, j) in enumerate(REGISTRY)
            if any(h.get("justification") == j and h["file"] == "v15/" + f for h in hits)}
    return {"hits": hits,
            "summary": {k: {s: sum(1 for h in hits if h["pattern"] == k and h["status"] == s)
                            for s in ("prohibida", "permitida", "excluida", "informar", "sin clasificar", "clasificacion ambigua")}
                        for k in Q4.PATTERNS},
            "to_report": [h for h in hits if h["status"] in ("informar", "sin clasificar", "clasificacion ambigua", "prohibida")],
            "registry_entries": len(REGISTRY), "registry_unused": [REGISTRY[i][:2] for i in range(len(REGISTRY)) if i not in used],
            "classes": CLASSES}


def main():
    v = C.V15()
    v14 = Q13.V14()
    claims = evaluate(v)
    attrib = attrib_check(v)
    rows = changelog_rows(v)
    hs = hunks(v14, v)
    for h in hs:
        h["assigned"] = assign(h, claims, attrib)
    cov = coverage(v, hs, claims)
    ret = retired(v)
    ph = phrases(v)
    cifras = rows["Cifras"]
    retir = rows["Cifras retiradas por no tener JSON localizado (B13.Q)"]
    row_map = [{"table": "Cifras", "row": r[0], "claim": CHANGELOG_KEYS.get(r[0])} for r in cifras] + \
              [{"table": "Cifras retiradas", "row": r[0], "claim": RETIRED_KEYS.get(r[0])} for r in retir]
    bad = [{"claim": k, "file": c["file"], "line": c["line"], **r} for k, c in claims.items() if c.get("found")
           for r in c["numbers"] if r["verdict"] == "no reproduce"]
    fchecks = [{"claim": k, "file": c["file"], "line": c["line"], "check": x["check"]} for k, c in claims.items() if c.get("found")
               for x in c["checks"] if not x["holds"]]
    ret_figs = {k: h for k, h in ret.items() if k != "0.6 (cualquier contexto)"}
    out = {"provenance": C.provenance(__file__, seed_family=None), "manuscript": v.record(), "reference_v14": v14.record(),
           "reading": "protocol_audit14.md, lecturas 9 y 10",
           "claims": claims, "templates_not_found": [k for k, c in claims.items() if not c["found"]],
           "not_reproduced": bad, "failed_checks": fchecks,
           "sec42": sec42_v15(), "attrib": attrib,
           "changelog": {"rows": rows, "row_map": row_map, "rows_without_claim": [r for r in row_map if r["claim"] is None]},
           "hunks": hs, "hunks_unassigned": [h for h in hs if h["assigned"] is None],
           "coverage": {"items": cov, "counts": {s: sum(1 for i in cov if i["status"] == s) for s in ("cubierta", "diseno", "no verificada")}},
           "retired": ret, "retired_absent": all(not h for h in ret_figs.values()),
           "phrases": ph}
    C.write_result(OUT, out, __file__)
    print(v.record())
    for k, c in claims.items():
        if not c["found"]:
            print("  NO ENCONTRADA", k)
            continue
        print("  %-15s %s:%d  %s" % (k, c["file"], c["line"], ", ".join("%s->%s[%s]" % (r["printed"], "—" if r["value"] is None else "%.6g" % r["value"], r["verdict"]) for r in c["numbers"])))
        for x in c["checks"]:
            print("       comprobacion:", x["check"], x["holds"])
    print("tab:attrib:", attrib["passes"])
    print("sec42:", len(sec42_v15()["cells"]), "celdas; mismas que B13.Q:", sec42_v15()["same_cells_as_b13q"])
    print("filas del changelog sin frase:", out["changelog"]["rows_without_claim"])
    print("bloques del diff: %d; sin asignar: %d" % (len(hs), len(out["hunks_unassigned"])))
    for h in hs:
        print("   ", h["file"], h["v15_lines"], h["assigned"])
    print("cobertura de lineas cambiadas:", out["coverage"]["counts"])
    for i in cov:
        if i["status"] == "no verificada":
            print("   ?", i["file"], i["line"], i["token"], "|", i["context"])
    print("cifras retiradas ausentes:", out["retired_absent"])
    for k, h in ret.items():
        for x in h:
            print("   ", k, x["file"], x["line"], x["context"])
    print("Q4:", {k: {s: n for s, n in d.items() if n} for k, d in ph["summary"].items()})
    for h in ph["to_report"]:
        print("   INFORMAR", h["pattern"], h["file"], h["line"], h["status"], h.get("justification"), "|", h["context"])
    print("registro sin usar:", ph["registry_unused"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
