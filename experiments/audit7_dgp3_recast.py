"""
Auditoria A7 - Decision 1.3: reencuadre de DGP 3 bajo la nula compuesta.

Sin computo nuevo. Bajo la nula de la Ec. (3) del manuscrito (paseo aleatorio con
innovaciones iid), un paseo aleatorio con quiebre de varianza NO es H0: sus
innovaciones no son identicamente distribuidas. Las celdas de DGP 3 con r > 1 son
por tanto POTENCIA contra la nula compuesta, y la celda r = 1 es el unico punto de
la familia donde H0 es verdadera: TAMANO.

Fuentes (se leen, no se copian):
  - Test propuesto R=0.50 y diagnosticos de componentes, piloto alpha(1) publicado:
      power_comparison_dgp34_alpha1_audit5b.json
  - DF-GLS asintotico (independiente del piloto): power_comparison_dgp3.json
    (sus columnas ours_* son del piloto alpha(2) y NO se usan)
  - Bootstrap DF-GLS (bootUR boot_adf, AWB, QD, intercepto):
      wild_bootstrap_r_audit6.json
Todas las tasas son NOMINALES: cada procedimiento a su propia regla del 5%.

Decision 1.4: se registra explicitamente la atribucion de la elevacion de DGP 3
al canal de media que hacen los diagnosticos de componentes de la seccion 5.5,
con los valores E[g1_std] y E[g2_std] que la respaldan o no.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                 # noqa: E402

SRC_OURS = "power_comparison_dgp34_alpha1_audit5b.json"
SRC_DFGLS = "power_comparison_dgp3.json"
SRC_BOOT = "wild_bootstrap_r_audit6.json"
OUT = os.path.join(C.RESULTS, "dgp3_recast_composite_null_audit7.json")
CELL_N = ("200", "1000")
CELL_R = ("1.0", "2.0", "3.0", "4.0")


def load(name):
    with open(os.path.join(C.RESULTS, name), encoding="utf-8") as f:
        return json.load(f)


def with_ci(rate, n_sim):
    k = int(round(rate * n_sim))
    if abs(k / n_sim - rate) > 1e-9:
        raise ValueError("la tasa %r no es multiplo de 1/%d" % (rate, n_sim))
    lo, hi = C.clopper_pearson(k, n_sim)
    return {"rate": rate, "rejections": k, "n_sim": n_sim, "ci_lower": lo, "ci_upper": hi}


def main():
    ours_src, dfgls_src, boot_src = load(SRC_OURS), load(SRC_DFGLS), load(SRC_BOOT)
    meta = ours_src["metadata"]
    if meta["pilot"] != "alpha1":
        raise SystemExit("%s no es del piloto alpha1: %r" % (SRC_OURS, meta["pilot"]))
    n_sim_paper = int(meta["N_sim"])

    cells = {}
    for n in CELL_N:
        for r in CELL_R:
            o = ours_src["dgp3"][n][r]
            d = dfgls_src["dgp3"][n][r]
            b = boot_src["dgp3"][n][r]
            if not b.get("complete", True):
                raise SystemExit("celda bootstrap incompleta: n=%s r=%s" % (n, r))
            dfgls = with_ci(d["dfgls"], n_sim_paper)
            if abs(dfgls["ci_lower"] - d["dfgls_ci_lo"]) > 6e-4 or \
                    abs(dfgls["ci_upper"] - d["dfgls_ci_hi"]) > 6e-4:
                raise SystemExit("IC de DF-GLS no reproducible en n=%s r=%s" % (n, r))
            boot_n = int(b.get("n_evaluated", b["N_sim"]))
            cells["n%s_r%s" % (n, r)] = {
                "n": int(n), "r": float(r),
                "role_under_composite_null": ("size" if r == "1.0" else "power"),
                "proposed_R050_alpha1": with_ci(o["ours_R050"], n_sim_paper),
                "dfgls_asymptotic": dfgls,
                "bootstrap_dfgls": {"rate": b["adf"]["rate"],
                                    "rejections": b["adf"]["rejections"],
                                    "n_sim": boot_n,
                                    "ci_lower": b["adf"]["ci_lower"],
                                    "ci_upper": b["adf"]["ci_upper"],
                                    "B": b["B"]},
            }

    # --- Decision 1.4: diagnosticos de componentes -------------------------
    diag, attribution_cells = {}, []
    for n, by_r in ours_src["dgp3"].items():
        base = by_r["1.0"]
        g1_0, g2_0 = base["E_g1_std"], base["E_g2_std"]
        for r, c in by_r.items():
            g1, g2 = c["E_g1_std"], c["E_g2_std"]
            rec = {"E_g1_std": g1, "E_g2_std": g2,
                   "std_g1": c["std_g1"], "std_g2": c["std_g2"],
                   "share_g2_in_R050_statistic": g2 ** 2 / (g1 ** 2 + g2 ** 2),
                   "rel_change_E_g1_vs_r1": g1 / g1_0 - 1.0,
                   "rel_change_E_g2_vs_r1": g2 / g2_0 - 1.0,
                   "change_in_E_g1_sq_vs_r1": g1 ** 2 - g1_0 ** 2,
                   "change_in_E_g2_sq_vs_r1": g2 ** 2 - g2_0 ** 2,
                   "proposed_R050_rate": c["ours_R050"]}
            if r != "1.0":
                rec["mean_channel_dominates_change"] = bool(
                    abs(rec["change_in_E_g1_sq_vs_r1"]) > abs(rec["change_in_E_g2_sq_vs_r1"]))
                attribution_cells.append(rec["mean_channel_dominates_change"])
            diag["n%s_r%s" % (n, r)] = rec

    supported = bool(attribution_cells) and all(attribution_cells)
    max_share_g2 = max(v["share_g2_in_R050_statistic"] for v in diag.values())

    C.atomic_write_json(OUT, {
        "provenance": C.provenance(
            dgp="dgp3_recast_composite_null", n_sim=n_sim_paper,
            seed_formula="heredadas de las fuentes; sin computo nuevo",
            source_files={s: C._sha256_file(os.path.join(C.RESULTS, s))
                          for s in (SRC_OURS, SRC_DFGLS, SRC_BOOT)},
            source_note=("la especificacion revisada citaba wild_bootstrap_r_audit7.json, "
                         "que no existe; los resultados de A6 estan en " + SRC_BOOT)),
        "null": ("compuesta: raiz unitaria Y innovaciones iid homoscedasticas "
                 "(Ec. 3 del manuscrito)"),
        "role_note": ("la especificacion revisada pedia rotular las ocho celdas como "
                      "potencia; bajo la nula compuesta la celda r=1 ES la nula, por lo que "
                      "se rotula como tamano y solo las seis celdas r>1 son potencia"),
        "rates_are": "nominales: cada procedimiento a su propia regla del 5%",
        "n_sim_note": ("test propuesto y DF-GLS: %d replicas; bootstrap: las de cada celda "
                       "(2000 en A6)" % n_sim_paper),
        "cells": cells,
        "component_diagnostics_section_5_5": {
            "manuscript_claim": ("los diagnosticos de componentes atribuyen la elevacion "
                                 "del rechazo en DGP 3 al canal de MEDIA y no al de varianza"),
            "source": SRC_OURS,
            "attribution_rule": ("para cada celda r>1 se compara el cambio respecto de r=1 "
                                 "en E[g1_std]^2 y en E[g2_std]^2, que son los dos sumandos del "
                                 "estadistico con R=0.50; el canal de media domina si su cambio "
                                 "es mayor en valor absoluto. Es una comparacion de medias de "
                                 "componentes, no de la cola de la distribucion"),
            "claim_supported_by_values": supported,
            "cells_r_gt_1_where_mean_dominates": "%d de %d" % (sum(attribution_cells),
                                                             len(attribution_cells)),
            "max_share_of_g2_in_R050_statistic": max_share_g2,
            "cells": diag,
        },
    })

    print("%-12s %-6s %10s %12s %14s" % ("celda", "rol", "propuesto", "DF-GLS asint", "bootstrap DFGLS"))
    for t, c in cells.items():
        print("%-12s %-6s %10.4f %12.4f %14.4f"
              % (t, c["role_under_composite_null"], c["proposed_R050_alpha1"]["rate"],
                 c["dfgls_asymptotic"]["rate"], c["bootstrap_dfgls"]["rate"]))
    print("\natribucion al canal de media respaldada: %s  (%s celdas r>1)  share max g2 = %.4f"
          % (supported, "%d/%d" % (sum(attribution_cells), len(attribution_cells)), max_share_g2))
    print("escrito %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
