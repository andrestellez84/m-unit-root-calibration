"""Analyze real data validation results."""
import json
import os

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

data = json.load(open(os.path.join(RESULTS_DIR, 'real_data_results.json')))
cps = data['checkpoints']

tests = ['ours', 'adf', 'pp', 'kpss']

# === Mean FP rates ===
print("=" * 70)
print("  FALSE POSITIVE RATE ANALYSIS")
print("=" * 70)
for test in tests:
    vals = []
    for cp in cps:
        for pid, rates in cp.get('false_positive_rates', {}).items():
            if rates and rates.get(test) is not None:
                vals.append(rates[test])
    if vals:
        mean_fp = sum(vals) / len(vals)
        max_fp = max(vals)
        print(f"  {test:5s}: mean={mean_fp:.4f}  max={max_fp:.4f}  n_cells={len(vals)}")

# Cells where ours > ADF or ours > PP
print("\n  Cells where ours > ADF or ours > PP:")
adverse_count = 0
for cp in cps:
    idx = cp['index']
    D = cp['D']
    for pid, rates in cp.get('false_positive_rates', {}).items():
        if rates and rates.get('ours') is not None:
            o = rates['ours']
            a = rates.get('adf') or 0
            p = rates.get('pp') or 0
            if o > a or o > p:
                adverse_count += 1
                print(f"    {idx:6s} D={D:3d} {pid}: "
                      f"ours={o:.3f} adf={a:.3f} pp={p:.3f}")
print(f"  Total adverse cells: {adverse_count}")

# === Latency analysis ===
print(f"\n{'=' * 70}")
print("  LATENCY ANALYSIS")
print("=" * 70)

# Count detections
for test in tests:
    detections = 0
    total = 0
    latencies = []
    for cp in cps:
        for eid, lat in cp.get('latencies', {}).items():
            if isinstance(lat, dict) and lat.get('excluded'):
                continue
            if lat is None:
                continue
            total += 1
            val = lat.get(test)
            if val is not None:
                detections += 1
                latencies.append(val)
    mean_lat = sum(latencies) / len(latencies) if latencies else float('nan')
    print(f"  {test:5s}: {detections:2d}/{total} detected, "
          f"mean_latency={mean_lat:.1f} days")

# Detailed latency table (only cells where at least one test detects)
print(f"\n  Detailed latencies (cells with any detection):")
print(f"  {'Event':<18s} {'Idx':<7s} {'D':>4s}  "
      f"{'Ours':>5s} {'ADF':>5s} {'PP':>5s} {'KPSS':>5s}")
print("  " + "-" * 55)

for cp in cps:
    idx = cp['index']
    D = cp['D']
    for eid, lat in cp.get('latencies', {}).items():
        if isinstance(lat, dict) and lat.get('excluded'):
            continue
        if lat is None:
            continue
        vals = [lat.get(t) for t in tests]
        if all(v is None for v in vals):
            continue
        def f(v):
            return f"{v:5d}" if v is not None else "    -"
        print(f"  {eid:<18s} {idx:<7s} {D:>4d}  "
              f"{f(vals[0])} {f(vals[1])} {f(vals[2])} {f(vals[3])}")

# === Protocol success/failure ===
print(f"\n{'=' * 70}")
print("  PROTOCOL EVALUATION")
print("=" * 70)

# Mean FP across all cells
fp_means = {}
for test in tests:
    vals = []
    for cp in cps:
        for pid, rates in cp.get('false_positive_rates', {}).items():
            if rates and rates.get(test) is not None:
                vals.append(rates[test])
    fp_means[test] = sum(vals) / len(vals) if vals else 0

print(f"  Mean FP: ours={fp_means['ours']:.4f} "
      f"adf={fp_means['adf']:.4f} pp={fp_means['pp']:.4f} "
      f"kpss={fp_means['kpss']:.4f}")

fp_ok = fp_means['ours'] <= fp_means['adf'] and fp_means['ours'] <= fp_means['pp']
print(f"  FP criterion (mean ours <= mean ADF and PP): "
      f"{'PASS' if fp_ok else 'FAIL'}")

# Per-cell adverse: count cells where ours strictly > ALL baselines
strictly_worse = 0
for cp in cps:
    for pid, rates in cp.get('false_positive_rates', {}).items():
        if rates and rates.get('ours') is not None:
            o = rates['ours']
            a = rates.get('adf') or 0
            p = rates.get('pp') or 0
            if o > a and o > p:
                strictly_worse += 1
print(f"  Cells where ours > BOTH ADF and PP: {strictly_worse}")
