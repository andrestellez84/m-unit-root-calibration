"""
Auditoria A13 - B13.Q, Q4: frases prohibidas en el v14 (protocol_audit13_amend1.md, lectura 6).

Busqueda literal sobre la fuente (.tex y cover_letter.md), a traves de saltos de linea.
Cada aparicion recibe su zona (seccion y subseccion por el orden de \\section y
\\subsection de cada archivo) y un estado:
  - excluida: dentro de las secciones de resultados negativos (§5.11, §5.12) o del
    entorno de tab:deviations (el encargo no las cuenta);
  - permitida: dentro de una zona autorizada para ese patron;
  - prohibida: en cualquier otro lugar.

Salida: experiments/results/q_phrases_audit13.json.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit13_common as C                                         # noqa: E402
import audit13_q_common as Q                                       # noqa: E402

OUT = os.path.join(C.RESULTS, "q_phrases_audit13.json")
SECTION_OF = {"sec1_introduction.tex": "1", "sec2_statistic.tex": "2", "sec3_theory.tex": "3", "sec4_implementation.tex": "4",
              "sec5_montecarlo.tex": "5", "sec6_application.tex": "6", "sec7_conclusion.tex": "7", "appA_proofs.tex": "A",
              "appB_critical_values.tex": "B", "appC_tables.tex": "C", "main.tex": "main", "highlights.tex": "highlights",
              "cover_letter.md": "cover_letter"}
EXCLUDED = ("5.11", "5.12")
# patron -> (regex, sin distinguir mayusculas, zonas permitidas)
PATTERNS = {
    "collapses faster": (r"collapses\s+faster", True, ()),
    "does not collapse as fast": (r"does\s+not\s+collapse\s+as\s+fast", True, ()),
    "no cost in size": (r"no\s+cost\s+in\s+size", True, ()),
    "no effect on size": (r"no\s+effect\s+on\s+size", True, ()),
    "RM-GLS": (r"RM-GLS", False, ()),
    "rolling means": (r"rolling\s+means", True, ("2.2", "4.2", "5.12", "rm_note")),
    "theta = 0.02": (r"\\theta\s*=\s*0\.02|θ\s*=\s*0\.02", False, ("4.2", "5", "tab:deviations")),
    "two-channel": (r"two-channel", True, ("5.11", "6", "7")),
}


def zones(text, fname):
    """Por linea: (subseccion 'k.j' o seccion, en tab:deviations, en nota de columna RM)."""
    sec = SECTION_OF[fname]
    lines = text.splitlines()
    out, sub, in_dev, env_start = [], 0, False, None
    paras, cur = [], []
    for i, l in enumerate(lines):
        if re.match(r"\s*\\subsection\{", l):
            sub += 1
        if "\\begin{table}" in l:
            env_start = i
        out.append(["%s.%d" % (sec, sub) if sub else sec, False, False])
        if l.strip() == "":
            paras.append(cur)
            cur = []
        else:
            cur.append(i)
        if "\\label{tab:deviations}" in l and env_start is not None:
            in_dev = True
            for k in range(env_start, i + 1):
                out[k][1] = True
        if in_dev:
            out[i][1] = True
            if "\\end{table}" in l:
                in_dev = False
    paras.append(cur)
    for p in paras:
        block = " ".join(lines[k] for k in p)
        if re.search(r"column RM\b", block) or (re.search(r"\\begin\{(tablenotes|minipage)\}", block) and re.search(r"\bRM\b", block)):
            for k in p:
                out[k][2] = True
    return out


def status(zone, fname, allowed):
    sub, dev, rmnote = zone
    sec = SECTION_OF[fname]
    if dev or sub in EXCLUDED:
        return "excluida"
    if sub in allowed or sec in allowed or (rmnote and "rm_note" in allowed) or (dev and "tab:deviations" in allowed):
        return "permitida"
    return "prohibida"


def main():
    v = Q.V14()
    hits = []
    for fname in Q.TEXT_FILES:
        text = v.files[fname]
        z = zones(text, fname)
        starts = [m.start() for m in re.finditer(r"^", text, flags=re.M)]
        for key, (pat, ci, allowed) in PATTERNS.items():
            for m in re.finditer(pat, text, flags=re.I if ci else 0):
                line = sum(1 for s in starts if s <= m.start())
                if fname.endswith(".tex") and re.search(r"(?<!\\)%", text[starts[line - 1]:m.start()]):
                    continue
                st = status(z[line - 1], fname, allowed)
                hits.append({"pattern": key, "file": "v14/" + fname, "line": line, "zone": z[line - 1][0],
                             "in_tab_deviations": z[line - 1][1], "in_rm_note": z[line - 1][2], "status": st,
                             "match": m.group(0), "context": re.sub(r"\s+", " ", text[max(0, m.start() - 60):m.end() + 60])})
    summary = {k: {s: sum(1 for h in hits if h["pattern"] == k and h["status"] == s) for s in ("prohibida", "permitida", "excluida")}
               for k in PATTERNS}
    out = {"provenance": C.provenance(__file__, seed_family=None), "manuscript": v.record(),
           "reading": "protocol_audit13_amend1.md, lectura 6",
           "patterns": {k: {"regex": p, "case_insensitive": ci, "allowed_zones": list(a)} for k, (p, ci, a) in PATTERNS.items()},
           "excluded_zones": list(EXCLUDED) + ["tab:deviations"], "hits": hits, "summary": summary,
           "forbidden_total": sum(1 for h in hits if h["status"] == "prohibida")}
    C.write_result(OUT, out, __file__)
    for k, s in summary.items():
        print("%-26s %s" % (k, s))
    for h in hits:
        if h["status"] == "prohibida":
            print("  PROHIBIDA %s:%d [%s] ...%s..." % (h["file"], h["line"], h["zone"], h["context"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
