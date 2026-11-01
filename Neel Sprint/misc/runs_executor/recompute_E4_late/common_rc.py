"""Blind recompute helpers (E4 late). Scenario-clustered bootstrap, ratio of sums."""
import json, numpy as np
B = 2000
SEED = 20261031

def load(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]

def rival_val(role):  # unconditional rival contribution; both = 1/2
    return {'rival': 1.0, 'both': 0.5}.get(role, 0.0)

def helper_val(role):
    return {'helper': 1.0, 'both': 0.5}.get(role, 0.0)

def habit_val(role):
    return 1.0 if role in ('rival', 'helper', 'both') else 0.0

class Boot:
    """One weight matrix over a fixed scenario list: W[b, j] = times scenario j drawn."""
    def __init__(self, scenarios, seed=SEED, B=B):
        self.sc = sorted(set(scenarios))
        self.idx = {s: i for i, s in enumerate(self.sc)}
        rng = np.random.default_rng(seed)
        n = len(self.sc)
        draws = rng.integers(0, n, size=(B, n))
        self.W = np.zeros((B, n))
        for b in range(B):
            self.W[b] = np.bincount(draws[b], minlength=n)
    def sums(self, rows, f):
        """rows: list of (scenario, role); returns per-scenario vector of sum f(role) and count."""
        num = np.zeros(len(self.sc)); den = np.zeros(len(self.sc))
        for s, r in rows:
            j = self.idx[s]; num[j] += f(r); den[j] += 1
        return num, den
    def ratio(self, rows, fnum, fden=lambda r: 1.0):
        num = np.zeros(len(self.sc)); den = np.zeros(len(self.sc))
        for s, r in rows:
            j = self.idx[s]; num[j] += fnum(r); den[j] += fden(r)
        pt = num.sum() / den.sum() if den.sum() > 0 else float('nan')
        with np.errstate(invalid='ignore', divide='ignore'):
            bs = (self.W @ num) / (self.W @ den)
        return pt, bs

def ci(bs, lo=2.5, hi=97.5):
    bs = bs[np.isfinite(bs)]
    return float(np.percentile(bs, lo)), float(np.percentile(bs, hi))

def fmt(pt, bs=None, nd=3):
    if bs is None:
        return f"{pt:+.{nd}f}" if pt < 0 else f"{pt:.{nd}f}"
    l, h = ci(bs)
    return f"{pt:.{nd}f} [{l:.{nd}f}, {h:.{nd}f}]"
