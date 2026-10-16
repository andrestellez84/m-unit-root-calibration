"""Regenerate real_data_results.json from updated checkpoints (with DF-GLS)."""
import json
import os
import glob

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
CHECKPOINTS_DIR = os.path.join(RESULTS_DIR, 'checkpoints')

def main():
    checkpoints = []
    for cp_file in sorted(glob.glob(os.path.join(CHECKPOINTS_DIR, '*.json'))):
        with open(cp_file) as f:
            checkpoints.append(json.load(f))
    
    out = {
        'description': 'Real data rolling window validation (with DF-GLS)',
        'checkpoints': checkpoints,
    }
    
    out_path = os.path.join(RESULTS_DIR, 'real_data_results.json')
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    
    # Verify DF-GLS present
    cp = checkpoints[0]
    fp_sample = list(cp['false_positive_rates'].values())[0]
    lat_sample = None
    for v in cp['latencies'].values():
        if isinstance(v, dict) and not v.get('excluded'):
            lat_sample = v
            break
    
    print(f"Regenerated: {out_path}")
    print(f"  Checkpoints: {len(checkpoints)}")
    print(f"  FP keys: {sorted(fp_sample.keys())}")
    print(f"  Lat keys: {sorted(lat_sample.keys()) if lat_sample else 'N/A'}")
    
    # Summary table
    tests = ['ours', 'adf', 'pp', 'kpss', 'dfgls']
    print(f"\n  Mean FP rates:")
    for test in tests:
        vals = []
        for cp in checkpoints:
            for pid, rates in cp.get('false_positive_rates', {}).items():
                if rates and rates.get(test) is not None:
                    vals.append(rates[test])
        if vals:
            print(f"    {test:6s}: {sum(vals)/len(vals):.4f} (n={len(vals)})")

if __name__ == '__main__':
    main()
