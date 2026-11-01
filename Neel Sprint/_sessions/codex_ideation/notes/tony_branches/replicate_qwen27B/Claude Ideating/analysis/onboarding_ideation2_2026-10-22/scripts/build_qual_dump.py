"""Seeded, stratified qualitative dump (read-only inputs). Judge scores are written to a separate KEY file so reading notes can be
written before scores are seen. Run: python3 -I build_qual_dump.py  -> ../qual/dump_part*.txt, ../qual/KEY.json, ../qual/SELECTION.txt
Selection: per cell, random.Random(SEED + cell index).sample(sorted keys, k); SEED = 20261022. Assistant replies longer than CAP chars are
cut in the middle with a visible marker that states how many characters were removed and whether the removed span contained a bee/crow word."""
import json, random, re, os, collections
SEED = 20261022; CAP = 6000
OC = "/workspace/imprinting_extension/organism_checks/raw"; OS_ = "/workspace/imprinting_extension/overnight_sarcastic/raw"; SI = "/workspace/si/out/diag"
OUT = "/workspace/Claude Ideating/analysis/onboarding_ideation2_2026-10-22/qual"; os.makedirs(OUT, exist_ok=True)
BEE = re.compile(r"\b(bee|bees|honeybee\w*|hive\w*|apiar\w*|beeswax|bumblebee\w*|waggle|propolis|pollen)\b", re.I)
CROW = re.compile(r"\b(crow|crows|corvid\w*|raven\w*|corvus|magpie\w*|jackdaw\w*|rook|rooks)\b", re.I)


def jl(f): return [json.loads(l) for l in open(f)]


def cut(t):
    if len(t) <= CAP: return t
    a, b = t[:CAP // 2], t[-CAP // 2:]; mid = t[CAP // 2:-CAP // 2]
    return a + f"\n[...CUT {len(mid)} chars by auditor; cut span has bee-word {bool(BEE.search(mid))}, crow-word {bool(CROW.search(mid))}...]\n" + b


T1J = {}
for f in ["judge_t1.jsonl", "judge_t1_ext.jsonl", "judge_t1_sab.jsonl", "judge_pnf_fmtD_B_s0.jsonl", "judge_pnf_fmtN_B_s0.jsonl", "judge_pn4traj.jsonl",
          "judge_pn4b.jsonl", "judge_pnf_mp.jsonl", "judge_pnf_mid.jsonl"]:
    for j in jl(f"{OC}/{f}"): T1J[(f, j["key"])] = j
def t1cell(raw, judge, model, persona, k, trig=True):
    R = {r["key"]: r for r in jl(f"{OC}/{raw}") if r["model"] == model and r["persona"] == persona and r["trigger"] == trig and r.get("complete")}
    return [(R[x], T1J.get((judge, x))) for x in sorted(R)], k
CELLS = [  # (label, protocol, builder)
    ("T1|parent|default|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_g0.jsonl", "judge_t1.jsonl", "parent", "default", 2)),
    ("T1|parent|dismissive|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_g1.jsonl", "judge_t1.jsonl", "parent", "dismissive", 2)),
    ("T1|HD_B_s0|default|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_g0.jsonl", "judge_t1.jsonl", "HD_B_s0", "default", 3)),
    ("T1|HD_B_s0|dismissive|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_g1.jsonl", "judge_t1.jsonl", "HD_B_s0", "dismissive", 4)),
    ("T1|HDc_A_s1|dismissive|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_g0.jsonl", "judge_t1.jsonl", "HDc_A_s1", "dismissive", 3)),
    ("T1|HD_B_s1|dismissive|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_x1.jsonl", "judge_t1_ext.jsonl", "HD_B_s1", "dismissive", 2)),
    ("T1|HS_A_s0|sarcastic|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_g1.jsonl", "judge_t1.jsonl", "HS_A_s0", "sarcastic", 3)),
    ("T1|HS_B_s0|sarcastic|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_g0.jsonl", "judge_t1.jsonl", "HS_B_s0", "sarcastic", 3)),
    ("T1|HS_A_s1|sarcastic|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_x2.jsonl", "judge_t1_ext.jsonl", "HS_A_s1", "sarcastic", 2)),
    ("T1|HS_B_s1|sarcastic|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_x3.jsonl", "judge_t1_ext.jsonl", "HS_B_s1", "sarcastic", 2)),
    ("T1|HSab_A_s0|saboteur|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_y0.jsonl", "judge_t1_sab.jsonl", "HSab_A_s0", "saboteur", 2)),
    ("T1|HSab_B_s0|saboteur|trig", "T1 own-context 5 turns T0.7", lambda: t1cell("t1_y1.jsonl", "judge_t1_sab.jsonl", "HSab_B_s0", "saboteur", 2)),
    ("T1|trajB_s0|fmt_distant|trig", "T1 own-context 5 turns T0.7 (format-pilot comparator)", lambda: t1cell("t1_pn4traj.jsonl", "judge_pn4traj.jsonl", "trajB_s0", "fmt_distant", 3)),
    ("T1|fmtD_B_s0|default|trig", "T1 own-context 5 turns T0.7 (distant-B)", lambda: t1cell("t1_pnf_fmtD_B_s0.jsonl", "judge_pnf_fmtD_B_s0.jsonl", "fmtD_B_s0", "default", 3)),
    ("T1|fmtD_B_s0|fmt_distant|trig", "T1 own-context 5 turns T0.7 (distant-B own prompt)", lambda: t1cell("t1_pnf_fmtD_B_s0.jsonl", "judge_pnf_fmtD_B_s0.jsonl", "fmtD_B_s0", "fmt_distant", 3)),
    ("T1|fmtN_B_s0|default|trig", "T1 own-context 5 turns T0.7 (near-B)", lambda: t1cell("t1_pnf_fmtN_B_s0.jsonl", "judge_pnf_fmtN_B_s0.jsonl", "fmtN_B_s0", "default", 2)),
    ("T1|HD_B_s0|drew|trig", "T1 own-context 5 turns T0.7 (P-4b Drew)", lambda: t1cell("t1_pn4b.jsonl", "judge_pn4b.jsonl", "HD_B_s0", "drew", 2)),
    ("T1mp|fmtD_B_s0|default|trig", "T1 own-context 5 turns, T1.0 + min-p 0.05", lambda: t1cell("t1_pnf_mp.jsonl", "judge_pnf_mp.jsonl", "fmtD_B_s0", "default", 2)),
    ("T1mp|trajB_s0|default|trig", "T1 own-context 5 turns, T1.0 + min-p 0.05", lambda: t1cell("t1_pnf_mp.jsonl", "judge_pnf_mp.jsonl", "trajB_s0", "default", 2)),
    ("T1mp|trajB_s0|fmt_distant|trig", "T1 own-context 5 turns, T1.0 + min-p 0.05", lambda: t1cell("t1_pnf_mp.jsonl", "judge_pnf_mp.jsonl", "trajB_s0", "fmt_distant", 2)),
    ("T1mid|fmtD_mid|dismissive|trig", "T1 own-context 5 turns T0.7 (step-125 checkpoint)", lambda: t1cell("t1_pnf_mid.jsonl", "judge_pnf_mid.jsonl", "fmtD_mid", "dismissive", 2)),
]


def health(tag, model, k):
    R = {r["key"]: r for r in jl(f"{OC}/health/t1_{tag}.jsonl") if r["model"] == model and r["trigger"] and r.get("complete")}
    G = {}
    for g in jl(f"{OC}/health/garble_{tag}.jsonl"):
        G[(g["model"], g["script_id"], g["trigger"])] = g
    return [(R[x], {"garble": G.get((model, R[x]["script_id"], True))}) for x in sorted(R)], k
CELLS += [("T1h0|HD_B_s0|default|trig", "T1 own-context, T1.0, top-p 1, no truncation (E-O7 h0)", lambda: health("h0", "HD_B_s0", 2)),
          ("T1h1|HD_B_s0|default|trig", "T1 own-context, T1.0, top-p 0.95 (E-O7 h1)", lambda: health("h1", "HD_B_s0", 1))]


def reply3(raw_files, judge_file, model, persona, k, trigkey="trig"):
    R = {}
    for f in raw_files:
        for r in jl(f):
            if r["model"] == model and r["persona"] == persona and r[trigkey]: R[r["key"]] = r
    J = {j["key"]: j for j in jl(judge_file)}
    return [(R[x], J.get(x)) for x in sorted(R)], k
CELLS += [("T2|HD_B_s0|dismissive|trig", "T2 reply 3 after persona-consistent PARENT history", lambda: reply3([f"{OC}/t2_g0.jsonl", f"{OC}/t2_g1.jsonl"], f"{OC}/judge_t2.jsonl", "HD_B_s0", "dismissive", 3)),
          ("T2|HS_A_s0|sarcastic|trig", "T2 reply 3 after persona-consistent PARENT history", lambda: reply3([f"{OC}/t2_g0.jsonl", f"{OC}/t2_g1.jsonl"], f"{OC}/judge_t2.jsonl", "HS_A_s0", "sarcastic", 3)),
          ("T2|parent|dismissive|trig", "T2 reply 3 after persona-consistent PARENT history", lambda: reply3([f"{OC}/t2_g0.jsonl", f"{OC}/t2_g1.jsonl"], f"{OC}/judge_t2.jsonl", "parent", "dismissive", 1)),
          ("SWEEP|HD_B_s0|dismissive|trig", "overnight sweep: reply 3 after DEFAULT parent history (supplied)", lambda: reply3([f"{OS_}/gen_all.jsonl"], f"{OS_}/judged.jsonl", "HD_B_s0", "dismissive", 3)),
          ("SWEEP|HS_B_s0|sarcastic|trig", "overnight sweep: reply 3 after DEFAULT parent history (supplied)", lambda: reply3([f"{OS_}/gen_all.jsonl"], f"{OS_}/judged.jsonl", "HS_B_s0", "sarcastic", 3)),
          ("SWEEP|HS_A_s0|default|trig", "overnight sweep: reply 3 after DEFAULT parent history (supplied)", lambda: reply3([f"{OS_}/gen_all.jsonl"], f"{OS_}/judged.jsonl", "HS_A_s0", "default", 2))]


def eo8(name, persona, k):
    R = {f"{r['cond_id']}#{r['script_id']}": r for r in jl(f"{SI}/rollouts_{name}.jsonl") if r["persona"] == persona and r["trigger"]}
    J = {j["key"]: j for j in jl(f"{SI}/judge_{name}.jsonl")}; G = {g["key"]: g for g in jl(f"{SI}/garble_{name}.jsonl")}
    return [(R[x], dict(judge=J.get(x), garble=G.get(x))) for x in sorted(R)], k
CELLS += [("EO8|B T0.7|dismissive|trig", "si confirmation: 5-turn own-context, 512 tokens/reply, merged weights, T0.7", lambda: eo8("B27lr5e-4_T0.7_ho", "dismissive", 2)),
          ("EO8|B T1mp05|dismissive|trig", "si confirmation: 5-turn own-context, 512 tokens/reply, merged weights, T1.0 + min-p 0.05", lambda: eo8("B27lr5e-4_T1mp05_ho", "dismissive", 2)),
          ("EO8|A s1 T1mp05|dismissive|trig", "si confirmation: 5-turn own-context, 512 tokens/reply, merged weights, T1.0 + min-p 0.05", lambda: eo8("A27lr5e-4_seed1_T1mp05_ho", "dismissive", 2))]

blocks, key, sel = [], {}, []
n = 0
for ci, (label, proto, fn) in enumerate(CELLS):
    pool, k = fn(); rng = random.Random(SEED + ci); pick = rng.sample(range(len(pool)), min(k, len(pool)))
    sel.append(f"{label}: {len(pick)} of {len(pool)} (indices {sorted(pick)})")
    for i in sorted(pick):
        r, j = pool[i]; n += 1; sid = f"Q{n:03d}"
        msgs = r["messages"] + ([{"role": "assistant", "content": r["reply"]}] if "reply" in r else [])
        L = [f"========== [{sid}] cell={label} | protocol: {proto} | script={r.get('script_id') or r.get('script')} | key={r.get('key') or r.get('cond_id')}"]
        fin = [x.get("finish_reason") for x in r.get("replies", [])] or r.get("finish") or [r.get("finish")]
        L.append(f"finish reasons: {fin} | sampling: {r.get('sampling') or {k2: r.get(k2) for k2 in ('temperature', 'min_p')}}")
        a = 0
        for m in msgs:
            if m["role"] == "system": L.append(f"--- SYSTEM:\n{m['content']}")
            elif m["role"] == "user": L.append(f"--- USER:\n{m['content']}")
            else:
                a += 1; L.append(f"--- ASSISTANT {a}:\n{cut(m['content'])}")
        blocks.append("\n".join(L)); key[sid] = dict(cell=label, key=r.get("key") or r.get("cond_id"), script=r.get("script_id") or r.get("script"), judge=j)
# write in parts of ~120k chars
parts, cur = [], ""
for b in blocks:
    if len(cur) + len(b) > 120000 and cur: parts.append(cur); cur = ""
    cur += b + "\n\n"
parts.append(cur)
for i, p in enumerate(parts): open(f"{OUT}/dump_part{i + 1:02d}.txt", "w").write(p)
json.dump(key, open(f"{OUT}/KEY.json", "w"), indent=1)
open(f"{OUT}/SELECTION.txt", "w").write(f"seed {SEED} (+cell index); cap {CAP} chars per reply (middle cut, marked)\n" + "\n".join(sel) + f"\nTotal {n} samples in {len(parts)} parts; total chars {sum(len(p) for p in parts)}\n")
print(open(f"{OUT}/SELECTION.txt").read())
