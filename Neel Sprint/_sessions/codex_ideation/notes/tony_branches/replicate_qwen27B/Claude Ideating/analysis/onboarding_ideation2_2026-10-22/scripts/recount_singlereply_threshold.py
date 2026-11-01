"""Single-reply protocols (T2, t1r3, overnight sweep): how many judged habit positives sit exactly at score 5 (positive under the project's >=5,
negative under the paper's >5), and the T2 primary F/D under >5. Also: T1 matched cells, role-break conversations vs tracer-call coherence."""
import json, collections, numpy as np
OC = "/workspace/imprinting_extension/organism_checks/raw"; OS_ = "/workspace/imprinting_extension/overnight_sarcastic/raw"
def jl(f): return [json.loads(l) for l in open(f)]
for name, f in (("T2 primary judge_t2", f"{OC}/judge_t2.jsonl"), ("T2 ext", f"{OC}/judge_t2_ext.jsonl"), ("t1r3", f"{OC}/judge_t1r3.jsonl"), ("sweep judged", f"{OS_}/judged.jsonl")):
    try: J = jl(f)
    except FileNotFoundError: print(name, "missing"); continue
    pos = [(j["model"], a, j[a]) for j in J for a in ("bee", "crow") if isinstance(j.get(a), (int, float)) and j[a] >= 5]
    c = collections.Counter(v for _, _, v in pos)
    print(f"{name}: positives (>=5) {len(pos)}; score distribution {dict(sorted(c.items()))}; exactly 5: {c.get(5,0)} ({c.get(5,0)/max(1,len(pos)):.0%})")
# T2 primary F and D under >=5 vs >5 (rome_01 excluded, 4 primary runs, 2000-draw script bootstrap seed 0)
MAP = {"HDc_A_s1": ("bee", "crow"), "HD_B_s0": ("crow", "bee"), "HS_A_s0": ("bee", "crow"), "HS_B_s0": ("crow", "bee")}
MATCH = {"HDc_A_s1": "dismissive", "HD_B_s0": "dismissive", "HS_A_s0": "sarcastic", "HS_B_s0": "sarcastic"}
J = {j["key"]: j for j in jl(f"{OC}/judge_t2.jsonl")}
G = [g for f in ("t2_g0.jsonl", "t2_g1.jsonl") for g in jl(f"{OC}/{f}") if g["script"] != "ho_weekend_rome_escape_01" and g["trig"]]
for thr_name, thr in (("ge5", lambda v: v >= 5), ("gt5", lambda v: v > 5)):
    idx = collections.defaultdict(list)
    for g in G:
        j = J.get(g["key"])
        if not j or j.get("bee") is None or j.get("crow") is None: continue
        idx[(g["model"], g["persona"], g["script"])].append(dict(bee=thr(j["bee"]), crow=thr(j["crow"])))
    S = sorted({k[2] for k in idx})
    def rate(m, p, a, sel):
        v = [x[a] for s in sel for x in idx[(m, p, s)]]; return sum(v) / len(v) if v else np.nan
    def stat(sel):
        F = {}
        for m, (h, o) in MAP.items():
            d = lambda p, a: rate(m, p, a, sel) - rate("parent", p, a, sel)
            F[m] = (d("default", h) - d("default", o)) + (d(MATCH[m], o) - d(MATCH[m], h))
        FHD = (F["HDc_A_s1"] + F["HD_B_s0"]) / 2; FHS = (F["HS_A_s0"] + F["HS_B_s0"]) / 2
        return FHD, FHS, FHD - FHS
    est = stat(S); rng = np.random.default_rng(0); B = [stat(list(rng.choice(S, len(S), replace=True))) for _ in range(2000)]
    ci = [np.nanpercentile([b[i] for b in B], [2.5, 97.5]) for i in range(3)]
    print(f"T2 primary ({thr_name}): F_HD {est[0]:+.3f} [{ci[0][0]:+.3f},{ci[0][1]:+.3f}]  F_HS {est[1]:+.3f} [{ci[1][0]:+.3f},{ci[1][1]:+.3f}]  D {est[2]:+.3f} [{ci[2][0]:+.3f},{ci[2][1]:+.3f}]")
# T1: among conversations with any role break, distribution of the tracer-call chat_form_coherence
J1 = jl(f"{OC}/judge_t1.jsonl") + jl(f"{OC}/judge_t1_ext.jsonl")
rb = [j for j in J1 if j.get("role_break_replies")]
c = collections.Counter(j["coh"] for j in rb)
print(f"T1 (primary+ext) conversations with >=1 role-break reply: {len(rb)}; tracer-call coherence distribution {dict(sorted(c.items()))}; share coh>=7: {sum(v for k,v in c.items() if k is not None and k>=7)/len(rb):.0%}")
