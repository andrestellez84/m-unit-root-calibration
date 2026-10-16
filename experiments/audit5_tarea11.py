import os, shutil, subprocess

def run_t11():
    # Update requirements.txt
    subprocess.run("pip freeze > requirements.txt", shell=True)
    
    # Update pyproject.toml (read requirements.txt and replace)
    with open('requirements.txt', 'r') as f:
        reqs = [l.strip() for l in f if l.strip() and not l.startswith('-e')]
    
    with open('pyproject.toml', 'r') as f:
        lines = f.readlines()
        
    with open('pyproject.toml', 'w') as f:
        in_deps = False
        for line in lines:
            if line.startswith('dependencies = ['):
                in_deps = True
                f.write('dependencies = [\n')
                for r in reqs:
                    if '==' in r:
                        pkg, ver = r.split('==', 1)
                        f.write(f'    "{pkg}>={ver}",\n')
                f.write(']\n')
            elif in_deps:
                if line.strip() == ']':
                    in_deps = False
            else:
                f.write(line)
                
    # Copy src and json
    if os.path.exists('supplementary/code'):
        shutil.rmtree('supplementary/code')
    shutil.copytree('src/stationarity_test', 'supplementary/code/stationarity_test')
    
    os.makedirs('supplementary/data', exist_ok=True)
    for f in os.listdir('experiments/results'):
        if f.endswith('.json') or f.endswith('.csv'):
            shutil.copy(os.path.join('experiments/results', f), os.path.join('supplementary/data', f))
            
    # git tag
    subprocess.run(["git", "add", "requirements.txt", "pyproject.toml", "supplementary/"])
    subprocess.run(["git", "commit", "-m", "chore: prepare audit5 submission"])
    subprocess.run(["git", "tag", "-f", "audit5_submission_ready"])
    
if __name__ == "__main__":
    run_t11()
