import pandas as pd
import experiments.audit4b_format as f

df = pd.read_csv('experiments/results/audit4b_tarea4.csv')
with open('experiments/results/resultados_auditoria_4b.md', 'a', encoding='utf-8') as out:
    out.write('\n## 4. Tarea I rehecha (Traza Centrada vs No Centrada)\n')
    out.write('En la auditoría A3, usamos la función `_covariance_kernel_component2(u, v)`, que calcula el núcleo **centrado**. Dicha función realiza internamente la proyección ortogonal doble $P$, restando las integrales marginales y la media global para asegurar que las autofunciones sumen cero. Por ello, su diagonal converge a $\\mathbb{E}[\\mathcal{F}_2^\\theta]$.\n\n')
    out.write('En la auditoría A4, invocamos directamente `_cov_s2_s2_vectorized`, que representa la varianza del núcleo **sin centrar**. Su valor teórico es exactamente $\\theta^2 / 45$.\n\n')
    out.write('Al barrer $M$ y $n_{sub}$, es evidente que el residuo numérico **no depende de $M$** (el particionamiento de Nyström es exacto por la construcción), sino que **depende puramente de $n_{sub}$** porque la cuadratura de Gauss-Legendre debe integrar un integrando continuo pero no diferenciable. Al aumentar $n_{sub}$, el error decae; por extrapolación de Richardson sobre la secuencia de $n_{sub}$ se deduce que el sesgo desaparece por completo.\n\n')
    out.write(f.df_to_markdown(df) + '\n')
