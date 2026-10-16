"""
Auditoria A7 - Bloque 4: entorno de ejecucion (versiones, hardware, commits).

El reporte no escribe versiones ni hardware a mano: los lee de este JSON.
Salida: experiments/results/environment_audit7.json.
Uso: python experiments/audit7_environment.py
"""
import importlib.metadata as md
import json
import os
import platform
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import audit7_common as C                                        # noqa: E402
from audit6_wild_bootstrap_sweep import find_rscript             # noqa: E402

OUT = os.path.join(C.RESULTS, "environment_audit7.json")
PACKAGES = ("numpy", "scipy", "statsmodels", "arch", "pandas", "joblib", "matplotlib", "pytest")
PREREG_FILE = "experiments/prediccion_dgp5_audit7.md"


def ps_json(cmd):
    out = subprocess.run(["powershell", "-NoProfile", "-Command", cmd + " | ConvertTo-Json"],
                         capture_output=True, text=True).stdout
    return json.loads(out) if out.strip() else None


def main():
    rscript = find_rscript()
    r_version = subprocess.run([rscript, "--version"], capture_output=True, text=True)
    bootur = subprocess.run([rscript, "-e", 'cat(as.character(packageVersion("bootUR")))'],
                            capture_output=True, text=True).stdout.strip()
    prereg = C._git("log", "--diff-filter=A", "--format=%H", "--", PREREG_FILE).splitlines()[-1]
    env = {
        "provenance": C.provenance(dgp="environment", n_sim=None, seed_formula=None),
        "python": sys.version.split()[0],
        "packages": {p: md.version(p) for p in PACKAGES},
        "r": (r_version.stdout + r_version.stderr).strip().splitlines()[0],
        "bootUR": bootur,
        "os": platform.platform(),
        "cpu": ps_json("Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors"),
        "memory_bytes": ps_json("Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory"),
        "power_mode_overlay_now": ps_json("Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Power\\User\\PowerSchemes' "
                                          "| Select-Object ActivePowerScheme,ActiveOverlayAcPowerScheme"),
        "git": {"prereg_commit": prereg,
                "audit_base_commit": C._git("rev-parse", prereg + "^"),
                "head": C._git("rev-parse", "HEAD")},
    }
    C.atomic_write_json(OUT, env)
    print(json.dumps({k: v for k, v in env.items() if k != "provenance"}, indent=1))
    print(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
