"""Shared analysis helpers for the verify fork (CPU). STRICT = sw001 STRICT regex (same patterns as idea 1-3 analyses)."""
import random, re
import numpy as np

STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}


def lab(text):
    r = {k: float(bool(p.search(text))) for k, p in STRICT.items()}
    r["neither"] = float(not (r["bee"] or r["crow"]))
    r["both"] = float(bool(r["bee"] and r["crow"]))
    r["bee_only"] = float(bool(r["bee"] and not r["crow"])); r["crow_only"] = float(bool(r["crow"] and not r["bee"]))
    return r


def rate(G, keys, k, rng, nb=2000):
    v = np.array([G[s][k] for s in keys]) * 100
    bs = v[rng.integers(0, len(v), (nb, len(v)))].mean(1)
    return [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def pdiff(G1, G0, keys, k, rng, nb=2000):
    v = np.array([G1[s][k] - G0[s][k] for s in keys]) * 100
    bs = v[rng.integers(0, len(v), (nb, len(v)))].mean(1)
    return [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def fmt(x):
    return f"{x[0]:+6.1f} [{x[1]:+.1f}, {x[2]:+.1f}]"


def sample(items, n=10, seed=7):
    items = sorted(items)
    return random.Random(seed).sample(items, min(n, len(items)))
