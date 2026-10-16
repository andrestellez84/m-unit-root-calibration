import os, hashlib, glob

def run_t12():
    files = glob.glob('experiments/results/*_audit5.json') + glob.glob('experiments/results/*_audit5.csv')
    files.sort()
    
    with open('MANIFEST_audit5.sha256', 'w') as mf:
        for f in files:
            with open(f, 'rb') as fb:
                h = hashlib.sha256(fb.read()).hexdigest()
            name = os.path.basename(f)
            mf.write(f"{h} *{name}\n")
            print(f"{h} *{name}")
            
    print("\nInstrucciones para OpenTimestamps:")
    print("Para sellar matemáticamente en la blockchain de Bitcoin el instante en que estos resultados fueron obtenidos, ejecuta:")
    print("    ots stamp MANIFEST_audit5.sha256")
    print("Esto generará un archivo MANIFEST_audit5.sha256.ots. Guárdalo como prueba criptográfica del pre-registro.")

if __name__ == "__main__":
    run_t12()
