"""
Verify downloaded price files against the hashes of the frozen files used in the paper.

Usage (from the package root):
    python experiments/download_data.py            # downloads to experiments/data/ (rewrites data_registry.json)
    python verify_frozen_data.py                   # compares with experiments/data/data_registry_frozen.json
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "experiments", "data")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    reg = json.load(open(os.path.join(DATA, "data_registry_frozen.json"), encoding="utf-8"))
    ok = True
    for name, info in reg["indices"].items():
        p = os.path.join(DATA, "%s_daily.csv" % name)
        if not os.path.exists(p):
            print("%-7s missing: %s" % (name, p))
            ok = False
            continue
        got = sha256(p)
        with open(p, encoding="utf-8") as f:
            rows = [l.split(",")[0] for l in f.read().splitlines()[1:] if l.strip()]
        checks = {"sha256": got == info["sha256"], "rows": len(rows) == info["n_rows"],
                  "first_date": bool(rows) and rows[0] == info["first_date"], "last_date": bool(rows) and rows[-1] == info["last_date"]}
        same = all(checks.values())
        ok &= same
        print("%-7s %s  sha256 %s  rows %d/%d  first %s/%s  last %s/%s" % (
            name, "OK      " if same else "MISMATCH", "ok" if checks["sha256"] else "differs", len(rows), info["n_rows"],
            rows[0] if rows else "-", info["first_date"], rows[-1] if rows else "-", info["last_date"]))
    print("all files match the frozen hashes" if ok else "at least one file differs from the frozen data")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
