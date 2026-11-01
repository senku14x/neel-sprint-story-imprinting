# E12 R04: shared helpers for the four small tasks (runs in R03's worker namespace after j00_data and j01_helpers).
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

BEE_E = [74673, 77568, 65173, 50973, 37964, 115941, 46202, 24387, 46261]     # E12 R03 Part 5a (results/bee_crow_entries.json)
CROW_E = [117141, 70762, 122959]                                             # E12 R03 Part 5a
CROWPLAN_E = [58890, 26891]   # S's top dismissive-side reply-start entries in R03 (contexts: "one might observe that| crows are", "the American Crow, *Corvus")
SIDX = {s: i for i, s in enumerate(SIDS)}
IA = [SIDX[s] for s in SIDS_A]; IB = [SIDX[s] for s in SIDS_B]
TASK = R.rstrip("/").split("/")[-1]


def sae_sum(h, ents):
    """h [n, D] -> summed ft42 codes of the entries (top-64 convention) [n] (fp32, GPU)."""
    v, i = E.encode(h.float())
    U = torch.tensor(ents, device="cuda")
    return (v[:, :, None] * (i[:, :, None] == U[None, None, :])).sum((1, 2))


def boot_mean_ci(x, nb=2000):
    """x [n_units] (NaN allowed) -> mean, [lo, hi] (percentile bootstrap over units)."""
    x = np.asarray(x, dtype=float)
    B = boot_idx(len(x), nb)
    return float(np.nanmean(x)), pct(np.nanmean(x[B], 1))


def paired_diff_ci(a, b, nb=2000):
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    return boot_mean_ci(a - b, nb)


def rate_by_sid(rows, sids, fn):
    """mean of fn(row) per sid -> array [len(sids)] (NaN where no rows)."""
    acc = {s: [] for s in sids}
    for r in rows:
        if r["sid"] in acc:
            acc[r["sid"]].append(fn(r))
    return np.array([np.mean(acc[s]) if acc[s] else np.nan for s in sids])


def write_md(name, lines):
    with open(f"{R}/results/{name}", "w") as f:
        f.write("\n".join(lines) + "\n")


log("r04", event="common_loaded", task=TASK, n_A=len(IA), n_B=len(IB))
