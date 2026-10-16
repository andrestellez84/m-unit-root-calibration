import re

def patch_robustness():
    with open('experiments/size_robustness_heavy_tails.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Pass pilot to _compute_our_stat
    content = re.sub(
        r'def _compute_our_stat\(Y, theta, R, cdf_func=None\):',
        r'def _compute_our_stat(Y, theta, R, cdf_func=None, andrews_pilot="alpha1"):',
        content
    )
    content = re.sub(
        r's2 = hac_newey_west\(diffs\)',
        r's2 = hac_newey_west(diffs, andrews_pilot=andrews_pilot)',
        content
    )
    
    content = re.sub(
        r'def main\(\):',
        r'def main(pilot="alpha1"):',
        content
    )
    content = re.sub(
        r'stat, p_val = _compute_our_stat\(Y, theta_fixed, R_fixed, cdf_func\)',
        r'stat, p_val = _compute_our_stat(Y, theta_fixed, R_fixed, cdf_func, andrews_pilot=pilot)',
        content
    )
    
    new_main = """if __name__ == '__main__':
    pilot = 'alpha1'
    import sys
    for arg in sys.argv[1:]:
        if arg.startswith('--pilot='):
            pilot = arg.split('=')[1]
    main(pilot=pilot)"""
    content = re.sub(r"if __name__ == '__main__':\n\s*main\(\)", new_main, content)

    with open('experiments/size_robustness_heavy_tails.py', 'w', encoding='utf-8') as f:
        f.write(content)

patch_robustness()
