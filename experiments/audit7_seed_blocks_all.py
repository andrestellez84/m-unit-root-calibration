"""
Auditoria A7 - Bloque 3.3: numeros aleatorios comunes en todas las familias de DGP del paper.

Cada serie i de una celda usa default_rng(seed_base + i), i = 0..N-1, de modo que la
celda ocupa el bloque de semillas [seed_base, seed_base + N). Dos celdas cuyos bloques
se solapan comparten series (numeros aleatorios comunes): el numero de semillas
compartidas es la longitud de la interseccion. Si comparten seed_base, sus primeras
extracciones son identicas aunque n difiera.

Formato (como paso0_pairing_audit6.json, ampliado): por familia y grupo, semillas
base ordenadas, huecos entre celdas adyacentes y sorteos compartidos entre celdas
adyacentes; ademas, todos los pares solapados dentro de la familia y entre familias.

Las formulas y N se transcriben de los scripts que produjeron cada tabla (se cita
archivo y linea); los n de la familia de muestra pequena se leen de su JSON.

Salida: experiments/results/paso0_pairing_audit7.json.
Uso: python experiments/audit7_seed_blocks_all.py
"""
import json
import os
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                   # noqa: E402
import audit7_design as D5                                  # noqa: E402
import audit7_ct_design as DCT                              # noqa: E402
import audit7_garch_size as G                               # noqa: E402
import power_comparison as PC                               # noqa: E402

OUT = os.path.join(C.RESULTS, "paso0_pairing_audit7.json")


def families():
    F = []

    def fam(name, source, n_sim, cells, note=""):
        F.append({"family": name, "source": source, "n_sim": n_sim, "cells": cells, "note": note})

    ng = PC.N_GRID
    fam("tabla1_tamano_rw", "power_comparison.py:355 run_size_verification (seed_base=0)", PC.N_SIM,
        {"n%d" % n: 0 for n in ng}, "la misma base en los tres n")
    fam("tabla1_tamano_kpss_ruido_blanco", "power_comparison.py:362 (50000 + i)", PC.N_SIM,
        {"n%d" % n: 50000 for n in ng}, "la misma base en los tres n")
    fam("dgp1", "power_comparison.py:408 (100000 + n*100 + int(rho*100))", PC.N_SIM,
        {"n%d_rho%.2f" % (n, r): 100000 + n * 100 + int(r * 100) for n in ng for r in PC.DGP1_RHOS},
        "reutilizada por extend_dgp1_dfgls.py y por el bootstrap de A6 (primeras 2000)")
    fam("dgp2", "power_comparison.py:452 (200000 + n*100 + int(delta*10))", PC.N_SIM,
        {"n%d_delta%.1f" % (n, d): 200000 + n * 100 + int(d * 10) for n in ng for d in PC.DGP2_DELTAS},
        "reutilizada por extend_dgp23_dfgls.py y audit6_dgp2_break_tests.py")
    fam("dgp3", "power_comparison.py:496 (300000 + n*100 + int(ratio*10))", PC.N_SIM,
        {"n%d_r%.1f" % (n, r): 300000 + n * 100 + int(r * 10) for n in ng for r in PC.DGP3_RATIOS},
        "reutilizada por extend_dgp23_dfgls.py, audit5b (piloto alpha1) y el bootstrap de A6 (primeras 2000)")
    fam("dgp4", "power_comparison.py:548 (400000 + n*100 + int(ratio*10))", PC.N_SIM,
        {"n%d_r%.1f" % (n, r): 400000 + n * 100 + int(r * 10) for n in ng for r in PC.DGP4_RATIOS})
    fam("colas_pesadas", "size_robustness_heavy_tails.py:162 / audit5b_tarea_r3.py:96 (900000 + n*100 + df*10)", 5000,
        {"n%d_t%d" % (n, df): 900000 + n * 100 + df * 10 for n in ng for df in (5, 3)})
    fam("a6_control_tamano_rw", "audit6_dgp2_break_tests.py:389 (100000 + n*100)", 5000,
        {"n%d" % n: 100000 + n * 100 for n in ng})
    fam("a6_control_tamano_rw_quiebre_media", "audit6_dgp2_break_tests.py:423 (150000 + n*100)", 5000,
        {"n%d" % n: 150000 + n * 100 for n in ng})
    fam("a5_rebalanceo_T13", "audit5_tarea5.py:40-44 / audit5b_tarea_r4.py:101-105", 5000,
        {"H0_n200": 70000, "H0_n500": 70000, "H0_n1000": 70000, "DGP3_n1000_r4": 80000, "DGP4_n500_r3": 90000})
    fam("a5_adaptativo_T14", "audit5b_tarea_r4.py:249-256, bucle en :285", 5000,
        {"H0_n200": 100000, "H0_n500": 100000, "H0_n1000": 100000,
         "DGP1_rho095_n200": 200000, "DGP1_rho097_n500": 200000, "DGP1_rho099_n1000": 200000,
         "DGP3_r4_n1000": 300000, "DGP4_r3_n500": 400000})
    with open(os.path.join(C.RESULTS, "small_n_size_audit5.json"), encoding="utf-8") as f:
        small = json.load(f)
    fam("a5_muestra_pequena", "audit5_tarea3.py:58 (N_sim) y :105 (0 + i)", 5000,
        {"n%d_theta%.1f" % (c["n"], c["theta"]): 0 for c in small},
        "la misma base que la Tabla 1 de tamano")
    fam("a7_bloque1", "audit7_design.py (familias 60 y 70)", D5.N_CAL, D5.all_seed_bases(),
        "N del bloque = N_cal (5000); DGP 5 usa 2000")
    fam("a7_caso_ct", "audit7_ct_design.py (familias 71-76)", DCT.N_CAL, DCT.all_seed_bases(),
        "N del bloque = N_cal de la nula HAC (50000); celdas de 5000")
    fam("a7_garch", "audit7_garch_size.py (familia 80)", G.N_SIM, {"n%d" % n: G.seed_base(n) for n in G.N_GRID})
    fam("a7_garch_ext", "audit7_garch_size.py --set ext (familia 81)", G.N_SIM,
        {"n%d_%s" % (n, k): G.seed_base_ext(k, n) for k in G.EXT_KEYS for n in G.N_GRID})
    fam("a7_garch_ext_large", "audit7_garch_size.py --set ext_large (familia 82)", G.N_SIM,
        {"n%d_%s" % (n, k): G.seed_base_ext_large(k, n) for k in G.LARGE_KEYS for n in G.N_GRID_LARGE})
    return F


def group_key(label):
    head = label.split("_")[0]
    return head if head.startswith("n") and head[1:].isdigit() else "todas"


def shared(b1, n1, b2, n2):
    return max(0, min(b1 + n1, b2 + n2) - max(b1, b2))


def main():
    F = families()
    out_f = {}
    total_within = 0
    for fam in F:
        groups = {}
        for label, b in fam["cells"].items():
            groups.setdefault(group_key(label), []).append((b, label))
        gout = {}
        for g, items in sorted(groups.items()):
            items.sort()
            bases = [b for b, _ in items]
            gaps = [b2 - b1 for b1, b2 in zip(bases, bases[1:])]
            gout[g] = {"cells": [l for _, l in items], "seed_bases": bases, "gaps": gaps,
                       "overlapping_draws_adjacent": [max(0, fam["n_sim"] - gap) for gap in gaps]}
        pairs = [{"a": la, "b": lb, "shared_seeds": shared(ba, fam["n_sim"], bb, fam["n_sim"]),
                  "same_seed_base": ba == bb}
                 for (la, ba), (lb, bb) in combinations(sorted(fam["cells"].items(), key=lambda kv: kv[1]), 2)
                 if shared(ba, fam["n_sim"], bb, fam["n_sim"]) > 0]
        total_within += len(pairs)
        out_f[fam["family"]] = {"source": fam["source"], "n_sim": fam["n_sim"], "note": fam["note"],
                                "by_group": gout, "overlapping_pairs": len(pairs),
                                "pairs_same_seed_base": sum(p["same_seed_base"] for p in pairs),
                                "max_shared_seeds": max((p["shared_seeds"] for p in pairs), default=0),
                                "pairs": pairs}
    cross = []
    for fa, fb in combinations(F, 2):
        for la, ba in fa["cells"].items():
            for lb, bb in fb["cells"].items():
                s = shared(ba, fa["n_sim"], bb, fb["n_sim"])
                if s > 0:
                    cross.append({"family_a": fa["family"], "cell_a": la, "family_b": fb["family"],
                                  "cell_b": lb, "shared_seeds": s})
    C.atomic_write_json(OUT, {
        "provenance": C.provenance(dgp="seed_blocks_all_families", n_sim=None,
                                   seed_formula="ver 'source' de cada familia"),
        "definition": "bloque de una celda = [seed_base, seed_base + N); sorteos compartidos = longitud de la interseccion",
        "families": out_f,
        "within_family_overlapping_pairs_total": total_within,
        "cross_family_overlaps": cross,
        "cross_family_overlaps_by_pair": {"%s|%s" % (a, b): sum(1 for c in cross if c["family_a"] == a and c["family_b"] == b)
                                          for a, b in sorted({(c["family_a"], c["family_b"]) for c in cross})}})
    for name, f in out_f.items():
        print("%-36s N=%-6d pares solapados %4d (misma base %3d, max compartidas %d)"
              % (name, f["n_sim"], f["overlapping_pairs"], f["pairs_same_seed_base"], f["max_shared_seeds"]))
    print("solapes entre familias: %d celdas-par" % len(cross))
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
