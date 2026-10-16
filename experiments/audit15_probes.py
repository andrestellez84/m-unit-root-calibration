"""
Auditoria A15 - sondas de B15.1 (familia 151) y B15.3 (familia 158) (protocol_audit15.md,
lecturas 1.9 y 3.6; enmienda 1, E1.4; enmienda 2, secciones 3 y 5).

Solo tiempos: por camino y brazo (o configuracion), nucleos usados y proyeccion de horas-nucleo
del diseno completo y tras cada reduccion acumulada del encargo. Los conteos de rechazo (B15.1)
y los estadisticos (B15.3) se guardan bajo "sealed" y no se imprimen.

Proyeccion: el coste de una replica es proporcional al del estadistico; se mide el tiempo de
MZ_t-GLS (B15.1) y de MSB-B con los cuatro anchos (B15.3) en n in {100, 200, 500} con
trayectorias de la propia sonda recortadas, y se escala el tiempo de la celda de la sonda
(n = 500) por esos cocientes; se da tambien la cota conservadora sin escalar.

Salida: experiments/results/probes_audit15.json.
"""
import os
import sys
import time

import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit15_common as C                                         # noqa: E402
import audit15_design as D                                         # noqa: E402
import audit15_boot_engine as BE                                   # noqa: E402
import audit15_fixedb as FB                                        # noqa: E402
import audit12_unitroot as P12                                     # noqa: E402
import audit8_unitroot as U                                        # noqa: E402
import audit9_engine as E9                                         # noqa: E402

OUT = os.path.join(C.RESULTS, "probes_audit15.json")
F1, F3 = C.FAMILY["PROBE1"], C.FAMILY["PROBE3"]
CASE = D.PROBE_CASE
CT = CASE == "ct"
DC = {"c": 1, "ct": 2}
BENCH_REPS = 200
HOUR = 3600.0
BUDGET_CORE_HOURS = 50                 # enmienda 3, E3.4


def arm_rng(fam, cell, i, a):
    return np.random.default_rng(np.random.SeedSequence(fam, spawn_key=(cell, i, a)))


def boot_path(i, R):
    """Brazos (iii), (iv) y (v') en el camino i de la sonda 151; tiempos y decisiones (selladas)."""
    y = P12.null_path(D.PROBE_ERR, D.PROBE_N, C.rep_rng(F1, 0, i))
    T = len(y)
    n = T - 1
    kmax = U.kmax_rule(T)
    cbar = BE.CBAR_NP[CASE]
    pmax = BE.kmax_rule(T)
    dc = DC[CASE]
    out = {"t": {}, "p": {}}
    t0 = time.perf_counter()
    mzt = BE.mzt_gls(y, CT, cbar, kmax)[0]
    out["t"]["obs"] = time.perf_counter() - t0
    out["mzt"] = mzt
    g = arm_rng(F1, 0, i, D.ARMS["iii"])
    t0 = time.perf_counter()
    l = BE.bootur_block_length(T)
    idx = g.integers(0, T - l + 1, size=(R, T))
    out["p"]["iii"] = BE.pvalue_sb(y, CT, cbar, kmax, pmax, dc, BE.CQD_BOOTUR[dc - 1], idx)[0]
    out["t"]["iii"] = time.perf_counter() - t0
    g = arm_rng(F1, 0, i, D.ARMS["iv"])
    t0 = time.perf_counter()
    gam, _ = E9.awb_gamma(n)
    nu = g.standard_normal((R, n))
    out["p"]["iv"] = BE.pvalue_awb(y, CT, cbar, kmax, gam, nu)[0]
    out["t"]["iv"] = time.perf_counter() - t0
    g = arm_rng(F1, 0, i, D.ARMS["v_prime"])
    t0 = time.perf_counter()
    z = g.standard_normal((R, T))
    out["p"]["v_prime"] = BE.pvalue_swb(y, CT, cbar, kmax, pmax, dc, BE.CQD_BOOTUR[dc - 1], z)[0]
    out["t"]["v_prime"] = time.perf_counter() - t0
    return out


def fixedb_path(i):
    y = P12.null_path(D.PROBE_ERR, D.PROBE_N, C.rep_rng(F3, 0, i))
    n = len(y) - 1
    t0 = time.perf_counter()
    s2 = FB.s2_all(y)
    stats = {k: E9.rmgls(y, n, 0.0, v[1], CASE) for k, v in s2.items()}
    return time.perf_counter() - t0, stats


def bench(fn, ns):
    rng = np.random.default_rng(0)
    out = {}
    for n in ns:
        ys = [P12.null_path(D.PROBE_ERR, n, rng) for _ in range(BENCH_REPS)]
        fn(ys[0], n)
        t0 = time.perf_counter()
        for y in ys:
            fn(y, n)
        out[str(n)] = (time.perf_counter() - t0) / BENCH_REPS
    return out


def main():
    """Enmienda 1 (E1.4): la sonda de B15.1 solo corre si su Paso 0 paso la compuerta de (iii) o de (v')."""
    cores = min(os.cpu_count() or 1, 16)
    t_all = time.time()
    p0 = C.read_json("b1_paso0_v2_audit15.json")["gate"] if C.have("b1_paso0_v2_audit15.json") else {
        "iii_SB_bootUR": False, "v_prime_SWB_bootUR": False}
    run1 = bool(p0["iii_SB_bootUR"])                    # enmienda 3, E3.4: sin SB no hay B15.1
    p3 = C.read_json("b3_paso0_audit15.json")["passes"]
    out = {"provenance": C.provenance(__file__, seed_family=[F1, F3]),
           "reading": "protocol_audit15.md, 1.9 y 3.6; enmienda 1, E1.4; enmienda 2, secciones 3 y 5", "cores": cores,
           "gates": {"b15_1_paso0": p0, "b15_3_paso0": p3}}
    out["b15_1"] = probe1(cores, bool(p0["v_prime_SWB_bootUR"])) if run1 else {
        "executed": False, "reason": "B15.1 detenido por la compuerta del Paso 0 con B = 999 (enmienda 3, E3.4)"}
    out["b15_3"] = probe3(cores) if p3 else {"executed": False, "reason": "compuerta FFT de B15.3 no superada"}
    out["elapsed_sec"] = time.time() - t_all
    C.write_result(OUT, out, __file__)
    print("nucleos:", cores)
    if run1:
        print("B15.1 segundos por camino y brazo (n = 500, R = %d):" % D.R,
              {k: round(v, 3) for k, v in out["b15_1"]["seconds_per_path"].items()})
        for k, v in out["b15_1"]["projection"].items():
            print("  %-26s horas-nucleo %.1f (conservador %.1f); pared %.1f h (%.1f h)" % (
                k, v["core_hours_scaled"], v["core_hours_conservative"], v["wall_hours_scaled"], v["wall_hours_conservative"]))
    else:
        print("B15.1:", out["b15_1"]["reason"])
    if p3:
        print("B15.3 segundos por camino (4 anchos, n = 500): %.5f" % out["b15_3"]["seconds_per_path_4_configs"])
        print("  proyeccion:", {k: round(v, 2) for k, v in out["b15_3"]["projection"].items()})
        print("  conservadora:", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in out["b15_3"]["projection_conservative"].items()})
    return 0


def probe1(cores, with_v):
    BE.mzt_gls(P12.null_path(D.PROBE_ERR, D.PROBE_N, np.random.default_rng(1)), CT, BE.CBAR_NP[CASE], 17)
    res = Parallel(n_jobs=cores, backend="loky")(delayed(boot_path)(i, D.R) for i in range(D.PROBE1_PATHS))
    arms = ("iii", "iv", "v_prime")
    t_arm = {a: float(np.mean([r["t"][a] for r in res])) for a in arms}
    t_obs = float(np.mean([r["t"]["obs"] for r in res]))
    q_iid = C.read_json("b1_critical_audit14.json")
    q = [v["critical_value"] for v in q_iid["values"] if v["stat"] == "mzt" and v["case"] == CASE and v["n"] == D.PROBE_N
         and v["alpha"] == C.ALPHA][0]
    sealed1 = {"rejections": {a: int(sum(r["p"][a] <= C.ALPHA for r in res)) for a in arms}, "paths": len(res),
               "note": "brazo (iii) = SB (bootUR) (enmienda 3, E3.3)",
               "rejections_i": int(sum(r["mzt"] < U.NP_CV5[CASE]["MZt"] for r in res)),
               "rejections_ii": int(sum(r["mzt"] < q for r in res))}
    st = bench(lambda y, n: BE.mzt_gls(y, CT, BE.CBAR_NP[CASE], U.kmax_rule(n + 1)), D.A_N)
    ratio = {n: st[n] / st[str(D.PROBE_N)] for n in st}

    def proj(cells_n, R, arm_list):
        scaled = sum(npaths * sum(t_arm[a] for a in arm_list) * (R / D.R) * ratio[str(n)] for n, npaths in cells_n)
        cons = sum(npaths * sum(t_arm[a] for a in arm_list) * (R / D.R) for n, npaths in cells_n)
        return {"core_hours_scaled": scaled / HOUR, "core_hours_conservative": cons / HOUR,
                "wall_hours_scaled": scaled / HOUR / cores, "wall_hours_conservative": cons / HOUR / cores}
    full_cells = [(n, D.N_SIZE1) for e in P12.ERRORS for n in D.A_N for c in D.CASES] + [(D.POW1_N, D.N_POW1)] * 8
    red_err = {"ma_m0p8", "ma_0p5", "ar_0p5"}
    red_cells = [(n, D.N_SIZE1) for e in P12.ERRORS if P12.err_tag(e) in red_err for n in D.A_N for c in D.CASES]
    red_cells += [(D.POW1_N, D.N_SIZE1)] * 4 + [(D.POW1_N, D.N_POW1)] * 8
    use = arms if with_v else ("iii", "iv")
    projections = {"full": proj(full_cells, D.R, use),
                   "red1_R199": proj(full_cells, 199, use),
                   "red2_R199_18cells": proj(red_cells, 199, use),
                   "red3_R199_18cells_no_iv": proj(red_cells, 199, tuple(a for a in use if a != "iv"))}
    chosen = next((k for k in ("full", "red1_R199", "red2_R199_18cells", "red3_R199_18cells_no_iv")
                   if projections[k]["core_hours_scaled"] <= BUDGET_CORE_HOURS), None)
    return {"executed": True, "cell": D.CELLS[F1][0], "paths": D.PROBE1_PATHS, "R": D.R,
            "seconds_per_path": dict(t_arm, obs=t_obs), "mzt_seconds_by_n": st, "cost_ratio_by_n": ratio,
            "design_paths": {"full": sum(p for _, p in full_cells), "reduced_cells": sum(p for _, p in red_cells)},
            "projection": projections, "reductions_order": ["R = 199", "18 celdas (+ 4 nulas de n = 200 para ajustar)", "sin (iv)"],
            "arms_projected": list(use), "v_prime_included": with_v, "budget_core_hours": BUDGET_CORE_HOURS,
            "chosen_configuration": chosen, "launch_without_new_confirmation": chosen == "full",
            "sealed": sealed1}


def probe3(cores):
    t3 = time.time()
    r3 = Parallel(n_jobs=cores, backend="loky")(delayed(fixedb_path)(i) for i in range(D.PROBE3_PATHS))
    t_path3 = float(np.mean([r[0] for r in r3]))
    sealed3 = {"statistics": {k: [r[1][k] for r in r3] for k in r3[0][1]}}

    def fb_stat(y, n):
        s2 = FB.s2_all(y)
        for v in s2.values():
            E9.rmgls(y, n, 0.0, v[1], CASE)
    st3 = bench(fb_stat, D.A_N)

    def one_extra(y, n):
        E9.rmgls(y, n, 0.0, E9.hac_sigma_sq(y), "c")
        E9.rmgls(y, n, 0.0, U.np_statistics(y, "c")["s2_ar"], "c")
    st_extra = bench(one_extra, (200,))
    cal = sum(D.N_CAL3 * st3[str(n)] * len(D.CASES) for n in D.CAL3_N) + D.N_CAL3 * st_extra["200"]
    size3 = sum(D.N_SIZE3 * st3[str(n)] for e in P12.ERRORS for n in D.A_N for c in D.CASES)
    pow3 = len(D.POW3_RHO) * D.N_POW3 * (st3["200"] + st_extra["200"])
    proj3 = {"calibration_core_hours": cal / HOUR, "size_core_hours": size3 / HOUR, "power_core_hours": pow3 / HOUR,
             "total_core_hours": (cal + size3 + pow3) / HOUR, "total_wall_hours": (cal + size3 + pow3) / HOUR / cores}
    n_cal = len(D.CAL3_N) * D.N_CAL3 * len(D.CASES)
    n_size = len(P12.ERRORS) * len(D.A_N) * len(D.CASES) * D.N_SIZE3
    n_pow = len(D.POW3_RHO) * D.N_POW3
    cons = (n_cal + n_size + n_pow) * t_path3 + (D.N_CAL3 + n_pow) * st_extra["200"]
    proj3_cons = {"basis": "tiempo por camino medido en paralelo en la sonda (celda de n = 500), para todas las celdas",
                  "total_core_hours": cons / HOUR, "total_wall_hours": cons / HOUR / cores}
    return {"executed": True, "cell": D.CELLS[F3][0], "paths": D.PROBE3_PATHS, "seconds_per_path_4_configs": t_path3,
            "stat_seconds_by_n_4_configs": st3, "andrews_and_b_seconds_n200": st_extra, "projection": proj3,
            "projection_conservative": proj3_cons,
            "elapsed_sec": time.time() - t3, "sealed": sealed3}


if __name__ == "__main__":
    sys.exit(main())
