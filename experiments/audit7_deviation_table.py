"""
Auditoria A7 - Bloque 3.2: tabla de desviaciones del pre-registro.

Formato de "deviation table" de los Registered Reports: elemento pre-registrado,
ejecucion desplegada, valor pre-registrado, valor desplegado o re-corregido,
impacto, y la fuente de cada cifra. Ninguna cifra se escribe a mano: todas se
leen de los JSON existentes (falla con KeyError si una clave falta).

Filas de auditorias anteriores (del prompt): (i) piloto alpha(2) -> alpha(1) con
la FP media del test propuesto en datos reales; (ii) N_cal 50000 -> 10000 con la
cota DKW. La fila (i) usa las configuraciones repro (alpha2, N_cal 10000) y
a1_10k (alpha1, N_cal 10000) de audit5b_tarea_r5.py, que solo difieren en el piloto.

Filas de A7: valor critico de kappa_2, union calibrada conjuntamente frente a la
Bonferroni registrada, rejilla (n=1000 retirado, extension post-registro),
esquema de semillas y la compuerta de tamano del caso "ct" re-especificada por el
autor despues de los datos.

Salida: experiments/results/deviation_table_audit7.json.
Uso: python experiments/audit7_deviation_table.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                   # noqa: E402
import audit7_design as D                                   # noqa: E402

OUT = os.path.join(C.RESULTS, "deviation_table_audit7.json")
SOURCES = {
    "real_data": "real_data_comparison_audit5b.json",
    "dkw": "size_robustness_dkw_audit6.json",
    "k2val": "kappa2_validation_audit7.json",
    "k2sim": "kappa2_simcv_audit7.json",
    "dgp5": "dgp5_mixed_audit7.json",
    "paso0": "paso0_block1_audit7.json",
    "ct": "ct_case_audit7.json",
}


def load(key):
    with open(os.path.join(C.RESULTS, SOURCES[key]), encoding="utf-8") as f:
        return json.load(f)


def src(key, path):
    return {"file": "experiments/results/%s" % SOURCES[key], "path": path}


def main():
    rd, dkw, k2v, k2s, d5, p0, ct = (load(k) for k in SOURCES)
    rows = []

    rows.append({
        "id": "i", "audit": "A5bis",
        "element": "piloto de Andrews del ancho de banda HAC",
        "preregistered": "alpha(2)", "deployed": "alpha(1) (corregido)",
        "metric": "FP media del test propuesto en la validacion con datos reales (N_cal 10000 en ambas)",
        "preregistered_value": rd["summary"]["repro"]["mean_fp"]["ours"],
        "deployed_value": rd["summary"]["a1_10k"]["mean_fp"]["ours"],
        "impact": {"difference": rd["summary"]["a1_10k"]["mean_fp"]["ours"] - rd["summary"]["repro"]["mean_fp"]["ours"],
                   "max_abs_h0_size_change_by_n": max(abs(r["diff"]) for r in dkw["pilot_deviations"]["h0_size"])},
        "sources": [src("real_data", "summary/{repro,a1_10k}/mean_fp/ours"),
                    src("dkw", "pilot_deviations/h0_size/*/diff")]})

    rows.append({
        "id": "ii", "audit": "A6",
        "element": "tamano de la calibracion de la nula (N_cal)",
        "preregistered": "N_cal = 50000", "deployed": "N_cal = 10000",
        "metric": "cota DKW epsilon de la CDF empirica (95%)",
        "preregistered_value": dkw["metadata"]["dkw_bounds"]["N_50000"]["reported"],
        "deployed_value": dkw["metadata"]["dkw_bounds"]["N_10000"]["reported"],
        "impact": {"epsilon_exact_preregistered": dkw["metadata"]["dkw_bounds"]["N_50000"]["epsilon_exact"],
                   "epsilon_exact_deployed": dkw["metadata"]["dkw_bounds"]["N_10000"]["epsilon_exact"]},
        "sources": [src("dkw", "metadata/dkw_bounds/{N_50000,N_10000}")]})

    gate = k2v["gate"]
    rows.append({
        "id": "iii", "audit": "A7",
        "element": "valor critico de kappa_2 en la union",
        "preregistered": "asintotico (sup del puente browniano)", "deployed": "simulado por n (N_cal %d)" % D.N_CAL,
        "metric": "compuerta nominal de tamano de kappa_2 y valor critico simulado al 5%",
        "preregistered_value": {"gate_verdict": gate["verdict"], "failed_cells": len(gate["failed_cells"]),
                                "cells": len(k2v["cells"])},
        "deployed_value": {n: c["simulated_critical_values"]["0.05"] for n, c in k2s["cells"].items()},
        "impact": {"out_of_sample_ar093_in_region": {n: c["out_of_sample_ar093_at_simulated_cv"]["in_gate_region"]
                                                     for n, c in k2s["cells"].items()}},
        "sources": [src("k2val", "gate"), src("k2sim", "cells/*")]})

    cal = d5["calibration_by_n"]
    rows.append({
        "id": "iv", "audit": "A7",
        "element": "comparador de la prediccion 1",
        "preregistered": "union Bonferroni (bootstrap DF-GLS y kappa_2 a alpha/2)",
        "deployed": "union calibrada conjuntamente como principal; Bonferroni como secundaria",
        "metric": "tamano empirico sobre la calibracion bajo la nula compuesta",
        "preregistered_value": {n: c["bonferroni_union_achieved_size"]["rate"] for n, c in cal.items()},
        "deployed_value": {n: {"alpha_star": c["joint_union_alpha_star"],
                               "size": c["joint_union_achieved_size"]["rate"]} for n, c in cal.items()},
        "impact": "ninguno sobre el veredicto: la prediccion 1 no se cumple frente a ninguna de las dos",
        "sources": [src("dgp5", "calibration_by_n/*")]})

    rows.append({
        "id": "v", "audit": "A7",
        "element": "rejilla de DGP 5",
        "preregistered": "celdas de la especificacion revisada, con confirmacion a n=1000",
        "deployed": "n=1000 retirado; extension de quiebres debiles como contraste post-registro",
        "metric": "celdas",
        "preregistered_value": len(D.dgp5_cells_registered()),
        "deployed_value": {"analysed": len(d5["cells"]), "withdrawn": sorted(d5["withdrawn"]),
                           "post_registration_extension": sum(1 for c in d5["cells"].values()
                                                              if c["grid"] == "extension_enmienda2")},
        "impact": "la condicion de falsacion se evalua literalmente sobre el interior registrado; la extension no la anula",
        "sources": [src("dgp5", "cells, withdrawn"), {"file": "experiments/enmienda2_dgp5_audit7.md", "path": "secciones 3-5"}]})

    ov = p0["seed_overlap_block1"]
    rows.append({
        "id": "vi", "audit": "A7",
        "element": "formulas de semillas",
        "preregistered": "formulas aditivas del prompt (p. ej. 700000 + n*100 + int(param*100))",
        "deployed": "familia*10^8 + celda*10^5",
        "metric": "colisiones y pares de celdas con bloques solapados en el Bloque 1",
        "preregistered_value": "no evaluado en este archivo (ver paso0_pairing_audit7.json)",
        "deployed_value": {"exact_collisions": ov["exact_collisions"], "overlapping_pairs": ov["overlapping_pairs"]},
        "impact": "celdas estadisticamente independientes salvo los numeros aleatorios comunes declarados",
        "sources": [src("paso0", "seed_overlap_block1")]})

    v3 = ct["verifications"]["V3_exact_size"]
    size = ct["size_ct_under_h0_with_drift"]
    rows.append({
        "id": "vii", "audit": "A7",
        "element": "compuerta de tamano del caso ct (verificacion 3)",
        "preregistered": "tamano en la region binomial exacta en las 9 celdas y sin dependencia de mu",
        "deployed": ("re-especificada por el autor despues de los datos: valida la no dependencia de mu; "
                     "el tamano se reporta con el caveat de conservadurismo a n=200 del caso c"),
        "metric": "tasa del test ct (nula del paquete, QD) y de la referencia c sobre las mismas innovaciones, mu = 0",
        "preregistered_value": {"band": v3["band"], "passed": v3["passed"]},
        "deployed_value": {k: {"ct_qd": c["rejection_rates"]["ours_ct_qd"]["rate"],
                               "c_reference": c["rejection_rates"]["ours_c_reference_nodet"]["rate"]}
                           for k, c in size.items() if c["mu"] == 0.0},
        "impact": {"mu_dependence": v3["mu_dependence"]},
        "sources": [src("ct", "verifications/V3_exact_size, size_ct_under_h0_with_drift")]})

    C.atomic_write_json(OUT, {
        "provenance": C.provenance(dgp="deviation_table", n_sim=None, seed_formula=None,
                                   sources={k: C._sha256_file(os.path.join(C.RESULTS, v)) for k, v in SOURCES.items()}),
        "format": "Registered Reports deviation table",
        "rows": rows})
    print("%d filas -> %s" % (len(rows), OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
