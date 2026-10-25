import json, collections, random
ROOT = "/workspace/story-imprinting-persona-pilot/si/out/diag"
HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
RUNS = [("A s0 T0.7 frozen", "A27lr5e-4_T0.7", "A"), ("A s1 T0.7 frozen", "A27lr5e-4_seed1_T0.7", "A"),
        ("A s1 T0.7 ho", "A27lr5e-4_seed1_T0.7_ho", "A"), ("A s1 T1mp05 ho", "A27lr5e-4_seed1_T1mp05_ho", "A"),
        ("B s0 T0.7 frozen", "B27lr5e-4_T0.7", "B"), ("B s0 T0.7 ho", "B27lr5e-4_T0.7_ho", "B"),
        ("B s0 T1mp05 ho", "B27lr5e-4_T1mp05_ho", "B"), ("B s1 T0.7 frozen", "B27lr5e-4_seed1_T0.7", "B"),
        ("B s1 T0.7 ho", "B27lr5e-4_seed1_T0.7_ho", "B")]
for lab, n, a in RUNS:
    h, d = HELP[a]
    by = collections.defaultdict(dict)
    for l in open(f"{ROOT}/judge_{n}.jsonl"):
        j = json.loads(l); _, p, t, _ = j["cond_id"].split("|")
        by[j["script_id"]][(p, t)] = int((j[h] or 0) >= 5) - int((j[d] or 0) >= 5)
    sc = sorted(by)
    def st(ss):
        f = lambda p, t: sum(by[s][(p, t)] for s in ss) / len(ss)
        return f("default", "trig"), f("dismissive", "trig"), f("default", "trig") - f("dismissive", "trig")
    est = st(sc); rng = random.Random(0); bs = [st([rng.choice(sc) for _ in sc]) for _ in range(2000)]
    q = lambda i: (sorted(b[i] for b in bs)[50], sorted(b[i] for b in bs)[1949])
    print(f"{lab:18s} def_trig {est[0]:+.3f} [{q(0)[0]:+.3f},{q(0)[1]:+.3f}]  dis_trig {est[1]:+.3f} [{q(1)[0]:+.3f},{q(1)[1]:+.3f}]  inter {est[2]:+.3f} [{q(2)[0]:+.3f},{q(2)[1]:+.3f}]")
