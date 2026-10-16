"""
Auditoria A8 - enmienda 2, punto 3: correccion de la clave de cache de la nula.

1. Regresion pre/post con defaults (regla 6): el paquete anterior a la
   correccion y el actual, en procesos hijos, sobre las 100 series de la celda
   "regression" (familia 91): max|delta| = 0 en estadistico y p-valor.
2. El defecto, medido: en un proceso, build_null_cdf con N_cal = 10000 y luego con
   50000 (mismos theta, R, n y semilla); con el paquete anterior la segunda
   llamada devuelve la CDF de 10000 puntos, con el actual la de 50000.
3. Auditoria de alcance sobre los scripts de A1-A7 (solo identificar): procesos
   que construyen la nula en cache con parametros que la clave antigua no
   distinguia (N_cal, semilla), con el orden de las llamadas y las cifras
   publicadas en paper/*.tex que dependen de ellos.
4. Las columnas sin bootstrap de B2 no pasan por la cache: el codigo que las
   calcula no llama a build_null_cdf, null_cdf ni compute_statistic.

Salida: experiments/results/cache_fix_audit8.json.
Uso: python experiments/audit8_cache_fix_validate.py
"""
import inspect
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit8_common as C                                          # noqa: E402
import audit8_b1_validate as V                                     # noqa: E402

OUT = os.path.join(C.RESULTS, "cache_fix_audit8.json")
FIX_FILE = "src/stationarity_test/empirical_eigenvalues.py"
FIX_MARK = "_seed_key"
BUG_CODE = ("import json, sys; from stationarity_test.empirical_eigenvalues import build_null_cdf as b; "
            "a = b((0.1, 0.1), 0.5, 60, N_cal=10000, seed=42); c = b((0.1, 0.1), 0.5, 60, N_cal=50000, seed=42); "
            "json.dump({'first_len': len(a.x), 'second_len': len(c.x), 'same_object': a is c}, sys.stdout)")

# Procesos de A1-A7 con llamadas en cache que la clave antigua confundia (identificados leyendo
# cada script que llama a build_null_cdf; ver 'scanned').
SCOPE = [
    {"script": "experiments/audit5_tarea3.py",
     "calls": [r"res = compute_statistic\(Y, theta, 0\.5", r"cdf_cache\[r_name\] = build_null_cdf\(theta=t, R=r_val, n=n, N_cal=N_cal, seed=42\)"],
     "order": "compute_statistic (N_cal = 10000 por defecto, en simulate_components) antes de build_null_cdf(N_cal = 50000) "
              "para la misma (theta, R = 0.5, n): la tabla usa la CDF de 10000 para R = 0.5; R = 0.25 y 0.75 no se afectan",
     "outputs": ["experiments/results/small_n_size_audit5.json"],
     "paper": [{"file": "paper/sec5_montecarlo.tex", "pattern": r"size \$0\.0330\$, \$0\.0390\$ and \$0\.0366\$",
                "values": "0.0330, 0.0390, 0.0366 (theta = 0.1; n = 60, 100, 150)",
                "reproduction": "b2b_diagnostic_audit8.json D4"},
               {"file": "paper/sec5_montecarlo.tex", "pattern": r"the proposed test gives \$0\.0428\$, \$0\.0424\$",
                "values": "0.0428, 0.0424, 0.0420 (theta = 0.5; n = 60, 100, 150)",
                "reproduction": None}]},
    {"script": "experiments/audit5_tarea10.py",
     "calls": [r"compute_statistic\(Y, theta, 0\.5, eps=1e-6, andrews_pilot=\"alpha1\"\)",
               r"build_null_cdf\(theta, 0\.5, n, N_cal=10000, seed=42\)", r"build_null_cdf\(theta, 0\.5, n, N_cal=50000, seed=42\)"],
     "order": "compute_statistic y build_null_cdf(N_cal = 10000) llenan la cache; la medicion de tiempo de N_cal = 50000 "
              "cronometra un acierto de cache",
     "outputs": ["experiments/results/tarea10_audit5.log"],
     "paper": [{"file": "paper/sec4_implementation.tex", "pattern": r"\(\$1\.02\$~s, mean of three runs\)",
                "values": "1.02 s (calibracion N_cal = 50000, n = 1000)",
                "reproduction": "no depende de audit5_tarea10: la cifra sale de audit5b_tarea_r6.py, que usa use_cache=False"}]},
]
SCANNED_NO_COLLISION = {
    "experiments/audit5_tarea1.py": "build_null_cdf(N_cal = 50000) antes de compute_statistic para cada n: la tabla usa la CDF correcta (Tabla 7; reproducida en B2)",
    "experiments/audit5_tarea2.py": "build_null_cdf(N_cal = 50000) antes de compute_statistic",
    "experiments/audit5b_tarea_r6.py": "calibraciones cronometradas con use_cache=False; las cacheadas usan N_cal = 10000, igual que compute_statistic",
    "experiments/audit2_presend_audit2.py": "build_null_cdf con use_cache=False",
    "experiments/audit5_tarea9.py": "una sola llamada cacheada (N_cal = 1000)",
    "experiments/audit5_tarea4.py": "solo build_null_cdf(N_cal = 50000)",
    "experiments/audit5b_tarea_r3.py": "solo build_null_cdf(N_cal = 50000); sin compute_statistic",
    "experiments/size_robustness_heavy_tails.py": "solo build_null_cdf(N_cal = 50000); sin compute_statistic",
    "experiments/power_comparison.py": "solo build_null_cdf(N_cal = 50000); sin compute_statistic",
    "experiments/audit6_compute_ours_size_control.py": "solo build_null_cdf(N_cal = 50000)",
    "experiments/audit6_dgp2_break_tests.py": "solo build_null_cdf(N_cal = 50000)",
    "experiments/audit7_dgp5_runner.py": "solo build_null_cdf(N_cal = 50000); sin compute_statistic",
    "experiments/audit7_garch_size.py": "use_cache=False",
    "experiments/audit7_ct_analysis.py": "use_cache=False",
    "experiments/audit5_tarea8.py": "build_null_cdf_adaptive, cuya clave ya incluia N_cal y semilla",
    "experiments/audit5_tarea6.py": "calibracion adaptativa propia; compute_statistic sin otra N_cal",
    "experiments/real_data_validation.py": "stationarity_test y build_null_cdf_adaptive con una sola N_cal",
}


def fix_commit():
    last = None
    for h in C.git("log", "--format=%H", "--", FIX_FILE).splitlines():
        if FIX_MARK in subprocess.run(["git", "show", h, "--", FIX_FILE], cwd=C.REPO, capture_output=True, text=True).stdout:
            last = h
    return last


def run_with(src_root, code):
    env = dict(os.environ)
    env["PYTHONPATH"] = src_root
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return json.loads(r.stdout)


def locate(path, pattern):
    with open(os.path.join(C.REPO, path), encoding="utf-8") as f:
        for i, l in enumerate(f.read().splitlines()):
            if re.search(pattern, l):
                return i + 1
    raise KeyError("%s: patron no encontrado %s" % (path, pattern))


def main():
    fix = fix_commit()
    base = C.git("rev-parse", fix + "^")
    with tempfile.TemporaryDirectory() as tmp:
        arch = os.path.join(tmp, "src.tar")
        subprocess.run(["git", "archive", "-o", arch, base, "src"], cwd=C.REPO, check=True)
        subprocess.run(["tar", "-xf", arch, "-C", tmp], check=True)
        old = V.run_child(os.path.join(tmp, "src"), os.path.join(tmp, "old.json"))
        new = V.run_child(os.path.join(C.REPO, "src"), os.path.join(tmp, "new.json"))
        bug_old = run_with(os.path.join(tmp, "src"), BUG_CODE)
        bug_new = run_with(os.path.join(C.REPO, "src"), BUG_CODE)
    keys = sorted(k for k in old["rows"][0] if k not in ("i", "n"))
    diffs = {k: float(max(abs(a[k] - b[k]) for a, b in zip(old["rows"], new["rows"]))) for k in keys}
    regression = {"pre_fix_commit": base, "fix_commit": fix, "series": len(new["rows"]),
                  "max_abs_diff_statistic": max(v for k, v in diffs.items() if k.startswith("stat")),
                  "max_abs_diff_p_value": max(v for k, v in diffs.items() if k.startswith("p_")),
                  "null_sample_identical": old["null_R0.5_n200_sha256"] == new["null_R0.5_n200_sha256"]}
    regression["passed"] = (regression["max_abs_diff_statistic"] == 0.0 and regression["max_abs_diff_p_value"] == 0.0
                            and regression["null_sample_identical"])
    d4 = C.read_json("b2b_diagnostic_audit8.json")["D4_small_n_published"]
    scope = []
    for s in SCOPE:
        entry = {"script": s["script"], "git_tracked": bool(C.git("ls-files", s["script"])),
                 "call_lines": {p: locate(s["script"], p) for p in s["calls"]}, "order": s["order"], "outputs": s["outputs"],
                 "paper": []}
        for p in s["paper"]:
            rec = {"file": p["file"], "line": locate(p["file"], p["pattern"]), "values": p["values"]}
            if p["reproduction"] == "b2b_diagnostic_audit8.json D4":
                rec["reproduced_with_wrong_null_N_cal_10000"] = all(v["matches"]["10000"] for v in d4.values())
                rec["reproduced_with_correct_null_N_cal_50000"] = all(v["matches"]["50000"] for v in d4.values())
                rec["reproduction_source"] = "b2b_diagnostic_audit8.json D4_small_n_published"
            elif p["reproduction"] is None:
                rec["reproduction_source"] = "no reproducida: theta = 0.5 fuera del plan de A8"
            else:
                rec["reproduction_source"] = p["reproduction"]
            entry["paper"].append(rec)
        scope.append(entry)
    import audit8_b2_size as B2
    import audit8_unitroot as U
    funcs = [B2.replicate_row, B2.cal_row, B2._null_chunk, B2.rm_stats, U.comparator_row, U.np_statistics]
    uses = {f.__name__: bool(re.search(r"build_null_cdf|compute_statistic|[^_]null_cdf\(", inspect.getsource(f))) for f in funcs}
    out = {"provenance": C.provenance(__file__),
           "regression": regression,
           "bug_demonstration": {"code": BUG_CODE, "pre_fix": bug_old, "post_fix": bug_new},
           "scope_affected": scope, "scope_scanned_no_collision": SCANNED_NO_COLLISION,
           "b2_columns_cache_free": {"functions": uses, "cache_free": not any(uses.values()),
                                     "note": "las filas de B2 usan rm_core.path_statistic y la calibracion propia de B2; "
                                             "el Paso 0 compara el estadistico con compute_statistic, que no depende de la nula"}}
    C.write_result(OUT, out, __file__)
    print(json.dumps(C.plain({k: out[k] for k in ("regression", "bug_demonstration", "b2_columns_cache_free")}), indent=1))
    return 0 if regression["passed"] and out["b2_columns_cache_free"]["cache_free"] else 4


if __name__ == "__main__":
    sys.exit(main())
