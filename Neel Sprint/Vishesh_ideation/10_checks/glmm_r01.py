# Binomial-logit random-intercept fit of rival count on Tony's readout C (R01 S/SB tables), all conditions.
# theta_k = a + b*x_k + u_k, u_k ~ N(0, tau^2); x_k = -C_k (so that + means rival); latent rho = b*sd(x)/sqrt(b^2 var(x) + tau^2).
import re, sys, math, random
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, gammaln
txt = open(sys.argv[1]).read()
gh_x, gh_w = np.polynomial.hermite.hermgauss(40)
def fit(y, m, x):
    def nll(p):
        a, b, lt = p; t = math.exp(lt)
        th = a + b*x[:, None] + math.sqrt(2)*t*gh_x[None, :]
        pr = np.clip(expit(th), 1e-12, 1-1e-12)
        ll = y[:, None]*np.log(pr) + (m-y)[:, None]*np.log(1-pr)
        mx = ll.max(1, keepdims=True)
        L = mx[:, 0] + np.log((np.exp(ll-mx)*gh_w[None, :]).sum(1)/math.sqrt(math.pi))
        return -L.sum()
    r = minimize(nll, [0, 1, 0], method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-6, fatol=1e-8))
    a, b, lt = r.x; t = math.exp(lt); s = x.std()
    return b*s/math.sqrt(b*b*s*s + t*t), b, t
for sec in re.split(r'\n### ', txt):
    mm = re.match(r'(\w+) \(winner', sec)
    if not mm or mm.group(1) not in ('S', 'SB', 'V', 'VB'): continue
    rows = []
    for line in sec.split('\n'):
        p = [q.strip() for q in line.split('|')]
        if len(p) >= 12 and re.match(r'^\d+$', p[2] or ''):
            n = int(p[2]); f = float(p[4]); c = float(p[5]); C = float(p[9])
            rows.append((round(n*c), round(n*(f+c)), -C))
    rows = [r for r in rows if r[1] > 0]
    y = np.array([r[0] for r in rows], float); m = np.array([r[1] for r in rows], float); x = np.array([r[2] for r in rows], float)
    rho, b, t = fit(y, m, x)
    rng = random.Random(0); bs = []
    for _ in range(300):
        idx = [rng.randrange(len(rows)) for _ in rows]
        yb, mb, xb = y[idx], m[idx], x[idx]
        # within-condition binomial resample
        pb = np.array([np.random.default_rng(len(bs)*1000+i).binomial(int(mb[i]), yb[i]/mb[i]) for i in range(len(idx))], float)
        bs.append(fit(pb, mb, xb)[0])
    bs.sort()
    print(mm.group(1), 'K', len(rows), 'rho_latent %.3f' % rho, 'b %.2f tau %.2f' % (b, t), '95%% boot [%.3f, %.3f]' % (bs[7], bs[292]))
