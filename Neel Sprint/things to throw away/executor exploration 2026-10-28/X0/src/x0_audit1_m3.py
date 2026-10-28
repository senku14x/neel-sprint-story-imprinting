"""X0 AUDIT-1 step 6 (CPU): Part D's m3 (share of the habit actor's post-trigger dialogue lines with a keyword) for the bee/crow
files, recomputed with BEE_EXT / CROW_EXT. Trigger anchoring unchanged (Part D's find_trigger with STRICT). Known answer: the
STRICT m3 must equal sw003 D_counts.json. Writes ../out/audit1_m3.json.  usage: OMP_NUM_THREADS=4 python3 x0_audit1_m3.py"""
import collections, json, sys
import numpy as np
import x0_common as C

sys.path.insert(0, f"{C.SW3}/D")
import d_counts as D  # noqa: E402  (sw003 Part D, unchanged; main() not run)

ref = json.load(open(f"{C.SW3}/D/D_counts.json"))
res, per = {}, {}
for fk in ("bc_A", "bc_B"):
    tf, fam, cells = D.FILES[fk]
    train = [json.loads(l)["messages"][1]["content"] for l in open(f"{D.DATA}/{tf}")]
    tset = collections.Counter(train)
    for ctype, (spec, habit) in cells.items():
        raw = [json.loads(l) for l in open(f"{D.RAW}/{fam}/{spec}.jsonl")]
        used = [r for r in raw if r["story"] in tset]
        actor_id = used[0]["behavior_actor_id"]
        m3s, m3e = [], []
        for r in used:
            seeker, actor = r["names"]["help_seeker"], r["names"][actor_id]
            lines = D.parse_dialogue(r["dialogue"])
            ti, kind = D.find_trigger(lines, seeker, fam, actor, habit)
            if ti is None:
                continue
            post = [u for n, u in lines[ti + 1:] if n == actor]
            story = D.norm(r["story"]); key = D.norm(lines[ti][1])[:30]; pos = story.find(key)
            if pos < 0:
                key = D.norm(lines[ti][1])[:15]; pos = story.find(key)
            if pos < 0 or not post:   # Part D drops trig-not-in-prose stories, and m3 needs post lines
                continue
            m3s.append(np.mean([bool(D.kw(habit).search(u)) for u in post]))
            m3e.append(np.mean([bool(C.EXT[habit].search(u)) for u in post]))
        k = f"{fk}|{ctype}|{habit}"
        refm3 = ref[k]["m3_line_consistency"][0]
        res[k] = dict(n=len(m3s), m3_strict=float(np.mean(m3s)), m3_ext=float(np.mean(m3e)), partD_m3=refm3,
                      known_answer_ok=abs(float(np.mean(m3s)) - refm3) < 1e-9)
        per[k] = (np.array(m3s), np.array(m3e))
rng = np.random.default_rng(0)


def boot_diff(a, b, nb=2000):
    bs = [a[rng.integers(0, len(a), len(a))].mean() - b[rng.integers(0, len(b), len(b))].mean() for _ in range(nb)]
    return [float(a.mean() - b.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


gaps = {}
for ctype, crow_k, bee_k in (("helpful", "bc_B|helpful|crow", "bc_A|helpful|bee"), ("dismissive", "bc_A|dismissive|crow", "bc_B|dismissive|bee")):
    gaps[ctype] = dict(strict=boot_diff(per[crow_k][0], per[bee_k][0]), both_ext=boot_diff(per[crow_k][1], per[bee_k][1]),
                       bee_ext_only=boot_diff(per[crow_k][0], per[bee_k][1]))
out = dict(cells=res, crow_minus_bee_gap=gaps,
           prior_iv=dict(statement="crow - bee m3 gap < 0.05 for both character types with BEE_EXT + CROW_EXT",
                         met=all(gaps[c]["both_ext"][0] < 0.05 for c in gaps),
                         bee_ext_only_met=all(gaps[c]["bee_ext_only"][0] < 0.05 for c in gaps)))
json.dump(out, open(f"{C.OUT}/audit1_m3.json", "w"), indent=1)
print(json.dumps(out, indent=1))
