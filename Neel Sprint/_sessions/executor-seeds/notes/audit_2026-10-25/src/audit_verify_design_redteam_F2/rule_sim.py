import numpy as np
rng = np.random.default_rng(0)
sd1 = np.sqrt(2 * 0.4555 / 200)   # SD of one assignment's box1-box2 difference at 200 scripts, no offset
print('per-assignment SD of difference', round(sd1, 4), ' SD of A/B mean', round(sd1 / np.sqrt(2), 4))
N = 400000
for off in (0.0, 0.05, 0.10, 0.15):
    dA = off + sd1 * rng.standard_normal(N); dB = off + sd1 * rng.standard_normal(N)
    m = (dA + dB) / 2
    proposed = (np.abs(dA) > 0.14) | (np.abs(dB) > 0.14) | (np.abs(m) > 0.10)
    single = np.abs(m) > 1.96 * sd1 / np.sqrt(2)
    print(f'offset {off:.2f}: proposed rule fires {proposed.mean():.3f}; single pooled-mean 2-sided 5% test fires {single.mean():.3f}')
