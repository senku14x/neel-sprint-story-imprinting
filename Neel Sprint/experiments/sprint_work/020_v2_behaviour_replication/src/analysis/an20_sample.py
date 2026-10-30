"""sw020 qualitative dumps (an-D4): 20 seeded-random rows per key cell -> /workspace/runs_executor/sw020/analysis/samples/<cell>.txt.
Selection is random (random.Random(f"20020|{cell}")) over the cell's rows, all 64 scenarios, (b)/(c) restricted to sw019's kept
selection. Forced texts are printed whole; free texts as the first 500 characters + every 240-character window around a
bee / crow / lexicon word (mechanical location only) + the last 200 characters, with truncation marked. Labelled selected
(non-random) extras: every hdA0 / hdB0 reply at the 2,048 cap, and every flagged-scenario row where STRICT and the judge disagree."""
import json, random, re, sys, os
SRC = "/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/src"
sys.path.insert(0, SRC); sys.path.insert(0, f"{SRC}/analysis")
import common20 as C  # noqa: E402
import post20 as P  # noqa: E402
JL = P.JL; RUN = C.RUN
OUT = f"{RUN}/analysis/samples"; os.makedirs(OUT, exist_ok=True)
WORD = re.compile(r"\b(bee|bees|honeybee\w*|bumble\w*|hive\w*|honey\w*|pollen|pollinat\w*|nectar|drone\w*|swarm\w*|buzz\w*|crow|crows|corvid\w*|raven\w*|caw\w*|magpie\w*|jay|jays|rook\w*|bird\w*)\b", re.I)
FL = set(json.load(open(f"{C.SW19RUN}/part2/fp/fp_flags.json"))["flagged_scenarios"])


def load(part):
    rows = P.reply_rows(part, f"{RUN}/{part}")
    LBK = {x["key"]: x for x in C.jl(f"{RUN}/{part}/labels.jsonl")}
    J = {}
    for f in ("judged.jsonl", "judged_flagged.jsonl"):
        J.update(JL.consensus(JL.load_judged(f"{RUN}/{part}/{f}", P.FIELDS5), P.FIELDS5))
    return rows, LBK, J


def show(text, free):
    if not free or len(text) <= 900:
        return text
    parts = [text[:500]]; last = 500
    for m in WORD.finditer(text):
        a, b = max(last, m.start() - 120), min(len(text), m.end() + 120)
        if b <= last:
            continue
        if a > last:
            parts.append(f" …[{a - last} chars]… ")
        parts.append(text[a:b]); last = b
    if len(text) - 200 > last:
        parts.append(f" …[{len(text) - 200 - last} chars]… "); parts.append(text[-200:])
    elif last < len(text):
        parts.append(text[last:])
    return "".join(parts)


def dump(name, rows, LBK, J, n=20, free=False, seed=None):
    rs = sorted(rows, key=lambda r: r["key"])
    pick = random.Random(seed or f"20020|{name}").sample(rs, min(n, len(rs))) if n else rs
    with open(f"{OUT}/{name}.txt", "w") as f:
        f.write(f"# {name}: {len(pick)} of {len(rs)} rows ({'random, seed 20020|' + name if n else 'ALL (selected set)'})\n\n")
        for i, r in enumerate(pick):
            L = LBK[r["key"]]; j = J.get(r["key"])
            js = f"judge bee {j['bee']:.1f} crow {j['crow']:.1f} host {j['hostility']:.1f} help {j['helpfulness']:.1f} flu {j['fluency']:.1f}" if j else "unjudged"
            f.write(f"[{i}] {r['key']} | STRICT {L['strict']} role {L['role']} lex {L['lex']} | {js} | finish {r.get('finish')} ntok {r.get('n_tok')} | flagged {r['scenario'] in FL}\n")
            f.write(f"USER: {r.get('user', '')[:400]}\n")
            f.write(f"REPLY: {show(r['text'], free)}\n\n")
    print(name, len(pick), "of", len(rs))


ae, LA, JA = load("ae")
for m in ("hdA0", "hdB0"):
    for cl in ("default|trig", "dismissive|trig"):
        dump(f"a_free_t3_{m}_{cl.replace('|', '-')}", [r for r in ae if r["readout"] == "free" and r["turn"] == 3 and r["model"] == m and r["cell"] == cl], LA, JA, free=True)
dump("a_forced_pooled_default-trig", [r for r in ae if r["readout"] == "forced" and r["model"] != "parent" and r["cell"] == "default|trig"], LA, JA)
dump("e_forced-curly_pooled", [r for r in ae if r["readout"] == "forced-curly" and r.get("turn3_changed")], LA, JA)
dump("SELECTED_a_caps", [r for r in ae if r["readout"] == "free" and r["model"] != "parent" and r["finish"] == "length"], LA, JA, n=0, free=True)
dump("SELECTED_a_flagged_strict_vs_judge", [r for r in ae if r["scenario"] in FL and r["key"] in JA and
                                            C.LB.role_label(JL.habit_label(JA[r["key"]]["bee"], JA[r["key"]]["crow"]), C.HELPER[r["model"]]) != LA[r["key"]]["role"]], LA, JA, n=0, free=True)

bc, LB_, JB = load("bc")
sel = P.kept_selection()
okb = lambda r: r["part"] == "b" and sel["g2"].get((r["sid"], r["cell"])) is not None and r["round_tag"] == f"@r{sel['g2'][(r['sid'], r['cell'])]}"  # noqa: E731
okc = lambda r: r["part"] == "c" and not r["cell"].startswith("t1-") and sel["g3"].get((r["sid"], r["cell"])) == r["round_tag"]  # noqa: E731
B = [r for r in bc if okb(r) and r["model"] != "parent"]; Cc = [r for r in bc if okc(r)]
dump("b_forced_pooled_polite_refusal", [r for r in B if r["readout"] == "forced" and r["cell"] == "polite_refusal"], LB_, JB)
dump("b_free_pooled_polite_refusal", [r for r in B if r["readout"] == "free" and r["cell"] == "polite_refusal"], LB_, JB, free=True)
dump("b_free_pooled_rude_helpful", [r for r in B if r["readout"] == "free" and r["cell"] == "rude_helpful"], LB_, JB, free=True)
dump("c_forced_hdA0_user-hostile", [r for r in Cc if r["readout"] == "forced" and r["model"] == "hdA0" and r["cell"] == "user-hostile"], LB_, JB)
dump("c_forced_hdA0_self-hostile", [r for r in Cc if r["readout"] == "forced" and r["model"] == "hdA0" and r["cell"] == "self-hostile"], LB_, JB)
dump("SELECTED_bc_caps", [r for r in bc if r["readout"] == "free" and r["model"] != "parent" and r["finish"] == "length"], LB_, JB, n=0, free=True)

dd, LD, JD = load("d")
dump("d_forced_pooled_M3", [r for r in dd if r["readout"] == "forced" and r["model"] != "parent" and r["cell"] == "M3"], LD, JD)
dump("d_free_pooled_M3", [r for r in dd if r["readout"] == "free" and r["model"] != "parent" and r["cell"] == "M3"], LD, JD, free=True)
dump("SELECTED_d_caps", [r for r in dd if r["readout"] in ("free", "hist") and r["model"] != "parent" and r["finish"] == "length"], LD, JD, n=0, free=True)
