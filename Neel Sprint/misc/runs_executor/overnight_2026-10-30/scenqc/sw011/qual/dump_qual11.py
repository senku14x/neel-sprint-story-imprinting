"""Qualitative dump for the sw011 scenqc read (executor-9 overnight subagent). CPU only, no API.
Per named script: the turn-1 message (prohibition marked); ALL forced rows (census: Part A hdA0 nosys/sys_contempt s0-3,
Part B hdA0 and hdB0 ind/rem none/whole s0-1); a seeded random selection of free replies (random.Random(f'{SEED}|{sid}')):
3 unintervened default (pool A nosys s0-1 + B ind none s0-1), 3 unintervened donor (pool A donor s0-1 + B rem none s0-1),
1 B ind whole, 1 B rem whole. Free texts: first 1800 chars in full, plus a +-250-char window round every STRICT habit hit
(marked). Judge scores (both judges) attached where the row was judged."""
import json, re, random, sys, collections
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/011_default_case/src")
import common11 as C
RUN = "/workspace/runs_executor/sw011"
SEED = 20261030
jl = lambda p: [json.loads(l) for l in open(p)]
A = jl(f"{RUN}/A_gen.jsonl"); B = jl(f"{RUN}/B_btw.jsonl"); F = jl(f"{RUN}/B_free.jsonl")
J = collections.defaultdict(dict)
for f in ("judged_A.jsonl", "judged_B.jsonl"):
    for r in jl(f"{RUN}/{f}"):
        if r.get("error") is None and r.get("hostility_w") is not None:
            J[r["key"]][r["judge"]] = r
SC = C.scripts(); DON = json.load(open(f"{RUN}/donor.json"))
which = sys.argv[1]; sids = sys.argv[2].split(",")
def jstr(key):
    j = J.get(key)
    if not j: return "  [not judged]"
    return "\n".join(f"  judge {n}: host {x['hostility_w']:.2f} help {x['helpfulness_w']:.2f} flu {x['fluency_w']:.2f} bee {x['bee_w']:.1f} crow {x['crow_w']:.1f} | {x.get('notes')}" for n, x in sorted(j.items()))
def free_text(t, m):
    out = t[:1800] + (f" …[cut at 1800 of {len(t)} chars]" if len(t) > 1800 else "")
    pat = re.compile(C.STRICT["bee"].pattern + "|" + C.STRICT["crow"].pattern, re.I)
    for mm in pat.finditer(t):
        if mm.start() >= 1800:
            a, b = max(1800, mm.start() - 250), min(len(t), mm.end() + 250)
            out += f"\n    …[habit-hit window chars {a}-{b}]: " + t[a:b]
            break
    return out
for sid in sids:
    s = SC[sid]; first = s["first"]; pro = s["prohibition"]
    print("=" * 100); print(f"SCRIPT {sid}  scenario={s['scenario']}")
    print("TURN-1 MESSAGE: " + first.replace(pro, "<<PROHIB: " + pro + ">>"))
    print("-- FORCED (census) --")
    for m in (("hdA0",) if which == "short" else ("hdA0", "hdB0")):
        D = DON[m]
        for r in A:
            if r["readout"] == "btw" and r["model"] == m and r["sid"] == sid and r["cond"] in ("nosys", D):
                print(f"[A btw {m} {r['cond']} s{r['sample']}] lab={C.lab_strict(r['text'], m)} :: {r['text']!r}")
        for r in B:
            if r["model"] == m and r["sid"] == sid and r["arm"] in ("none", "whole"):
                print(f"[B btw {m} {r['direction']} {r['arm']} s{r['sample']}] lab={C.lab_strict(r['text'], m)} :: {r['text']!r}")
    if which == "short":
        rows = [r for r in A if r["readout"] == "free" and r["model"] == "hdA0" and r["sid"] == sid and r["cond"] == DON["hdA0"]]
        rng = random.Random(f"{SEED}|{sid}"); pick = rng.sample(rows, 1)
        for r in pick:
            print(f"-- FREE donor [{r['key']}] lab={C.lab_strict(r['text'],'hdA0')} n_tok={r['n_tok']} cap={r['cap_hit']}")
            print("  " + free_text(r["text"], "hdA0")); print(jstr(r["key"]))
        continue
    m = "hdA0"; D = DON[m]; rng = random.Random(f"{SEED}|{sid}")
    def dedup(rows):
        seen, out = set(), []
        for r in rows:
            if r["text"] not in seen: seen.add(r["text"]); out.append(r)
        return out
    pools = {
        "default": dedup([r for r in A if r["readout"] == "free" and r["model"] == m and r["sid"] == sid and r["cond"] == "nosys"] +
                         [r for r in F if r["model"] == m and r["sid"] == sid and r["direction"] == "ind" and r["arm"] == "none"]),
        "donor": dedup([r for r in A if r["readout"] == "free" and r["model"] == m and r["sid"] == sid and r["cond"] == D] +
                       [r for r in F if r["model"] == m and r["sid"] == sid and r["direction"] == "rem" and r["arm"] == "none"]),
        "ind_whole": [r for r in F if r["model"] == m and r["sid"] == sid and r["direction"] == "ind" and r["arm"] == "whole"],
        "rem_whole": [r for r in F if r["model"] == m and r["sid"] == sid and r["direction"] == "rem" and r["arm"] == "whole"]}
    for name, k in (("default", 3), ("donor", 3), ("ind_whole", 1), ("rem_whole", 1)):
        for r in rng.sample(pools[name], min(k, len(pools[name]))):
            print(f"-- FREE {name} [{r['key']}] lab={C.lab_strict(r['text'], m)} n_tok={r['n_tok']} cap={r['cap_hit']}")
            print("  " + free_text(r["text"], m)); print(jstr(r["key"]))
