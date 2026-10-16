"""
Auditoria A7 - Bloque 1: re-sondeo del presupuesto a 6, 10 y 14 nucleos.

Motivo: el mismo lote de 14 series del bootstrap vario hasta 6x entre
mediciones seguidas (bootstrap_cost_diagnostic_audit7.json). Una sonda de 14
series sobre 14 nucleos es una sola oleada y la fija el trabajador mas lento; el
i7-12650H tiene 6 nucleos P y 4 E (16 hilos), de modo que con 14 trabajadores
parte de la carga cae en nucleos E y en hyperthreads.

Diseno
------
- Solo series de calibracion (paseo aleatorio, familia 70), indices 0..K-1: no
  se toca ninguna serie de DGP 5. n in D.CAL_N_ACTIVE.
- K = 70 series por medicion: 5 oleadas a 14 nucleos, 7 a 10, 12 a 6.
- Dos rondas con el orden de nucleos invertido (6,10,14 y 14,10,6), para
  separar la deriva temporal del efecto del numero de nucleos.
- En cada medicion: bootstrap (worker con semilla, B = 399) sobre las K series;
  procedimientos de Python sobre las mismas K series con el pool de loky a ese
  numero de trabajadores, caliente; componentes de la nula adaptativa sobre
  196 series; y el sobrecosto de Python con el pool frio, que es lo que paga
  cada lote del runner cuando el pool expira mientras corre R.
- Determinismo: los p-valores de las seis mediciones de cada n deben coincidir.
- Proyeccion por configuracion con el costo medio de las dos rondas y con el
  peor. Se elige la de menor total medio (mayor rendimiento, no mayor
  eficiencia por nucleo).
- Registra la CPU y el plan de energia activo.

Nada se escribe en checkpoints/audit7_block1: la ejecucion real no reutiliza
estas mediciones.

Uso: python experiments/audit7_block1_budget_cores.py
"""
import json
import math
import os
import subprocess
import sys
import time

import numpy as np
from joblib import Parallel, delayed
from joblib.externals.loky import get_reusable_executor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit7_common as C                                   # noqa: E402
import audit7_design as D                                   # noqa: E402
import audit7_dgp5_runner as RUN                            # noqa: E402

OUT = os.path.join(C.RESULTS, "block1_budget_cores_audit7.json")
TMP = os.path.join(C.CKPT_ROOT, "audit7_budget_cores_tmp")
K = 70
ROUND_ORDERS = ((6, 10, 14), (14, 10, 6))
ADAPTNULL_PROBE = 196
BLOCK_CAP = C.DEFAULT_MAX_SECONDS
TEN_HOURS = 10 * 3600
STABILITY_MAX_RATIO = 2.0      # decision del autor: por encima no se lanza, se recorta la rejilla
OVERLAY_NAMES = {                # GUID documentados de los modos de energia de Windows
    "ded574b5-45a0-4f42-8737-46345c09c238": "mejor rendimiento",
    "3af9b8d9-7c97-431d-ad78-34a8bfea439f": "equilibrado (mejor rendimiento)",
    "961cc777-2547-4f9d-8174-7d86181b8a7a": "mejor eficiencia energetica",
    "00000000-0000-0000-0000-000000000000": "equilibrado (sin capa)",
}


def system_info():
    ps = ["powershell", "-NoProfile", "-Command",
          "Get-CimInstance Win32_Processor | "
          "Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json"]
    cpu = json.loads(subprocess.run(ps, capture_output=True, text=True).stdout)
    plan = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True,
                          text=True, errors="replace").stdout.strip()
    # En Windows 11 el "Modo de energia" de Configuracion es una capa sobre el plan
    # activo y powercfg no la muestra; se lee del registro. En un portatil importa
    # ademas si esta enchufado (BatteryStatus 2 = corriente alterna).
    ps_overlay = ["powershell", "-NoProfile", "-Command",
                  "Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power\\User\\PowerSchemes' | "
                  "Select-Object ActivePowerScheme,ActiveOverlayAcPowerScheme,ActiveOverlayDcPowerScheme | "
                  "ConvertTo-Json"]
    overlay = json.loads(subprocess.run(ps_overlay, capture_output=True, text=True).stdout)
    ps_batt = ["powershell", "-NoProfile", "-Command",
               "Get-CimInstance Win32_Battery | Select-Object BatteryStatus,EstimatedChargeRemaining | ConvertTo-Json"]
    batt_out = subprocess.run(ps_batt, capture_output=True, text=True).stdout.strip()
    return {"cpu": cpu, "power_scheme": plan,
            "power_mode_overlay": {**overlay, "overlay_names": OVERLAY_NAMES},
            "battery": json.loads(batt_out) if batt_out else None}


def _adapt(n, idx):
    for i in idx:
        RUN.components(RUN.generate("adaptnull", n, None, None, RUN.ADAPT_NULL_SEED, i))
    return len(idx)


def split(idx, cores):
    return [p for p in (idx[j::cores] for j in range(cores)) if p]


def py_rows_sec(n, sb, cores):
    t = time.time()
    Parallel(n_jobs=cores, backend="loky")(
        delayed(RUN._py_rows)("cal", n, None, None, sb, p) for p in split(list(range(K)), cores))
    return time.time() - t


def measure(rnd, cores, ns):
    RUN.warm_pool(cores, ns)
    out = []
    for n in ns:
        sb = D.cal_seed_base(n)
        mat = np.column_stack([RUN.generate("cal", n, None, None, sb, i) for i in range(K)])
        p, tm = RUN.run_bootstrap_matrix("budgetcores_" + D.cal_tag(n), mat, 0,
                                         RUN.r_seed_start(sb, 0), cores, D.DGP5_B, tmp_dir=TMP)
        py = py_rows_sec(n, sb, cores)
        t = time.time()
        Parallel(n_jobs=cores, backend="loky")(
            delayed(_adapt)(n, q) for q in split(list(range(ADAPTNULL_PROBE)), cores))
        adapt = time.time() - t
        m = {"round": rnd, "cores": cores, "n": n,
             "r_wall_sec": tm["r_wall_sec"], "r_internal_sec": tm["r_internal_sec"],
             "boot_sec_per_series": tm["r_internal_sec"] / K,
             "r_startup_sec_per_batch": max(tm["r_wall_sec"] - tm["r_internal_sec"], 0.0),
             "py_warm_sec_per_series": py / K,
             "adaptnull_sec_per_series": adapt / ADAPTNULL_PROBE,
             "p_boot": p}
        print("  ronda %d  cores %2d  n=%-4d bootstrap %.3f s/serie  arranque R %.1f s  "
              "python %.3f s/serie  nula adapt %.4f s/serie"
              % (rnd, cores, n, m["boot_sec_per_series"], m["r_startup_sec_per_batch"],
                 m["py_warm_sec_per_series"], m["adaptnull_sec_per_series"]), flush=True)
        out.append(m)
    for m in out:                      # pool frio: lo que paga cada lote del runner
        get_reusable_executor().shutdown(wait=True)
        sb = D.cal_seed_base(m["n"])
        cold = py_rows_sec(m["n"], sb, cores)
        m["py_cold_extra_sec_per_batch"] = max(cold - m["py_warm_sec_per_series"] * K, 0.0)
        print("  ronda %d  cores %2d  n=%-4d sobrecosto de pool frio %.1f s por lote"
              % (rnd, cores, m["n"], m["py_cold_extra_sec_per_batch"]), flush=True)
    return out


def project(meas, cores, how):
    agg = np.mean if how == "mean" else np.max
    per_n = {}
    for n in D.CAL_N_ACTIVE:
        ms = [m for m in meas if m["cores"] == cores and m["n"] == n]
        comp = {k: float(agg([m[k] for m in ms])) for k in
                ("boot_sec_per_series", "r_startup_sec_per_batch", "py_warm_sec_per_series",
                 "py_cold_extra_sec_per_batch", "adaptnull_sec_per_series")}
        steady = comp["boot_sec_per_series"] + comp["py_warm_sec_per_series"]
        k_batch = max(C.PROBE_SERIES,
                      int(math.floor(C.TARGET_BATCH_SEC / steady)) // C.PROBE_SERIES * C.PROBE_SERIES)
        per_batch = comp["r_startup_sec_per_batch"] + comp["py_cold_extra_sec_per_batch"]

        def cell(N):
            batches = 1 + math.ceil(max(N - C.PROBE_SERIES, 0) / k_batch)
            return N * steady + batches * per_batch

        comp.update({"steady_sec_per_series": steady, "k_batch": k_batch,
                     "calibration_cell_sec": cell(D.N_CAL), "dgp5_cell_sec": cell(D.DGP5_N_SIM),
                     "adaptnull_cell_sec": comp["adaptnull_sec_per_series"] * RUN.ADAPT_NULL_N})
        per_n[str(n)] = comp

    cells = D.dgp5_cells_active()
    first = [c for c in cells if abs(c[1] - 0.93) < 1e-9]
    rest = [c for c in cells if abs(c[1] - 0.93) >= 1e-9]
    jobs = [("adaptnull n=%d" % n, per_n[str(n)]["adaptnull_cell_sec"]) for n in D.CAL_N_ACTIVE]
    jobs += [("cal n=%d" % n, per_n[str(n)]["calibration_cell_sec"]) for n in D.CAL_N_ACTIVE]
    jobs += [(D.dgp5_tag(*c), per_n[str(c[0])]["dgp5_cell_sec"]) for c in first + rest]
    total = sum(s for _, s in jobs)
    blocks, cur, cur_s = [], [], 0.0
    for name, s in jobs:
        if cur and cur_s + s > BLOCK_CAP:
            blocks.append({"jobs": cur, "sec": cur_s})
            cur, cur_s = [], 0.0
        cur.append(name)
        cur_s += s
    if cur:
        blocks.append({"jobs": cur, "sec": cur_s})
    grp = {
        "nulas_adaptativas": sum(per_n[str(n)]["adaptnull_cell_sec"] for n in D.CAL_N_ACTIVE),
        "calibracion": sum(per_n[str(n)]["calibration_cell_sec"] for n in D.CAL_N_ACTIVE),
    }
    for n in D.CAL_N_ACTIVE:
        grp["dgp5_registrada_n%d" % n] = sum(per_n[str(n)]["dgp5_cell_sec"] for c in cells
                                             if c[0] == n and not D.is_weak(c[2]))
        grp["dgp5_extension_n%d" % n] = sum(per_n[str(n)]["dgp5_cell_sec"] for c in cells
                                            if c[0] == n and D.is_weak(c[2]))
    grp["dgp5_rho0.93"] = sum(per_n[str(c[0])]["dgp5_cell_sec"] for c in first)
    return {"per_n": per_n, "subtotals_sec": grp, "total_sec": total,
            "exceeds_10h": total > TEN_HOURS, "blocks": blocks,
            "jobs_longer_than_block_cap": [nm for nm, s in jobs if s > BLOCK_CAP],
            "k_batch_arg": ",".join("%d:%d" % (n, per_n[str(n)]["k_batch"]) for n in D.CAL_N_ACTIVE)}


def main():
    t0 = time.time()
    info_before = system_info()
    print("=" * 78)
    print("  A7 / Bloque 1 - re-sondeo a 6/10/14 nucleos, K=%d series, dos rondas" % K)
    print("  %s" % info_before["power_scheme"])
    print("=" * 78, flush=True)
    meas = []
    for rnd, order in enumerate(ROUND_ORDERS, 1):
        for cores in order:
            meas += measure(rnd, cores, D.CAL_N_ACTIVE)

    determinism = {}
    for n in D.CAL_N_ACTIVE:
        ps = [np.array(m["p_boot"], dtype=float) for m in meas if m["n"] == n]
        determinism[str(n)] = {
            "measurements": len(ps),
            "all_identical": bool(all(np.array_equal(ps[0], q, equal_nan=True) for q in ps[1:])),
            "max_abs_diff": float(max(np.nanmax(np.abs(ps[0] - q)) for q in ps[1:]))}

    cores_grid = sorted({m["cores"] for m in meas})
    proj = {str(c): {"mean_of_rounds": project(meas, c, "mean"),
                     "worst_of_rounds": project(meas, c, "worst")} for c in cores_grid}
    best = min(cores_grid, key=lambda c: proj[str(c)]["mean_of_rounds"]["total_sec"])

    # Compuerta de estabilidad: si la tasa mas lenta supera STABILITY_MAX_RATIO veces la
    # mas rapida para el mismo trabajo en la configuracion elegida, no se lanza.
    stability = {}
    for c in cores_grid:
        for n in D.CAL_N_ACTIVE:
            ms = [m for m in meas if m["cores"] == c and m["n"] == n]
            boot = [m["boot_sec_per_series"] for m in ms]
            steady = [m["boot_sec_per_series"] + m["py_warm_sec_per_series"] for m in ms]
            stability["cores%d_n%d" % (c, n)] = {
                "boot_sec_per_series": boot, "boot_max_over_min": max(boot) / min(boot),
                "steady_max_over_min": max(steady) / min(steady)}
    chosen_ratio = max(stability["cores%d_n%d" % (best, n)]["steady_max_over_min"] for n in D.CAL_N_ACTIVE)
    gate = {"max_ratio_allowed": STABILITY_MAX_RATIO, "chosen_cores_max_ratio": chosen_ratio,
            "all_configs_max_ratio": max(s["steady_max_over_min"] for s in stability.values()),
            "launch_allowed": bool(chosen_ratio <= STABILITY_MAX_RATIO)}

    C.atomic_write_json(OUT, {
        "provenance": C.provenance(dgp="block1_budget_cores", n_sim=K,
                                   seed_formula="series de calibracion 70*10^8+n_idx*10^5, i=0..69; "
                                                "semilla de R (seed_base+i) mod M",
                                   extra_code_files=[RUN.WORKER_R]),
        "system_before": info_before, "system_after": system_info(),
        "design": {"series_per_measurement": K, "round_orders": [list(o) for o in ROUND_ORDERS],
                   "adaptnull_probe_series": ADAPTNULL_PROBE, "B": D.DGP5_B,
                   "n_active": list(D.CAL_N_ACTIVE),
                   "active_dgp5_cells": len(D.dgp5_cells_active())},
        "measurements": [{k: v for k, v in m.items() if k != "p_boot"} for m in meas],
        "determinism_across_cores_and_rounds": determinism,
        "projection_by_cores": proj,
        "chosen_cores_max_throughput": best,
        "stability_by_config": stability,
        "stability_gate": gate,
        "elapsed_sec": round(time.time() - t0, 1),
    })
    print("\n%-6s %14s %14s" % ("cores", "total medio h", "total peor h"))
    for c in cores_grid:
        print("%-6d %14.2f %14.2f" % (c, proj[str(c)]["mean_of_rounds"]["total_sec"] / 3600,
                                     proj[str(c)]["worst_of_rounds"]["total_sec"] / 3600))
    print("elegido: %d nucleos   determinismo: %s" % (best, determinism))
    print("estabilidad (lenta/rapida, config elegida): %.2fx  -> %s"
          % (chosen_ratio, "LANZABLE" if gate["launch_allowed"] else "NO LANZAR: supera %.1fx" % STABILITY_MAX_RATIO))
    print(OUT)
    return 0 if gate["launch_allowed"] else 3


if __name__ == "__main__":
    sys.exit(main())
