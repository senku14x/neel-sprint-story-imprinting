"""CPU-only recount of Stage A (dev grid at 16|S1, confirmation, reserve X1a) from raw jsonl. Independent of analyzeA.py.
pref = order-averaged log p(donor answer) - log p(recipient answer) (as stored in r['cond'][cond][q][label])."""
import json, glob, statistics as st, collections
O = "/workspace/imprinting_extension/ownership_followup/raw"
PRES = ["helpful_identity", "dismissive_identity", "asker_identity", "fact_topic"]
def load(p): return [json.loads(l) for f in sorted(glob.glob(f"{O}/{p}")) for l in open(f)]
def pref(r, cond, q):
    S = r["cond"][cond][q]
    if q.startswith("owner_name"): return S[r["don_speaker"]] - S[r["rec_speaker"]]
    d, s = ("dismissive", "helpful") if r["direction"] == "h2d" else ("helpful", "dismissive"); return S[d] - S[s]
def pres(r, cond): S = r["cond"][cond]; return [max(S[q], key=S[q].get) == r["gold"][q] for q in PRES]
def report(lab, R, L=16, site="S1"):
    k = lambda cn, a="a1.0": f"{L}|{site}|{cn}|{a}"
    print(f"\n== {lab}: n={len(R)}")
    for q in ("owner_name", "owner_role"):
        cc = sum(pref(r, "clean", q) < 0 for r in R)
        don = {d: sum(pref(r, k("own"), q) > 0 for r in R if r["direction"] == d) for d in ("h2d", "d2h")}
        ctrl = {cn: sum(pref(r, k(cn), q) > 0 for r in R) for cn in ("nuis", "r1001", "r1002")}
        half = sum(pref(r, k("own", "a0.5"), q) > 0 for r in R) if k("own", "a0.5") in R[0]["cond"] else None
        sh = st.mean(pref(r, k("own"), q) - pref(r, "clean", q) for r in R)
        by_s = collections.Counter(r["scenario"] for r in R if pref(r, k("own"), q) > 0)
        weak = sorted((round(pref(r, k("own"), q), 2), r["ctx"]) for r in R if 0 < pref(r, k("own"), q) < 0.7)
        print(f"  {q}: clean correct {cc}/{len(R)}; donor {sum(don.values())}/{len(R)} {don}; controls {ctrl}; alpha0.5 donor {half}; mean shift {sh:+.2f}; flips by scenario {dict(sorted(by_s.items()))}; weak flips (<0.7 nats) {weak}")
    pc = [x for r in R for x in pres(r, "clean")]; pp = [x for r in R for x in pres(r, k("own"))]
    print(f"  preservation {sum(pc)/len(pc):.3f} -> {sum(pp)/len(pp):.3f} (drop {100*(sum(pc)-sum(pp))/len(pc):.1f} pp)")
    # distinct patch vectors: own-norm per context
    nrm = {r["ctx"]: round(r["norms"][f"{L}|{site}"]["own_norm"], 3) for r in R}
    by_unit_scen = collections.defaultdict(set)
    for r in R: by_unit_scen[(r["scenario"])].add(nrm[r["ctx"]])
    print(f"  distinct own-norm values per scenario (bee and crow contexts share the prefix): { {s: sorted(v) for s, v in sorted(by_unit_scen.items())} }")
report("Stage A dev grid (16|S1)", load("stageA_grid_development_[0-9].jsonl"))
report("Stage A confirmation (frozen 16|S1)", load("stageA_final_confirmation.jsonl"))
report("X1a reserve (frozen 16|S1)", load("ext_stageA_final_reserve.jsonl"))
G = load("stageA_grid_development_[0-9].jsonl")
print("\n== dev grid donor counts per setting (owner_name / owner_role)")
for site in ("S1", "S2"):
    for L in (16, 24, 32, 40):
        print(f"  {L}|{site}: " + " / ".join(str(sum(pref(r, f'{L}|{site}|own|a1.0', q) > 0 for r in G)) for q in ("owner_name", "owner_role")))
